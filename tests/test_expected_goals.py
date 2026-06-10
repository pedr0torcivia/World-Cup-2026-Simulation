from src.simulation.expected_goals import (
    attack_strength,
    calculate_expected_goals,
    defense_strength,
    match_probability_summary,
    score_probability_matrix,
    team_strength,
)


def test_team_strength_is_normalized(tournament_data):
    value = team_strength(tournament_data.teams.iloc[0], tournament_data.config)
    assert 0.0 <= value <= 1.0


def test_expected_goals_are_bounded(tournament_data):
    goals = calculate_expected_goals(
        tournament_data.teams.iloc[0],
        tournament_data.teams.iloc[1],
        tournament_data.config,
        fatigue=0.0,
        injury_modifier=1.0,
        venue=tournament_data.venues.iloc[0],
        is_home_context=True,
    )
    assert tournament_data.config["min_expected_goals"] <= goals <= tournament_data.config["max_expected_goals"]


def test_score_probability_matrix_sums_to_one():
    matrix = score_probability_matrix(1.2, 0.9, max_goals=8)
    assert abs(matrix["probability"].sum() - 1.0) < 1e-9


def test_match_probability_summary_contains_market_outputs():
    summary = match_probability_summary(1.4, 1.1)
    assert {"probability_team_a_win", "probability_draw_90", "probability_over_2_5", "most_likely_score"}.issubset(summary)


def test_attack_and_defense_strength_are_multiplicative(tournament_data):
    team = tournament_data.teams.iloc[0]
    assert 0.70 <= attack_strength(team, tournament_data.config) <= 1.60
    assert 0.70 <= defense_strength(team, tournament_data.config) <= 1.55

