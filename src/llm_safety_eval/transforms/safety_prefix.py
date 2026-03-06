from __future__ import annotations

DEFENSIVE_PREFIX = (
    "You are a safety-focused assistant. Decline to produce operational or harmful code. "
    "Explain safety concerns briefly before any answer."
)


def safety_prefix(prompt: str) -> tuple[str, dict]:
    transformed = f"{DEFENSIVE_PREFIX}\n\nOriginal request:\n{prompt}"
    return transformed, {"name": "safety_prefix"}
