from __future__ import annotations

import numpy as np
import pandas as pd


def team_penalty_conversion_probability(team: pd.Series, opponent: pd.Series, fatigue: float, config: dict) -> float:
    base = float(config.get("penalty_conversion_base", 0.76))
    team_skill = (float(team["penalty_rating"]) - 75.0) * 0.003
    keeper_pressure = (float(opponent["goalkeeper_rating"]) - 75.0) * 0.0025
    experience = (float(team["experience"]) - 75.0) * 0.0015
    fatigue_penalty = fatigue * 0.08
    return min(0.92, max(0.45, base + team_skill + experience - keeper_pressure - fatigue_penalty))


def simulate_penalty_shootout(
    team_a: pd.Series,
    team_b: pd.Series,
    rng: np.random.Generator,
    config: dict,
    fatigue_a: float,
    fatigue_b: float,
) -> tuple[str, int, int]:
    probability_a = team_penalty_conversion_probability(team_a, team_b, fatigue_a, config)
    probability_b = team_penalty_conversion_probability(team_b, team_a, fatigue_b, config)

    score_a = 0
    score_b = 0
    for kick in range(5):
        score_a += int(rng.random() < probability_a)
        score_b += int(rng.random() < probability_b)
        remaining_b = 4 - kick
        if score_a > score_b + remaining_b:
            return str(team_a["team_id"]), score_a, score_b
        remaining_a = 4 - kick
        if score_b > score_a + remaining_a:
            return str(team_b["team_id"]), score_a, score_b

    while score_a == score_b:
        score_a += int(rng.random() < probability_a)
        score_b += int(rng.random() < probability_b)

    winner = str(team_a["team_id"] if score_a > score_b else team_b["team_id"])
    return winner, score_a, score_b

