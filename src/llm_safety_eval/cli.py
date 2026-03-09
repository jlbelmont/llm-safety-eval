from __future__ import annotations

from pathlib import Path

import typer
import os
import json

from .runner import Runner
from .labeling import label_cli
from .analysis import report_cli
from .experiment_matrix import build_matrix
from .config import load_config

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def run(
    base_config: Path = typer.Option(Path("configs/base.yaml"), help="Base config path"),
    matrix: Path = typer.Option(Path("configs/matrix.yaml"), help="Experiment matrix path"),
    models: Path = typer.Option(Path("configs/models.yaml"), help="Models config path"),
    providers: Path = typer.Option(Path("configs/providers.yaml"), help="Providers config path"),
    execute: bool = typer.Option(
        False,
        "--execute/--no-execute",
        help="If true, allow clients to make network/model calls (requires LSE_ALLOW_NETWORK=1).",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print planned matrix and exit."),
    limit: int = typer.Option(None, help="Limit number of matrix cells to run."),
    sample: int = typer.Option(None, help="Randomly sample this many matrix cells."),
    output_dir: Path = typer.Option(None, help="Override output directory for runs."),
    seed: int = typer.Option(42, help="Seed for sampling."),
) -> None:
    if execute and os.getenv("LSE_ALLOW_NETWORK", "0") != "1":
        typer.echo("ERROR: --execute set but LSE_ALLOW_NETWORK != 1. Aborting for safety.", err=True)
        raise typer.Exit(code=1)
    if dry_run:
        base_cfg = load_config(base_config)
        matrix_cfg = Runner._load_yaml(matrix)
        prompts_path = Path(base_cfg["paths"]["prompt_suite"])
        prompt_suite = Runner._load_yaml(prompts_path)
        cats = set(prompt_suite.get("categories", {}).keys())
        if "benign_control" not in cats:
            typer.echo("Warning: benign_control category missing in prompt suite.", err=True)
        cells = list(build_matrix(matrix_cfg))
        typer.echo(f"Seed: {seed}")
        typer.echo(f"Planned cells: {len(cells)}")
        typer.echo(json.dumps(matrix_cfg["matrix"], indent=2))
        raise typer.Exit(code=0)
    runner = Runner(repo_root=Path("."))
    run_id = runner.run(
        base_config,
        matrix,
        models,
        providers,
        execute=execute,
        limit=limit,
        sample=sample,
        output_dir=output_dir,
        seed=seed,
    )
    typer.echo(f"Run complete: {run_id}")


@app.command()
def label(
    responses_path: Path = typer.Argument(..., help="Path to responses.jsonl"),
    output_path: Path = typer.Option(..., help="Where to write labels.jsonl"),
    labeler: str = typer.Option("human", help="Labeler identifier"),
) -> None:
    label_cli.label(responses_path=responses_path, output_path=output_path, labeler=labeler)


@app.command()
def summarize(
    run_dir: Path = typer.Argument(..., help="Run directory (contains responses.jsonl)"),
    matrix_config: Path = typer.Option(None, help="Optional matrix config path for experiment-group definitions"),
    bootstrap_iterations: int = typer.Option(1000, help="Bootstrap iterations for confidence intervals"),
    confidence_level: float = typer.Option(0.95, help="Bootstrap confidence level"),
    seed: int = typer.Option(42, help="Bootstrap random seed"),
) -> None:
    report_cli.summarize_run(
        run_dir=run_dir,
        matrix_config=matrix_config,
        bootstrap_iterations=bootstrap_iterations,
        confidence_level=confidence_level,
        seed=seed,
    )


if __name__ == "__main__":
    app()
