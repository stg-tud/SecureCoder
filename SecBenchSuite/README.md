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

Run benchmarks (e.g., CWEval):

```bash
uv run secbench evaluate --benchmark cweval --model openai/gpt-3.5-turbo
```

## Configuration

Create a `secbench.yaml` file in the project root to configure API keys and defaults:

```yaml
openai_api_key: "sk-..."
openrouter_api_key: "sk-or-..."
default_model: "openai/gpt-3.5-turbo"
output_dir: "results"
```

If `openrouter_api_key` is provided, models will be automatically routed through OpenRouter (and prefixed with `openrouter/` if needed).
