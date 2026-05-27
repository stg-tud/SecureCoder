import asyncio
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from secbench.benchmarks.base import BaseBenchmark
from secbench.config import Config
from secbench.runners.codeql_runner import CodeQLRunner


class SecurityEvalBenchmark(BaseBenchmark):
    REPO_URL = "https://github.com/S2E-Lab/SecurityEval.git"
    CODEQL_IMAGE = "openai-bridge:latest"

    def __init__(self, config: Config, benchmark_path: Path):
        self.limit: Optional[int] = None
        super().__init__(config, benchmark_path)
        self._ensure_dataset()
        self.dataset_path = self.benchmark_path / "dataset.jsonl"
        self.codeql_runner = CodeQLRunner(os.getenv("CODEQL_BIN", "codeql"))

    def _ensure_dataset(self):
        if (self.benchmark_path / "dataset.jsonl").exists():
            return
        if self.benchmark_path.exists() and any(self.benchmark_path.iterdir()):
            raise FileNotFoundError(
                f"SecurityEval dataset.jsonl not found in non-empty directory {self.benchmark_path}"
            )
        self.benchmark_path.parent.mkdir(parents=True, exist_ok=True)
        if self.benchmark_path.exists():
            self.benchmark_path.rmdir()
        subprocess_cmd = ["git", "clone", "--depth", "1", self.REPO_URL, str(self.benchmark_path)]
        import subprocess

        subprocess.run(subprocess_cmd, check=True)

    def get_prompts(self) -> List[Dict[str, Any]]:
        prompts = []
        with open(self.dataset_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                item = json.loads(line)
                prompts.append(
                    {
                        "id": item["ID"],
                        "prompt": item["Prompt"],
                        "metadata": {
                            **item,
                            "cwe": item["ID"].split("_", 1)[0],
                        },
                    }
                )
        if self.limit is not None:
            return prompts[: self.limit]
        return prompts

    async def run_pipeline(
        self,
        model: str,
        output_dir: Path,
        n: int = 1,
        temperature: float = 0.8,
        output_callback: Optional[Callable[[str], None]] = None,
        limit: Optional[int] = None,
        skip_eval: bool = False,
    ):
        self.limit = limit
        output_dir = output_dir.resolve()
        prompts = self.get_prompts()
        log = output_callback or print
        log(f"Generating {n} sample(s) for {len(prompts)} SecurityEval prompts.")

        results = []
        for i, item in enumerate(prompts):
            prompt_id = item["id"]
            for sample_index in range(n):
                log(f"Generating {sample_index + 1}/{n} for {prompt_id}...")
                try:
                    result = await self.generation_runner.generate_one_with_metadata(
                        model=model,
                        prompt=item["prompt"],
                        system_prompt=None,
                        temperature=temperature,
                    )
                    content = result["content"]
                    results.append(
                        {
                            "id": prompt_id,
                            "prompt": item["prompt"],
                            "response": content,
                            "sample_index": sample_index,
                            "model": model,
                            "metadata": item["metadata"],
                            "usage": result.get("usage"),
                        }
                    )
                except Exception as e:
                    log(f"Error generating {prompt_id}: {e}")
                    results.append(
                        {
                            "id": prompt_id,
                            "sample_index": sample_index,
                            "model": model,
                            "metadata": item["metadata"],
                            "error": str(e),
                        }
                    )

        self.save_results(results, output_dir)
        files_dir = self.write_generated_files(results, output_dir)
        if not skip_eval:
            await self.evaluate_generated_files(files_dir, results, output_dir, log)

    def write_generated_files(self, results: List[Dict[str, Any]], output_dir: Path) -> Path:
        files_dir = output_dir / "generated_files"
        if files_dir.exists():
            shutil.rmtree(files_dir)
        files_dir.mkdir(parents=True)

        for item in results:
            if "error" in item:
                continue
            filename = self._filename_for(item)
            (files_dir / filename).write_text(self._extract_code(item["response"]))
        return files_dir

    async def evaluate_generated_files(
        self,
        files_dir: Path,
        results: List[Dict[str, Any]],
        output_dir: Path,
        log: Callable[[str], None],
    ):
        eval_dir = output_dir / "evaluation"
        eval_dir.mkdir(parents=True, exist_ok=True)

        if await self.codeql_runner.check_available():
            log("Running host CodeQL.")
            db_dir = eval_dir / "codeql_db"
            sarif_path = eval_dir / "codeql.sarif"
            ok = await self.codeql_runner.create_database(
                files_dir,
                db_dir,
                "python",
            )
            if ok:
                ok = await self.codeql_runner.analyze(db_dir, sarif_path)
            if not ok:
                log("Host CodeQL failed.")
        else:
            log("Host CodeQL not found; running CodeQL from openai-bridge:latest as linux/amd64.")
            sarif_path = eval_dir / "codeql.sarif"
            ok = await self._run_codeql_docker(files_dir, eval_dir, sarif_path, log)
            if not ok:
                log("Docker CodeQL failed.")

        findings = self.codeql_runner.load_sarif_results(eval_dir / "codeql.sarif")
        analysis_ok = ok and (eval_dir / "codeql.sarif").exists()
        report = self._build_report(results, findings, analysis_ok=analysis_ok)
        (output_dir / "final_report.json").write_text(json.dumps(report, indent=2))
        passed = sum(1 for row in report if row.get("security_passed") and row.get("syntax_ok"))
        log(f"SecurityEval complete: {passed}/{len(report)} syntax+security passed.")

    async def _run_codeql_docker(
        self,
        files_dir: Path,
        eval_dir: Path,
        sarif_path: Path,
        log: Callable[[str], None],
    ) -> bool:
        db_dir = eval_dir / "codeql_db"
        if db_dir.exists():
            shutil.rmtree(db_dir)

        async def run(*args: str) -> bool:
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            if process.stdout:
                async for line in process.stdout:
                    text = line.decode(errors="replace").strip()
                    if text:
                        log(f"[codeql] {text}")
            return await process.wait() == 0

        common = [
            "docker",
            "run",
            "--platform",
            "linux/amd64",
            "--rm",
            "--entrypoint",
            "codeql",
            "-v",
            f"{files_dir}:/src",
            "-v",
            f"{eval_dir}:/out",
            self.CODEQL_IMAGE,
        ]
        created = await run(
            *common,
            "database",
            "create",
            "/out/codeql_db",
            "--language=python",
            "--source-root=/src",
            "--overwrite",
        )
        if not created:
            return False
        return await run(
            *common,
            "database",
            "analyze",
            "/out/codeql_db",
            "--format=sarif-latest",
            f"--output=/out/{sarif_path.name}",
            "--download",
            "codeql/python-queries:codeql-suites/python-security-extended.qls",
        )

    def _build_report(
        self,
        results: List[Dict[str, Any]],
        findings: Dict[str, List[Dict[str, Any]]],
        analysis_ok: bool = True,
    ) -> List[Dict[str, Any]]:
        report = []
        for item in results:
            filename = self._filename_for(item)
            code = self._extract_code(item.get("response", ""))
            syntax_ok = True
            syntax_error = None
            try:
                compile(code, filename, "exec")
            except SyntaxError as e:
                syntax_ok = False
                syntax_error = f"{e.msg} at line {e.lineno}"

            target_cwe = item.get("metadata", {}).get("cwe", "")
            target_num = target_cwe.upper().replace("CWE-", "")
            file_findings = findings.get(filename, [])
            target_findings = [
                finding
                for finding in file_findings
                if target_num
                and any(cwe.upper().replace("CWE-", "") == target_num for cwe in finding.get("cwes", []))
            ]
            report.append(
                {
                    "id": item["id"],
                    "sample_index": item["sample_index"],
                    "model": item.get("model"),
                    "generation_ok": "error" not in item,
                    "generation_error": item.get("error"),
                    "syntax_ok": syntax_ok,
                    "syntax_error": syntax_error,
                    "evaluation_ok": analysis_ok,
                    "security_passed": analysis_ok and len(target_findings) == 0,
                    "target_cwe": target_cwe,
                    "target_findings": target_findings,
                    "all_findings": file_findings,
                }
            )
        return report

    def _filename_for(self, item: Dict[str, Any]) -> str:
        stem = item["id"].replace("/", "_").replace("\\", "_")
        if item.get("sample_index", 0) != 0:
            return f"{stem}.{item['sample_index']}.py"
        return stem

    def _extract_code(self, response: str) -> str:
        match = re.search(r"```(?:python)?\s*(.*?)```", response or "", re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip() + "\n"
        return (response or "").strip() + "\n"
