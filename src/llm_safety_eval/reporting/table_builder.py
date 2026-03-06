from __future__ import annotations

import pandas as pd


def model_comparison_table(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["model_id", "REFUSAL_rate", "PARTIAL_COMPLIANCE_rate", "UNSAFE_COMPLIANCE_rate", "total"]
    existing = [c for c in cols if c in df.columns]
    return df[existing].copy()


def prompt_category_table(cat_df: pd.DataFrame) -> pd.DataFrame:
    return cat_df.copy()


def to_latex_table(df: pd.DataFrame, caption: str, label: str) -> str:
    return df.to_latex(index=False, caption=caption, label=label, float_format="%.3f")
