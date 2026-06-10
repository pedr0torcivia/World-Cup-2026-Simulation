import pandas as pd

from src.simulation.injuries import calculate_player_injury_probability, simulate_team_injuries
from src.utils.random_utils import create_rng


def test_injury_probability_increases_with_fatigue(tournament_data):
    player = pd.Series(
        {
            "age": 31,
            "stamina": 72,
            "injury_proneness": 0.2,
        }
    )
    venue = tournament_data.venues.iloc[0]
    low = calculate_player_injury_probability(player, 0.01, 90, 0.0, 1.0, venue["expected_temperature"], venue["expected_humidity"])
    high = calculate_player_injury_probability(player, 0.01, 90, 1.0, 1.0, venue["expected_temperature"], venue["expected_humidity"])
    assert high > low


def test_injuries_can_be_disabled(tournament_data):
    config = dict(tournament_data.config)
    config["enable_injuries"] = False
    events = simulate_team_injuries(tournament_data.players, "T01", create_rng(1), config, 1.0, 2.0, tournament_data.venues.iloc[0])
    assert events == []


def test_empty_players_use_team_level_injury_fallback(tournament_data):
    config = dict(tournament_data.config)
    config["injury_base_probability"] = 1.0
    events = simulate_team_injuries(tournament_data.players, "MEX", create_rng(1), config, 1.0, 2.0, tournament_data.venues.iloc[0])
    assert events
    assert events[0]["position"] == "TEAM"
