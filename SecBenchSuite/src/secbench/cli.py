import argparse
import sys
import questionary
from pathlib import Path
from rich.console import Console, Group
from rich.panel import Panel
from rich.live import Live
import datetime
import yaml

from secbench.config import Config

from secbench.benchmarks.cweval import CWEvalBenchmark
from secbench.benchmarks.cyberseceval import CyberSecEvalBenchmark

console = Console()


def run_generation(args, config: Config):
    api_key = config.openrouter_api_key or config.openai_api_key
    if not api_key:
        console.print(
            "[red]Error: No API key found in config (openrouter_api_key or openai_api_key).[/]"
        )
        return

    runner = GenerationRunner(api_key=api_key)

    # Live view setup
    output_lines = []

    def generate_view():
        return Panel(
            Group(*[line for line in output_lines[-20:]]),
            title=f"Generating with {args.model}",
            border_style="green",
        )

    with Live(generate_view(), refresh_per_second=10) as live:
        for line in runner.generate(args.model, args.prompt, args.count):
            output_lines.append(line)
            live.update(generate_view())


def run_cweval(args, config: Config):
    # Assuming CWEval is located at ./Benchmarks/CWEval relative to project root
    # In a real app, this path might be configured or discovered
    bench_path = Path("Benchmarks/CWEval")
    if not bench_path.exists():
        console.print(f"[red]Error: CWEval benchmark not found at {bench_path}[/]")
        return

    benchmark = CWEvalBenchmark(config, bench_path)

    # Create timestamped output directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_model = args.model.replace("/", "_").replace(":", "_")
    run_id = f"{timestamp}_{sanitized_model}"
    output_dir = Path(config.output_dir) / "cweval" / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save run configuration
    run_config = {
        "timestamp": timestamp,
        "model": args.model,
        "n": args.n,
        "temperature": args.temperature,
        "sanity_check": args.sanity_check,
        "eval_only": args.eval_only,
        "benchmark": "cweval",
    }
    with open(output_dir / "run_config.yaml", "w") as f:
        yaml.dump(run_config, f)

    output_lines = []

    def generate_view():
        return Panel(
            Group(*[line for line in output_lines[-20:]]),
            title=f"Running CWEval with {args.model}",
            border_style="magenta",
        )

    with Live(generate_view(), refresh_per_second=10) as live:

        def update_output(msg: str):
            output_lines.append(msg)
            live.update(generate_view())

        benchmark.run_pipeline(
            model=args.model,
            output_dir=output_dir,
            n=args.n,
            temperature=args.temperature,
            output_callback=update_output,
            sanity_check=args.sanity_check,
            eval_only=args.eval_only,
        )
        # Keep the final view for a moment or just exit
        live.update(generate_view())


def run_cyberseceval(args, config: Config):
    # Assuming CyberSecEval is located at ./Benchmarks/PurpleLlama relative to project root
    bench_path = Path("Benchmarks/PurpleLlama")
    if not bench_path.exists():
        console.print(
            f"[red]Error: CyberSecEval benchmark not found at {bench_path}[/]"
        )
        return

    benchmark = CyberSecEvalBenchmark(config, bench_path, runner_type=args.runner)

    # Create timestamped output directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_model = args.model.replace("/", "_").replace(":", "_")
    run_id = f"{timestamp}_{sanitized_model}"
    output_dir = Path(config.output_dir) / "cyberseceval" / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save run configuration
    run_config = {
        "timestamp": timestamp,
        "model": args.model,
        "n": args.n,
        "temperature": args.temperature,
        "benchmark": "cyberseceval",
        "benchmark_type": args.benchmark_type,
        "runner": args.runner,
    }
    with open(output_dir / "run_config.yaml", "w") as f:
        yaml.dump(run_config, f)

    output_lines = []

    def generate_view():
        return Panel(
            Group(*[line for line in output_lines[-20:]]),
            title=f"Running CyberSecEval ({args.benchmark_type}) with {args.model}",
            border_style="cyan",
        )

    with Live(generate_view(), refresh_per_second=10) as live:

        def update_output(msg: str):
            output_lines.append(msg)
            live.update(generate_view())

        benchmark.run_pipeline(
            model=args.model,
            output_dir=output_dir,
            n=args.n,
            temperature=args.temperature,
            output_callback=update_output,
            benchmark_type=args.benchmark_type,
        )
        live.update(generate_view())


def interactive_mode(config: Config):
    console.print(
        Panel.fit("[bold blue]SecBench Suite[/]\nInteractive Mode", border_style="blue")
    )

    action = questionary.select(
        "Select Mode:", choices=["Generate Samples", "Exit"]
    ).ask()

    if action == "Exit":
        sys.exit(0)

    if action == "Generate Samples":
        model = questionary.text(
            "Model (e.g. openai/gpt-4o-mini):", default=config.default_model
        ).ask()
        prompt = questionary.text("Prompt:").ask()
        count = int(questionary.text("Count:", default="1").ask())

        # Mock args object
        args = argparse.Namespace(model=model, prompt=prompt, count=count)
        run_generation(args, config)


def main():
    parser = argparse.ArgumentParser(description="SecBench: Security Benchmark Suite")
    parser.add_argument("--config", help="Path to config file", default="config.yaml")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate Command
    gen_parser = subparsers.add_parser("generate", help="Generate code samples")
    gen_parser.add_argument("--model", help="Model name", default="openai/gpt-4o-mini")
    gen_parser.add_argument("--prompt", help="Prompt for generation", required=True)
    gen_parser.add_argument("--count", type=int, default=1, help="Number of samples")
    gen_parser.add_argument("--output", help="Output file")

    # Evaluate Command (Placeholder)
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate samples")
    eval_parser.add_argument(
        "--benchmark",
        choices=["cweval", "cyberseceval"],
        default="cweval",
        help="Benchmark to run",
    )
    eval_parser.add_argument(
        "--benchmark-type",
        default="instruct",
        help="Sub-benchmark type for CyberSecEval (e.g. instruct, mitre)",
    )
    eval_parser.add_argument(
        "--runner", choices=["docker", "local"], default="local", help="Runner type"
    )
    eval_parser.add_argument(
        "--model", default="openai/gpt-4o-mini", help="Model to evaluate"
    )
    eval_parser.add_argument(
        "--n", type=int, default=1, help="Number of samples per task"
    )
    eval_parser.add_argument(
        "--temperature", type=float, default=0.8, help="Temperature"
    )

    eval_parser.add_argument(
        "--sanity-check",
        action="store_true",
        help="Run sanity check (compile and test reference solutions) before evaluation",
    )
    eval_parser.add_argument(
        "--eval-only",
        action="store_true",
        help="Skip generation and only run evaluation",
    )

    args = parser.parse_args()

    config = Config.load(args.config)

    if args.command == "generate":
        run_generation(args, config)
    elif args.command == "evaluate":
        if args.benchmark == "cweval":
            run_cweval(args, config)
        elif args.benchmark == "cyberseceval":
            run_cyberseceval(args, config)
        else:
            print("Evaluation not implemented yet.")
    else:
        # No command provided -> Interactive
        interactive_mode(config)


if __name__ == "__main__":
    main()
