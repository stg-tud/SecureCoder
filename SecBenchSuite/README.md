# SecBench Suite

A modular security benchmarking and static analysis orchestrator with a TUI, built for Python.

## Prerequisites

- [uv](https://github.com/astral-sh/uv) installed.
- **Docker**: Required for running functional tests in a sandboxed environment.
- **CodeQL CLI**: Required for running security analysis (evaluation). Ensure `codeql` is in your PATH.

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
uv run secbench generate --prompt "Generate a Login form in javascript" --model "llama3:latest"
```

Run benchmarks (e.g., CWEval):

```bash
uv run secbench evaluate --benchmark cweval --model openai/gpt-3.5-turbo
```

### SecCodePLT Benchmark

SecCodePLT is a benchmark for generating and evaluating secure code, featuring both functional correctness tests (via Docker) and security scanning (via CodeQL).

**1. Download the Dataset:**

```bash
uv run python SecBenchSuite/Benchmarks/SecCodePLT/download_dataset.py
```

**2. Run Evaluation:**

```bash
uv run secbench evaluate --benchmark seccodeplt --model openai/gpt-4o --n 1
```

*   **Functional Evaluation**: Runs the provided unittests in a Docker container (`python:3.10`).
*   **Security Evaluation**: Uses CodeQL to scan generated code for specific CWEs defined in the dataset.
*   **Results**: Saved in `results/seccodeplt/evaluation/final_report.json`.

## Configuration

Create a `secbench.yaml` file in the project root to configure API keys and defaults:

```yaml
openai_api_key: "sk-..."
openrouter_api_key: "sk-or-..."
default_model: "openai/gpt-3.5-turbo"
output_dir: "results"
```

~~If `openrouter_api_key` is provided, models will be automatically routed through OpenRouter (and prefixed with `openrouter/` if needed).~~
