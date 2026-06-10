from src.simulation.match_engine import calculate_expected_goals, simulate_match
from src.utils.random_utils import create_rng


def test_match_engine_returns_group_draw_without_forced_winner(tournament_data):
    config = dict(tournament_data.config)
    config["enable_cards"] = False
    config["enable_injuries"] = False
    team_a = tournament_data.teams.iloc[0].copy()
    team_b = tournament_data.teams.iloc[1].copy()
    venue = tournament_data.venues.iloc[0]
    rng = create_rng(5)
    result = simulate_match("T", "group", team_a, team_b, venue, tournament_data.players, rng, config, {}, knockout=False)
    assert result.goals_a >= 0
    assert result.goals_b >= 0
    assert result.expected_goals_a > 0
    assert result.expected_goals_b > 0


def test_expected_goals_decline_with_high_fatigue(tournament_data):
    config = dict(tournament_data.config)
    team_a = tournament_data.teams.iloc[0]
    team_b = tournament_data.teams.iloc[1]
    venue = tournament_data.venues.iloc[0]
    fresh = calculate_expected_goals(team_a, team_b, config, 0.0, 1.0, venue, False)
    tired = calculate_expected_goals(team_a, team_b, config, 1.0, 1.0, venue, False)
    assert tired < fresh

