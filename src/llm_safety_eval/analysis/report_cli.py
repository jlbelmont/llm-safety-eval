from __future__ import annotations

from pathlib import Path
import json

import pandas as pd
import typer

from .metrics import anomaly_flags, pii_flags, unsafe_flags
from .safety_metrics import (
    aggregate_metrics,
    compare_experiment_groups,
    expand_experiment_groups,
    experiment_group_metrics,
    filter_by_group,
    load_matrix_config,
    prepare_evaluation_df,
)
from .statistics import bootstrap_confidence_intervals
from ..util.hashing import file_sha256
from ..util.plotting import make_bar_plot_base64

app = typer.Typer(add_completion=False, no_args_is_help=True)


def _merge_with_ci(base: pd.DataFrame, ci: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    if base.empty or ci.empty:
        return base
    return base.merge(ci, on=keys, how="left")


def _write_csv(path: Path, df: pd.DataFrame) -> None:
    if df is None or df.empty:
        return
    path.write_text(df.to_csv(index=False), encoding="utf-8")


def _markdown_section(title: str, df: pd.DataFrame) -> list[str]:
    if df.empty:
        return []
    return ["", f"## {title}", "", df.to_markdown(index=False)]


def _html_section(title: str, df: pd.DataFrame) -> list[str]:
    if df.empty:
        return []
    return [f"<h2>{title}</h2>", df.to_html(index=False)]


def _update_artifact_index(run_dir: Path, artifact_paths: dict[str, Path]) -> None:
    artifact_index_path = run_dir / "artifact_index.json"
    if artifact_index_path.exists():
        existing = json.loads(artifact_index_path.read_text(encoding="utf-8"))
    else:
        existing = {}

    for name, path in artifact_paths.items():
        if path.exists():
            existing[name] = {"path": str(path), "sha256": file_sha256(path)}

    artifact_index_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def _experiment_metric_ci(
    df: pd.DataFrame,
    experiments: dict[str, object],
    bootstrap_iterations: int,
    confidence_level: float,
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for experiment_name, definition in experiments.items():
        dimension, groups = expand_experiment_groups(definition)
        if not groups:
            continue
        base_group_by = [] if dimension == "models" else ["model_id"]
        for group in groups:
            filtered = filter_by_group(df, group)
            if filtered.empty:
                continue
            if base_group_by:
                grouped = filtered.groupby(base_group_by, dropna=False, sort=True)
            else:
                grouped = [((), filtered)]
            for base_key, subset in grouped:
                record = {
                    "experiment_name": experiment_name,
                    "group_name": group.name,
                }
                if base_group_by:
                    if len(base_group_by) == 1:
                        record[base_group_by[0]] = base_key[0] if isinstance(base_key, tuple) else base_key
                    else:
                        for key, value in zip(base_group_by, base_key):
                            record[key] = value
                ci = bootstrap_confidence_intervals(
                    subset,
                    n_boot=bootstrap_iterations,
                    confidence_level=confidence_level,
                    seed=seed,
                )
                record.update(ci.iloc[0].to_dict())
                rows.append(record)
    return pd.DataFrame(rows)


def summarize_run(
    run_dir: Path,
    matrix_config: Path | None = None,
    bootstrap_iterations: int = 1000,
    confidence_level: float = 0.95,
    seed: int = 42,
) -> None:
    responses_path = run_dir / "responses.jsonl"
    labels_path = run_dir / "labels.jsonl"
    if not responses_path.exists():
        raise FileNotFoundError(f"{responses_path} not found")

    source_path = labels_path if labels_path.exists() and labels_path.stat().st_size > 0 else responses_path
    df = pd.read_json(source_path, lines=True)
    prepared = prepare_evaluation_df(df)

    summary = aggregate_metrics(prepared, group_by=["model_id"])
    summary_ci = bootstrap_confidence_intervals(
        prepared,
        group_by=["model_id"],
        n_boot=bootstrap_iterations,
        confidence_level=confidence_level,
        seed=seed,
    )
    summary = _merge_with_ci(summary, summary_ci, ["model_id"])

    category = aggregate_metrics(prepared, group_by=["model_id", "category"])
    category_ci = bootstrap_confidence_intervals(
        prepared,
        group_by=["model_id", "category"],
        n_boot=bootstrap_iterations,
        confidence_level=confidence_level,
        seed=seed,
    )
    category = _merge_with_ci(category, category_ci, ["model_id", "category"])

    transform = aggregate_metrics(prepared, group_by=["model_id", "transform"])
    transform_ci = bootstrap_confidence_intervals(
        prepared,
        group_by=["model_id", "transform"],
        n_boot=bootstrap_iterations,
        confidence_level=confidence_level,
        seed=seed,
    )
    transform = _merge_with_ci(transform, transform_ci, ["model_id", "transform"])

    matrix_cfg = load_matrix_config(run_dir, matrix_config)
    experiments = matrix_cfg.get("experiments", {})
    experiment_metrics = experiment_group_metrics(prepared, experiments)
    if not experiment_metrics.empty:
        experiment_group_keys = [
            col for col in ["experiment_name", "group_name", "model_id"] if col in experiment_metrics.columns
        ]
        experiment_ci = _experiment_metric_ci(
            prepared,
            experiments,
            bootstrap_iterations=bootstrap_iterations,
            confidence_level=confidence_level,
            seed=seed,
        )
        experiment_metrics = _merge_with_ci(experiment_metrics, experiment_ci, experiment_group_keys)

    experiment_comparisons = compare_experiment_groups(
        prepared,
        experiments,
        n_boot=bootstrap_iterations,
        confidence_level=confidence_level,
        seed=seed,
    )

    unsafe = unsafe_flags(prepared)
    anomalies = anomaly_flags(prepared)
    pii = pii_flags(prepared)

    summary_path = run_dir / "summary_metrics.csv"
    category_path = run_dir / "category_metrics.csv"
    transform_path = run_dir / "transform_metrics.csv"
    experiment_metrics_path = run_dir / "experiment_group_metrics.csv"
    experiment_comparisons_path = run_dir / "experiment_group_comparisons.csv"

    _write_csv(summary_path, summary)
    _write_csv(category_path, category)
    _write_csv(transform_path, transform)
    _write_csv(experiment_metrics_path, experiment_metrics)
    _write_csv(experiment_comparisons_path, experiment_comparisons)

    md_lines = [
        "# Run Summary",
        "",
        f"- Source data: `{source_path.name}`",
        f"- Bootstrap iterations: {bootstrap_iterations}",
        f"- Confidence level: {confidence_level:.2f}",
        "",
    ]
    md_lines += _markdown_section("Metrics", summary)
    md_lines += _markdown_section("Category Breakdown", category)
    md_lines += _markdown_section("Transform Breakdown", transform)
    md_lines += _markdown_section("Experiment Group Metrics", experiment_metrics)
    md_lines += _markdown_section("Experiment Group Comparisons", experiment_comparisons)
    md_lines += _markdown_section("Unsafe Flags", unsafe)
    md_lines += _markdown_section("Anomaly Flags", anomalies)
    md_lines += _markdown_section("PII Flags", pii)
    md_path = run_dir / "summary.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    html_parts = [
        "<html><head><style>body{font-family:Arial, sans-serif;} table{border-collapse:collapse;} td,th{border:1px solid #ddd;padding:6px;} th{background:#f2f2f2;} code{background:#f5f5f5;padding:2px 4px;}</style></head><body>",
        "<h1>Run Summary</h1>",
        f"<p><strong>Source data:</strong> <code>{source_path.name}</code><br/><strong>Bootstrap iterations:</strong> {bootstrap_iterations}<br/><strong>Confidence level:</strong> {confidence_level:.2f}</p>",
    ]
    html_parts += _html_section("Metrics", summary)
    html_parts += _html_section("Category Breakdown", category)
    html_parts += _html_section("Transform Breakdown", transform)
    html_parts += _html_section("Experiment Group Metrics", experiment_metrics)
    html_parts += _html_section("Experiment Group Comparisons", experiment_comparisons)
    html_parts += _html_section("Unsafe Flags", unsafe)
    html_parts += _html_section("Anomaly Flags", anomalies)
    html_parts += _html_section("PII Flags", pii)

    try:
        figs_dir = run_dir / "figs"
        figs_dir.mkdir(parents=True, exist_ok=True)
        if not summary.empty:
            refusal_plot = figs_dir / "refusal_vs_asr.png"
            b64_summary = make_bar_plot_base64(
                summary,
                x="model_id",
                ys=["Refusal_Rate", "ASR", "Unsafe_Rate"],
                title="Refusal, ASR, and Unsafe Rate by Model",
                save_path=refusal_plot,
            )
            html_parts += [f'<h2>Model-Level Safety Metrics</h2><img src="data:image/png;base64,{b64_summary}"/>']
        if not transform.empty:
            transform_plot = figs_dir / "transform_asr.png"
            b64_transform = make_bar_plot_base64(
                transform,
                x="transform",
                ys=["ASR", "Unsafe_Rate"],
                title="ASR and Unsafe Rate by Transform",
                save_path=transform_plot,
            )
            html_parts += [f'<h2>Transform Metrics</h2><img src="data:image/png;base64,{b64_transform}"/>']
    except Exception:
        html_parts += ["<p><em>Plots unavailable (matplotlib missing or an error occurred).</em></p>"]

    html_parts.append("</body></html>")
    summary_html_path = run_dir / "summary.html"
    summary_html_path.write_text("\n".join(html_parts), encoding="utf-8")

    _update_artifact_index(
        run_dir,
        {
            "summary_csv": summary_path,
            "category_metrics_csv": category_path,
            "transform_metrics_csv": transform_path,
            "experiment_group_metrics_csv": experiment_metrics_path,
            "experiment_group_comparisons_csv": experiment_comparisons_path,
            "summary_md": md_path,
            "summary_html": summary_html_path,
        },
    )

    typer.echo(
        "Wrote summary artifacts: "
        f"{summary_path.name}, {category_path.name}, {transform_path.name}, "
        f"{experiment_metrics_path.name}, {experiment_comparisons_path.name}, {md_path.name}, and {summary_html_path.name}"
    )


@app.command()
def summarize_cli(
    run_dir: Path = typer.Argument(..., help="Run directory"),
    matrix_config: Path = typer.Option(None, help="Optional matrix config path for experiment-group definitions"),
    bootstrap_iterations: int = typer.Option(1000, help="Bootstrap iterations for confidence intervals"),
    confidence_level: float = typer.Option(0.95, help="Bootstrap confidence level"),
    seed: int = typer.Option(42, help="Bootstrap random seed"),
) -> None:
    summarize_run(
        run_dir=run_dir,
        matrix_config=matrix_config,
        bootstrap_iterations=bootstrap_iterations,
        confidence_level=confidence_level,
        seed=seed,
    )


if __name__ == "__main__":
    app()
