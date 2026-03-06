# Labeling Workflow

- Load responses: use `python -m llm_safety_eval.cli label runs/<run_id>/responses.jsonl --output-path runs/<run_id>/labels.jsonl`.
- The CLI shows a suggested label based on heuristics (refusal, safety-prefix, unsafe-content patterns) but humans make the final decision.
- Reports may flag unsafe/anomaly/PII signals; treat them as aids, not ground truth.
- Label definitions: see `labeling/rubric.md`.
- Keep prompts and labels non-operational; do not execute any generated content.
