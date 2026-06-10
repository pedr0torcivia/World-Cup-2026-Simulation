from __future__ import annotations

import math

import pandas as pd


def monte_carlo_standard_error(probability: float, simulations: int) -> float:
    if simulations <= 0:
        return 0.0
    return math.sqrt(max(0.0, probability * (1.0 - probability) / simulations))


def confidence_interval(probability: float, simulations: int, z_value: float = 1.96) -> tuple[float, float, float]:
    se = monte_carlo_standard_error(probability, simulations)
    return se, max(0.0, probability - z_value * se), min(1.0, probability + z_value * se)


def add_probability_uncertainty(frame: pd.DataFrame, probability_columns: list[str], simulations: int) -> pd.DataFrame:
    output = frame.copy()
    for column in probability_columns:
        if column not in output.columns:
            continue
        se_values = []
        low_values = []
        high_values = []
        for probability in output[column].astype(float):
            se, low, high = confidence_interval(probability, simulations)
            se_values.append(se)
            low_values.append(low)
            high_values.append(high)
        output[f"{column}_standard_error"] = se_values
        output[f"{column}_ci_low"] = low_values
        output[f"{column}_ci_high"] = high_values
    output["simulations_used"] = simulations
    return output

