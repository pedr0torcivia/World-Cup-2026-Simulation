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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = load_tournament_data(args.project_root)
    result = run_monte_carlo(data, simulations=args.simulations, seed=args.seed)
    champion_table = result["tables"]["champion_probabilities"].head(5)
    print("Top champion probabilities")
    print(champion_table.to_string(index=False))
    print("Outputs written to outputs/")


if __name__ == "__main__":
    main()

