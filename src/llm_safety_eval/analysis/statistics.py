from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from .safety_metrics import compute_metric_values, normalize_group_keys, prepare_evaluation_df


DEFAULT_METRICS = [
    "ASR",
    "SSS",
    "FRR",
    "Unsafe_Rate",
    "Partial_Compliance_Rate",
    "Refusal_Rate",
]


def bootstrap_confidence_intervals(
    df: pd.DataFrame,
    group_by: Iterable[str] | None = None,
    metrics: Iterable[str] | None = None,
    n_boot: int = 1000,
    confidence_level: float = 0.95,
    seed: int = 42,
) -> pd.DataFrame:
    """Bootstrap confidence intervals for evaluation metrics."""

    prepared = prepare_evaluation_df(df)
    keys = normalize_group_keys(group_by)
    metric_names = list(metrics or DEFAULT_METRICS)
    alpha = 1.0 - confidence_level
    rng = np.random.default_rng(seed)

    def summarize_group(group_df: pd.DataFrame) -> dict[str, float]:
        intervals: dict[str, float] = {}
        if group_df.empty:
            for metric in metric_names:
                intervals[f"{metric}_ci_lower"] = float("nan")
                intervals[f"{metric}_ci_upper"] = float("nan")
            return intervals

        boot_values: dict[str, list[float]] = {metric: [] for metric in metric_names}
        values = group_df.reset_index(drop=True)
        for _ in range(n_boot):
            sample_indices = rng.integers(0, len(values), size=len(values))
            sample = values.iloc[sample_indices]
            metric_row = compute_metric_values(sample)
            for metric in metric_names:
                value = metric_row.get(metric)
                if pd.notna(value):
                    boot_values[metric].append(float(value))

        for metric in metric_names:
            if not boot_values[metric]:
                intervals[f"{metric}_ci_lower"] = float("nan")
                intervals[f"{metric}_ci_upper"] = float("nan")
                continue
            intervals[f"{metric}_ci_lower"] = float(np.percentile(boot_values[metric], 100 * (alpha / 2)))
            intervals[f"{metric}_ci_upper"] = float(
                np.percentile(boot_values[metric], 100 * (1 - alpha / 2))
            )
        return intervals

    if not keys:
        return pd.DataFrame([summarize_group(prepared)])

    records: list[dict[str, float | str]] = []
    for group_key, group_df in prepared.groupby(keys, dropna=False, sort=True):
        record = summarize_group(group_df)
        if len(keys) == 1:
            record[keys[0]] = group_key[0] if isinstance(group_key, tuple) else group_key
        else:
            for key, value in zip(keys, group_key):
                record[key] = value
        records.append(record)

    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)


def bootstrap_metric_difference(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    metric: str,
    n_boot: int = 1000,
    confidence_level: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    """Bootstrap CI for the difference between two grouped metric estimates."""

    left = prepare_evaluation_df(left_df)
    right = prepare_evaluation_df(right_df)
    if left.empty or right.empty:
        return float("nan"), float("nan")

    alpha = 1.0 - confidence_level
    rng = np.random.default_rng(seed)
    diffs: list[float] = []
    left_reset = left.reset_index(drop=True)
    right_reset = right.reset_index(drop=True)
    for _ in range(n_boot):
        left_indices = rng.integers(0, len(left_reset), size=len(left_reset))
        right_indices = rng.integers(0, len(right_reset), size=len(right_reset))
        left_metric = compute_metric_values(left_reset.iloc[left_indices]).get(metric)
        right_metric = compute_metric_values(right_reset.iloc[right_indices]).get(metric)
        if pd.notna(left_metric) and pd.notna(right_metric):
            diffs.append(float(left_metric) - float(right_metric))

    if not diffs:
        return float("nan"), float("nan")

    lower = float(np.percentile(diffs, 100 * (alpha / 2)))
    upper = float(np.percentile(diffs, 100 * (1 - alpha / 2)))
    return lower, upper
