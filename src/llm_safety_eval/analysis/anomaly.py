from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AnomalyScore:
    repetition: float
    length: int
    score: float


def anomaly_score(text: str) -> AnomalyScore:
    tokens = text.split()
    length = len(tokens)
    if length == 0:
        return AnomalyScore(repetition=0.0, length=0, score=0.0)
    repeats = sum(1 for i in range(1, length) if tokens[i] == tokens[i - 1])
    repetition_ratio = repeats / length
    # score combines repetition and length extremes
    score = min(1.0, repetition_ratio * 2 + (1.0 if length > 400 else 0))
    return AnomalyScore(repetition=repetition_ratio, length=length, score=score)
