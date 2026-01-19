import json
import asyncio
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Set

from secbench.config import Config
from secbench.benchmarks.base import BaseBenchmark
from secbench.runners.docker_runner import DockerRunner
from secbench.runners.codeql_runner import CodeQLRunner


class SecCodePLTBenchmark(BaseBenchmark):
    BASE_IMAGE = "python:3.10"

    def __init__(self, config: Config, benchmark_path: Path):
        super().__init__(config, benchmark_path)
        self.dataset_path = self._find_dataset()
        self.docker_runner = DockerRunner(self.BASE_IMAGE)
        self.codeql_runner = CodeQLRunner()

    def _find_dataset(self) -> Path:
        """Find the single JSON or JSONL dataset file in the benchmark directory."""
        candidates = list(self.benchmark_path.glob("*.json")) + list(
            self.benchmark_path.glob("*.jsonl")
        )
        if not candidates:
            # Fallback for when the path is the file itself or specific structure
            if self.benchmark_path.is_file() and self.benchmark_path.suffix in [
                ".json",
                ".jsonl",
            ]:
                return self.benchmark_path
            raise FileNotFoundError(
                f"No .json or .jsonl dataset found in {self.benchmark_path}"
            )
        return candidates[0]

    def get_prompts(self) -> List[Dict[str, Any]]:
        is_jsonl = self.dataset_path.suffix == ".jsonl"
        data = []

        with open(self.dataset_path, "r") as f:
            if is_jsonl:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            else:
                data = json.load(f)

        # Ensure data is a list
        if isinstance(data, dict):
            # Maybe it's wrapped?
            if "data" in data and isinstance(data["data"], list):
                data = data["data"]
            else:
                # If it's a dict but not a list, maybe it's not the right format,
                # or maybe it's a list of lines (jsonl)?
                # The user said "just one json". Assuming standard list of dicts.
                pass

        prompts = []
        for i, item in enumerate(data):
            # Reuse dataset ID if available, else index
            p_id = item.get("id", str(i))

            # User mentioned task_description
            prompt_text = item.get("task_description")
            if not prompt_text:
                continue

            if item.get("use_rule"):
                rule = item.get("rule")
                if rule:
                    prompt_text = f"{prompt_text}\n\n{rule}"

            prompts.append({"id": p_id, "prompt": prompt_text, "metadata": item})
        return prompts

    async def run_pipeline(
        self,
        model: str,
        output_dir: Path,
        n: int = 1,
        temperature: float = 0.8,
        output_callback: Optional[Callable[[str], None]] = None,
    ):
        output_dir = output_dir.resolve()

        def log(msg):
            if output_callback:
                output_callback(msg)
            else:
                print(msg)

        # 1. Generate
        log("Fetching prompts...")
        prompts = self.get_prompts()

        log(f"Generating {n} samples for {len(prompts)} prompts...")
        results = await self.generate_samples(
            model, prompts, n, temperature, output_callback
        )
        self.save_results(results, output_dir)

        # 2. Evaluate
        log("Starting evaluation in Docker...")
        await self.evaluate(results, output_dir, output_callback)

    async def evaluate(
        self,
        results: List[Dict[str, Any]],
        output_dir: Path,
        output_callback: Optional[Callable[[str], None]] = None,
    ):
        def log(msg):
            if output_callback:
                output_callback(msg)
            else:
                print(msg)

        # Prepare directory structure
        eval_dir = output_dir / "evaluation"
        eval_dir.mkdir(exist_ok=True, parents=True)

        # 1. Collect requirements and Prepare Test Files
        all_requirements: Set[str] = set()

        runner_files = []

        for item in results:
            if "error" in item:
                continue

            p_id = item["id"]
            sample_index = item["sample_index"]
            response_code = self._extract_code(item["response"])
            metadata = item["metadata"]

            # Ground truth unused for now, using unittests
            unittests = metadata.get("unittests", "")

            # Combine code
            # Note: naive combination.
            full_code = f"{response_code}\n\n# Unittests\n{unittests}"

            # Save to file
            filename = f"test_{p_id}_{sample_index}.py"
            file_path = eval_dir / filename
            with open(file_path, "w") as f:
                f.write(full_code)

            runner_files.append(filename)

            # Collect requirements
            reqs = metadata.get("install_requires", [])
            if isinstance(reqs, list):
                all_requirements.update(reqs)

        # Write requirements.txt
        req_path = eval_dir / "requirements.txt"
        with open(req_path, "w") as f:
            for req in sorted(all_requirements):
                f.write(f"{req}\n")

        # Create runner script
        runner_script_content = """
import glob
import subprocess
import json
import os
import sys

def run_tests():
    results = {}
    test_files = glob.glob("test_*.py")
    print(f"Found {len(test_files)} test files.")
    
    for i, test_file in enumerate(test_files):
        print(f"Running {i+1}/{len(test_files)}: {test_file}")
        try:
            # Run the test file as a separate process
            # Capture output
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=30 # Timeout per test
            )
            
            results[test_file] = {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            results[test_file] = {
                "return_code": -1,
                "error": "Timeout"
            }
        except Exception as e:
            results[test_file] = {
                "return_code": -1,
                "error": str(e)
            }

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_tests()
"""
        with open(eval_dir / "runner.py", "w") as f:
            f.write(runner_script_content)

        # Run Docker
        # We mount eval_dir to /app
        log(f"Running Docker container with image {self.BASE_IMAGE}...")

        # Install requirements and run runner.py
        # We use a single command string
        # "pip install -r requirements.txt && python runner.py"
        # We need to ensure pip is available or upgraded? Default python image usually has it.

        command = '/bin/bash -c "pip install -r requirements.txt && python runner.py"'

        eval_results = {}
        try:
            exit_code = await self.docker_runner.run_ephemeral(
                command=command,
                volumes={str(eval_dir): "/app"},
                workdir="/app",
                output_callback=log,
            )

            log(f"Docker run finished with exit code {exit_code}")

            # Read back results
            result_json_path = eval_dir / "results.json"
            if result_json_path.exists():
                with open(result_json_path, "r") as f:
                    eval_results = json.load(f)

                # Calculate summary
                passed = sum(
                    1 for r in eval_results.values() if r.get("return_code") == 0
                )
                total = len(eval_results)
                log(f"Functional Evaluation Complete. Passed: {passed}/{total}")
            else:
                log("Error: results.json not found after execution.")

        except Exception as e:
            log(f"Error running docker: {e}")

        # 2. Run CodeQL Security Analysis
        await self._run_codeql_analysis(results, output_dir, eval_results, log)

    async def _run_codeql_analysis(
        self,
        results: List[Dict[str, Any]],
        output_dir: Path,
        functional_results: Dict[str, Any],
        log: Callable[[str], None],
    ):
        if not await self.codeql_runner.check_available():
            log("CodeQL not found. Skipping security analysis.")
            return

        log("Starting CodeQL security analysis...")
        
        # Prepare source for CodeQL (without unittests)
        codeql_src_dir = output_dir / "codeql_source"
        codeql_src_dir.mkdir(exist_ok=True, parents=True)
        
        codeql_db_dir = output_dir / "codeql_db"
        codeql_results_file = output_dir / "codeql_results.sarif"
        
        # Map filename -> (id, sample_index, cwe_list)
        file_map = {}
        
        for item in results:
            if "error" in item:
                continue
                
            p_id = item["id"]
            sample_index = item["sample_index"]
            response_code = self._extract_code(item["response"])
            
            filename = f"sample_{p_id}_{sample_index}.py"
            file_path = codeql_src_dir / filename
            with open(file_path, "w") as f:
                f.write(response_code)
                
            # Get CWEs from metadata
            # Assuming metadata has 'cwe' which could be string or list
            metadata = item["metadata"]
            cwes = []
            if "cwe" in metadata:
                val = metadata["cwe"]
                if isinstance(val, list):
                    cwes = val
                else:
                    cwes = [str(val)]
            
            # Normalize CWEs: "CWE-78" -> "78" (or match loosely later)
            file_map[filename] = {
                "id": p_id,
                "sample_index": sample_index,
                "cwes": cwes
            }
            
        # Run CodeQL
        log("Creating CodeQL database...")
        if not await self.codeql_runner.create_database(codeql_src_dir, codeql_db_dir, "python"):
            log("Failed to create CodeQL database.")
            return
            
        log("Running CodeQL analysis...")
        if not await self.codeql_runner.analyze(codeql_db_dir, codeql_results_file):
            log("CodeQL analysis failed.")
            return
            
        # Parse Results
        sarif_findings = self.codeql_runner.load_sarif_results(codeql_results_file)
        
        # Match findings
        security_stats = {"secure": 0, "insecure": 0}
        final_report = []

        for filename, info in file_map.items():
            findings = sarif_findings.get(filename, [])
            target_cwes = info["cwes"]
            
            # Check if any finding matches target CWEs
            is_secure = True
            detected_issues = []
            
            for finding in findings:
                # finding['cwes'] is list of found CWE tags e.g. ["78", "89"]
                # info['cwes'] is list of target CWEs e.g. ["CWE-78"]
                
                # Check intersection
                found_cwes = finding["cwes"]
                
                # Simple matching logic: check if any target CWE number is in found CWEs
                # found_cwes usually strictly numbers or "CWE-XXX" depending on query metadata
                # standard queries usually have tags like "external/cwe/cwe-78" -> parsed as "CWE-78" in my runner
                
                match = False
                for target in target_cwes:
                    # Normalize target: "CWE-78" -> "78", "78" -> "78"
                    t_num = target.upper().replace("CWE-", "")
                    
                    for found in found_cwes:
                        f_num = found.upper().replace("CWE-", "")
                        if t_num == f_num:
                            match = True
                            break
                    if match:
                        break
                
                if match:
                    is_secure = False
                    detected_issues.append(finding)
            
            if is_secure:
                security_stats["secure"] += 1
            else:
                security_stats["insecure"] += 1
                
            # Combine with functional result
            # Functional result keys are "test_ID_INDEX.py"
            # Here we have "sample_ID_INDEX.py"
            func_filename = f"test_{info['id']}_{info['sample_index']}.py"
            func_res = functional_results.get(func_filename, {})
            func_passed = func_res.get("return_code") == 0
            
            final_report.append({
                "id": info["id"],
                "sample_index": info["sample_index"],
                "target_cwes": target_cwes,
                "functional_passed": func_passed,
                "security_passed": is_secure,
                "detected_issues": detected_issues,
                "functional_details": func_res
            })
            
        log(f"Security Analysis Complete. Secure: {security_stats['secure']}, Insecure: {security_stats['insecure']}")
        
        # Save final report
        report_path = output_dir / "final_report.json"
        with open(report_path, "w") as f:
            json.dump(final_report, f, indent=2)
        log(f"Final report saved to {report_path}")

    def _extract_code(self, response: str) -> str:
        """Extract code from markdown code blocks if present."""
        code_block = re.search(r"```python\s*(.*?)\s*```", response, re.DOTALL)
        if code_block:
            return code_block.group(1)

        # Try generic block
        code_block = re.search(r"```\s*(.*?)\s*```", response, re.DOTALL)
        if code_block:
            return code_block.group(1)

        return response
