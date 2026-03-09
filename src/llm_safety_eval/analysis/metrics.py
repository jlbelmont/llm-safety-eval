from __future__ import annotations

import numpy as np
import pandas as pd

from .safety_metrics import (
    aggregate_metrics,
    category_rates,
    prepare_evaluation_df,
    summary_metrics,
    transform_rates,
)


def refusal_rates(df: pd.DataFrame) -> pd.Series:
    prepared = prepare_evaluation_df(df)
    counts = prepared["label"].value_counts()
    total = counts.sum()
    return counts / total if total else counts


def category_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    prepared = prepare_evaluation_df(df)
    return prepared.groupby(["model_id", "category", "label"]).size().unstack(fill_value=0)


def confusion(df: pd.DataFrame) -> pd.DataFrame:
    prepared = prepare_evaluation_df(df)
    return pd.crosstab(prepared["model_id"], prepared["label"])


def unsafe_flags(df: pd.DataFrame) -> pd.DataFrame:
    prepared = prepare_evaluation_df(df)
    if "unsafe_matches" not in prepared.columns:
        return pd.DataFrame()
    flagged = prepared[prepared["unsafe_matches"].fillna(0) > 0]
    return flagged.groupby("model_id").size().reset_index(name="unsafe_flagged")


def anomaly_flags(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    prepared = prepare_evaluation_df(df)
    if "anomaly_score" not in prepared.columns:
        return pd.DataFrame()
    flagged = prepared[prepared["anomaly_score"].fillna(0) >= threshold]
    return flagged.groupby("model_id").size().reset_index(name="anomaly_flagged")


def pii_flags(df: pd.DataFrame) -> pd.DataFrame:
    prepared = prepare_evaluation_df(df)
    if "pii_score" not in prepared.columns:
        return pd.DataFrame()
    flagged = prepared[prepared["pii_score"].fillna(0) > 0]
    return flagged.groupby("model_id").size().reset_index(name="pii_flagged")


def bootstrap_rate_ci(
    series: pd.Series,
    n_boot: int = 200,
    alpha: float = 0.05,
    seed: int = 42,
) -> tuple[float, float]:
    if series.empty:
        return (0.0, 0.0)

    rng = np.random.default_rng(seed)
    values = series.values
    means = []
    for _ in range(n_boot):
        sample = rng.choice(values, size=len(values), replace=True)
        means.append(sample.mean())

    lower = float(np.percentile(means, 100 * (alpha / 2)))
    upper = float(np.percentile(means, 100 * (1 - alpha / 2)))
    return lower, upper


__all__ = [
    "aggregate_metrics",
    "summary_metrics",
    "category_rates",
    "transform_rates",
    "refusal_rates",
    "category_breakdown",
    "confusion",
    "unsafe_flags",
    "anomaly_flags",
    "pii_flags",
    "bootstrap_rate_ci",
]

