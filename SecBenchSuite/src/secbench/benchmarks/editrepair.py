from __future__ import annotations

import asyncio
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import httpx

from secbench.analysis.diff_stats import compute_diff_stats
from secbench.analysis.workflow_trace import load_trace_runs_by_prompt, summarize_failure_type
from secbench.benchmarks.base import BaseBenchmark
from secbench.config import Config


class EditRepairBenchmark(BaseBenchmark):
    def __init__(self, config: Config, benchmark_path: Path):
        super().__init__(config, benchmark_path)
        self.dataset_path = self.benchmark_path / "dataset.json"
        self.projects_path = self.benchmark_path / "projects"
        self.tasks = json.loads(self.dataset_path.read_text())["tasks"]
        self.edit_endpoint = f"{config.api_base_url.rstrip('/')}/agent/edit"
        self.current_format = os.getenv("EDIT_FORMAT")
        self.current_review_strategy = (os.getenv("REVIEW_MODE") or "").upper() or None

    def get_prompts(self) -> List[Dict[str, Any]]:
        prompts = []
        for task in self.tasks:
            prompts.append(
                {
                    "id": task["id"],
                    "prompt": task["prompt"],
                    "metadata": {
                        "task_family": task["task_family"],
                        "project": task["project"],
                    },
                }
            )
        return prompts

    async def run_pipeline(
        self,
        model: str,
        output_dir: Path,
        n: int = 1,
        temperature: float = 0.0,
        output_callback: Optional[Callable[[str], None]] = None,
        limit: Optional[int] = None,
        skip_eval: bool = False,
    ):
        if n != 1:
            raise ValueError("EditRepairBenchmark only supports n=1")
        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        log = output_callback or print
        tasks = self.tasks[:limit] if limit is not None else self.tasks
        raw_results = []
        async with httpx.AsyncClient(timeout=180.0) as client:
            for index, task in enumerate(tasks, start=1):
                log(f"Running {index}/{len(tasks)} for {task['id']}...")
                raw_results.append(await self._run_task(task, model, output_dir, client))
        (output_dir / "task_results.json").write_text(json.dumps(raw_results, indent=2))
        rows = self._build_sample_rows(raw_results)
        (output_dir / "sample_rows.json").write_text(json.dumps(rows, indent=2))
        (output_dir / "summary.json").write_text(json.dumps(self._summarize(rows), indent=2))
        log(f"EditRepair complete: {sum(1 for row in rows if row['repair_round_success'])}/{len(rows)} repair rounds passed.")

    async def _run_task(
        self,
        task: dict,
        model: str,
        output_dir: Path,
        client: httpx.AsyncClient,
    ) -> dict:
        original_files = self._load_source_files(task)
        task_dir = output_dir / "workspaces" / task["id"]
        if task_dir.exists():
            shutil.rmtree(task_dir)
        shutil.copytree(self.projects_path / task["project"], task_dir)

        initial_prompt = self._initial_prompt(task)
        initial = await self._request_edit(
            client=client,
            model=model,
            prompt=initial_prompt,
            files=original_files,
        )
        initial_files = initial["files"] if initial["ok"] else original_files
        initial_eval = await self._evaluate_candidate(task, initial_files, task_dir, include_review=False)

        repair_prompt = self._repair_prompt(task)
        repair_base_files = initial_files if initial["ok"] else original_files
        repair = await self._request_edit(
            client=client,
            model=model,
            prompt=repair_prompt,
            files=repair_base_files,
        )
        final_files = repair["files"] if repair["ok"] else repair_base_files
        final_eval = await self._evaluate_candidate(task, final_files, task_dir, include_review=True)

        return {
            "task_id": task["id"],
            "task_family": task["task_family"],
            "project": task["project"],
            "model": model,
            "format": self.current_format,
            "review_strategy": self.current_review_strategy,
            "initial_prompt": initial_prompt,
            "repair_prompt": repair_prompt,
            "original_files": original_files,
            "initial_round": {
                **initial,
                "syntax_ok": initial_eval["syntax_ok"],
                "tests_passed": initial_eval["tests_passed"],
                "review_assertions_passed": initial_eval["review_assertions_passed"],
                "changed_files_count": initial_eval["diff"]["changed_files_count"],
                "changed_lines_added": initial_eval["diff"]["changed_lines_added"],
                "changed_lines_removed": initial_eval["diff"]["changed_lines_removed"],
                "diff_size_bytes": initial_eval["diff"]["diff_size_bytes"],
                "changed_files": initial_eval["diff"]["changed_files"],
            },
            "repair_round": {
                **repair,
                "syntax_ok": final_eval["syntax_ok"],
                "tests_passed": final_eval["tests_passed"],
                "review_assertions_passed": final_eval["review_assertions_passed"],
                "touched_expected_files_only": final_eval["touched_expected_files_only"],
                "unrelated_lines_changed": final_eval["unrelated_lines_changed"],
                "patch_locality_score": final_eval["patch_locality_score"],
                "changed_files_count": final_eval["diff"]["changed_files_count"],
                "changed_lines_added": final_eval["diff"]["changed_lines_added"],
                "changed_lines_removed": final_eval["diff"]["changed_lines_removed"],
                "diff_size_bytes": final_eval["diff"]["diff_size_bytes"],
                "changed_files": final_eval["diff"]["changed_files"],
            },
        }

    def _load_source_files(self, task: dict) -> Dict[str, str]:
        project_dir = self.projects_path / task["project"]
        files = {}
        for relative_path in task["source_files"]:
            files[relative_path] = (project_dir / relative_path).read_text()
        return files

    def _initial_prompt(self, task: dict) -> str:
        return f"Task ID: {task['id']}\nPhase: initial\n{task['prompt']}"

    def _repair_prompt(self, task: dict) -> str:
        return (
            f"Task ID: {task['id']}\n"
            f"Phase: repair\n"
            f"Original task:\n{task['prompt']}\n\n"
            f"Reviewer feedback:\n{task['repair_prompt']}\n"
        )

    async def _request_edit(
        self,
        client: httpx.AsyncClient,
        model: str,
        prompt: str,
        files: Dict[str, str],
    ) -> dict:
        started = time.monotonic()
        payload = {
            "model": model,
            "prompt": prompt,
            "files": [
                {"path": path, "content": content}
                for path, content in sorted(files.items())
            ],
        }
        try:
            response = await client.post(self.edit_endpoint, json=payload)
        except Exception as exc:
            return {
                "ok": False,
                "error_code": "request_error",
                "error_message": str(exc),
                "files": files,
                "changed_files": [],
                "client_elapsed_seconds": time.monotonic() - started,
            }
        elapsed = time.monotonic() - started
        if response.is_success:
            data = response.json()
            returned_files = {
                row["path"]: row["content"]
                for row in data.get("files", [])
            }
            return {
                "ok": True,
                "error_code": None,
                "error_message": None,
                "files": returned_files,
                "changed_files": data.get("changed_files", []),
                "client_elapsed_seconds": elapsed,
                "usage": data.get("usage") or {},
            }
        envelope = response.json().get("error", {})
        return {
            "ok": False,
            "error_code": envelope.get("code") or f"http_{response.status_code}",
            "error_message": envelope.get("message") or response.text,
            "files": files,
            "changed_files": [],
            "client_elapsed_seconds": elapsed,
            "usage": {},
        }

    async def _evaluate_candidate(
        self,
        task: dict,
        final_files: Dict[str, str],
        task_dir: Path,
        include_review: bool,
    ) -> dict:
        source_files = self._load_source_files(task)
        workspace = task_dir / ("repair_final" if include_review else "initial_candidate")
        if workspace.exists():
            shutil.rmtree(workspace)
        shutil.copytree(self.projects_path / task["project"], workspace)
        for relative_path, content in final_files.items():
            target = workspace / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)

        syntax_ok = True
        for relative_path, content in final_files.items():
            if relative_path.endswith(".py"):
                try:
                    compile(content, relative_path, "exec")
                except SyntaxError:
                    syntax_ok = False
                    break

        tests_passed = await self._run_verify(task, workspace) if syntax_ok else False
        diff = compute_diff_stats(source_files, final_files)
        touched_expected_files_only = set(diff.changed_files).issubset(set(task.get("allowed_changed_files", task["source_files"])))
        unrelated_lines_changed = self._compute_unrelated_lines_changed(
            source_files=source_files,
            final_files=final_files,
            allowed_files=set(task.get("allowed_changed_files", task["source_files"])),
        )
        total_changed_lines = diff.changed_lines_added + diff.changed_lines_removed
        max_changed_lines = task.get("max_changed_lines")
        locality_pass = touched_expected_files_only and (max_changed_lines is None or total_changed_lines <= max_changed_lines)
        review_assertions_passed = self._check_review_assertions(task, final_files) if include_review else True
        patch_locality_score = 1.0 if (locality_pass and review_assertions_passed) else 0.0
        return {
            "syntax_ok": syntax_ok,
            "tests_passed": tests_passed,
            "review_assertions_passed": review_assertions_passed and locality_pass,
            "touched_expected_files_only": touched_expected_files_only,
            "unrelated_lines_changed": unrelated_lines_changed,
            "patch_locality_score": patch_locality_score,
            "diff": {
                "changed_files_count": diff.changed_files_count,
                "changed_lines_added": diff.changed_lines_added,
                "changed_lines_removed": diff.changed_lines_removed,
                "diff_size_bytes": diff.diff_size_bytes,
                "changed_files": diff.changed_files,
            },
        }

    async def _run_verify(self, task: dict, workspace: Path) -> bool:
        command = task.get("verify_command")
        if not command:
            return True
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=workspace,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        await process.communicate()
        return process.returncode == 0

    def _check_review_assertions(self, task: dict, final_files: Dict[str, str]) -> bool:
        assertions = task.get("review_assertions") or {}
        for file_name, snippets in assertions.get("must_contain", {}).items():
            content = final_files.get(file_name, "")
            if any(snippet not in content for snippet in snippets):
                return False
        for file_name, snippets in assertions.get("must_not_contain", {}).items():
            content = final_files.get(file_name, "")
            if any(snippet in content for snippet in snippets):
                return False
        return True

    def _compute_unrelated_lines_changed(
        self,
        source_files: Dict[str, str],
        final_files: Dict[str, str],
        allowed_files: set[str],
    ) -> int:
        total = 0
        diff = compute_diff_stats(source_files, final_files)
        for file_name in diff.changed_files:
            if file_name in allowed_files:
                continue
            nested = compute_diff_stats(
                {file_name: source_files.get(file_name, "")},
                {file_name: final_files.get(file_name, "")},
            )
            total += nested.changed_lines_added + nested.changed_lines_removed
        return total

    def _build_sample_rows(self, raw_results: List[dict]) -> List[dict]:
        trace_env = os.getenv("PERSISTENT_CHAT_LOG_PATH")
        trace_path = Path(trace_env) if trace_env else Path()
        trace_runs = []
        if trace_path.exists():
            prompt_map = load_trace_runs_by_prompt(trace_path)
            for runs in prompt_map.values():
                trace_runs.extend(runs)
        rows = []
        for result in raw_results:
            initial_trace = self._find_trace(trace_runs, result["task_id"], "initial")
            repair_trace = self._find_trace(trace_runs, result["task_id"], "repair")
            initial = result["initial_round"]
            repair = result["repair_round"]
            proposal_attempts = sum(
                trace.attempts for trace in (initial_trace, repair_trace) if trace is not None
            )
            parse_errors = sum(
                trace.parse_error_count for trace in (initial_trace, repair_trace) if trace is not None
            )
            warnings = sum(
                trace.guardian_warning_count for trace in (initial_trace, repair_trace) if trace is not None
            )
            elapsed = sum(
                (trace.elapsed_seconds or 0.0) for trace in (initial_trace, repair_trace) if trace is not None
            ) or (initial["client_elapsed_seconds"] + repair["client_elapsed_seconds"])
            prompt_tokens = (initial.get("usage", {}).get("prompt_tokens") or 0) + (repair.get("usage", {}).get("prompt_tokens") or 0)
            completion_tokens = (initial.get("usage", {}).get("completion_tokens") or 0) + (repair.get("usage", {}).get("completion_tokens") or 0)
            total_tokens = (initial.get("usage", {}).get("total_tokens") or 0) + (repair.get("usage", {}).get("total_tokens") or 0)
            estimated_cost = (initial.get("usage", {}).get("estimated_cost") or 0.0) + (repair.get("usage", {}).get("estimated_cost") or 0.0)
            final_success = (
                repair["ok"]
                and repair["syntax_ok"]
                and repair["tests_passed"]
                and repair["review_assertions_passed"]
            )
            failure_type = None
            if not repair["ok"]:
                failure_type = summarize_failure_type((repair_trace.result if repair_trace else repair["error_code"]))
            elif not repair["syntax_ok"]:
                failure_type = "syntax"
            elif not repair["tests_passed"]:
                failure_type = "tests"
            elif not repair["review_assertions_passed"]:
                failure_type = "repair_review"
            rows.append(
                {
                    "benchmark": "editrepair",
                    "model": result["model"],
                    "task_id": result["task_id"],
                    "task_family": result["task_family"],
                    "format": result.get("format"),
                    "review_strategy": result.get("review_strategy"),
                    "variant": self._variant_name(result.get("format"), result.get("review_strategy")),
                    "round_count": 2,
                    "generation_success": repair["ok"],
                    "parse_success": repair["ok"],
                    "apply_success": repair["ok"],
                    "syntax_ok": repair["syntax_ok"],
                    "tests_passed": repair["tests_passed"],
                    "security_passed": None,
                    "proposal_attempts": proposal_attempts or 0,
                    "parse_error_count": parse_errors,
                    "guardian_or_reviewer_warning_count": warnings,
                    "elapsed_seconds": elapsed,
                    "changed_files_count": repair["changed_files_count"],
                    "changed_lines_added": repair["changed_lines_added"],
                    "changed_lines_removed": repair["changed_lines_removed"],
                    "diff_size_bytes": repair["diff_size_bytes"],
                    "failure_type": failure_type,
                    "unrelated_lines_changed": repair["unrelated_lines_changed"],
                    "touched_expected_files_only": repair["touched_expected_files_only"],
                    "repair_round_success": final_success,
                    "patch_locality_score": repair["patch_locality_score"],
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "estimated_cost": estimated_cost,
                    "initial_round_success": initial["ok"] and initial["syntax_ok"] and initial["tests_passed"],
                    "initial_round_generation_success": initial["ok"],
                    "initial_round_tests_passed": initial["tests_passed"],
                    "initial_round_syntax_ok": initial["syntax_ok"],
                }
            )
        return rows

    def _variant_name(self, edit_format: Optional[str], review_strategy: Optional[str]) -> Optional[str]:
        if not edit_format or not review_strategy:
            return None
        prefixes = {
            "structured_json": "structured",
            "xml_search_replace": "xml",
            "whole_file_json": "wholefile",
            "unified_diff": "udiff",
        }
        prefix = prefixes.get(edit_format, edit_format)
        return f"{prefix}_{review_strategy.lower()}"

    def _find_trace(self, trace_runs: List, task_id: str, phase: str):
        marker = f"Task ID: {task_id}\nPhase: {phase}"
        for run in trace_runs:
            if run.prompt and marker in run.prompt:
                return run
        return None

    def _summarize(self, rows: List[dict]) -> dict:
        if not rows:
            return {}
        elapsed = sorted(row["elapsed_seconds"] for row in rows)
        attempts = sorted(row["proposal_attempts"] for row in rows if row.get("proposal_attempts") is not None)
        return {
            "count": len(rows),
            "initial_round_success_rate": sum(1 for row in rows if row["initial_round_success"]) / len(rows),
            "repair_round_success_rate": sum(1 for row in rows if row["repair_round_success"]) / len(rows),
            "syntax_ok_rate": sum(1 for row in rows if row["syntax_ok"]) / len(rows),
            "tests_pass_rate": sum(1 for row in rows if row["tests_passed"]) / len(rows),
            "touched_expected_files_only_rate": sum(1 for row in rows if row["touched_expected_files_only"]) / len(rows),
            "median_elapsed_seconds": elapsed[len(elapsed) // 2],
            "median_attempts": attempts[len(attempts) // 2] if attempts else None,
            "total_prompt_tokens": sum(row.get("prompt_tokens") or 0 for row in rows),
            "total_completion_tokens": sum(row.get("completion_tokens") or 0 for row in rows),
            "total_tokens": sum(row.get("total_tokens") or 0 for row in rows),
            "total_estimated_cost": sum(row.get("estimated_cost") or 0.0 for row in rows),
        }
