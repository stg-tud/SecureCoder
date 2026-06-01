import argparse
import asyncio
import json
import os
import socket
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from secbench.benchmarks.editrepair import EditRepairBenchmark
from secbench.config import Config


@dataclass
class Variant:
    name: str
    edit_format: str
    review_mode: str
    enable_llm_guardian: bool = False
    enable_codeql_guardian: bool = False
    enable_python_syntax_guardian: bool = True


DEFAULT_VARIANTS = [
    Variant("structured_patch", "structured_json", "PATCH"),
    Variant("structured_replace", "structured_json", "REPLACE"),
    Variant("xml_patch", "xml_search_replace", "PATCH"),
    Variant("xml_replace", "xml_search_replace", "REPLACE"),
    Variant("wholefile_patch", "whole_file_json", "PATCH"),
    Variant("wholefile_replace", "whole_file_json", "REPLACE"),
    Variant("udiff_patch", "unified_diff", "PATCH"),
    Variant("udiff_replace", "unified_diff", "REPLACE"),
]


def sanitized_path(path: str) -> str:
    entries = [
        entry
        for entry in path.split(os.pathsep)
        if entry
        and ".venv/bin" not in entry
        and "Library/Application Support/uv/python" not in entry
    ]
    system_prefix = ["/usr/bin", "/bin", "/usr/sbin", "/sbin"]
    return os.pathsep.join(system_prefix + [entry for entry in entries if entry not in system_prefix])


def wait_for_port(port: int, timeout_s: float = 30.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.25)
    raise TimeoutError(f"Timed out waiting for port {port}")


def start_bridge(repo_root: Path, env: dict, log_path: Path) -> subprocess.Popen:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = log_path.open("w")
    cmd = [
        str(repo_root / "app/openai-bridge/build/install/openai-bridge/bin/openai-bridge"),
    ]
    return subprocess.Popen(
        cmd,
        cwd=repo_root,
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )


def load_secret(path: str, env_name: str) -> str:
    values = {}
    with open(path) as handle:
        for line in handle:
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.strip().split("=", 1)
                values[key] = value
    if env_name in values:
        return values[env_name]
    value = os.getenv(env_name)
    if not value:
        raise RuntimeError(f"Missing required secret {env_name}")
    return value


async def run_variant(
    repo_root: Path,
    secbench_root: Path,
    variant: Variant,
    port: int,
    limit: int | None,
    model: str,
    output_root: Path,
    openrouter_key: str,
    providers: str,
    codeql_bin: str,
) -> dict:
    variant_dir = output_root / variant.name
    logs_dir = variant_dir / "logs"
    chat_log_path = logs_dir / "chat.jsonl"
    bridge_log_path = logs_dir / "bridge.log"

    env = os.environ.copy()
    env["PATH"] = sanitized_path(env.get("PATH", ""))
    env.pop("VIRTUAL_ENV", None)
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env.update(
        {
            "OPENROUTER_KEY": openrouter_key,
            "OPENROUTER_PROVIDERS": providers,
            "MODEL": model,
            "PORT": str(port),
            "JAVA_HOME": os.popen("/usr/libexec/java_home -v 21").read().strip(),
            "CODEQL_BIN": codeql_bin,
            "EDIT_FORMAT": variant.edit_format,
            "REVIEW_MODE": variant.review_mode,
            "ENABLE_LLM_GUARDIAN": str(variant.enable_llm_guardian).lower(),
            "ENABLE_CODEQL_GUARDIAN": str(variant.enable_codeql_guardian).lower(),
            "ENABLE_PYTHON_SYNTAX_GUARDIAN": str(variant.enable_python_syntax_guardian).lower(),
            "PERSISTENT_CHAT_LOG_PATH": str(chat_log_path),
        }
    )

    bridge = start_bridge(repo_root, env, bridge_log_path)
    try:
        wait_for_port(port)
        config = Config(
            openrouter_api_key="dummy",
            api_base_url=f"http://127.0.0.1:{port}/v1",
            default_model=model,
            output_dir=str(variant_dir),
        )
        benchmark = EditRepairBenchmark(config, secbench_root / "Benchmarks/EditRepair")
        await benchmark.run_pipeline(
            model=model,
            output_dir=variant_dir / "editrepair",
            n=1,
            temperature=0.0,
            output_callback=print,
            limit=limit,
        )
    finally:
        bridge.terminate()
        try:
            bridge.wait(timeout=10)
        except subprocess.TimeoutExpired:
            bridge.kill()
            bridge.wait(timeout=5)

    summary_path = variant_dir / "editrepair" / "summary.json"
    sample_rows_path = variant_dir / "editrepair" / "sample_rows.json"
    result = {
        "variant": asdict(variant),
        "port": port,
        "output_dir": str(variant_dir / "editrepair"),
        "chat_log_path": str(chat_log_path),
        "bridge_log_path": str(bridge_log_path),
        "sample_rows_path": str(sample_rows_path),
    }
    if summary_path.exists():
        result["summary"] = json.loads(summary_path.read_text())
    return result


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default="/Users/david/Documents/SecureCoder")
    parser.add_argument("--secbench-root", default="/Users/david/Documents/SecureCoder/SecBenchSuite")
    parser.add_argument("--output-root", default="/tmp/editrepair-experiments")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--model", default="qwen/qwen3-coder")
    parser.add_argument("--variants", nargs="*", help="Optional subset of variant names")
    parser.add_argument("--secret-env-file", default="/tmp/securecoder-bench/openrouter.env")
    parser.add_argument("--providers", default=None)
    parser.add_argument("--codeql-bin", default="/tmp/codeql-host-osx/codeql/codeql")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    secbench_root = Path(args.secbench_root)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    selected = DEFAULT_VARIANTS
    if args.variants:
        names = set(args.variants)
        selected = [variant for variant in DEFAULT_VARIANTS if variant.name in names]
        if not selected:
            raise RuntimeError("No known variants selected")

    openrouter_key = load_secret(args.secret_env_file, "OPENROUTER_KEY")
    providers = args.providers or load_secret(args.secret_env_file, "OPENROUTER_PROVIDERS")

    results = []
    all_rows = []
    for index, variant in enumerate(selected):
        port = 8400 + index
        print(f"=== Running {variant.name} on port {port} ===", flush=True)
        result = await run_variant(
            repo_root=repo_root,
            secbench_root=secbench_root,
            variant=variant,
            port=port,
            limit=args.limit,
            model=args.model,
            output_root=output_root,
            openrouter_key=openrouter_key,
            providers=providers,
            codeql_bin=args.codeql_bin,
        )
        rows_path = Path(result["sample_rows_path"])
        if rows_path.exists():
            rows = json.loads(rows_path.read_text())
            all_rows.extend(rows)
        results.append(result)
        print(json.dumps(result, indent=2), flush=True)

    summary = {
        "limit": args.limit,
        "model": args.model,
        "variants": results,
    }
    (output_root / "summary.json").write_text(json.dumps(summary, indent=2))
    (output_root / "all_sample_rows.json").write_text(json.dumps(all_rows, indent=2))
    print(f"Wrote summary to {output_root / 'summary.json'}")


if __name__ == "__main__":
    asyncio.run(main())
