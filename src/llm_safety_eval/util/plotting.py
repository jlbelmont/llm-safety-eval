from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd


def make_bar_plot_base64(df: pd.DataFrame, x: str, ys: Iterable[str], title: str, save_path: Path | None = None) -> str:
    fig, ax = plt.subplots(figsize=(6, 4))
    for y in ys:
        if y in df.columns:
            ax.bar(df[x], df[y], label=y, alpha=0.8)
    ax.set_title(title)
    ax.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150)
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=150)
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
