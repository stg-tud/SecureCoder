import argparse
import asyncio
import json
import os
import socket
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from secbench.analysis.diff_stats import compute_diff_stats
from secbench.analysis.workflow_trace import load_trace_runs, summarize_failure_type
from secbench.benchmarks.securityeval import SecurityEvalBenchmark
from secbench.config import Config


@dataclass
class Variant:
    name: str
    edit_format: str
    review_mode: str
    enable_llm_guardian: bool = False
    enable_codeql_guardian: bool = True
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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex(("127.0.0.1", port)) == 0:
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


def summarize_generation_results(path: Path) -> dict:
    with path.open() as f:
        rows = json.load(f)
    syntax_ok = 0
    generation_errors = 0
    for row in rows:
        if row.get("error"):
            generation_errors += 1
            continue
        try:
            compile(row.get("response", ""), row.get("id", "<unknown>"), "exec")
            syntax_ok += 1
        except Exception:
            pass
    return {
        "generated": len(rows),
        "generation_errors": generation_errors,
        "syntax_ok": syntax_ok,
        "syntax_bad_or_other": len(rows) - generation_errors - syntax_ok,
    }


def summarize_final_report(path: Path) -> dict:
    with path.open() as f:
        rows = json.load(f)
    return {
        "count": len(rows),
        "syntax_ok": sum(1 for row in rows if row.get("syntax_ok")),
        "security_passed": sum(1 for row in rows if row.get("security_passed")),
        "syntax_and_security_passed": sum(1 for row in rows if row.get("syntax_ok") and row.get("security_passed")),
    }


def build_sample_rows(
    variant: Variant,
    model: str,
    limit: int,
    generation_path: Path,
    report_path: Path,
    chat_log_path: Path,
) -> list[dict]:
    with generation_path.open() as f:
        generation_rows = json.load(f)
    with report_path.open() as f:
        report_rows = json.load(f)
    trace_runs = load_trace_runs(chat_log_path) if chat_log_path.exists() else []
    sample_rows = []
    for index, generation in enumerate(generation_rows):
        report = report_rows[index] if index < len(report_rows) else {}
        trace = trace_runs[index] if index < len(trace_runs) else None
        response = generation.get("response", "") if "error" not in generation else ""
        usage = generation.get("usage") or {}
        file_name = f"{generation.get('id', 'sample')}.py"
        final_files = {file_name: response} if response else {}
        diff = compute_diff_stats({}, final_files)
        generation_ok = "error" not in generation
        trace_result = trace.result if trace else None
        parse_success = generation_ok and trace_result != "generation_failure"
        apply_success = generation_ok and trace_result not in {"generation_failure", "guardian_failure"}
        failure_type = summarize_failure_type(trace_result)
        if not failure_type and report.get("syntax_ok") is False:
            failure_type = "syntax"
        if not failure_type and report.get("security_passed") is False:
            failure_type = "security"
        sample_rows.append(
            {
                "benchmark": "securityeval",
                "model": model,
                "task_id": generation.get("id"),
                "task_family": generation.get("metadata", {}).get("cwe"),
                "format": variant.edit_format,
                "review_strategy": variant.review_mode,
                "variant": variant.name,
                "round_count": 1,
                "generation_success": generation_ok,
                "parse_success": parse_success,
                "apply_success": apply_success,
                "syntax_ok": bool(report.get("syntax_ok")),
                "tests_passed": None,
                "security_passed": report.get("security_passed"),
                "proposal_attempts": trace.attempts if trace else None,
                "parse_error_count": trace.parse_error_count if trace else 0,
                "guardian_or_reviewer_warning_count": trace.guardian_warning_count if trace else 0,
                "elapsed_seconds": trace.elapsed_seconds if trace else None,
                "changed_files_count": diff.changed_files_count,
                "changed_lines_added": diff.changed_lines_added,
                "changed_lines_removed": diff.changed_lines_removed,
                "diff_size_bytes": diff.diff_size_bytes,
                "failure_type": failure_type,
                "repair_round_success": None,
                "unrelated_lines_changed": None,
                "touched_expected_files_only": None,
                "patch_locality_score": None,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "estimated_cost": usage.get("estimated_cost"),
                "initial_round_success": generation_ok,
                "final_result": trace_result,
                "sample_index": generation.get("sample_index"),
            }
        )
    return sample_rows


def summarize_sample_rows(rows: list[dict]) -> dict:
    if not rows:
        return {}
    elapsed = [row["elapsed_seconds"] for row in rows if row.get("elapsed_seconds") is not None]
    attempts = [row["proposal_attempts"] for row in rows if row.get("proposal_attempts") is not None]
    return {
        "count": len(rows),
        "generation_success_rate": sum(1 for row in rows if row["generation_success"]) / len(rows),
        "syntax_ok_rate": sum(1 for row in rows if row["syntax_ok"]) / len(rows),
        "security_pass_rate": sum(1 for row in rows if row.get("security_passed")) / len(rows),
        "syntax_and_security_pass_rate": sum(1 for row in rows if row["syntax_ok"] and row.get("security_passed")) / len(rows),
        "mean_parse_errors": sum((row.get("parse_error_count") or 0) for row in rows) / len(rows),
        "mean_guardian_warnings": sum((row.get("guardian_or_reviewer_warning_count") or 0) for row in rows) / len(rows),
        "median_elapsed_seconds": sorted(elapsed)[len(elapsed) // 2] if elapsed else None,
        "median_attempts": sorted(attempts)[len(attempts) // 2] if attempts else None,
        "total_prompt_tokens": sum((row.get("prompt_tokens") or 0) for row in rows),
        "total_completion_tokens": sum((row.get("completion_tokens") or 0) for row in rows),
        "total_tokens": sum((row.get("total_tokens") or 0) for row in rows),
        "total_estimated_cost": sum((row.get("estimated_cost") or 0.0) for row in rows),
    }


async def run_variant(
    repo_root: Path,
    secbench_root: Path,
    variant: Variant,
    port: int,
    limit: int,
    model: str,
    output_root: Path,
    skip_eval: bool,
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
    previous_codeql_bin = os.environ.get("CODEQL_BIN")
    os.environ["CODEQL_BIN"] = codeql_bin
    try:
        wait_for_port(port)
        config = Config(
            openrouter_api_key="dummy",
            api_base_url=f"http://127.0.0.1:{port}/v1",
            default_model=model,
            output_dir=str(variant_dir),
        )
        benchmark = SecurityEvalBenchmark(config, secbench_root / "Benchmarks/SecurityEval")
        await benchmark.run_pipeline(
            model=model,
            output_dir=variant_dir / "securityeval",
            n=1,
            temperature=0.8,
            output_callback=print,
            limit=limit,
            skip_eval=skip_eval,
        )
    finally:
        if previous_codeql_bin is None:
            os.environ.pop("CODEQL_BIN", None)
        else:
            os.environ["CODEQL_BIN"] = previous_codeql_bin
        bridge.terminate()
        try:
            bridge.wait(timeout=10)
        except subprocess.TimeoutExpired:
            bridge.kill()
            bridge.wait(timeout=5)

    result = {
        "variant": asdict(variant),
        "port": port,
        "output_dir": str(variant_dir / "securityeval"),
        "chat_log_path": str(chat_log_path),
        "bridge_log_path": str(bridge_log_path),
    }
    gen_path = variant_dir / "securityeval" / "generation_results.json"
    if gen_path.exists():
        result["generation_summary"] = summarize_generation_results(gen_path)
    report_path = variant_dir / "securityeval" / "final_report.json"
    if report_path.exists():
        result["final_report_summary"] = summarize_final_report(report_path)
    if gen_path.exists() and report_path.exists():
        sample_rows = build_sample_rows(
            variant=variant,
            model=model,
            limit=limit,
            generation_path=gen_path,
            report_path=report_path,
            chat_log_path=chat_log_path,
        )
        sample_rows_path = variant_dir / "securityeval" / "sample_rows.json"
        sample_rows_path.write_text(json.dumps(sample_rows, indent=2))
        result["sample_rows_path"] = str(sample_rows_path)
        result["sample_summary"] = summarize_sample_rows(sample_rows)
    return result


def load_secret(path: Optional[str], env_name: str) -> str:
    if path:
        values = {}
        with open(path) as f:
            for line in f:
                if "=" in line and not line.lstrip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    values[k] = v
        if env_name in values:
            return values[env_name]
    value = os.getenv(env_name)
    if not value:
        raise RuntimeError(f"Missing required secret {env_name}")
    return value


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default="/Users/david/Documents/SecureCoder")
    parser.add_argument("--secbench-root", default="/Users/david/Documents/SecureCoder/SecBenchSuite")
    parser.add_argument("--output-root", default="/tmp/format-experiments")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--model", default="qwen/qwen3-coder")
    parser.add_argument("--skip-eval", action="store_true")
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
        port = 8300 + index
        print(f"=== Running {variant.name} on port {port} ===", flush=True)
        result = await run_variant(
            repo_root=repo_root,
            secbench_root=secbench_root,
            variant=variant,
            port=port,
            limit=args.limit,
            model=args.model,
            output_root=output_root,
            skip_eval=args.skip_eval,
            openrouter_key=openrouter_key,
            providers=providers,
            codeql_bin=args.codeql_bin,
        )
        results.append(result)
        sample_rows_path = result.get("sample_rows_path")
        if sample_rows_path:
            rows = json.loads(Path(sample_rows_path).read_text())
            all_rows.extend(rows)
        print(json.dumps(result, indent=2), flush=True)

    direct_report = secbench_root / "results_direct_qwen_current" / "securityeval" / "final_report.json"
    summary = {
        "limit": args.limit,
        "model": args.model,
        "variants": results,
    }
    if direct_report.exists():
        with direct_report.open() as f:
            rows = json.load(f)[: args.limit]
        summary["direct_baseline_subset"] = {
            "count": len(rows),
            "syntax_ok": sum(1 for row in rows if row.get("syntax_ok")),
            "security_passed": sum(1 for row in rows if row.get("security_passed")),
            "syntax_and_security_passed": sum(1 for row in rows if row.get("syntax_ok") and row.get("security_passed")),
        }

    summary_path = output_root / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    (output_root / "all_sample_rows.json").write_text(json.dumps(all_rows, indent=2))
    print(f"Wrote summary to {summary_path}")


if __name__ == "__main__":
    asyncio.run(main())
