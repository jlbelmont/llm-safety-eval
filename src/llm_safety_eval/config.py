from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(base_path: Path) -> dict[str, Any]:
    """Load base config and resolve relative paths to repo root."""

    data = load_yaml(base_path)
    repo_root = base_path.parent.parent

    paths = data.get("paths", {})
    resolved_paths = {
        key: str((repo_root / Path(value)).resolve())
        for key, value in paths.items()
    }
    data["paths"] = resolved_paths
    return data
