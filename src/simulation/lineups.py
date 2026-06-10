from __future__ import annotations

import pandas as pd


def select_starting_lineup(players: pd.DataFrame, team_id: str) -> dict:
    if players.empty:
        return {
            "starting_11": [],
            "bench": [],
            "unavailable_players": [],
            "data_quality": "missing_players_team_fallback",
        }
    team_players = players[players["team_id"] == team_id].copy()
    unavailable = team_players[(team_players.get("is_injured", False).astype(bool)) | (team_players.get("is_suspended", False).astype(bool))]
    available = team_players.drop(unavailable.index).sort_values(["starter_probability", "overall_rating"], ascending=False)
    return {
        "starting_11": list(available.head(11)["player_id"]),
        "bench": list(available.iloc[11:23]["player_id"]),
        "unavailable_players": list(unavailable["player_id"]),
        "data_quality": "real_or_loaded_players",
    }

