from src.simulation.fatigue import initialize_team_fatigue
from src.simulation.group_stage import simulate_group_stage
from src.utils.random_utils import create_rng


def test_group_stage_qualifies_32_teams(tournament_data):
    config = dict(tournament_data.config)
    config["enable_injuries"] = False
    rng = create_rng(123)
    table, qualifiers, results = simulate_group_stage(
        tournament_data.teams,
        tournament_data.players,
        tournament_data.fixtures,
        tournament_data.venues,
        rng,
        config,
        initialize_team_fatigue(tournament_data.teams),
    )
    assert len(table) == 48
    assert len(qualifiers) == 32
    assert len(results) == 72

