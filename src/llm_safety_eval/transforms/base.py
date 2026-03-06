from __future__ import annotations

from typing import Callable, Tuple

TransformFn = Callable[[str], Tuple[str, dict]]


def noop_transform(prompt: str) -> tuple[str, dict]:
    return prompt, {"name": "none"}


def apply_transform(name: str, prompt: str) -> tuple[str, dict]:
    from .safety_prefix import safety_prefix
    from .sanitization import sanitize_prompt
    from .chain_of_denial import chain_of_denial
    from .perturbation import perturbation

    registry: dict[str, TransformFn] = {
        "none": noop_transform,
        "safety_prefix": safety_prefix,
        "sanitization": sanitize_prompt,
        "chain_of_denial": chain_of_denial,
        "perturbation": perturbation,
    }
    transform = registry.get(name, noop_transform)
    return transform(prompt)
