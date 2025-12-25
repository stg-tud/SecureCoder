from pathlib import Path
from typing import Callable, Optional
import sys
from secbench.config import Config
from secbench.runners.docker_runner import DockerRunner
from secbench.benchmarks.base import Benchmark


class CyberSecEvalBenchmark(Benchmark):
    def __init__(self, config: Config, bench_path: Path, runner_type: str = "docker"):
        super().__init__(config, bench_path)
        self.runner_type = runner_type
        # Use standard python image
        self.runner = DockerRunner()
        self.image_name = "python:3.10"

    def run_pipeline(
        self,
        model: str,
        output_dir: Path,
        n: int,
        temperature: float,
        output_callback: Callable[[str], None],
        benchmark_type: str = "instruct",
        **kwargs,
    ):
        # 1. Pull Image
        self.runner.pull_image(self.image_name, output_callback)

        # 2. Prepare Output Directory
        output_dir.mkdir(parents=True, exist_ok=True)
        abs_output_dir = output_dir.resolve()

        # 3. Define Volumes
        # Only mount output directory. We will clone the repo inside the container.
        container_output_path = "/app/output"

        volumes = {
            str(abs_output_dir): {"bind": container_output_path, "mode": "rw"},
        }

        # 4. Construct LLM Argument
        # Format: PROVIDER::MODEL::KEY[::BASE_URL]
        llm_arg = ""

        # Check if we should treat this as an OpenRouter request
        # 1. Explicit OpenRouter key present
        # 2. Model name implies OpenRouter (contains '/')
        is_openrouter_model = "/" in model

        if self.config.openrouter_api_key or (
            is_openrouter_model and self.config.openai_api_key
        ):
            # OpenRouter
            provider = "OPENAI"
            # Use OpenRouter key if available, otherwise fallback to OpenAI key (common pattern)
            api_key = self.config.openrouter_api_key or self.config.openai_api_key
            base_url = "https://openrouter.ai/api/v1"

            # OpenRouter expects model ID like 'openai/gpt-4o-mini'
            # If the user passed just 'gpt-4o-mini' but has OpenRouter key, we might want to prepend 'openai/'?
            # But usually users pass full ID.
            llm_arg = f"{provider}::{model}::{api_key}::{base_url}"

            if not self.config.openrouter_api_key:
                output_callback(
                    "Warning: Using OPENAI_API_KEY for OpenRouter request (inferred from model name)."
                )

        elif self.config.openai_api_key:
            # OpenAI Direct
            # Strip 'openai/' prefix if present, as OpenAI API expects just 'gpt-4o-mini'
            real_model = model
            if real_model.startswith("openai/"):
                real_model = real_model[7:]
            llm_arg = f"OPENAI::{real_model}::{self.config.openai_api_key}"
        else:
            output_callback("Error: No API key found for OpenAI or OpenRouter.")
            return

        # 5. Construct Command
        # We clone PurpleLlama to /app/PurpleLlama
        repo_root = "/app/PurpleLlama"
        bench_root = f"{repo_root}/CybersecurityBenchmarks"

        # Paths inside container
        requirements_path = f"{bench_root}/requirements.txt"
        response_path = f"{container_output_path}/responses.json"
        stat_path = f"{container_output_path}/stats.json"

        # Benchmark specific paths
        cmd_args = ""
        if benchmark_type == "instruct":
            prompt_path = f"{bench_root}/datasets/instruct/instruct-v2.json"
            cmd_args = (
                f"--benchmark=instruct "
                f"--prompt-path={prompt_path} "
                f"--response-path={response_path} "
                f"--stat-path={stat_path} "
                f'--llm-under-test "{llm_arg}" '
            )
        elif benchmark_type == "autocomplete":
            prompt_path = f"{bench_root}/datasets/autocomplete/autocomplete.json"
            cmd_args = (
                f"--benchmark=autocomplete "
                f"--prompt-path={prompt_path} "
                f"--response-path={response_path} "
                f"--stat-path={stat_path} "
                f'--llm-under-test "{llm_arg}" '
            )
        elif benchmark_type == "mitre":
            prompt_path = f"{bench_root}/datasets/mitre/mitre_benchmark_100_per_category_with_augmentation.json"
            cmd_args = (
                f"--benchmark=mitre "
                f"--prompt-path={prompt_path} "
                f"--response-path={response_path} "
                f"--stat-path={stat_path} "
                f'--llm-under-test "{llm_arg}" '
                f'--judge-llm "{llm_arg}" '
                f'--expansion-llm "{llm_arg}" '
            )
        else:
            output_callback(f"Benchmark type '{benchmark_type}' not supported.")
            return

        # Environment variables for container
        env = {
            "DATASETS": f"{bench_root}/datasets",
            "PYTHONPATH": repo_root,
            "PYTHONUNBUFFERED": "1",
        }
        if self.config.openai_api_key:
            env["OPENAI_API_KEY"] = self.config.openai_api_key
        if self.config.openrouter_api_key:
            env["OPENROUTER_API_KEY"] = self.config.openrouter_api_key

        # Chained command: Install git -> Clone -> Install deps -> Run benchmark
        # We use /bin/bash -c to execute the chain
        full_command = (
            "apt-get update && apt-get install -y git && "
            "git clone https://github.com/Meta-Llama/PurpleLlama.git /app/PurpleLlama && "
            f"pip install -r {requirements_path} && "
            f"cd {bench_root} && "
            f"python -m CybersecurityBenchmarks.benchmark.run {cmd_args}"
        )

        output_callback(
            f"Running {benchmark_type} benchmark in Docker (cloning repo)..."
        )
        output_callback(f"Image: python:3.10")

        # Mask API keys in logs
        safe_cmd = full_command.replace(
            self.config.openrouter_api_key or "___", "***"
        ).replace(self.config.openai_api_key or "___", "***")
        output_callback(f"Command: {safe_cmd}")

        # Run via DockerRunner
        # We wrap in bash -c to handle &&
        docker_cmd = f'/bin/bash -c "{full_command}"'

        self.runner.run(
            image=self.image_name,
            command=docker_cmd,
            environment=env,
            volumes=volumes,
            output_callback=output_callback,
        )
