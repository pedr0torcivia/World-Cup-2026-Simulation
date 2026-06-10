from pathlib import Path

from src.simulation.monte_carlo import run_monte_carlo


def test_monte_carlo_is_reproducible(tournament_data, tmp_path):
    first = run_monte_carlo(tournament_data, simulations=2, seed=77, output_dir=tmp_path / "a")
    second = run_monte_carlo(tournament_data, simulations=2, seed=77, output_dir=tmp_path / "b")
    first_table = first["tables"]["champion_probabilities"].reset_index(drop=True)
    second_table = second["tables"]["champion_probabilities"].reset_index(drop=True)
    assert first_table.equals(second_table)


def test_monte_carlo_writes_outputs(tournament_data, tmp_path):
    run_monte_carlo(tournament_data, simulations=1, seed=10, output_dir=tmp_path)
    assert (tmp_path / "champion_probabilities.csv").exists()
    assert (tmp_path / "qualification_probabilities.csv").exists()
    assert (tmp_path / "group_probabilities.csv").exists()
    assert (tmp_path / "injuries_summary.csv").exists()
    assert (tmp_path / "match_results_sample.csv").exists()
    assert (tmp_path / "full_report.md").exists()


def test_complete_tournament_has_104_matches(tournament_data, tmp_path):
    result = run_monte_carlo(tournament_data, simulations=1, seed=11, output_dir=tmp_path)
    assert len(result["match_sample"]) == 104
