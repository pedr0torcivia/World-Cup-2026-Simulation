import pandas as pd

from src.match_results_interface import likely_winner_label, prepare_group_matches, print_match_results_interface


def sample_matches():
    return pd.DataFrame(
        {
            "match_id": ["G001", "R001"],
            "stage": ["group", "round_of_32"],
            "team_a": ["Argentina", "France"],
            "team_b": ["Japan", "Brazil"],
            "team_a_id": ["ARG", "FRA"],
            "team_b_id": ["JPN", "BRA"],
            "samples": [100, 3],
            "most_likely_score": ["2-1", "1-1"],
            "most_likely_score_probability": [0.18, 0.33],
            "average_goals_a": [1.8, 1.1],
            "average_goals_b": [1.0, 1.2],
            "average_xg_a": [1.7, 1.0],
            "average_xg_b": [0.9, 1.1],
            "team_a_win_probability": [0.62, 0.3],
            "draw_probability_90": [0.22, 0.4],
            "team_b_win_probability": [0.16, 0.3],
        }
    )


def test_likely_winner_label_returns_highest_probability():
    assert likely_winner_label(sample_matches().iloc[0]) == "Argentina"


def test_prepare_group_matches_filters_knockout_and_team():
    prepared = prepare_group_matches(sample_matches(), "arg")
    assert len(prepared) == 1
    assert prepared.iloc[0]["match_id"] == "G001"
    assert prepared.iloc[0]["average_total_goals"] == 2.8


def test_print_match_results_interface_outputs_simulations(capsys):
    print_match_results_interface(sample_matches(), "argentina")
    output = capsys.readouterr().out
    assert "Simulaciones usadas" in output
    assert "Argentina vs Japan" in output

