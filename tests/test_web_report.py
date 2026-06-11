import pandas as pd

from src.web_report import build_worldcup_html_report


def test_build_worldcup_html_report(tmp_path):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    pd.DataFrame(
        {
            "match_id": ["G001"],
            "stage": ["group"],
            "team_a": ["Argentina"],
            "team_b": ["Japan"],
            "team_a_id": ["ARG"],
            "team_b_id": ["JPN"],
            "samples": [100],
            "most_likely_score": ["2-1"],
            "most_likely_score_probability": [0.18],
            "average_goals_a": [1.8],
            "average_goals_b": [1.0],
            "average_xg_a": [1.7],
            "average_xg_b": [0.9],
            "team_a_win_probability": [0.62],
            "draw_probability_90": [0.22],
            "team_b_win_probability": [0.16],
        }
    ).to_csv(outputs / "match_predictions.csv", index=False)
    pd.DataFrame(
        {
            "team": ["Argentina"],
            "rank": [1],
            "champion_probability": [0.12],
            "final_probability": [0.22],
            "semifinal_probability": [0.35],
            "quarterfinal_probability": [0.50],
            "round_of_16_probability": [0.72],
            "round_of_32_probability": [0.90],
            "group_qualification_probability": [0.96],
        }
    ).to_csv(outputs / "team_dashboard_stats.csv", index=False)
    pd.DataFrame({"team": ["Argentina"], "simulations_used": [100]}).to_csv(outputs / "champion_probabilities.csv", index=False)

    output = build_worldcup_html_report(outputs)
    html = output.read_text(encoding="utf-8")
    assert "Argentina vs Japan" in html
    assert "2-1" in html
    assert "Resto del torneo" in html

