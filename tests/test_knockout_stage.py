import numpy as np

from src.simulation.match_engine import simulate_match
from src.simulation.knockout_stage import pair_seeded_teams, seed_qualifiers


class FixedRng:
    def __init__(self, poisson_values, random_values=None):
        self.poisson_values = list(poisson_values)
        self.random_values = list(random_values or [0.99] * 100)

    def poisson(self, _lambda):
        return self.poisson_values.pop(0)

    def random(self):
        return self.random_values.pop(0) if self.random_values else 0.99

    def choice(self, values, p=None):
        return values[0]

    def integers(self, low, high=None):
        return low


def test_pair_seeded_teams_pairs_first_with_last():
    assert pair_seeded_teams(["A", "B", "C", "D"]) == [("A", "D"), ("B", "C")]


def test_knockout_match_without_draw_ends_in_90(tournament_data):
    config = dict(tournament_data.config)
    config["enable_cards"] = False
    config["enable_injuries"] = False
    rng = FixedRng([2, 0])
    result = simulate_match("K1", "round_of_32", tournament_data.teams.iloc[0], tournament_data.teams.iloc[1], tournament_data.venues.iloc[0], tournament_data.players, rng, config, {}, knockout=True)
    assert result.winner == tournament_data.teams.iloc[0]["team_id"]
    assert not result.went_to_extra_time


def test_knockout_match_can_be_decided_in_extra_time(tournament_data):
    config = dict(tournament_data.config)
    config["enable_cards"] = False
    config["enable_injuries"] = False
    rng = FixedRng([1, 1, 1, 0])
    result = simulate_match("K2", "round_of_32", tournament_data.teams.iloc[0], tournament_data.teams.iloc[1], tournament_data.venues.iloc[0], tournament_data.players, rng, config, {}, knockout=True)
    assert result.went_to_extra_time
    assert not result.went_to_penalties
    assert result.winner == tournament_data.teams.iloc[0]["team_id"]


def test_knockout_match_can_be_decided_by_penalties(tournament_data):
    config = dict(tournament_data.config)
    config["enable_cards"] = False
    config["enable_injuries"] = False
    rng = FixedRng([1, 1, 0, 0], [0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9])
    result = simulate_match("K3", "round_of_32", tournament_data.teams.iloc[0], tournament_data.teams.iloc[1], tournament_data.venues.iloc[0], tournament_data.players, rng, config, {}, knockout=True)
    assert result.went_to_penalties
    assert result.winner == tournament_data.teams.iloc[0]["team_id"]

