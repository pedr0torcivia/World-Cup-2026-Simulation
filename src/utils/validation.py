from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = {
    "teams": [
        "team_id",
        "team_name",
        "confederation",
        "group",
        "fifa_ranking",
        "elo_rating",
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
        "home_advantage",
        "travel_fatigue_base",
    ],
    "players": [
        "player_id",
        "player_name",
        "team_id",
        "position",
        "age",
        "overall_rating",
        "importance",
        "starter_probability",
        "stamina",
        "injury_proneness",
        "penalty_skill",
        "yellow_card_risk",
        "red_card_risk",
        "minutes_played",
        "is_injured",
        "injury_days_remaining",
        "is_suspended",
        "yellow_cards",
    ],
    "fixtures": ["match_id", "stage", "group", "matchday", "date", "venue_id", "team_a", "team_b"],
    "venues": [
        "venue_id",
        "venue_name",
        "city",
        "country",
        "altitude",
        "expected_temperature",
        "expected_humidity",
        "travel_difficulty",
        "home_team_bonus",
    ],
}


def require_columns(name: str, frame: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS[name] if column not in frame.columns]
    if missing:
        raise ValueError(f"{name}.csv missing required columns: {', '.join(missing)}")


def validate_tournament_data(teams: pd.DataFrame, players: pd.DataFrame, fixtures: pd.DataFrame, venues: pd.DataFrame) -> None:
    require_columns("teams", teams)
    require_columns("players", players)
    require_columns("fixtures", fixtures)
    require_columns("venues", venues)

    if teams["team_id"].duplicated().any():
        raise ValueError("teams.csv has duplicated team_id values")
    if len(teams) < 32:
        raise ValueError("At least 32 teams are required to simulate the knockout stage")

    known_teams = set(teams["team_id"])
    missing_player_teams = set(players["team_id"]) - known_teams
    if missing_player_teams:
        raise ValueError(f"players.csv references unknown teams: {sorted(missing_player_teams)}")

    fixture_teams = (set(fixtures["team_a"].dropna()) | set(fixtures["team_b"].dropna())) - {"TBD", ""}
    missing_fixture_teams = fixture_teams - known_teams
    if missing_fixture_teams:
        raise ValueError(f"fixtures.csv references unknown teams: {sorted(missing_fixture_teams)}")

    missing_venues = set(fixtures["venue_id"].dropna()) - set(venues["venue_id"])
    if missing_venues:
        raise ValueError(f"fixtures.csv references unknown venues: {sorted(missing_venues)}")

