#!/usr/bin/env bash
set -euo pipefail

# Run a mock experiment using default configs and mock client.
python -m llm_safety_eval.cli run

# Summarize the most recent run directory (user should adjust run_id as needed).
latest_run=$(ls -1dt runs/*/ | head -n 1 || true)
if [ -n "$latest_run" ]; then
  python -m llm_safety_eval.cli summarize "$latest_run"
fi
