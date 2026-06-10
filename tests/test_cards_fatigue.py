from src.simulation.cards import simulate_team_cards
from src.simulation.fatigue import calculate_match_fatigue, recover_fatigue
from src.utils.random_utils import create_rng


def test_fatigue_recovers_but_not_below_zero():
    assert recover_fatigue(0.2, 10, 0.05) == 0.0


def test_extra_time_adds_more_fatigue():
    normal = calculate_match_fatigue(90, 0.4, 25, 60, 0.6)
    extra = calculate_match_fatigue(120, 0.4, 25, 60, 0.6)
    assert extra > normal


def test_cards_can_be_disabled(tournament_data):
    config = dict(tournament_data.config)
    config["enable_cards"] = False
    yellow, red, events = simulate_team_cards(tournament_data.players, tournament_data.teams.iloc[0], create_rng(1), config, 1.0, 0.0)
    assert (yellow, red, events) == (0, 0, [])

