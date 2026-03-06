from __future__ import annotations

import re
from dataclasses import dataclass


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}")
IP_RE = re.compile(r"\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b")


@dataclass
class PiiScore:
    email_hits: int
    ip_hits: int

    @property
    def score(self) -> float:
        return float(self.email_hits + self.ip_hits)


def pii_score(text: str) -> PiiScore:
    return PiiScore(email_hits=len(EMAIL_RE.findall(text)), ip_hits=len(IP_RE.findall(text)))
