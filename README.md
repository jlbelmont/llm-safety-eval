# LLM Safety Eval

Modular framework for research-grade evaluation of adversarial prompting and safety boundary failures in large language models (LLMs). Focused on code-generation refusal and compliance behaviors across local and API models.

## Goals
- Measure refusal consistency, partial compliance, and unsafe compliance.
- Compare adversarial prompt strategies (baseline, roleplay, fictional, decomposition, obfuscation).
- Support multiple backends: Ollama, vLLM, llama.cpp server, TGI, OpenAI-compatible APIs (incl. GPT-4o), and mock clients.
- Keep all prompts **non-operational**; outputs are never executed.

## Quick Start (scaffold)
1. Create and activate a Python 3.11 venv (macOS/Homebrew example):
   ```
   /opt/homebrew/bin/python3.11 -m venv .venv
   source .venv/bin/activate
   ```
2. Install deps:
   ```
   python -m pip install --upgrade pip
   python -m pip install -e ".[dev]"   # or: python -m pip install -r requirements.txt
   ```
3. Review configs in `configs/` and prompt suites in `prompts/` (your local prompt file is git-ignored).
4. Run orchestrator (mocked by default): `python -m llm_safety_eval.cli run --limit 10`
5. Label (optional): `python -m llm_safety_eval.cli label runs/<run_id>/responses.jsonl --output-path runs/<run_id>/labels.jsonl`.
6. Summarize: `python -m llm_safety_eval.cli summarize runs/<run_id>/`.

## Safety & Ethics
- Prompts use placeholders like "restricted device-control code"; no exploit/malware content.
- Generated outputs are for evaluation only and must not be executed.
- Network/model calls are disabled unless you set `LSE_ALLOW_NETWORK=1` **and** pass `--execute` (CLI) or `execute=True` (programmatic); otherwise clients return stubbed responses.
- See `docs/PROTOCOL.md` and `docs/THREAT_MODEL.md` for safeguards.

## Execution Checklist
- Need live calls? Set `LSE_ALLOW_NETWORK=1` and pass `--execute`; otherwise CLI aborts.
- Keep prompts non-operational; review request logs before sharing.
- Use `--dry-run` to inspect planned experiments before writing artifacts.
- For quick smoke tests, add `--limit N` or `--sample N` to shrink the matrix.
- Override output dir with `--output-dir` and sampling seed with `--seed` if desired.

## What gets logged per response
- run_id, model_id, model_name, provider_id
- prompt_id, category, prompt_text, trial_index
- generation_parameters (temperature, max_tokens, top_p if set, transform + meta)
- raw_response_text, timestamp, latency_ms
- heuristics: refusal, safety_prefix, unsafe matches/score, anomaly score, PII score

## Repository Map
Key modules live under `src/llm_safety_eval/` for configs, clients, transforms, labeling, and analysis. Artifacts are stored in `runs/`. Notebooks in `notebooks/` consume the package instead of duplicating logic.
