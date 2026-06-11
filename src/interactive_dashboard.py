from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.analytics.team_dashboard import load_dashboard_data, search_team
from src.utils.console_utils import format_decimal, format_percentage, normalize_text, print_separator, safe_get


TOP_COMMANDS = {
    "campeon": ("champion_probability", False, "Top 10 por probabilidad de campeon"),
    "grupos": ("group_qualification_probability", False, "Top 10 por probabilidad de superar grupos"),
    "lesiones": ("severe_injury_probability", False, "Top 10 por riesgo de lesion grave"),
    "sorpresa": ("dark_horse_index", False, "Top 10 candidatos a sorpresa"),
    "decepcion": ("upset_victim_probability", False, "Top 10 posibles decepciones"),
    "goles": ("average_xg_for", False, "Top 10 por xG a favor"),
    "defensa": ("average_xg_against", True, "Top 10 por menor xG recibido"),
    "penales": ("penalty_shootout_probability", False, "Top 10 por probabilidad de tanda"),
}


def _percentage(value: object) -> str:
    return format_percentage(value).rjust(7)


def _team_by_number(df: pd.DataFrame, number: int) -> pd.Series | None:
    if number < 1 or number > len(df):
        return None
    return df.iloc[number - 1]


def print_main_ranking(df: pd.DataFrame) -> None:
    simulations = safe_get(df.iloc[0], "simulations_used", "No disponible") if not df.empty else "No disponible"
    print_separator()
    print("SIMULADOR MUNDIAL 2026 - PROBABILIDADES POR EQUIPO")
    print(f"Simulaciones: {simulations} | Modelo: Monte Carlo")
    try:
        simulation_count = int(float(simulations))
    except (TypeError, ValueError):
        simulation_count = 0
    if simulation_count and simulation_count < 1000:
        print("ADVERTENCIA: muestra chica. Estos porcentajes son una prueba tecnica, no una estimacion estable.")
        print("Para probabilidades interpretables usa al menos: python -m src.main --simulations 1000 --seed 123")
    print_separator()
    print(f"{'N':>3}  {'Equipo':<24} {'Campeon':>8} {'Final':>8} {'Semi':>8} {'Cuartos':>8} {'R16':>8} {'R32':>8} {'Grupo':>8}")
    for _, row in df.iterrows():
        print(
            f"{int(row['rank']):>3}  "
            f"{str(row['team'])[:24]:<24} "
            f"{_percentage(row.get('champion_probability'))} "
            f"{_percentage(row.get('final_probability'))} "
            f"{_percentage(row.get('semifinal_probability'))} "
            f"{_percentage(row.get('quarterfinal_probability'))} "
            f"{_percentage(row.get('round_of_16_probability'))} "
            f"{_percentage(row.get('round_of_32_probability'))} "
            f"{_percentage(row.get('group_qualification_probability'))}"
        )
    print()
    print("Opciones:")
    print('- Escribi el numero de un equipo para ver estadisticas completas.')
    print('- Escribi "buscar argentina" para buscar un equipo.')
    print('- Escribi "comparar 1 2" para comparar dos equipos.')
    print('- Escribi "top lesiones", "top sorpresa", "top campeon", "top grupos", "top goles", "top defensa" o "top penales".')
    print('- Escribi "partidos" para ver marcadores mas probables o "partidos argentina" para filtrar por equipo.')
    print('- Escribi "0", "q", "quit" o "salir" para terminar.')


def print_team_detail(df: pd.DataFrame, team_index: int) -> None:
    row = _team_by_number(df, team_index)
    if row is None:
        print(f"Equipo numero {team_index} no existe. Elegi un numero entre 1 y {len(df)}.")
        return
    print_separator()
    print(f"{str(row['team']).upper()} - ESTADISTICAS COMPLETAS")
    print_separator()
    print("Resumen general:")
    print(f"- Ranking de candidato: {int(row['rank'])}/{len(df)}")
    print(f"- Probabilidad de campeon: {format_percentage(row.get('champion_probability'))}")
    print(f"- Intervalo de confianza 95%: {format_percentage(row.get('champion_ci_low'))} - {format_percentage(row.get('champion_ci_high'))}")
    print(f"- Probabilidad de llegar a la final: {format_percentage(row.get('final_probability'))}")
    print(f"- Probabilidad de semifinal: {format_percentage(row.get('semifinal_probability'))}")
    print(f"- Probabilidad de cuartos: {format_percentage(row.get('quarterfinal_probability'))}")
    print(f"- Probabilidad de octavos/R16: {format_percentage(row.get('round_of_16_probability'))}")
    print(f"- Probabilidad de ronda de 32: {format_percentage(row.get('round_of_32_probability'))}")
    print(f"- Probabilidad de superar fase de grupos: {format_percentage(row.get('group_qualification_probability'))}")
    print(f"- Probabilidad de quedar eliminado en grupos: {format_percentage(row.get('group_exit_probability'))}")
    print()
    print("Fase de grupos:")
    print(f"- Probabilidad de terminar 1ro: {format_percentage(row.get('group_winner_probability'))}")
    print(f"- Probabilidad de terminar 2do: {format_percentage(row.get('group_runner_up_probability'))}")
    print(f"- Probabilidad de terminar 3ro: {format_percentage(row.get('third_place_probability'))}")
    print(f"- Probabilidad de terminar 4to: {format_percentage(row.get('fourth_place_probability'))}")
    print(f"- Puntos promedio: {format_decimal(row.get('average_points'))}")
    print(f"- Goles a favor promedio: {format_decimal(row.get('average_goals_for'))}")
    print(f"- Goles en contra promedio: {format_decimal(row.get('average_goals_against'))}")
    print(f"- Diferencia de gol promedio: {format_decimal(row.get('average_goal_difference'), signed=True)}")
    print()
    print("Produccion ofensiva y defensiva:")
    print(f"- xG a favor promedio: {format_decimal(row.get('average_xg_for'))}")
    print(f"- xG en contra promedio: {format_decimal(row.get('average_xg_against'))}")
    print(f"- Probabilidad de valla invicta: {format_percentage(row.get('clean_sheet_probability'))}")
    print(f"- Probabilidad de no marcar: {format_percentage(row.get('failed_to_score_probability'))}")
    print()
    print("Disciplina, lesiones, fatiga y penales:")
    print(f"- Amarillas promedio por torneo: {format_decimal(row.get('average_yellow_cards'))}")
    print(f"- Rojas promedio por torneo: {format_decimal(row.get('average_red_cards'))}")
    print(f"- Probabilidad de expulsion: {format_percentage(row.get('red_card_probability'))}")
    print(f"- Lesiones promedio por torneo: {format_decimal(row.get('average_injuries'))}")
    print(f"- Probabilidad de lesion grave: {format_percentage(row.get('severe_injury_probability'))}")
    print(f"- Posicion mas afectada: {safe_get(row, 'most_affected_position')}")
    print(f"- Fatiga promedio acumulada: {format_decimal(row.get('average_fatigue'))}")
    print(f"- Probabilidad de alargue: {format_percentage(row.get('extra_time_probability'))}")
    print(f"- Probabilidad de tanda de penales: {format_percentage(row.get('penalty_shootout_probability'))}")
    print()
    print("Indices del modelo:")
    print(f"- Team strength: {format_decimal(row.get('team_strength'))}")
    print(f"- Attack strength: {format_decimal(row.get('attack_strength'))}")
    print(f"- Defense strength: {format_decimal(row.get('defense_strength'))}")
    print(f"- Goalkeeper strength: {format_decimal(row.get('goalkeeper_strength'))}")
    print(f"- Squad depth: {format_decimal(row.get('squad_depth_index'))}")
    print(f"- Recent form: {format_decimal(row.get('recent_form_index'))}")
    print(f"- Dark horse index: {format_decimal(row.get('dark_horse_index'))}")
    print(f"- Upset victim probability: {format_percentage(row.get('upset_victim_probability'))}")
    print(f"- Data quality score: {format_decimal(row.get('data_quality_score'))}")
    print()
    print("Opciones: 4 comparar contra otro equipo | 5 volver al ranking | 0 salir")


def compare_teams(df: pd.DataFrame, team_a: int, team_b: int) -> None:
    row_a = _team_by_number(df, team_a)
    row_b = _team_by_number(df, team_b)
    if row_a is None or row_b is None:
        print(f"No se puede comparar: elegi numeros entre 1 y {len(df)}.")
        return
    print_separator()
    print(f"COMPARACION: {row_a['team']} vs {row_b['team']}")
    print_separator()
    metrics = [
        ("Campeon", "champion_probability", "pct"),
        ("Final", "final_probability", "pct"),
        ("Semifinal", "semifinal_probability", "pct"),
        ("Cuartos", "quarterfinal_probability", "pct"),
        ("Supera grupos", "group_qualification_probability", "pct"),
        ("Goles promedio a favor", "average_goals_for", "num"),
        ("Goles promedio en contra", "average_goals_against", "num"),
        ("xG a favor", "average_xg_for", "num"),
        ("xG en contra", "average_xg_against", "num"),
        ("Lesiones promedio", "average_injuries", "num"),
        ("Riesgo lesion grave", "severe_injury_probability", "pct"),
        ("Tanda de penales", "penalty_shootout_probability", "pct"),
        ("Team strength", "team_strength", "num"),
        ("Attack strength", "attack_strength", "num"),
        ("Defense strength", "defense_strength", "num"),
        ("Data quality", "data_quality_score", "num"),
    ]
    print(f"{'Metrica':<32} {str(row_a['team'])[:18]:>18} {str(row_b['team'])[:18]:>18}")
    for label, column, kind in metrics:
        formatter = format_percentage if kind == "pct" else format_decimal
        print(f"{label:<32} {formatter(row_a.get(column)):>18} {formatter(row_b.get(column)):>18}")
    print()
    delta = float(row_a.get("champion_probability", 0.0)) - float(row_b.get("champion_probability", 0.0))
    if abs(delta) < 0.01:
        print("- La diferencia de campeon es pequena; puede no ser estadisticamente significativa.")
    elif delta > 0:
        print(f"- {row_a['team']} tiene mayor probabilidad de campeon en esta corrida.")
    else:
        print(f"- {row_b['team']} tiene mayor probabilidad de campeon en esta corrida.")
    print("- Revisar intervalos de confianza antes de interpretar diferencias pequenas.")


def print_top(df: pd.DataFrame, metric: str, n: int = 10) -> None:
    if metric not in TOP_COMMANDS:
        print(f"Top desconocido: {metric}")
        return
    column, ascending, title = TOP_COMMANDS[metric]
    if column not in df.columns:
        print(f"No disponible: falta la columna {column}.")
        return
    ranked = df.copy()
    ranked[column] = pd.to_numeric(ranked[column], errors="coerce")
    ranked = ranked.dropna(subset=[column]).sort_values(column, ascending=ascending).head(n)
    print_separator()
    print(title)
    print_separator()
    print(f"{'N':>3} {'Equipo':<24} {'Valor':>14}")
    for position, (_, row) in enumerate(ranked.iterrows(), start=1):
        value = format_percentage(row[column]) if "probability" in column or column.endswith("_rate") else format_decimal(row[column])
        print(f"{position:>3} {str(row['team'])[:24]:<24} {value:>14}")


def load_match_predictions(outputs_dir: Path = Path("outputs")) -> pd.DataFrame:
    path = outputs_dir / "match_predictions.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def print_match_predictions(matches: pd.DataFrame, query: str | None = None, limit: int = 72) -> None:
    if matches.empty:
        print("No hay predicciones por partido. Ejecuta primero una simulacion para generar outputs/match_predictions.csv.")
        return
    filtered = matches[matches["stage"].astype(str).str.lower() == "group"].copy()
    if query:
        normalized_query = normalize_text(query)
        filtered = filtered[
            filtered["team_a"].map(normalize_text).str.contains(normalized_query, na=False)
            | filtered["team_b"].map(normalize_text).str.contains(normalized_query, na=False)
            | filtered["team_a_id"].map(normalize_text).str.contains(normalized_query, na=False)
            | filtered["team_b_id"].map(normalize_text).str.contains(normalized_query, na=False)
        ]
    if filtered.empty:
        print(f"No encontre partidos para: {query}")
        return
    print_separator(120)
    title = "RESULTADOS MAS PROBABLES POR PARTIDO - FASE DE GRUPOS"
    if query:
        title += f" - filtro: {query}"
    print(title)
    if "samples" in filtered.columns and not filtered.empty and float(filtered["samples"].min()) < 1000:
        print("ADVERTENCIA: muestra chica. Los marcadores mas probables mejoran con mas simulaciones.")
    print_separator(120)
    print(
        f"{'ID':<15} {'Fase':<14} {'Partido':<39} {'Marcador':>9} {'Prob.':>8} "
        f"{'xG A':>7} {'xG B':>7} {'Gana A':>8} {'Empate':>8} {'Gana B':>8}"
    )
    for _, row in filtered.head(limit).iterrows():
        matchup = f"{row['team_a']} vs {row['team_b']}"
        print(
            f"{str(row['match_id'])[:15]:<15} "
            f"{str(row['stage'])[:14]:<14} "
            f"{matchup[:39]:<39} "
            f"{str(row['most_likely_score']):>9} "
            f"{format_percentage(row.get('most_likely_score_probability')):>8} "
            f"{format_decimal(row.get('average_xg_a')):>7} "
            f"{format_decimal(row.get('average_xg_b')):>7} "
            f"{format_percentage(row.get('team_a_win_probability')):>8} "
            f"{format_percentage(row.get('draw_probability_90')):>8} "
            f"{format_percentage(row.get('team_b_win_probability')):>8}"
        )
    if len(filtered) > limit:
        print(f"... {len(filtered) - limit} partidos mas. Usa un filtro por equipo, por ejemplo: partidos argentina")


def _handle_search(df: pd.DataFrame, query: str) -> None:
    matches = search_team(df, query)
    if not matches:
        print(f"No encontre equipos para: {query}")
        return
    print("Coincidencias:")
    for index in matches:
        row = df.iloc[index]
        print(f"{int(row['rank'])}. {row['team']} - campeon {format_percentage(row.get('champion_probability'))}")


def interactive_loop(df: pd.DataFrame) -> None:
    if df.empty:
        print("No hay equipos cargados. Ejecuta primero una simulacion.")
        return
    matches = load_match_predictions()
    print_main_ranking(df)
    while True:
        command = input("\nEntrada: ").strip()
        normalized = command.casefold()
        if normalized in {"0", "q", "quit", "salir"}:
            print("Saliendo.")
            return
        if normalized in {"ranking", "volver", "5"}:
            print_main_ranking(df)
            continue
        if normalized.isdigit():
            print_team_detail(df, int(normalized))
            continue
        if normalized.startswith("buscar "):
            _handle_search(df, command[7:].strip())
            continue
        if normalized.startswith("comparar "):
            parts = normalized.split()
            if len(parts) != 3 or not parts[1].isdigit() or not parts[2].isdigit():
                print('Uso: comparar 1 2')
                continue
            compare_teams(df, int(parts[1]), int(parts[2]))
            continue
        if normalized.startswith("top "):
            print_top(df, normalized.split(maxsplit=1)[1])
            continue
        if normalized == "partidos":
            print_match_predictions(matches)
            continue
        if normalized.startswith("partidos "):
            print_match_predictions(matches, command.split(maxsplit=1)[1].strip())
            continue
        print("Comando no reconocido. Usa un numero, buscar <equipo>, comparar <n> <n>, top <metrica> o salir.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactive dashboard for World Cup 2026 simulator outputs.")
    parser.add_argument("--outputs-dir", type=Path, default=Path("outputs"), help="Directory containing simulator output CSV files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        data = load_dashboard_data(args.outputs_dir)
    except FileNotFoundError as error:
        print(error)
        return
    interactive_loop(data)


if __name__ == "__main__":
    main()
