import argparse
import asyncio
import sys
import questionary
from pathlib import Path
from rich.console import Console, Group
from rich.panel import Panel
from rich.live import Live

# Text is available in rich.text but sometimes pylance complains if not installed in env
# We can use simple strings or import inside function if needed, but let's try explicit import again
# or just use strings in Group which works fine for simple text


from secbench.config import Config
from secbench.runners.generation import GenerationRunner
from secbench.benchmarks.cweval import CWEvalBenchmark
from secbench.benchmarks.seccodeplt import SecCodePLTBenchmark

console = Console()


async def run_generation(args, config: Config):
    api_key = config.openrouter_api_key or config.openai_api_key or "dummy"

    runner = GenerationRunner(api_key=api_key, base_url=config.api_base_url)

    # Prepare output directory
    output_dir = Path(config.output_dir) / "generated_samples"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Live view setup
    output_lines = []
    output_lines.append(f"Output directory: {output_dir}")

    def generate_view():
        return Panel(
            Group(*[line for line in output_lines[-20:]]),
            title=f"Generating with {args.model}",
            border_style="green",
        )

    with Live(generate_view(), refresh_per_second=10) as live:
        async for line in runner.generate(
            model=args.model,
            prompt=args.prompt,
            count=args.count,
            system_prompt=config.system_prompt,
            output_dir=output_dir,
        ):
            output_lines.append(line)
            live.update(generate_view())


async def run_cweval(args, config: Config):
    # Assuming CWEval is located at ./Benchmarks/CWEval relative to project root
    # In a real app, this path might be configured or discovered
    bench_path = Path("Benchmarks/CWEval")
    if not bench_path.exists():
        console.print(f"[red]Error: CWEval benchmark not found at {bench_path}[/]")
        return

    benchmark = CWEvalBenchmark(config, bench_path)
    output_dir = Path(config.output_dir) / "cweval"

    output_lines = []

    def generate_view():
        return Panel(
            Group(*[line for line in output_lines[-20:]]),
            title=f"Running CWEval with {args.model}",
            border_style="magenta",
        )

    def update_output(msg: str):
        output_lines.append(msg)

    with Live(generate_view(), refresh_per_second=10) as live:
        await benchmark.run_pipeline(
            model=args.model,
            output_dir=output_dir,
            n=args.n,
            temperature=args.temperature,
            output_callback=update_output,
        )
        # Keep the final view for a moment or just exit
        live.update(generate_view())


async def run_seccodeplt(args, config: Config):
    # Assuming seccodeplt is located at ./Benchmarks/SecCodePLT relative to project root
    bench_path = Path("Benchmarks/SecCodePLT")
    if not bench_path.exists():
        console.print(f"[red]Error: SecCodePLT benchmark not found at {bench_path}[/]")
        return

    try:
        benchmark = SecCodePLTBenchmark(config, bench_path)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/]")
        return

    output_dir = Path(config.output_dir) / "seccodeplt"

    output_lines = []

    def generate_view():
        return Panel(
            Group(*[line for line in output_lines[-20:]]),
            title=f"Running SecCodePLT with {args.model}",
            border_style="cyan",
        )

    def update_output(msg: str):
        output_lines.append(msg)

    with Live(generate_view(), refresh_per_second=10) as live:
        await benchmark.run_pipeline(
            model=args.model,
            output_dir=output_dir,
            n=args.n,
            temperature=args.temperature,
            output_callback=update_output,
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
            "Model (e.g. openai/gpt-3.5-turbo):", default=config.default_model
        ).ask()
        prompt = questionary.text("Prompt:").ask()
        count = int(questionary.text("Count:", default="1").ask())

        # Mock args object
        args = argparse.Namespace(model=model, prompt=prompt, count=count)
        asyncio.run(run_generation(args, config))


def main():
    parser = argparse.ArgumentParser(description="SecBench: Security Benchmark Suite")
    parser.add_argument("--config", help="Path to config file", default="secbench.yaml")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate Command
    gen_parser = subparsers.add_parser("generate", help="Generate code samples")
    gen_parser.add_argument(
        "--model", help="Model name", default="openai/gpt-3.5-turbo"
    )
    gen_parser.add_argument("--prompt", help="Prompt for generation", required=True)
    gen_parser.add_argument("--count", type=int, default=1, help="Number of samples")
    gen_parser.add_argument("--output", help="Output file")

    # Evaluate Command (Placeholder)
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate samples")
    eval_parser.add_argument(
        "--benchmark",
        choices=["cweval", "seccodeplt"],
        default="cweval",
        help="Benchmark to run",
    )
    eval_parser.add_argument(
        "--model", default="openai/gpt-3.5-turbo", help="Model to evaluate"
    )
    eval_parser.add_argument(
        "--n", type=int, default=1, help="Number of samples per task"
    )
    eval_parser.add_argument(
        "--temperature", type=float, default=0.8, help="Temperature"
    )

    args = parser.parse_args()

    config = Config.load(args.config)

    if args.command == "generate":
        asyncio.run(run_generation(args, config))
    elif args.command == "evaluate":
        if args.benchmark == "cweval":
            asyncio.run(run_cweval(args, config))
        elif args.benchmark == "seccodeplt":
            asyncio.run(run_seccodeplt(args, config))
        else:
            print("Evaluation not implemented yet.")
    else:
        # No command provided -> Interactive
        interactive_mode(config)


if __name__ == "__main__":
    main()
