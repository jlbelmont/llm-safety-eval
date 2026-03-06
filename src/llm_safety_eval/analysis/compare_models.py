from __future__ import annotations

import pandas as pd


def compare_pairwise(df: pd.DataFrame, model_a: str, model_b: str) -> pd.DataFrame:
    filtered = df[df["model_id"].isin([model_a, model_b])]
    return filtered.pivot_table(
        index=["prompt_id", "category", "trial_index"],
        columns="model_id",
        values="label",
        aggfunc="first",
    )
