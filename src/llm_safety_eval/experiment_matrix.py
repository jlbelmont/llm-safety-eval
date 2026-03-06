from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable


@dataclass(frozen=True)
class ExperimentCell:
    model_id: str
    prompt_category: str
    transform: str
    temperature: float
    max_tokens: int
    trial_index: int


def build_matrix(matrix_config: dict, trials: int | None = None) -> Iterable[ExperimentCell]:
    cfg = matrix_config["matrix"]
    temperatures = cfg["generation_parameters"]["temperature"]
    max_tokens = cfg["generation_parameters"]["max_tokens"]
    trials = trials or cfg.get("trials", 1)

    for model_id, prompt_category, transform, temp, max_tok, trial_index in product(
        cfg["models"], cfg["prompt_categories"], cfg["transforms"], temperatures, max_tokens, range(trials)
    ):
        yield ExperimentCell(
            model_id=model_id,
            prompt_category=prompt_category,
            transform=transform,
            temperature=temp,
            max_tokens=max_tok,
            trial_index=trial_index,
        )
