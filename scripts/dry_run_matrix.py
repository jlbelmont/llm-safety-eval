from __future__ import annotations

import json
from pathlib import Path

import typer
import yaml

from llm_safety_eval.experiment_matrix import build_matrix

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def main(
    matrix_path: Path = typer.Argument(Path("configs/matrix.yaml")),
    prompt_suite_path: Path = typer.Option(Path("prompts/prompt_suites.yaml")),
) -> None:
    matrix_cfg = yaml.safe_load(matrix_path.read_text())
    prompt_suite = yaml.safe_load(prompt_suite_path.read_text()) or {}
    categories = prompt_suite.get("categories", {})
    missing = [cat for cat in matrix_cfg["matrix"]["prompt_categories"] if cat not in categories]
    if missing:
        typer.echo(f"Warning: prompt categories missing prompts: {missing}")
    cells = list(build_matrix(matrix_cfg))
    typer.echo(f"Total planned cells: {len(cells)}")
    typer.echo(json.dumps(matrix_cfg["matrix"], indent=2))


if __name__ == "__main__":
    app()
