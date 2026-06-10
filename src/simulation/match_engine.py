from __future__ import annotations

import numpy as np
import pandas as pd

from src.models.match import MatchResult
from src.simulation.cards import simulate_team_cards
from src.simulation.fatigue import calculate_match_fatigue, fatigue_performance_modifier
from src.simulation.injuries import simulate_team_injuries, team_injury_modifier
from src.simulation.penalties import simulate_penalty_shootout


def _rating_modifier(value: float, baseline: float = 75.0, scale: float = 40.0) -> float:
    return max(0.45, min(1.65, 1.0 + (float(value) - baseline) / scale))


def tactical_modifier(attacking_style: str, defending_style: str) -> float:
    matchups = {
        ("possession", "pressing"): 0.96,
        ("pressing", "direct"): 1.05,
        ("direct", "possession"): 1.04,
        ("balanced", "balanced"): 1.0,
    }
    return matchups.get((str(attacking_style), str(defending_style)), 1.0)


def calculate_expected_goals(
    team: pd.Series,
    opponent: pd.Series,
    config: dict,
    fatigue: float,
    injury_modifier: float,
    venue: pd.Series,
    is_home_context: bool,
) -> float:
    base_goal_rate = float(config.get("base_goal_rate", 1.35))
    attack_strength = _rating_modifier(team["attack_rating"])
    midfield_strength = _rating_modifier(team["midfield_rating"], scale=60.0)
    defense_weakness = _rating_modifier(100.0 - float(opponent["defense_rating"]), baseline=25.0, scale=55.0)
    form_modifier = _rating_modifier(team["recent_form"], scale=80.0)
    fatigue_modifier = fatigue_performance_modifier(fatigue) if config.get("enable_fatigue", True) else 1.0
    home_modifier = 1.0
    if config.get("enable_home_advantage", True) and is_home_context:
        home_modifier += float(team["home_advantage"]) + float(venue.get("home_team_bonus", 0.0))
    venue_modifier = 1.0
    if config.get("enable_venues", True):
        venue_modifier -= max(0.0, float(venue["travel_difficulty"]) - float(team["travel_fatigue_base"])) * 0.03
        venue_modifier -= max(0.0, float(venue["expected_temperature"]) - 30.0) * 0.006
    tactical = tactical_modifier(team["tactical_style"], opponent["tactical_style"])

    expected = (
        base_goal_rate
        * attack_strength
        * midfield_strength
        * defense_weakness
        * form_modifier
        * fatigue_modifier
        * injury_modifier
        * home_modifier
        * max(0.75, venue_modifier)
        * tactical
    )
    return round(max(0.05, float(expected)), 4)


def simulate_match(
    match_id: str,
    stage: str,
    team_a: pd.Series,
    team_b: pd.Series,
    venue: pd.Series,
    players: pd.DataFrame,
    rng: np.random.Generator,
    config: dict,
    team_fatigue: dict[str, float] | None = None,
    knockout: bool = False,
) -> MatchResult:
    fatigue_a = team_fatigue.get(team_a["team_id"], 0.0) if team_fatigue else 0.0
    fatigue_b = team_fatigue.get(team_b["team_id"], 0.0) if team_fatigue else 0.0
    injury_modifier_a = team_injury_modifier(players, team_a["team_id"])
    injury_modifier_b = team_injury_modifier(players, team_b["team_id"])
    expected_a = calculate_expected_goals(team_a, team_b, config, fatigue_a, injury_modifier_a, venue, bool(team_a.get("home_advantage", 0) > 0.02))
    expected_b = calculate_expected_goals(team_b, team_a, config, fatigue_b, injury_modifier_b, venue, bool(team_b.get("home_advantage", 0) > 0.02))

    goals_a = int(rng.poisson(expected_a))
    goals_b = int(rng.poisson(expected_b))
    went_to_extra_time = False
    went_to_penalties = False
    penalty_score_a = 0
    penalty_score_b = 0
    winner: str | None = None

    if goals_a > goals_b:
        winner = str(team_a["team_id"])
    elif goals_b > goals_a:
        winner = str(team_b["team_id"])

    total_minutes = 90
    if knockout and goals_a == goals_b:
        went_to_extra_time = True
        total_minutes = 120
        extra_multiplier = float(config.get("extra_time_goal_multiplier", 0.35))
        extra_a = int(rng.poisson(expected_a * extra_multiplier))
        extra_b = int(rng.poisson(expected_b * extra_multiplier))
        goals_a += extra_a
        goals_b += extra_b
        if goals_a > goals_b:
            winner = str(team_a["team_id"])
        elif goals_b > goals_a:
            winner = str(team_b["team_id"])
        else:
            went_to_penalties = True
            winner, penalty_score_a, penalty_score_b = simulate_penalty_shootout(team_a, team_b, rng, config, fatigue_a, fatigue_b)

    match_intensity = 1.0 + (float(team_a["pressing_intensity"]) + float(team_b["pressing_intensity"])) / 4.0
    yellow_a, red_a, card_events_a = simulate_team_cards(players, team_a, rng, config, match_intensity, fatigue_a)
    yellow_b, red_b, card_events_b = simulate_team_cards(players, team_b, rng, config, match_intensity, fatigue_b)
    injuries = []
    injuries.extend(simulate_team_injuries(players, team_a["team_id"], rng, config, fatigue_a, match_intensity, venue, total_minutes))
    injuries.extend(simulate_team_injuries(players, team_b["team_id"], rng, config, fatigue_b, match_intensity, venue, total_minutes))

    fatigue_added_a = calculate_match_fatigue(total_minutes, venue["travel_difficulty"], venue["expected_temperature"], venue["expected_humidity"], team_a["pressing_intensity"])
    fatigue_added_b = calculate_match_fatigue(total_minutes, venue["travel_difficulty"], venue["expected_temperature"], venue["expected_humidity"], team_b["pressing_intensity"])
    if team_fatigue is not None and config.get("enable_fatigue", True):
        team_fatigue[str(team_a["team_id"])] = fatigue_a + fatigue_added_a
        team_fatigue[str(team_b["team_id"])] = fatigue_b + fatigue_added_b

    return MatchResult(
        match_id=match_id,
        stage=stage,
        team_a=str(team_a["team_id"]),
        team_b=str(team_b["team_id"]),
        goals_a=goals_a,
        goals_b=goals_b,
        expected_goals_a=expected_a,
        expected_goals_b=expected_b,
        winner=winner,
        draw=(winner is None),
        went_to_extra_time=went_to_extra_time,
        went_to_penalties=went_to_penalties,
        penalty_score_a=penalty_score_a,
        penalty_score_b=penalty_score_b,
        yellow_cards={str(team_a["team_id"]): yellow_a, str(team_b["team_id"]): yellow_b},
        red_cards={str(team_a["team_id"]): red_a, str(team_b["team_id"]): red_b},
        injuries=injuries,
        fatigue_added={str(team_a["team_id"]): fatigue_added_a, str(team_b["team_id"]): fatigue_added_b},
        events=[event["card"] for event in card_events_a + card_events_b],
    )

