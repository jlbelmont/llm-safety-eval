from __future__ import annotations

from pathlib import Path
import yaml

from .schemas import Prompt, PromptCategory, PromptSuite
from .validate import validate_prompt_suite


def load_prompt_suite(path: Path) -> PromptSuite:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    categories: dict[str, PromptCategory] = {}
    for name, payload in data.get("categories", {}).items():
        prompts = [Prompt(category=name, **p) for p in payload.get("prompts", [])]
        categories[name] = PromptCategory(description=payload.get("description", ""), prompts=prompts)

    suite = PromptSuite(version=str(data.get("version", "0.0.0")), categories=categories)
    validate_prompt_suite(suite)
    return suite
