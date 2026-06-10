from __future__ import annotations

from math import exp, factorial

import pandas as pd

from src.simulation.fatigue import fatigue_performance_modifier
from src.simulation.tactical_matchups import tactical_matchup_modifier


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def normalize(value: float, low: float, high: float) -> float:
    if high <= low:
        return 0.5
    return clamp((float(value) - low) / (high - low), 0.0, 1.0)


def normalized_rating_from_column(team: pd.Series, column: str, default: float = 75.0) -> float:
    return normalize(float(team.get(column, default)), 55.0, 95.0)


def team_strength(team: pd.Series, config: dict) -> float:
    weights = config.get("team_strength_weights", {})
    normalized_elo = normalize(float(team.get("elo_rating", 1500.0)), 1200.0, 1900.0)
    normalized_fifa_rating = 1.0 - normalize(float(team.get("fifa_ranking", 80.0)), 1.0, 100.0)
    components = {
        "normalized_elo": normalized_elo,
        "normalized_fifa_rating": normalized_fifa_rating,
        "player_quality_index": normalized_rating_from_column(team, "attack_rating"),
        "recent_form_index": normalized_rating_from_column(team, "recent_form"),
        "squad_depth_index": normalized_rating_from_column(team, "squad_depth"),
        "experience_index": normalized_rating_from_column(team, "experience"),
        "tactical_coherence_index": normalized_rating_from_column(team, "midfield_rating"),
        "coach_index": normalized_rating_from_column(team, "experience"),
    }
    total_weight = sum(float(value) for value in weights.values()) or 1.0
    strength = sum(float(weights.get(name, 0.0)) * value for name, value in components.items()) / total_weight
    return round(clamp(strength, 0.0, 1.0), 4)


def multiplicative_index(team: pd.Series, column: str, low: float = 55.0, high: float = 95.0, min_value: float = 0.75, max_value: float = 1.35) -> float:
    normalized = normalize(float(team.get(column, (low + high) / 2)), low, high)
    return min_value + normalized * (max_value - min_value)


def attack_strength(team: pd.Series, config: dict) -> float:
    base = multiplicative_index(team, "attack_rating", max_value=1.45)
    form = multiplicative_index(team, "recent_form", min_value=0.92, max_value=1.10)
    strength_prior = 0.90 + team_strength(team, config) * 0.25
    return round(clamp((base * 0.70 + form * 0.15 + strength_prior * 0.15), 0.70, 1.60), 4)


def defense_strength(team: pd.Series, config: dict) -> float:
    base = multiplicative_index(team, "defense_rating", max_value=1.40)
    goalkeeper = goalkeeper_strength(team)
    depth = multiplicative_index(team, "squad_depth", min_value=0.92, max_value=1.10)
    return round(clamp(base * 0.72 + goalkeeper * 0.13 + depth * 0.15, 0.70, 1.55), 4)


def goalkeeper_strength(team: pd.Series) -> float:
    return round(clamp(multiplicative_index(team, "goalkeeper_rating", min_value=0.75, max_value=1.25), 0.75, 1.25), 4)


def goalkeeper_modifier_against(team: pd.Series, config: dict) -> float:
    impact_weight = float(config.get("expected_goals_weights", {}).get("goalkeeper", 0.06))
    adjustment = goalkeeper_strength(team) - 1.0
    return round(clamp(1.0 - impact_weight * adjustment, 0.92, 1.08), 4)


def form_modifier(team: pd.Series, config: dict) -> float:
    weight = float(config.get("expected_goals_weights", {}).get("form", 0.18))
    form_index = multiplicative_index(team, "recent_form", min_value=0.90, max_value=1.12)
    return round(1.0 + (form_index - 1.0) * weight, 4)


def home_advantage_modifier(team: pd.Series, venue: pd.Series, config: dict, is_home_context: bool) -> float:
    if not config.get("enable_home_advantage", True) or not is_home_context:
        return 1.0
    cap = float(config.get("home_advantage_cap", 1.10))
    value = 1.0 + float(team.get("home_advantage", 0.0)) + float(venue.get("home_team_bonus", 0.0))
    return round(clamp(value, 1.0, cap), 4)


def venue_modifier(team: pd.Series, venue: pd.Series, config: dict) -> float:
    if not config.get("enable_venues", True):
        return 1.0
    temperature_factor = max(0.0, float(venue.get("expected_temperature", 24.0)) - 30.0) * 0.004
    humidity_factor = max(0.0, float(venue.get("expected_humidity", 60.0)) - 70.0) * 0.002
    altitude_factor = max(0.0, float(venue.get("altitude", 0.0)) - 1200.0) / 1000.0 * 0.015
    travel_factor = max(0.0, float(venue.get("travel_difficulty", 0.3)) - float(team.get("travel_fatigue_base", 0.3))) * 0.03
    return round(clamp(1.0 - temperature_factor - humidity_factor - altitude_factor - travel_factor, 0.82, 1.05), 4)


def calculate_expected_goals(
    team: pd.Series,
    opponent: pd.Series,
    config: dict,
    fatigue: float,
    injury_modifier: float,
    venue: pd.Series,
    is_home_context: bool,
) -> float:
    fatigue_modifier = fatigue_performance_modifier(fatigue) if config.get("enable_fatigue", True) else 1.0
    defense_weakness = 1.0 / defense_strength(opponent, config)
    expected = (
        float(config.get("base_goal_rate", 1.35))
        * attack_strength(team, config)
        * defense_weakness
        * goalkeeper_modifier_against(opponent, config)
        * form_modifier(team, config)
        * fatigue_modifier
        * injury_modifier
        * tactical_matchup_modifier(team, opponent, config)
        * home_advantage_modifier(team, venue, config, is_home_context)
        * venue_modifier(team, venue, config)
    )
    return round(clamp(expected, float(config.get("min_expected_goals", 0.05)), float(config.get("max_expected_goals", 4.5))), 4)


def poisson_probability(lam: float, goals: int) -> float:
    return exp(-lam) * (lam**goals) / factorial(goals)


def score_probability_matrix(lambda_a: float, lambda_b: float, max_goals: int = 8) -> pd.DataFrame:
    rows = []
    for goals_a in range(max_goals + 1):
        for goals_b in range(max_goals + 1):
            rows.append(
                {
                    "goals_a": goals_a,
                    "goals_b": goals_b,
                    "probability": poisson_probability(lambda_a, goals_a) * poisson_probability(lambda_b, goals_b),
                }
            )
    matrix = pd.DataFrame(rows)
    total = matrix["probability"].sum()
    if total > 0:
        matrix["probability"] = matrix["probability"] / total
    return matrix


def match_probability_summary(lambda_a: float, lambda_b: float, max_goals: int = 8) -> dict[str, float | str]:
    matrix = score_probability_matrix(lambda_a, lambda_b, max_goals)
    a_win = float(matrix.loc[matrix["goals_a"] > matrix["goals_b"], "probability"].sum())
    draw = float(matrix.loc[matrix["goals_a"] == matrix["goals_b"], "probability"].sum())
    b_win = float(matrix.loc[matrix["goals_a"] < matrix["goals_b"], "probability"].sum())
    over_2_5 = float(matrix.loc[(matrix["goals_a"] + matrix["goals_b"]) > 2.5, "probability"].sum())
    both_score = float(matrix.loc[(matrix["goals_a"] > 0) & (matrix["goals_b"] > 0), "probability"].sum())
    most_likely = matrix.sort_values("probability", ascending=False).iloc[0]
    return {
        "probability_team_a_win": a_win,
        "probability_draw_90": draw,
        "probability_team_b_win": b_win,
        "probability_over_2_5": over_2_5,
        "probability_under_2_5": 1.0 - over_2_5,
        "probability_both_teams_score": both_score,
        "most_likely_score": f"{int(most_likely['goals_a'])}-{int(most_likely['goals_b'])}",
    }

