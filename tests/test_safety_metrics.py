import pandas as pd

from llm_safety_eval.analysis.safety_metrics import (
    aggregate_metrics,
    compare_experiment_groups,
    experiment_group_metrics,
    prepare_evaluation_df,
)
from llm_safety_eval.analysis.statistics import bootstrap_confidence_intervals


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "model_id": "m1",
                "category": "baseline_direct",
                "label": "REFUSAL",
                "generation_parameters": {"transform": "none"},
            },
            {
                "model_id": "m1",
                "category": "baseline_direct",
                "label": "PARTIAL_COMPLIANCE",
                "generation_parameters": {"transform": "none"},
            },
            {
                "model_id": "m1",
                "category": "decomposition",
                "label": "UNSAFE_COMPLIANCE",
                "generation_parameters": {"transform": "safety_prefix"},
            },
            {
                "model_id": "m1",
                "category": "benign_control",
                "label": "REFUSAL",
                "generation_parameters": {"transform": "safety_prefix"},
            },
            {
                "model_id": "m2",
                "category": "baseline_direct",
                "label": "REFUSAL",
                "generation_parameters": {"transform": "none"},
            },
            {
                "model_id": "m2",
                "category": "benign_control",
                "label": "REFUSAL",
                "generation_parameters": {"transform": "none"},
            },
        ]
    )


def test_aggregate_metrics_adds_formal_safety_metrics():
    summary = aggregate_metrics(_sample_df(), group_by=["model_id"])
    row = summary.loc[summary["model_id"] == "m1"].iloc[0]
    assert row["ASR"] == 0.5
    assert row["SSS"] == 0.625
    assert row["FRR"] == 1.0
    assert row["model_id"] == "m1"


def test_prepare_evaluation_df_extracts_transform():
    prepared = prepare_evaluation_df(_sample_df())
    assert set(prepared["transform"]) == {"none", "safety_prefix"}


def test_bootstrap_confidence_intervals_return_expected_columns():
    ci = bootstrap_confidence_intervals(_sample_df(), group_by=["model_id"], n_boot=50, seed=7)
    assert "ASR_ci_lower" in ci.columns
    assert "FRR_ci_upper" in ci.columns


def test_experiment_group_metrics_and_comparisons():
    experiments = {
        "baseline_vs_decomposition": {
            "categories": ["baseline_direct", "decomposition"]
        },
        "transform_effect": {
            "transforms": ["none", "safety_prefix"]
        },
    }
    prepared = prepare_evaluation_df(_sample_df())
    metrics = experiment_group_metrics(prepared, experiments)
    comparisons = compare_experiment_groups(prepared, experiments, n_boot=50, seed=3)
    assert not metrics.empty
    assert not comparisons.empty
    assert "ASR_difference" in comparisons.columns
