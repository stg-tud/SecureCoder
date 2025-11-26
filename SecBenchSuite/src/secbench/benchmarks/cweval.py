import asyncio
import os
from pathlib import Path
from typing import Optional, Callable

from secbench.config import Config
from secbench.runners.docker_runner import DockerRunner


class CWEvalBenchmark:
    IMAGE = "co1lin/cweval"
    CONTAINER_WORKDIR = "/home/ubuntu/CWEval"

    def __init__(self, config: Config, benchmark_path: Path):
        self.config = config
        self.benchmark_path = benchmark_path.resolve()
        self.runner = DockerRunner(self.IMAGE)

    async def run_pipeline(
        self,
        model: str,
        output_dir: Path,
        n: int = 1,
        temperature: float = 0.8,
        output_callback: Optional[Callable[[str], None]] = None,
    ):
        """
        Run the full CWEval pipeline: Generation -> Evaluation.
        """
        container_name = "secbench_cweval"
        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        def log(msg):
            if output_callback:
                output_callback(msg)
            else:
                print(msg)

        # Map host paths to container paths
        volumes = {
            str(self.benchmark_path): self.CONTAINER_WORKDIR,
            str(output_dir): f"{self.CONTAINER_WORKDIR}/evals_output",
        }

        # Environment variables for API keys
        env = {"PYTHONUNBUFFERED": "1"}
        if self.config.openai_api_key:
            env["OPENAI_API_KEY"] = self.config.openai_api_key
        if self.config.openrouter_api_key:
            # CWEval uses litellm, which supports OPENAI_API_KEY.
            # If using OpenRouter, we might need to set OPENAI_API_BASE or similar if the model name implies it.
            # But litellm usually handles 'openrouter/...' models if OPENROUTER_API_KEY is set.
            env["OPENROUTER_API_KEY"] = self.config.openrouter_api_key
            env["OPENAI_API_KEY"] = self.config.openrouter_api_key  # Fallback/Alias

        log(f"Starting CWEval container ({container_name})...")

        # Cleanup existing container if any
        await self.runner.remove(container_name)

        try:
            # Start container
            await self.runner.run_detached(
                name=container_name,
                volumes=volumes,
                env=env,
                workdir=self.CONTAINER_WORKDIR,
            )

            # Fix for missing tenacity dependency in the docker image
            # litellm requires tenacity but it seems to be missing in the current image
            # We need to install it in the 'cweval' environment (activated via .env)
            install_cmd = f'zsh -c "source ~/miniforge3/bin/activate && source {self.CONTAINER_WORKDIR}/.env && pip install tenacity"'
            log("Installing missing dependency: tenacity...")
            await self.runner.exec_command(
                container_name, install_cmd, output_callback=output_callback
            )

            # 1. Setup/Check environment (optional but good for sanity)
            # await self.runner.exec_command(container_name, "python cweval/commons.py compile_all_in --path benchmark/")

            # 2. Generate
            # Note: eval_path inside container should map to the mounted output volume
            eval_path_container = "evals_output/current_run"

            # Adjust model name for OpenRouter if needed
            # The user requested to prepend 'openrouter/' if using OpenRouter
            if self.config.openrouter_api_key and not model.startswith("openrouter/"):
                model = f"openrouter/{model}"
                log(f"Using OpenRouter: Adjusted model name to {model}")

            # We use zsh to source the environment variables and activate conda
            # This ensures PYTHONPATH and other deps are set correctly as per CWEval docs
            gen_cmd_inner = (
                f"python -u cweval/generate.py gen "
                f"--model {model} "
                f"--n {n} "
                f"--temperature {temperature} "
                f"--eval_path {eval_path_container} "
                f"--num_proc 4"
            )
            gen_cmd = f'zsh -c "source ~/miniforge3/bin/activate && source .env && {gen_cmd_inner}"'

            log(f"Running Generation: {gen_cmd}")
            exit_code = await self.runner.exec_command(
                container_name, gen_cmd, output_callback=output_callback
            )
            if exit_code != 0:
                log("Generation failed.")
                return

            # 3. Evaluate
            # --docker False because we are ALREADY inside docker
            eval_cmd_inner = (
                f"python -u cweval/evaluate.py pipeline "
                f"--eval_path {eval_path_container} "
                f"--docker False "
                f"--num_proc 4"
            )
            eval_cmd = f'zsh -c "source ~/miniforge3/bin/activate && source .env && {eval_cmd_inner}"'

            log(f"Running Evaluation: {eval_cmd}")
            exit_code = await self.runner.exec_command(
                container_name, eval_cmd, output_callback=output_callback
            )
            if exit_code != 0:
                log("Evaluation failed.")
                return

            log(f"CWEval pipeline completed. Results in {output_dir}/current_run")

        finally:
            log("Stopping container...")
            await self.runner.stop(container_name)
