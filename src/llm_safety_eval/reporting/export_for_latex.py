from __future__ import annotations

from pathlib import Path
import pandas as pd


def export_table(df: pd.DataFrame, path: Path, caption: str, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tex = df.to_latex(index=False, caption=caption, label=label, float_format="%.3f")
    path.write_text(tex, encoding="utf-8")
