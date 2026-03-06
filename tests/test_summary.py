import pandas as pd

from llm_safety_eval.analysis.summarize import summarize_df


def test_summarize_df_rates():
    df = pd.DataFrame(
        [
            {"model_id": "m1", "label": "REFUSAL"},
            {"model_id": "m1", "label": "UNSAFE_COMPLIANCE"},
            {"model_id": "m1", "label": "PARTIAL_COMPLIANCE"},
        ]
    )
    summary = summarize_df(df)
    assert "REFUSAL_rate" in summary.columns
    assert summary.loc[summary["model_id"] == "m1", "total"].iloc[0] == 3


def test_transform_rates():
    df = pd.DataFrame(
        [
            {"model_id": "m1", "label": "REFUSAL", "transform": "none"},
            {"model_id": "m1", "label": "UNSAFE_COMPLIANCE", "transform": "safety_prefix"},
        ]
    )
    from llm_safety_eval.analysis.metrics import transform_rates

    tr = transform_rates(df)
    assert set(tr["transform"]) == {"none", "safety_prefix"}


def test_unsafe_flags():
    df = pd.DataFrame(
        [
            {"model_id": "m1", "unsafe_matches": 1},
            {"model_id": "m1", "unsafe_matches": 0},
            {"model_id": "m2", "unsafe_matches": 2},
        ]
    )
    from llm_safety_eval.analysis.metrics import unsafe_flags

    uf = unsafe_flags(df)
    assert set(uf["model_id"]) == {"m1", "m2"}
