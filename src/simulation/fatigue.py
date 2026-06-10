from __future__ import annotations

import pandas as pd


def initialize_team_fatigue(teams: pd.DataFrame) -> dict[str, float]:
    return {team_id: 0.0 for team_id in teams["team_id"]}


def recover_fatigue(current: float, days_rest: int, recovery_per_day: float) -> float:
    return max(0.0, current - max(days_rest, 0) * recovery_per_day)


def calculate_match_fatigue(
    minutes: int,
    travel_difficulty: float,
    temperature: float,
    humidity: float,
    pressing_intensity: float,
) -> float:
    minutes_factor = minutes / 90.0
    climate_factor = max(0.0, (temperature - 26.0) * 0.015) + max(0.0, (humidity - 65.0) * 0.005)
    return round(0.06 * minutes_factor + 0.03 * travel_difficulty + climate_factor + 0.04 * pressing_intensity, 4)


def fatigue_performance_modifier(fatigue: float) -> float:
    return max(0.72, 1.0 - fatigue * 0.28)

