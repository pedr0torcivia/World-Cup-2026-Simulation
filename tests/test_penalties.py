from src.simulation.penalties import simulate_penalty_shootout, team_penalty_conversion_probability
from src.utils.random_utils import create_rng


def test_penalty_conversion_probability_is_bounded(tournament_data):
    probability = team_penalty_conversion_probability(tournament_data.teams.iloc[0], tournament_data.teams.iloc[1], 0.2, tournament_data.config)
    assert 0.45 <= probability <= 0.92


def test_shootout_returns_one_of_the_teams(tournament_data):
    winner, score_a, score_b = simulate_penalty_shootout(
        tournament_data.teams.iloc[0],
        tournament_data.teams.iloc[1],
        create_rng(12),
        tournament_data.config,
        0.1,
        0.1,
    )
    assert winner in {tournament_data.teams.iloc[0]["team_id"], tournament_data.teams.iloc[1]["team_id"]}
    assert score_a != score_b

