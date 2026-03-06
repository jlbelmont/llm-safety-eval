from __future__ import annotations

import re


def sanitize_prompt(prompt: str) -> tuple[str, dict]:
    """Redact obvious dangerous terms while preserving intent signals."""

    redacted = re.sub(r"(exploit|payload|malware|shellcode)", "[redacted]", prompt, flags=re.IGNORECASE)
    return redacted, {"name": "sanitization", "original_length": len(prompt)}
