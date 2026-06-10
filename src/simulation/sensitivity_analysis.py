from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pandas as pd

from src.simulation.monte_carlo import run_monte_carlo


def _set_nested(config: dict, dotted_key: str, value: float) -> dict:
    updated = deepcopy(config)
    target = updated
    parts = dotted_key.split(".")
    for part in parts[:-1]:
        target = target.setdefault(part, {})
    target[parts[-1]] = value
    return updated


def _get_nested(config: dict, dotted_key: str, default: float = 1.0) -> float:
    target = config
    for part in dotted_key.split("."):
        if not isinstance(target, dict) or part not in target:
            return default
        target = target[part]
    return float(target)


def run_sensitivity_analysis(tournament_data, output_dir: Path, seed: int, simulations: int | None = None) -> dict[str, pd.DataFrame]:
    base_config = dict(tournament_data.config)
    parameters = base_config.get("sensitivity_parameters", [])
    sensitivity_simulations = int(simulations or base_config.get("sensitivity_simulations", 20))
    baseline = run_monte_carlo(tournament_data, simulations=sensitivity_simulations, seed=seed, output_dir=output_dir / "_sensitivity_baseline")
    baseline_champions = baseline["tables"]["champion_probabilities"][["team", "probability"]].rename(columns={"probability": "baseline_probability"})
    rows = []
    for parameter in parameters:
        original = _get_nested(base_config, parameter)
        for multiplier in (0.9, 1.1):
            scenario_data = deepcopy(tournament_data)
            scenario_data.config = _set_nested(base_config, parameter, original * multiplier)
            scenario = run_monte_carlo(scenario_data, simulations=sensitivity_simulations, seed=seed, output_dir=output_dir / f"_sensitivity_{parameter.replace('.', '_')}_{multiplier}")
            merged = baseline_champions.merge(
                scenario["tables"]["champion_probabilities"][["team", "probability"]],
                on="team",
                how="left",
            )
            merged["parameter"] = parameter
            merged["multiplier"] = multiplier
            merged["delta_probability"] = merged["probability"] - merged["baseline_probability"]
            rows.extend(merged.to_dict("records"))
    champion_sensitivity = pd.DataFrame(rows)
    if champion_sensitivity.empty:
        champion_sensitivity = pd.DataFrame(columns=["team", "parameter", "multiplier", "delta_probability"])
    if champion_sensitivity.empty:
        variable_importance = pd.DataFrame(columns=["parameter", "mean_absolute_probability_delta"])
        tornado = pd.DataFrame(columns=["team", "parameter", "min", "max"])
    else:
        variable_importance = (
            champion_sensitivity.assign(abs_delta=lambda frame: frame["delta_probability"].abs())
            .groupby("parameter", as_index=False)["abs_delta"]
            .mean()
            .rename(columns={"abs_delta": "mean_absolute_probability_delta"})
            .sort_values("mean_absolute_probability_delta", ascending=False)
        )
        tornado = champion_sensitivity.groupby(["team", "parameter"], as_index=False)["delta_probability"].agg(["min", "max"]).reset_index()
    output_dir.mkdir(parents=True, exist_ok=True)
    champion_sensitivity.to_csv(output_dir / "champion_probability_sensitivity.csv", index=False)
    variable_importance.to_csv(output_dir / "variable_importance.csv", index=False)
    tornado.to_csv(output_dir / "tornado_chart_data.csv", index=False)
    return {
        "champion_probability_sensitivity": champion_sensitivity,
        "variable_importance": variable_importance,
        "tornado_chart_data": tornado,
    }
