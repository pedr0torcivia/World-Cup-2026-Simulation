import pandas as pd

from src.interactive_dashboard import compare_teams, print_main_ranking, print_match_predictions, print_team_detail, print_top
from src.utils.console_utils import format_percentage


def sample_dashboard():
    return pd.DataFrame(
        {
            "team": ["France", "Argentina"],
            "rank": [1, 2],
            "champion_probability": [0.12, 0.11],
            "champion_ci_low": [0.10, 0.09],
            "champion_ci_high": [0.14, 0.13],
            "final_probability": [0.22, 0.21],
            "semifinal_probability": [0.35, 0.34],
            "quarterfinal_probability": [0.50, 0.49],
            "round_of_16_probability": [0.72, 0.70],
            "round_of_32_probability": [0.90, 0.89],
            "group_qualification_probability": [0.96, 0.95],
            "group_exit_probability": [0.04, 0.05],
            "group_winner_probability": [0.65, 0.63],
            "group_runner_up_probability": [0.22, 0.23],
            "third_place_probability": [0.09, 0.10],
            "fourth_place_probability": [0.04, 0.04],
            "average_goals_for": [1.9, 1.8],
            "average_goals_against": [0.8, 0.9],
            "average_xg_for": [1.95, 1.85],
            "average_xg_against": [0.85, 0.90],
            "clean_sheet_probability": [0.4, 0.38],
            "failed_to_score_probability": [0.1, 0.12],
            "average_injuries": [1.2, 1.3],
            "severe_injury_probability": [0.04, 0.05],
            "most_affected_position": ["TEAM", "TEAM"],
            "extra_time_probability": [0.2, 0.22],
            "penalty_shootout_probability": [0.15, 0.16],
            "team_strength": [0.93, 0.91],
            "attack_strength": [1.2, 1.18],
            "defense_strength": [1.14, 1.12],
            "goalkeeper_strength": [1.1, 1.08],
            "squad_depth_index": [0.9, 0.88],
            "recent_form_index": [0.84, 0.83],
            "dark_horse_index": [0.1, 0.11],
            "upset_victim_probability": [0.03, 0.04],
            "data_quality_score": [0.8, 0.78],
        }
    )


def test_format_percentage():
    assert format_percentage(0.1234) == "12.3%"
    assert format_percentage(None) == "No disponible"


def test_print_main_ranking_does_not_error(capsys):
    print_main_ranking(sample_dashboard())
    assert "SIMULADOR MUNDIAL 2026" in capsys.readouterr().out


def test_print_team_detail_handles_out_of_range(capsys):
    print_team_detail(sample_dashboard(), 99)
    assert "no existe" in capsys.readouterr().out


def test_compare_teams_without_error(capsys):
    compare_teams(sample_dashboard(), 1, 2)
    assert "COMPARACION" in capsys.readouterr().out


def test_print_top_orders_by_metric(capsys):
    print_top(sample_dashboard(), "campeon")
    assert "France" in capsys.readouterr().out


def test_print_match_predictions_without_error(capsys):
    matches = pd.DataFrame(
        {
            "match_id": ["G001"],
            "stage": ["group"],
            "team_a": ["Argentina"],
            "team_b": ["France"],
            "team_a_id": ["ARG"],
            "team_b_id": ["FRA"],
            "most_likely_score": ["1-1"],
            "most_likely_score_probability": [0.12],
            "average_xg_a": [1.2],
            "average_xg_b": [1.1],
            "team_a_win_probability": [0.36],
            "draw_probability_90": [0.28],
            "team_b_win_probability": [0.36],
        }
    )
    print_match_predictions(matches, "arg")
    assert "Argentina vs France" in capsys.readouterr().out
