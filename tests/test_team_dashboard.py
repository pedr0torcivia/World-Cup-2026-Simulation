from pathlib import Path

import pandas as pd

from src.analytics.team_dashboard import build_team_dashboard_stats, load_dashboard_data, search_team


def test_loads_existing_team_dashboard_stats(tmp_path):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    pd.DataFrame(
        {
            "team": ["Argentina", "Spain"],
            "rank": [1, 2],
            "champion_probability": [0.2, 0.1],
        }
    ).to_csv(outputs / "team_dashboard_stats.csv", index=False)
    data = load_dashboard_data(outputs)
    assert list(data["team"]) == ["Argentina", "Spain"]


def test_builds_dashboard_when_some_csvs_are_missing(tmp_path):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    pd.DataFrame({"team": ["Argentina"], "probability": [0.3], "probability_ci_low": [0.2], "probability_ci_high": [0.4]}).to_csv(
        outputs / "champion_probabilities.csv", index=False
    )
    data = build_team_dashboard_stats(outputs)
    assert len(data) == 1
    assert data.iloc[0]["team"] == "Argentina"


def test_search_team_ignores_case_and_accents():
    data = pd.DataFrame({"team": ["España", "Argentina"], "rank": [1, 2], "champion_probability": [0.2, 0.1]})
    assert search_team(data, "espana") == [0]
    assert search_team(data, "ARG") == [1]


def test_load_dashboard_raises_when_no_outputs(tmp_path):
    try:
        load_dashboard_data(tmp_path / "outputs")
    except FileNotFoundError as error:
        assert "Run" in str(error)
    else:
        raise AssertionError("Expected FileNotFoundError")

