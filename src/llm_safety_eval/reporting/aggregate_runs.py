from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
import yaml


def _load_jsonl(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_json(path, lines=True)


def load_run(run_dir: Path) -> dict[str, pd.DataFrame]:
    responses = _load_jsonl(run_dir / "responses.jsonl")
    labels = _load_jsonl(run_dir / "labels.jsonl")
    metadata = yaml.safe_load((run_dir / "metadata.json").read_text()) if (run_dir / "metadata.json").exists() else {}
    return {"responses": responses, "labels": labels, "metadata": metadata}


def merge_runs(run_dirs: Iterable[Path]) -> pd.DataFrame:
    frames = []
    for rdir in run_dirs:
        run_data = load_run(rdir)
        df = run_data["labels"] if not run_data["labels"].empty else run_data["responses"]
        if df.empty:
            continue
        df = df.copy()
        df["run_id"] = rdir.name
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def aggregate_metrics(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (model_comparison, category_breakdown)."""

    if "label" not in df.columns:
        raise ValueError("No 'label' column found. Label runs first or ensure 'label' is present.")

    model_cmp = (
        df.groupby(["model_id", "label"])
        .size()
        .unstack(fill_value=0)
        .assign(total=lambda x: x.sum(axis=1))
    )
    for label in ["REFUSAL", "PARTIAL_COMPLIANCE", "UNSAFE_COMPLIANCE"]:
        if label in model_cmp:
            model_cmp[f"{label}_rate"] = model_cmp[label] / model_cmp["total"]
    model_cmp = model_cmp.reset_index()

    cat_bd = (
        df.groupby(["model_id", "category", "label"])
        .size()
        .unstack(fill_value=0)
        .assign(total=lambda x: x.sum(axis=1))
    )
    for label in ["REFUSAL", "PARTIAL_COMPLIANCE", "UNSAFE_COMPLIANCE"]:
        if label in cat_bd:
            cat_bd[f"{label}_rate"] = cat_bd[label] / cat_bd["total"]
    cat_bd = cat_bd.reset_index()
    return model_cmp, cat_bd
