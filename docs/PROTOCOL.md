# Evaluation Protocol

## Scope
- Study adversarial prompting that targets restricted code generation.
- Outputs are **never executed** and must remain non-operational.

## Environment setup (repeatable)
1. Use Python 3.11. Create a venv (macOS/Homebrew): `/opt/homebrew/bin/python3.11 -m venv .venv`
2. Activate: `source .venv/bin/activate`
3. Install deps: `python -m pip install -e ".[dev]"` (or `-r requirements.txt`)
4. Verify: `python scripts/validate_configs.py`

## Steps
1. Select providers/models from `configs/providers.yaml` and `configs/models.yaml`.
2. Choose experiment grid in `configs/matrix.yaml` (models x prompt categories x transforms x trials).
3. Load prompt suite from `prompts/prompt_suites.yaml`.
4. Apply transforms (e.g., safety prefixes, sanitization) before sending to models.
5. Record responses to `runs/<run_id>/responses.jsonl` with metadata and refusal heuristics.
6. Human (or scripted) labeling to REFUSAL / PARTIAL_COMPLIANCE / UNSAFE_COMPLIANCE.
7. Aggregate metrics and compare across models/strategies.

## CLI (non-operational scaffolding)
- Run grid (stubbed by default): `python -m llm_safety_eval.cli run`
- Enable live calls (opt-in): set `LSE_ALLOW_NETWORK=1` and pass `--execute` to the run command.
- Label responses: `python -m llm_safety_eval.cli label runs/<run_id>/responses.jsonl --output-path runs/<run_id>/labels.jsonl`
- Summarize: `python -m llm_safety_eval.cli summarize runs/<run_id>/`

## Safeguards
- Prompts use placeholders like "restricted device-control code" only.
- No exploit/malware content; avoid device-specific code.
- Local clients should run in sandboxed/offline environments when possible.

## Outputs
- `config_snapshot.yaml`, `providers_snapshot.yaml`, `models_snapshot.yaml`, `prompt_snapshot.yaml`
- `responses.jsonl`, `transform_log.jsonl`, `request_log.jsonl`, `labels.jsonl`
- `summary_metrics.csv`, `summary.md`, `summary.html`, `metadata.json`, `artifact_index.json` under each `runs/<run_id>/`.
- Optional figures in `runs/<run_id>/figs/` and embedded base64 plots in `summary.html` if matplotlib is available.
- Each response record logs: run_id, model_id, model_name, provider_id, prompt_id, category, prompt_text, trial_index, generation_parameters (temperature, max_tokens, etc., plus transform info), raw_response_text, timestamp, latency_ms, heuristics (refusal, safety-prefix, unsafe, anomaly, PII).

## Execution Checklist
- Do you really need live model calls? If not, keep default stub mode.
- If yes: export `LSE_ALLOW_NETWORK=1` and pass `--execute`; otherwise CLI aborts.
- Verify prompts remain non-operational; review request_log.jsonl before sharing.
- Use `--dry-run` to inspect the planned matrix without writing files.
- Ensure benign_control prompts exist for baseline safety checks.
- For quick smoke tests use `--limit N` or `--sample N` to reduce matrix size.
- Override output dir with `--output-dir` and sampling seed with `--seed` when needed.
