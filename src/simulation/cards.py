from __future__ import annotations

import numpy as np
import pandas as pd


def simulate_team_cards(
    players: pd.DataFrame,
    team: pd.Series,
    rng: np.random.Generator,
    config: dict,
    match_intensity: float,
    fatigue: float,
) -> tuple[int, int, list[dict]]:
    if not config.get("enable_cards", True):
        return 0, 0, []

    team_players = players[(players["team_id"] == team["team_id"]) & (~players["is_suspended"].astype(bool))]
    if team_players.empty:
        yellow_lambda = float(config.get("yellow_card_base_probability", 0.22)) * 10.0
        red_lambda = float(config.get("red_card_base_probability", 0.025)) * 2.0
        return int(rng.poisson(yellow_lambda)), int(rng.poisson(red_lambda)), []

    discipline = max(0.2, float(team["discipline_rating"]))
    yellow_events: list[dict] = []
    red_events: list[dict] = []
    for _, player in team_players.sort_values("starter_probability", ascending=False).head(16).iterrows():
        yellow_probability = (
            float(config.get("yellow_card_base_probability", 0.22))
            * float(player["yellow_card_risk"])
            * match_intensity
            * (1.0 + fatigue * 0.4)
            / discipline
        )
        red_probability = (
            float(config.get("red_card_base_probability", 0.025))
            * float(player["red_card_risk"])
            * match_intensity
            / discipline
        )
        if rng.random() < min(0.75, yellow_probability):
            yellow_events.append({"team_id": team["team_id"], "player_id": player["player_id"], "card": "yellow"})
        if rng.random() < min(0.25, red_probability):
            red_events.append({"team_id": team["team_id"], "player_id": player["player_id"], "card": "red"})

    return len(yellow_events), len(red_events), yellow_events + red_events

