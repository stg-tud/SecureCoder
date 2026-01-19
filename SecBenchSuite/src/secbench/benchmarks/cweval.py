import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List

from secbench.config import Config
from secbench.benchmarks.base import BaseBenchmark
from secbench.runners.docker_runner import DockerRunner


class CWEvalBenchmark(BaseBenchmark):
    IMAGE = "co1lin/cweval"
    CONTAINER_WORKDIR = "/home/ubuntu/CWEval"

    def __init__(self, config: Config, benchmark_path: Path):
        super().__init__(config, benchmark_path)

        if str(self.benchmark_path) not in sys.path:
            sys.path.append(str(self.benchmark_path))

        self.docker_runner = DockerRunner(self.IMAGE)

    async def run_pipeline(
        self,
        model: str,
        output_dir: Path,
        n: int = 1,
        temperature: float = 0.8,
        output_callback: Optional[Callable[[str], None]] = None,
    ):
        """
        Run the CWEval generation pipeline using the suite's generation runner.
        """
        # Save current working directory and change to benchmark path
        original_cwd = os.getcwd()
        os.chdir(str(self.benchmark_path))
        
        try:
            from cweval.commons import BENCHMARK_DIR, LANGS
            from cweval.ppt import DirectPrompt

            try:
                from natsort import natsorted
            except ImportError:
                natsorted = sorted
        except ImportError as e:
            os.chdir(original_cwd)
            raise ImportError(
                f"Could not import cweval modules: {e}. Make sure benchmark_path is correct."
            )

        output_dir = output_dir.resolve()

        def log(msg):
            if output_callback:
                output_callback(msg)
            else:
                print(msg)

        try:
            # Get cases
            cases = {}
            begin_prompt_anchor = "BEGIN PROMPT"
            begin_solution_anchor = "BEGIN SOLUTION"

            log(f"Scanning for cases in {BENCHMARK_DIR}...")

            for root, _, files in os.walk(BENCHMARK_DIR):
                if "__pycache__" in root:
                    continue
                for file in natsorted(files):
                    file_wo_ext, ext = os.path.splitext(file)
                    task_file_path = os.path.join(root, file)
                    lang = ext[1:]

                    if not (ext and file_wo_ext.endswith("_task")):
                        continue
                    if lang not in LANGS:
                        continue

                    with open(task_file_path, "r") as f:
                        task_code = f.read()

                    begin_solution_line_src = ""
                    for line in task_code.splitlines():
                        if begin_solution_anchor in line:
                            begin_solution_line_src = line
                            break

                    if not begin_solution_line_src:
                        log(f"Warning: No solution anchor found in {task_file_path}")
                        continue

                    try:
                        code_prompt = (
                            task_code.split(begin_prompt_anchor)[-1]
                            .split(begin_solution_line_src)[0]
                            .strip()
                        )
                    except IndexError:
                        log(f"Warning: Could not parse prompt in {task_file_path}")
                        continue

                    rel_path = os.path.relpath(task_file_path, BENCHMARK_DIR)
                    cases[rel_path] = {
                        "code": code_prompt,
                        "lang": lang,
                        "path": task_file_path,
                        "rel_path": rel_path,
                    }

            log(f"Found {len(cases)} cases.")

            prompts = []
            for case_id, case_data in cases.items():
                lang = case_data["lang"]
                code_prompt = case_data["code"]

                prompt_text = DirectPrompt.PPT.format(
                    lang=lang,
                    lang_instr=DirectPrompt.LANG_INSTR.get(lang, ""),
                    code_prompt=code_prompt,
                )

                prompts.append(
                    {"id": case_id, "prompt": prompt_text, "metadata": case_data}
                )

            results = await self.generate_samples(
                model, prompts, n, temperature, output_callback
            )

            self.save_cweval_results(results, output_dir, n)
        finally:
            # Restore original working directory
            os.chdir(original_cwd)

    def save_cweval_results(self, results, output_dir, n):
        """Save results in CWEval structure."""
        # Structure: output_dir/generated_X/rel_path_wo_task_raw.ext

        for i in range(n):
            gen_dir = output_dir / f"generated_{i}"
            gen_dir.mkdir(parents=True, exist_ok=True)

            # Filter results for this sample index
            sample_results = [r for r in results if r.get("sample_index") == i]

            for res in sample_results:
                if "error" in res:
                    continue

                metadata = res["metadata"]
                rel_path = metadata["rel_path"]  # e.g. core/py/cwe_020_0_task.py
                response = res["response"]

                # Construct output path
                # Replace _task with _raw
                # rel_path is relative to BENCHMARK_DIR

                # We need to preserve directory structure
                dest_path = gen_dir / rel_path.replace("_task", "_raw")
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Clean response (remove markdown code blocks if present)
                clean_response = self._clean_response(response)

                with open(dest_path, "w") as f:
                    f.write(clean_response)

        print(f"Saved results to {output_dir}")

    def _clean_response(self, response: str) -> str:
        # Simple cleaner for markdown code blocks
        lines = response.splitlines()
        # Remove leading ```lang
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        # Remove trailing ```
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines)
