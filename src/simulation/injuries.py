from __future__ import annotations

import numpy as np
import pandas as pd


INJURY_DAYS = {
    "minor": (0, 1),
    "muscular": (1, 2),
    "moderate": (2, 4),
    "severe": (999, 999),
}


def calculate_player_injury_probability(
    player: pd.Series,
    base_probability: float,
    minutes: int,
    fatigue: float,
    match_intensity: float,
    temperature: float,
    humidity: float,
) -> float:
    age_factor = max(0.0, (float(player["age"]) - 29.0) * 0.003)
    stamina_factor = max(0.0, (75.0 - float(player["stamina"])) * 0.002)
    minutes_factor = minutes / 90.0
    climate_factor = max(0.0, (temperature - 28.0) * 0.002) + max(0.0, (humidity - 70.0) * 0.001)
    risk = (
        base_probability
        * (1.0 + float(player["injury_proneness"]))
        * minutes_factor
        * (1.0 + fatigue)
        * (1.0 + match_intensity * 0.5)
    )
    return min(0.65, max(0.0, risk + age_factor + stamina_factor + climate_factor))


def sample_injury_type(rng: np.random.Generator) -> tuple[str, int]:
    injury_type = str(rng.choice(["minor", "muscular", "moderate", "severe"], p=[0.5, 0.28, 0.17, 0.05]))
    low, high = INJURY_DAYS[injury_type]
    days = int(low if low == high else rng.integers(low, high + 1))
    return injury_type, days


def simulate_team_injuries(
    players: pd.DataFrame,
    team_id: str,
    rng: np.random.Generator,
    config: dict,
    fatigue: float,
    match_intensity: float,
    venue: pd.Series,
    minutes: int = 90,
) -> list[dict]:
    if not config.get("enable_injuries", True):
        return []

    base_probability = float(config.get("injury_base_probability", 0.015))
    if players.empty:
        aggregate_probability = min(
            0.95,
            base_probability * 11.0 * (1.0 + fatigue) * (1.0 + match_intensity * 0.35),
        )
        if rng.random() >= aggregate_probability:
            return []
        injury_type, days = sample_injury_type(rng)
        return [
            {
                "team_id": team_id,
                "player_id": "",
                "player_name": "Team-level injury estimate",
                "position": "TEAM",
                "injury_type": injury_type,
                "days_out": days,
                "importance": 0.5,
                "overall_rating": 70.0,
            }
        ]

    candidates = players[(players["team_id"] == team_id) & (~players["is_injured"].astype(bool)) & (~players["is_suspended"].astype(bool))]
    if candidates.empty:
        return []

    events: list[dict] = []
    likely_players = candidates.sort_values("starter_probability", ascending=False).head(16)
    for _, player in likely_players.iterrows():
        played_minutes = minutes if rng.random() < float(player["starter_probability"]) else int(minutes * 0.35)
        probability = calculate_player_injury_probability(
            player,
            base_probability,
            played_minutes,
            fatigue,
            match_intensity,
            float(venue["expected_temperature"]),
            float(venue["expected_humidity"]),
        )
        if rng.random() < probability:
            injury_type, days = sample_injury_type(rng)
            events.append(
                {
                    "team_id": team_id,
                    "player_id": player["player_id"],
                    "player_name": player["player_name"],
                    "position": player["position"],
                    "injury_type": injury_type,
                    "days_out": days,
                    "importance": float(player["importance"]),
                    "overall_rating": float(player["overall_rating"]),
                }
            )
    return events


def team_injury_modifier(players: pd.DataFrame, team_id: str) -> float:
    if players.empty:
        return 1.0
    injured = players[(players["team_id"] == team_id) & (players["is_injured"].astype(bool))]
    if injured.empty:
        return 1.0
    impact = ((injured["importance"].astype(float) * injured["overall_rating"].astype(float)) / 10000.0).sum()
    return max(0.78, 1.0 - float(impact))
