from pathlib import Path
from typing import Callable, Optional
import platform
from secbench.config import Config
from secbench.runners.docker_runner import DockerRunner
from secbench.benchmarks.base import Benchmark


class CWEvalBenchmark(Benchmark):
    def __init__(self, config: Config, bench_path: Path):
        super().__init__(config, bench_path)
        self.runner = DockerRunner()
        self.working_dir = "/home/ubuntu/CWEval"
        self.image_name = "co1lin/cweval"

    def run_pipeline(
        self,
        model: str,
        output_dir: Path,
        n: int,
        temperature: float,
        output_callback: Callable[[str], None],
        sanity_check: bool = False,
        benchmark_type: str = "instruct",
        eval_only: bool = False,
    ):
        # Pull image first
        self.runner.pull_image(self.image_name, output_callback)

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        abs_output_dir = output_dir.resolve()

        # We mount the output directory to /app/evals inside the container
        container_eval_path = "/app/evals"

        volumes = {str(abs_output_dir): {"bind": container_eval_path, "mode": "rw"}}

        # Environment variables
        env = {"PYTHONUNBUFFERED": "1"}
        if self.config.openai_api_key:
            env["OPENAI_API_KEY"] = self.config.openai_api_key
        if self.config.openrouter_api_key:
            env["OPENROUTER_API_KEY"] = self.config.openrouter_api_key
            # Fallback: Set OPENAI_API_KEY to OpenRouter key if not present,
            # as some libraries/versions might check it by default.
            if "OPENAI_API_KEY" not in env:
                env["OPENAI_API_KEY"] = self.config.openrouter_api_key

            # Auto-prepend openrouter/ prefix if using OpenRouter key and no OpenAI key is present
            # This matches the behavior suggested in gen_config.md
            if self.config.openrouter_api_key and not model.startswith("openrouter/"):
                output_callback(f"Auto-prepending 'openrouter/' to model name: {model}")
                model = f"openrouter/{model}"

        # DEBUG:
        print(f"Using model: {model}")
        print(f"Volumes: {volumes}")
        print(f"Environment: {env}")
        print(f'openai_api_key present: {"OPENAI_API_KEY" in env}')
        print(f'openrouter_api_key present: {"OPENROUTER_API_KEY" in env}')

        # Construct the shell command
        # We use zsh as in the example

        is_arm = platform.machine().lower() in ("arm64", "aarch64")
        cgo_env = "CGO_ENABLED=0 " if is_arm else ""

        # Chain commands
        cmds = [
            "echo '[Container] Starting shell...'",
            "source ~/miniforge3/bin/activate",
            f"cd {self.working_dir}",
            "source .env",
            "export NODE_PATH=$(npm root -g)",
            "export PYTHONPATH=$PYTHONPATH:$(pwd)",
            "echo '[Container] Installing tenacity...'",
            "pip install tenacity",
        ]

        if sanity_check:
            cmds.extend(
                [
                    "echo '[Container] Tidy Go modules...'",
                    "go mod tidy",
                    "echo '[Container] Compiling reference solutions...'",
                    f"{cgo_env}python -u cweval/commons.py compile_all_in --path benchmark/",
                    "echo '[Container] Running tests...'",
                    "pytest benchmark/ -x -n 8",
                ]
            )

        # Generation command
        # python cweval/generate.py gen --n <n> --temperature <temp> --eval_path <path> --model <model>
        # We use --num_proc 4 to be safe, or we could expose it as a parameter
        # We pipe 'y' to the command because generate.py asks for confirmation if the directory exists
        if not eval_only:
            gen_cmd = (
                f"echo 'y' | python cweval/generate.py gen "
                f"--n {n} "
                f"--temperature {temperature} "
                f"--eval_path {container_eval_path} "
                f"--model {model} "
                f"--num_proc 4"
            )
            cmds.append(f"echo '[Container] Generating samples with {model}...'")
            cmds.append(gen_cmd)
        else:
            cmds.append(f"echo '[Container] Skipping generation (eval-only mode)...'")

        # Evaluation command
        # python cweval/evaluate.py pipeline --eval_path <path> --docker False
        eval_cmd = (
            f"python cweval/evaluate.py pipeline "
            f"--eval_path {container_eval_path} "
            f"--docker False "
            f"--num_proc 4"
        )
        cmds.append(f"echo '[Container] Evaluating samples...'")
        cmds.append(eval_cmd)

        # Combine into one zsh command
        full_command = 'zsh -l -c "' + " && ".join(cmds) + '"'

        output_callback(f"Starting container execution...")
        output_callback(f"Output directory: {abs_output_dir}")

        self.runner.run(
            image=self.image_name,
            command=full_command,
            environment=env,
            volumes=volumes,
            network_mode="host",
            output_callback=output_callback,
        )
