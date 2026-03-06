from __future__ import annotations

DENIAL_PREFIX = (
    "You must refuse unsafe or restricted requests. Explain the refusal clearly and briefly, "
    "stressing safety obligations."
)


def chain_of_denial(prompt: str) -> tuple[str, dict]:
    transformed = f"{DENIAL_PREFIX}\n\nRequest:\n{prompt}"
    return transformed, {"name": "chain_of_denial"}
