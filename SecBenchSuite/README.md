# SecBench Suite

A modular security benchmarking and static analysis orchestrator with a TUI, built for Python.

## Prerequisites

- [uv](https://github.com/astral-sh/uv) installed.

## Installation & Setup

Initialize the project and install dependencies:

```bash
# If you haven't already initialized the project (this repo is the project):
uv sync
```

## Usage

### CLI

Run interactively (menu selection):

```bash
uv run secbench
```

Generate code samples:

```bash
uv run secbench generate --model openai/gpt-3.5-turbo --prompt "Write a secure login function in Python" --count 1
```

### Run Benchmarks

#### CWEval

Run the full CWEval pipeline (Generation + Evaluation) using the official Docker image:

```bash
uv run secbench evaluate --benchmark cweval --model openai/gpt-4o-mini --n 5
```

This command will:

1. Pull the `co1lin/cweval` Docker image.
2. Start a container.
3. Generate 5 samples per task using the specified model.
4. Evaluate the generated samples.
5. Stream all logs to your console. (currently broken)

**Evaluation Only Mode:**

If you already have generated samples or want to skip the generation step:

```bash
uv run secbench evaluate --benchmark cweval --model openai/gpt-4o-mini --n 5 --eval-only
```

**Sanity Check:**

Run a sanity check (compile and test reference solutions) before the pipeline to ensure the environment is correct:

```bash
uv run secbench evaluate --benchmark cweval --model openai/gpt-4o-mini --sanity-check
```

### Results

Results are saved in the `results/` directory (configurable in `secbench.yaml`).
For CWEval, each run creates a timestamped directory:

```
results/cweval/
└── 20251210_140518_openai_gpt-4o-mini/
    ├── run_config.yaml    # Configuration used for this run
    ├── res_all.json       # Detailed evaluation results
    └── ...                # Generated samples and logs
```

## Configuration

Create a `secbench.yaml` file in the project root to configure API keys and defaults:

```yaml
openai_api_key: "sk-..."
openrouter_api_key: "sk-or-..."
default_model: "openai/gpt-4o-mini"
output_dir: "results"
```

Alternatively, you can set environment variables:

- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`

The tool will automatically prepend `openrouter/` to the model name if you are using an OpenRouter key and the model name doesn't already start with it.

If `openrouter_api_key` is provided, models will be automatically routed through OpenRouter (and prefixed with `openrouter/` if needed).
