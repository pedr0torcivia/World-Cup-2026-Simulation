from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.utils.console_utils import format_decimal, format_percentage, normalize_text, print_separator


def load_match_predictions(outputs_dir: str | Path = "outputs") -> pd.DataFrame:
    path = Path(outputs_dir) / "match_predictions.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"No encontre {path}. Ejecuta primero: python -m src.main --simulations 1000 --seed 123"
        )
    data = pd.read_csv(path)
    if data.empty:
        raise ValueError(f"{path} esta vacio. Ejecuta nuevamente la simulacion.")
    return data


def get_simulation_count(matches: pd.DataFrame) -> int | str:
    if "samples" not in matches.columns or matches["samples"].dropna().empty:
        return "No disponible"
    return int(matches["samples"].max())


def likely_winner_label(row: pd.Series) -> str:
    probabilities = {
        str(row["team_a"]): float(row.get("team_a_win_probability", 0.0)),
        "Empate": float(row.get("draw_probability_90", 0.0)),
        str(row["team_b"]): float(row.get("team_b_win_probability", 0.0)),
    }
    return max(probabilities, key=probabilities.get)


def prepare_group_matches(matches: pd.DataFrame, team_filter: str | None = None) -> pd.DataFrame:
    group_matches = matches[matches["stage"].astype(str).str.lower() == "group"].copy()
    if team_filter:
        query = normalize_text(team_filter)
        group_matches = group_matches[
            group_matches["team_a"].map(normalize_text).str.contains(query, na=False)
            | group_matches["team_b"].map(normalize_text).str.contains(query, na=False)
            | group_matches["team_a_id"].map(normalize_text).str.contains(query, na=False)
            | group_matches["team_b_id"].map(normalize_text).str.contains(query, na=False)
        ]
    if group_matches.empty:
        return group_matches
    group_matches["likely_winner"] = group_matches.apply(likely_winner_label, axis=1)
    group_matches["average_total_goals"] = (
        pd.to_numeric(group_matches["average_goals_a"], errors="coerce").fillna(0.0)
        + pd.to_numeric(group_matches["average_goals_b"], errors="coerce").fillna(0.0)
    )
    return group_matches.sort_values("match_id").reset_index(drop=True)


def print_match_results_interface(matches: pd.DataFrame, team_filter: str | None = None) -> None:
    simulation_count = get_simulation_count(matches)
    group_matches = prepare_group_matches(matches, team_filter)
    print_separator(132)
    print("MUNDIAL 2026 - RESULTADOS MAS PROBABLES POR PARTIDO")
    print(f"Simulaciones usadas por partido de fase de grupos: {simulation_count}")
    if isinstance(simulation_count, int) and simulation_count < 1000:
        print("ADVERTENCIA: muestra chica. Usa 1000+ simulaciones para porcentajes mas estables.")
    if team_filter:
        print(f"Filtro: {team_filter}")
    print_separator(132)
    if group_matches.empty:
        print("No hay partidos para mostrar con ese filtro.")
        return
    print(
        f"{'ID':<6} {'Partido':<42} {'Ganador mas probable':<24} {'Marcador':>9} {'P marc.':>8} "
        f"{'Goles prom.':>11} {'xG':>13} {'A':>8} {'Emp':>8} {'B':>8}"
    )
    for _, row in group_matches.iterrows():
        matchup = f"{row['team_a']} vs {row['team_b']}"
        xg_label = f"{format_decimal(row.get('average_xg_a'))}-{format_decimal(row.get('average_xg_b'))}"
        print(
            f"{str(row['match_id'])[:6]:<6} "
            f"{matchup[:42]:<42} "
            f"{str(row['likely_winner'])[:24]:<24} "
            f"{str(row['most_likely_score']):>9} "
            f"{format_percentage(row.get('most_likely_score_probability')):>8} "
            f"{format_decimal(row.get('average_total_goals')):>11} "
            f"{xg_label:>13} "
            f"{format_percentage(row.get('team_a_win_probability')):>8} "
            f"{format_percentage(row.get('draw_probability_90')):>8} "
            f"{format_percentage(row.get('team_b_win_probability')):>8}"
        )
    print()
    print("Referencias: A = gana el primer equipo, Emp = empate, B = gana el segundo equipo.")
    print("Comando util: python -m src.match_results_interface --team argentina")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple match results interface for World Cup 2026 simulations.")
    parser.add_argument("--outputs-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--team", type=str, default=None, help="Filter group-stage matches by team name or code.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        matches = load_match_predictions(args.outputs_dir)
    except (FileNotFoundError, ValueError) as error:
        print(error)
        return
    print_match_results_interface(matches, args.team)


if __name__ == "__main__":
    main()

