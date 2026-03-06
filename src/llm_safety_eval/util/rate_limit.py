from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class TokenBucket:
    rate_per_min: int
    capacity: int
    tokens: float
    last_refill: float

    @classmethod
    def create(cls, rate_per_min: int) -> "TokenBucket":
        now = time.time()
        return cls(rate_per_min=rate_per_min, capacity=rate_per_min, tokens=rate_per_min, last_refill=now)

    def consume(self, amount: int = 1) -> float:
        now = time.time()
        elapsed = now - self.last_refill
        refill = (self.rate_per_min / 60.0) * elapsed
        self.tokens = min(self.capacity, self.tokens + refill)
        self.last_refill = now
        if self.tokens >= amount:
            self.tokens -= amount
            return 0.0
        deficit = amount - self.tokens
        wait = deficit / (self.rate_per_min / 60.0)
        self.tokens = 0
        return wait
