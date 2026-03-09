from __future__ import annotations

from pathlib import Path
import pandas as pd


def build_paper_dataset(df: pd.DataFrame, prompt_map: dict | None = None) -> pd.DataFrame:
    out = df.copy()
    if prompt_map:
        out["prompt_text"] = out["prompt_id"].map(prompt_map)
    return out


def prompt_text_map(prompt_suite_path: Path) -> dict[str, str]:
    import yaml

    data = yaml.safe_load(prompt_suite_path.read_text()) or {}
    mapping = {}
    for _category, payload in data.get("categories", {}).items():
        for p in payload.get("prompts", []):
            mapping[p["prompt_id"]] = p.get("text", "")
    return mapping
