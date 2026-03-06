from __future__ import annotations

import pandas as pd


def refusal_rates(df: pd.DataFrame) -> pd.Series:
    counts = df["label"].value_counts()
    total = counts.sum()
    return counts / total if total else counts


def category_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["model_id", "category", "label"]).size().unstack(fill_value=0)


def summary_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute high-level metrics per model."""

    per_model = (
        df.groupby(["model_id", "label"])
        .size()
        .unstack(fill_value=0)
        .rename_axis(index="model_id", columns="label")
    )
    per_model["total"] = per_model.sum(axis=1)
    for label in ["REFUSAL", "PARTIAL_COMPLIANCE", "UNSAFE_COMPLIANCE"]:
        if label in per_model:
            per_model[f"{label}_rate"] = per_model[label] / per_model["total"]
        else:
            per_model[f"{label}_rate"] = 0.0
    return per_model.reset_index()


def category_rates(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(["model_id", "category", "label"])
        .size()
        .unstack(fill_value=0)
        .rename_axis(index=["model_id", "category"], columns="label")
    )
    grouped["total"] = grouped.sum(axis=1)
    for label in ["REFUSAL", "PARTIAL_COMPLIANCE", "UNSAFE_COMPLIANCE"]:
        if label in grouped:
            grouped[f"{label}_rate"] = grouped[label] / grouped["total"]
        else:
            grouped[f"{label}_rate"] = 0.0
    return grouped.reset_index()


def confusion(df: pd.DataFrame) -> pd.DataFrame:
    return pd.crosstab(df["model_id"], df["label"])


def transform_rates(df: pd.DataFrame) -> pd.DataFrame:
    if "transform" not in df.columns:
        return pd.DataFrame()
    grouped = (
        df.groupby(["model_id", "transform", "label"])
        .size()
        .unstack(fill_value=0)
        .rename_axis(index=["model_id", "transform"], columns="label")
    )
    grouped["total"] = grouped.sum(axis=1)
    for label in ["REFUSAL", "PARTIAL_COMPLIANCE", "UNSAFE_COMPLIANCE"]:
        if label in grouped:
            grouped[f"{label}_rate"] = grouped[label] / grouped["total"]
        else:
            grouped[f"{label}_rate"] = 0.0
    return grouped.reset_index()


def unsafe_flags(df: pd.DataFrame) -> pd.DataFrame:
    if "unsafe_matches" not in df.columns:
        return pd.DataFrame()
    flagged = df[df["unsafe_matches"].fillna(0) > 0]
    return flagged.groupby("model_id").size().reset_index(name="unsafe_flagged")


def anomaly_flags(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    if "anomaly_score" not in df.columns:
        return pd.DataFrame()
    flagged = df[df["anomaly_score"].fillna(0) >= threshold]
    return flagged.groupby("model_id").size().reset_index(name="anomaly_flagged")


def pii_flags(df: pd.DataFrame) -> pd.DataFrame:
    if "pii_score" not in df.columns:
        return pd.DataFrame()
    flagged = df[df["pii_score"].fillna(0) > 0]
    return flagged.groupby("model_id").size().reset_index(name="pii_flagged")


def bootstrap_rate_ci(series: pd.Series, n_boot: int = 200, alpha: float = 0.05) -> tuple[float, float]:
    if series.empty:
        return (0.0, 0.0)
    import numpy as np

    rates = []
    values = series.values
    for _ in range(n_boot):
        sample = np.random.choice(values, size=len(values), replace=True)
        rates.append(sample.mean())
    lower = float(np.percentile(rates, 100 * (alpha / 2)))
    upper = float(np.percentile(rates, 100 * (1 - alpha / 2)))
    return lower, upper
