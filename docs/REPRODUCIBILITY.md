# Reproducibility Checklist

- Fix random seed in `configs/base.yaml` (`run.seed`).
- Snapshot configs per run to `runs/<run_id>/config_snapshot.yaml` and prompt suite to `prompt_snapshot.yaml`.
- Record model/provider versions and base URLs in `metadata.json`.
- Store generation parameters with every response record.
- Emit `summary_metrics.csv` per run via the summarize CLI for consistent comparisons.
- Capture request-only log in `request_log.jsonl` to trace prompts without responses.
- Artifact index at `artifact_index.json` lists all run files with paths for quick navigation.
- Optional plots saved under `runs/<run_id>/figs/` and embedded in `summary.html`; hashes recorded in artifact index.
- Keep notebook outputs in `notebooks/_artifacts/` or `runs/` for traceability.
- Document environment: Python version (3.11), package versions (lock via `pip freeze > runs/<run_id>/requirements.txt`).
