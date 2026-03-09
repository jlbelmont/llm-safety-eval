# LLM Safety Eval

Configuration-driven framework for evaluating large language model safety under adversarial prompting. The repository is built around auditable experiment matrices, reproducible run artifacts, human labeling, grouped safety metrics, and report-generation utilities.

## What the project does

- Measures three outcome classes: `REFUSAL`, `PARTIAL_COMPLIANCE`, and `UNSAFE_COMPLIANCE`.
- Compares prompt families such as direct prompts, roleplay, fictional framing, decomposition, obfuscation, and benign controls.
- Runs the same matrix across local and hosted backends through one interface.
- Preserves per-run snapshots, request logs, transform logs, responses, labels, summaries, and derived metrics.
- Supports report-generation workflows from structured section files and run artifacts.

The codebase is an evaluation pipeline, not a model-training or defense repository. It is meant to measure safety behavior under controlled prompting changes and make the resulting evidence easy to audit.

## Supported backends and transforms

Backends implemented in `src/llm_safety_eval/llm_clients/` include:

- OpenAI-compatible APIs
- Ollama
- vLLM
- llama.cpp server
- Hugging Face Text Generation Inference
- Mock clients for offline testing

Transforms implemented in `src/llm_safety_eval/transforms/` include:

- `none`
- `safety_prefix`
- `sanitization`
- `chain_of_denial`
- `perturbation`

The default tracked matrices currently exercise only `none` and `safety_prefix`.

## Current tracked configs

- `configs/base.yaml`: global run settings and default artifact location.
- `configs/matrix.yaml`: default smoke-test matrix using `gpt4o_api` and `mock_safe`.
- `configs/matrix_ollama.yaml`: mixed live matrix using `gpt4o_api` and `llama3_ollama`.
- `configs/models.yaml`: model registry and per-model generation defaults.
- `configs/providers.yaml`: provider registry and endpoint definitions.
- `prompts/prompt_suites.yaml`: tracked prompt-suite definition used by the runner.

Generated prompts are supported by the codebase but disabled in the tracked matrices by default.

## Installation

Python `>=3.11,<3.13` is required.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

If you prefer a non-editable install, `requirements.txt` is also available.

## Typical workflow

1. Validate the configs and prompt suite.

```bash
python scripts/validate_configs.py
python scripts/lint_prompt_suite.py
```

2. Inspect the planned matrix without making any model calls.

```bash
python -m llm_safety_eval.cli run --dry-run
python -m llm_safety_eval.cli run --matrix configs/matrix_ollama.yaml --dry-run
```

3. Run a small offline smoke test.

```bash
python -m llm_safety_eval.cli run --limit 10
```

4. Run a live experiment only when you intend to hit real endpoints.

```bash
LSE_ALLOW_NETWORK=1 python -m llm_safety_eval.cli run \
  --matrix configs/matrix_ollama.yaml \
  --execute
```

5. Label responses.

```bash
python -m llm_safety_eval.cli label \
  runs/<run_id>/responses.jsonl \
  --output-path runs/<run_id>/labels.jsonl
```

6. Summarize a run.

```bash
python -m llm_safety_eval.cli summarize \
  runs/<run_id> \
  --matrix-config configs/matrix_ollama.yaml
```

7. Generate report-ready LaTeX if you have a local report template configured.

```bash
python scripts/generate_report.py \
  --config reports/report_config.yaml \
  --output reports/build/research_report.tex
```

Add `--build-pdf` if `latexmk` is installed and you want the script to compile the PDF after rendering.

## Safety guardrails

- Live model calls are blocked unless both conditions are true:
  - `--execute` is passed to the CLI.
  - `LSE_ALLOW_NETWORK=1` is set in the environment.
- `--dry-run`, `--limit`, and `--sample` are available to inspect or reduce a matrix before execution.
- Prompt outputs are collected for evaluation only and should not be executed.
- The prompt suite is designed around non-operational placeholders rather than deployable harmful content.

## Run artifacts

Each run is written to `runs/<run_id>/` and includes:

- `responses.jsonl`
- `labels.jsonl`
- `request_log.jsonl`
- `transform_log.jsonl`
- `metadata.json`
- `artifact_index.json`
- snapshots of the base config, prompt suite, matrix, providers, and models

After `summarize`, the run directory also includes:

- `summary_metrics.csv`
- `category_metrics.csv`
- `transform_metrics.csv`
- `experiment_group_metrics.csv`
- `experiment_group_comparisons.csv`
- `summary.md`
- `summary.html`
- figures under `figs/` when plot generation succeeds

The summarizer uses `labels.jsonl` when labels are present and non-empty; otherwise it falls back to `responses.jsonl`.

## Repository layout

- `src/llm_safety_eval/`: package code for configs, runner, clients, transforms, labeling, analysis, and reporting.
- `configs/`: tracked base, model, provider, and matrix configs plus JSON schemas.
- `prompts/`: tracked prompt-suite definitions.
- `scripts/`: validation, dry-run, report, and helper scripts.
- `reports/sections/`: section files used by the report-generation pipeline.
- `runs/`: per-run artifacts. This directory is ignored except for `.gitkeep`.
- `tests/`: unit tests for configs, prompts, clients, transforms, runner behavior, and summary logic.
- `notebooks/`: exploratory notebooks that consume the package rather than duplicating pipeline code.

## Development

Run the main quality checks with:

```bash
pytest
ruff check .
black --check .
mypy src
```

## Notes on report generation

The repository tracks report sections, bibliography inputs, and reporting utilities. Local paper drafts, templates, and generated outputs can be kept out of version control through `.gitignore`, which is the default setup in this workspace.
