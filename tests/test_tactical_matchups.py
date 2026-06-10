from src.simulation.tactical_matchups import tactical_matchup_modifier


def test_tactical_matchup_modifier_is_moderate(tournament_data):
    modifier = tactical_matchup_modifier(tournament_data.teams.iloc[0], tournament_data.teams.iloc[1], tournament_data.config)
    assert 0.90 <= modifier <= 1.10

