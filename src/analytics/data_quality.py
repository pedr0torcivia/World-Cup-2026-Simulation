from __future__ import annotations

import pandas as pd


MODEL_DERIVED_COLUMNS = {
    "attack_rating",
    "defense_rating",
    "midfield_rating",
    "goalkeeper_rating",
    "squad_depth",
    "recent_form",
    "experience",
    "penalty_rating",
    "discipline_rating",
    "pressing_intensity",
    "tactical_style",
    "travel_fatigue_base",
}


def classify_team_column(column: str) -> str:
    if column in {"team_id", "team_name", "confederation", "group", "fifa_ranking", "elo_rating"}:
        return "real"
    if column in MODEL_DERIVED_COLUMNS:
        return "estimated"
    return "missing"


def build_data_quality_report(teams: pd.DataFrame, players: pd.DataFrame, venues: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, team in teams.iterrows():
        real_count = sum(1 for column in teams.columns if classify_team_column(column) == "real" and pd.notna(team[column]))
        estimated_count = sum(1 for column in teams.columns if classify_team_column(column) == "estimated" and pd.notna(team[column]))
        total = max(1, real_count + estimated_count)
        player_quality = "missing" if players.empty else "real_or_loaded"
        score = (real_count * 1.0 + estimated_count * 0.55) / total
        if players.empty:
            score *= 0.90
        rows.append(
            {
                "team": team["team_name"],
                "team_id": team["team_id"],
                "real_fields": real_count,
                "estimated_fields": estimated_count,
                "player_data_quality": player_quality,
                "team_data_quality_score": round(float(score), 4),
                "warning": "player-level data missing; using team-level fallback" if players.empty else "",
            }
        )
    return pd.DataFrame(rows).sort_values("team_data_quality_score")

