from __future__ import annotations

from typing import Any


def extract_text_from_openai(payload: dict[str, Any]) -> str:
    try:
        return payload["choices"][0]["message"]["content"]
    except Exception:
        return ""


def extract_text_generic(payload: dict[str, Any]) -> str:
    return payload.get("response") or payload.get("generated_text") or payload.get("content", "")
