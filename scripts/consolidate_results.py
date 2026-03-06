from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from llm_safety_eval.reporting.aggregate_runs import merge_runs, aggregate_metrics
from llm_safety_eval.reporting.figure_builder import bar_by_model, bar_by_category, safety_degradation
from llm_safety_eval.reporting.table_builder import model_comparison_table, prompt_category_table
from llm_safety_eval.reporting.export_for_latex import export_table

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def main(runs_root: Path = typer.Argument(Path("runs")), output_root: Path = typer.Option(Path("analysis_outputs"))) -> None:
    run_dirs = [p for p in runs_root.iterdir() if p.is_dir()]
    combined = merge_runs(run_dirs)
    output_root.mkdir(parents=True, exist_ok=True)
    combined_path = output_root / "combined_results.csv"
    combined.to_csv(combined_path, index=False)

    model_cmp, cat_bd = aggregate_metrics(combined)
    model_cmp_path = output_root / "model_comparison_table.csv"
    cat_bd_path = output_root / "prompt_category_breakdown.csv"
    model_cmp.to_csv(model_cmp_path, index=False)
    cat_bd.to_csv(cat_bd_path, index=False)

    # figures
    figs_dir = output_root / "figures"
    bar_by_model(model_cmp, "REFUSAL_rate", figs_dir / "refusal_by_model.png")
    if "UNSAFE_COMPLIANCE_rate" in model_cmp:
        bar_by_model(model_cmp, "UNSAFE_COMPLIANCE_rate", figs_dir / "unsafe_by_model.png")
    bar_by_category(cat_bd, "REFUSAL_rate", figs_dir / "refusal_by_category.png")
    if "UNSAFE_COMPLIANCE_rate" in cat_bd:
        bar_by_category(cat_bd, "UNSAFE_COMPLIANCE_rate", figs_dir / "unsafe_by_category.png")
    safety_degradation(cat_bd, figs_dir / "safety_degradation.png")

    # latex tables
    tables_dir = output_root / "tables"
    export_table(model_comparison_table(model_cmp), tables_dir / "model_comparison_table.tex", "Model comparison", "tab:model-comparison")
    export_table(prompt_category_table(cat_bd), tables_dir / "prompt_category_table.tex", "Prompt category breakdown", "tab:prompt-category")

    typer.echo(f"Wrote combined results to {combined_path}")
    typer.echo(f"Tables -> {tables_dir}")
    typer.echo(f"Figures -> {figs_dir}")


if __name__ == "__main__":
    main()
