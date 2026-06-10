from src.simulation.sensitivity_analysis import run_sensitivity_analysis


def test_sensitivity_analysis_writes_expected_tables(tournament_data, tmp_path):
    result = run_sensitivity_analysis(tournament_data, tmp_path, seed=3, simulations=1)
    assert "champion_probability_sensitivity" in result
    assert (tmp_path / "champion_probability_sensitivity.csv").exists()
    assert (tmp_path / "variable_importance.csv").exists()
    assert (tmp_path / "tornado_chart_data.csv").exists()

