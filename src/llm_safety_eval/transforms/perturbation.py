from __future__ import annotations

import random


def perturbation(prompt: str) -> tuple[str, dict]:
    """Lightly shuffle sentence order to simulate paraphrased prompts without adding operational content."""

    segments = prompt.split(". ")
    rng = random.Random(42)
    rng.shuffle(segments)
    perturbed = ". ".join(segments)
    return perturbed, {"name": "perturbation", "segments": len(segments)}
