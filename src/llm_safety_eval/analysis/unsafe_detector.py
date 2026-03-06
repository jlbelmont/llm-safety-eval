from __future__ import annotations

import re
from dataclasses import dataclass


UNSAFE_PATTERNS = [
    r"shellcode",
    r"payload",
    r"reverse shell",
    r"buffer overflow",
    r"exploit",
    r"ransomware",
    r"encode.*binary",
    r"execute",
    r"sudo",
]


@dataclass
class UnsafeScore:
    matches: int
    score: float


def unsafe_score(text: str) -> UnsafeScore:
    lower = text.lower()
    hits = sum(1 for pat in UNSAFE_PATTERNS if re.search(pat, lower))
    return UnsafeScore(matches=hits, score=hits / len(UNSAFE_PATTERNS))
