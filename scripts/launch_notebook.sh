#!/usr/bin/env bash
set -euo pipefail

notebooks_dir="$(cd "$(dirname "$0")/.." && pwd)/notebooks"
cd "$notebooks_dir"
exec jupyter lab --NotebookApp.notebook_dir="$notebooks_dir"
