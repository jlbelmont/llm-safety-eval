from __future__ import annotations

import pandas as pd

from .metrics import summary_metrics


def summarize_df(df: pd.DataFrame) -> pd.DataFrame:
    return summary_metrics(df)


def summarize(labels_path: str) -> pd.DataFrame:
    df = pd.read_json(labels_path, lines=True)
    return summarize_df(df)
