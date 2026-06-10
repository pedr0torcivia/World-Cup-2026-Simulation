from __future__ import annotations

import numpy as np


def sample_low_probability_events(rng: np.random.Generator, base_probability: float = 0.015) -> list[str]:
    events = []
    if rng.random() < base_probability:
        events.append("defensive_error")
    if rng.random() < base_probability * 0.5:
        events.append("var_reversal")
    return events

