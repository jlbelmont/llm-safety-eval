from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd


def _save_fig(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def bar_by_model(df: pd.DataFrame, metric: str, path: Path):
    fig, ax = plt.subplots(figsize=(6, 4))
    df.plot.bar(x="model_id", y=metric, ax=ax, legend=False)
    ax.set_ylabel(metric)
    ax.set_title(f"{metric} by model")
    _save_fig(fig, path)


def bar_by_category(cat_df: pd.DataFrame, metric: str, path: Path):
    fig, ax = plt.subplots(figsize=(7, 4))
    pivot = cat_df.pivot(index="category", columns="model_id", values=metric)
    pivot.plot(kind="bar", ax=ax)
    ax.set_ylabel(metric)
    ax.set_title(f"{metric} by category and model")
    _save_fig(fig, path)


def safety_degradation(cat_df: pd.DataFrame, path: Path):
    fig, ax = plt.subplots(figsize=(7, 4))
    # assume categories encode strategy; plot unsafe rate
    pivot = cat_df.pivot(index="category", columns="model_id", values="UNSAFE_COMPLIANCE_rate")
    pivot.plot(kind="bar", ax=ax)
    ax.set_ylabel("unsafe rate")
    ax.set_title("Safety degradation across prompt strategies")
    _save_fig(fig, path)
