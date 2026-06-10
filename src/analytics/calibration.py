from __future__ import annotations

import math


def brier_score(probability: float, outcome: int) -> float:
    return (probability - outcome) ** 2


def log_loss(probability: float, outcome: int, epsilon: float = 1e-12) -> float:
    p = min(1.0 - epsilon, max(epsilon, probability))
    return -(outcome * math.log(p) + (1 - outcome) * math.log(1 - p))

