from __future__ import annotations

import argparse
from pathlib import Path

from src.simulation.monte_carlo import run_monte_carlo
from src.utils.data_loader import load_tournament_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monte Carlo simulator for the FIFA World Cup 2026.")
    parser.add_argument("--simulations", type=int, default=None, help="Number of tournament simulations to run.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible simulations.")
    parser.add_argument("--project-root", type=Path, default=Path("."), help="Project root containing data/ and outputs/.")
    parser.add_argument("--sensitivity", action="store_true", help="Run a lightweight sensitivity analysis after the base simulation.")
    parser.add_argument("--interactive", action="store_true", help="Open the interactive console dashboard after running the simulation.")
    parser.add_argument("--interactive-only", action="store_true", help="Open the interactive dashboard from existing outputs without running a simulation.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.interactive_only:
        from src.interactive_dashboard import interactive_loop
        from src.analytics.team_dashboard import load_dashboard_data

        interactive_loop(load_dashboard_data(args.project_root / "outputs"))
        return

    data = load_tournament_data(args.project_root)
    result = run_monte_carlo(data, simulations=args.simulations, seed=args.seed)
    if args.sensitivity:
        from src.simulation.sensitivity_analysis import run_sensitivity_analysis

        run_sensitivity_analysis(
            data,
            args.project_root / "outputs",
            seed=args.seed if args.seed is not None else int(data.config.get("random_seed", 123)),
        )
    champion_table = result["tables"]["champion_probabilities"].head(5)
    print("Top champion probabilities")
    print(champion_table.to_string(index=False))
    print("Outputs written to outputs/")
    if args.interactive:
        from src.interactive_dashboard import interactive_loop
        from src.analytics.team_dashboard import load_dashboard_data

        interactive_loop(load_dashboard_data(args.project_root / "outputs"))


if __name__ == "__main__":
    main()
