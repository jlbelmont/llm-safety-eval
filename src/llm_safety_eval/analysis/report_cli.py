from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from .summarize import summarize_df
from .metrics import category_rates, transform_rates, unsafe_flags, anomaly_flags, pii_flags
from ..util.plotting import make_bar_plot_base64

app = typer.Typer(add_completion=False, no_args_is_help=True)


def summarize_run(run_dir: Path) -> None:
    responses_path = run_dir / "responses.jsonl"
    labels_path = run_dir / "labels.jsonl"
    if not responses_path.exists():
        raise FileNotFoundError(f"{responses_path} not found")

    if labels_path.exists() and labels_path.stat().st_size > 0:
        df = pd.read_json(labels_path, lines=True)
    else:
        df = pd.read_json(responses_path, lines=True)

    summary = summarize_df(df)
    cat = category_rates(df)
    transform = transform_rates(df) if "transform" in df.columns else None
    unsafe = unsafe_flags(df)
    anomalies = anomaly_flags(df)
    pii = pii_flags(df)

    summary_path = run_dir / "summary_metrics.csv"
    summary.to_csv(summary_path, index=False)

    md_lines = ["# Run Summary", "", "## Metrics", "", summary.to_markdown(index=False)]
    md_lines += ["", "## Category Breakdown", "", cat.to_markdown(index=False)]
    if transform is not None:
        md_lines += ["", "## Transform Breakdown", "", transform.to_markdown(index=False)]
    if not unsafe.empty:
        md_lines += ["", "## Unsafe Flags", "", unsafe.to_markdown(index=False)]
    if not anomalies.empty:
        md_lines += ["", "## Anomaly Flags", "", anomalies.to_markdown(index=False)]
    if not pii.empty:
        md_lines += ["", "## PII Flags", "", pii.to_markdown(index=False)]
    md_path = run_dir / "summary.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    # HTML with simple inline styling and optional plots
    html_parts = [
        "<html><head><style>body{font-family:Arial, sans-serif;} table{border-collapse:collapse;} td,th{border:1px solid #ddd;padding:6px;} th{background:#f2f2f2;} </style></head><body>",
        "<h1>Run Summary</h1>",
        "<h2>Metrics</h2>",
        summary.to_html(index=False),
        "<h2>Category Breakdown</h2>",
        cat.to_html(index=False),
    ]
    if transform is not None:
        html_parts += ["<h2>Transform Breakdown</h2>", transform.to_html(index=False)]
    if not unsafe.empty:
        html_parts += ["<h2>Unsafe Flags</h2>", unsafe.to_html(index=False)]
    if not anomalies.empty:
        html_parts += ["<h2>Anomaly Flags</h2>", anomalies.to_html(index=False)]
    if not pii.empty:
        html_parts += ["<h2>PII Flags</h2>", pii.to_html(index=False)]

    try:
        figs_dir = run_dir / "figs"
        figs_dir.mkdir(parents=True, exist_ok=True)
        if not summary.empty:
            img_refusal = figs_dir / "refusal_rates.png"
            b64_refusal = make_bar_plot_base64(
                summary, x="model_id", ys=["REFUSAL_rate", "UNSAFE_COMPLIANCE_rate"], title="Refusal vs Unsafe Compliance", save_path=img_refusal
            )
            html_parts += [f'<h2>Refusal vs Unsafe</h2><img src="data:image/png;base64,{b64_refusal}"/>']
        if transform is not None and not transform.empty:
            img_transform = figs_dir / "transform_refusal.png"
            b64_transform = make_bar_plot_base64(
                transform,
                x="transform",
                ys=["REFUSAL_rate"],
                title="Refusal rate by transform",
                save_path=img_transform,
            )
            html_parts += [f'<h2>Transform Refusal Rates</h2><img src="data:image/png;base64,{b64_transform}"/>']
        if not cat.empty:
            img_tc = figs_dir / "transform_category.png"
            # prepare stacked bars by category/refusal
            tc_df = transform if transform is not None and not transform.empty else cat
            b64_tc = make_bar_plot_base64(
                tc_df,
                x="category" if "category" in tc_df.columns else "transform",
                ys=[col for col in tc_df.columns if col.endswith("_rate") and "REFUSAL" in col],
                title="Refusal-related rates by group",
                save_path=img_tc,
            )
            html_parts += [f'<h2>Transform/Category Rates</h2><img src="data:image/png;base64,{b64_tc}"/>']
    except Exception:
        html_parts += ["<p><em>Plots unavailable (matplotlib missing or error encountered).</em></p>"]

    html_parts.append("</body></html>")
    (run_dir / "summary.html").write_text("\n".join(html_parts), encoding="utf-8")

    typer.echo(f"Wrote summary to {summary_path}, {md_path}, and summary.html")


@app.command()
def summarize_cli(run_dir: Path = typer.Argument(..., help="Run directory")) -> None:
    summarize_run(run_dir)


if __name__ == "__main__":
    app()
