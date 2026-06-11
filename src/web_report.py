from __future__ import annotations

import argparse
import html
from pathlib import Path

import pandas as pd


def _pct(value: object) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "No disponible"
    if pd.isna(number):
        return "No disponible"
    return f"{number * 100:.1f}%"


def _num(value: object, digits: int = 2) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "No disponible"
    if pd.isna(number):
        return "No disponible"
    return f"{number:.{digits}f}"


def _read_csv(outputs_dir: Path, name: str) -> pd.DataFrame:
    path = outputs_dir / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _winner(row: pd.Series) -> str:
    options = {
        row["team_a"]: float(row.get("team_a_win_probability", 0.0)),
        "Empate": float(row.get("draw_probability_90", 0.0)),
        row["team_b"]: float(row.get("team_b_win_probability", 0.0)),
    }
    return str(max(options, key=options.get))


def _render_group_matches(matches: pd.DataFrame) -> str:
    if matches.empty:
        return "<p>No hay predicciones de partidos. Ejecuta primero una simulacion.</p>"
    group = matches[matches["stage"].astype(str).str.lower() == "group"].copy()
    if group.empty:
        return "<p>No hay partidos de fase de grupos en match_predictions.csv.</p>"
    group["winner"] = group.apply(_winner, axis=1)
    rows = []
    for _, row in group.sort_values("match_id").iterrows():
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(row['match_id']))}</td>"
            f"<td>{html.escape(str(row['team_a']))} vs {html.escape(str(row['team_b']))}</td>"
            f"<td>{html.escape(str(row['winner']))}</td>"
            f"<td class='score'>{html.escape(str(row['most_likely_score']))}</td>"
            f"<td>{_pct(row.get('most_likely_score_probability'))}</td>"
            f"<td>{_num(float(row.get('average_goals_a', 0)) + float(row.get('average_goals_b', 0)))}</td>"
            f"<td>{_num(row.get('average_xg_a'))} - {_num(row.get('average_xg_b'))}</td>"
            f"<td>{_pct(row.get('team_a_win_probability'))}</td>"
            f"<td>{_pct(row.get('draw_probability_90'))}</td>"
            f"<td>{_pct(row.get('team_b_win_probability'))}</td>"
            "</tr>"
        )
    return (
        "<table id='matchesTable'>"
        "<thead><tr><th>ID</th><th>Partido</th><th>Ganador mas probable</th><th>Marcador</th>"
        "<th>Prob. marcador</th><th>Goles prom.</th><th>xG</th><th>Gana A</th><th>Empate</th><th>Gana B</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def _render_tournament_table(dashboard: pd.DataFrame) -> str:
    if dashboard.empty:
        return "<p>No hay probabilidades consolidadas por equipo.</p>"
    rows = []
    for _, row in dashboard.sort_values("champion_probability", ascending=False).iterrows():
        rows.append(
            "<tr>"
            f"<td>{int(row.get('rank', 0))}</td>"
            f"<td>{html.escape(str(row['team']))}</td>"
            f"<td>{_pct(row.get('champion_probability'))}</td>"
            f"<td>{_pct(row.get('final_probability'))}</td>"
            f"<td>{_pct(row.get('semifinal_probability'))}</td>"
            f"<td>{_pct(row.get('quarterfinal_probability'))}</td>"
            f"<td>{_pct(row.get('round_of_16_probability'))}</td>"
            f"<td>{_pct(row.get('round_of_32_probability'))}</td>"
            f"<td>{_pct(row.get('group_qualification_probability'))}</td>"
            "</tr>"
        )
    return (
        "<table id='teamsTable'>"
        "<thead><tr><th>#</th><th>Equipo</th><th>Campeon</th><th>Final</th><th>Semi</th>"
        "<th>Cuartos</th><th>R16</th><th>R32</th><th>Supera grupo</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def build_worldcup_html_report(outputs_dir: str | Path = "outputs", output_file: str | Path | None = None) -> Path:
    outputs_path = Path(outputs_dir)
    matches = _read_csv(outputs_path, "match_predictions.csv")
    dashboard = _read_csv(outputs_path, "team_dashboard_stats.csv")
    champion = _read_csv(outputs_path, "champion_probabilities.csv")
    simulations = "No disponible"
    if not champion.empty and "simulations_used" in champion.columns:
        simulations = str(int(float(champion["simulations_used"].iloc[0])))
    warning = ""
    try:
        if int(simulations) < 1000:
            warning = "<div class='warning'>Muestra chica: usa 1000+ simulaciones para probabilidades mas estables.</div>"
    except ValueError:
        pass

    html_text = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Simulador Mundial 2026 - Reporte</title>
  <style>
    :root {{ color-scheme: light; --border:#d8dee9; --ink:#172033; --muted:#5b6577; --head:#f3f6fa; }}
    body {{ margin:0; font-family: Arial, Helvetica, sans-serif; color:var(--ink); background:#ffffff; }}
    header {{ padding:24px 32px; border-bottom:1px solid var(--border); background:#0f1f3a; color:white; }}
    main {{ padding:24px 32px 48px; }}
    h1 {{ margin:0 0 8px; font-size:26px; }}
    h2 {{ margin-top:34px; }}
    .meta {{ color:#d7e1f5; }}
    .warning {{ margin-top:12px; padding:10px 12px; background:#fff3cd; border:1px solid #eed27a; color:#4d3b00; border-radius:6px; }}
    .toolbar {{ display:flex; gap:12px; align-items:center; margin:14px 0; flex-wrap:wrap; }}
    input {{ padding:9px 10px; min-width:260px; border:1px solid var(--border); border-radius:4px; }}
    table {{ border-collapse:collapse; width:100%; font-size:14px; }}
    th, td {{ padding:8px 10px; border-bottom:1px solid var(--border); text-align:left; white-space:nowrap; }}
    th {{ background:var(--head); position:sticky; top:0; z-index:1; }}
    .table-wrap {{ overflow:auto; border:1px solid var(--border); border-radius:6px; }}
    .score {{ font-weight:bold; }}
    .muted {{ color:var(--muted); }}
  </style>
</head>
<body>
  <header>
    <h1>Simulador Mundial 2026 - Reporte externo</h1>
    <div class="meta">Simulaciones: {html.escape(simulations)} | Fuente: outputs/*.csv</div>
    {warning}
  </header>
  <main>
    <section>
      <h2>Fase de grupos: resultados mas probables</h2>
      <p class="muted">Ganador mas probable, marcador mas probable y probabilidad empirica de ese marcador.</p>
      <div class="toolbar">
        <input id="matchSearch" placeholder="Filtrar partido o equipo...">
      </div>
      <div class="table-wrap">{_render_group_matches(matches)}</div>
    </section>
    <section>
      <h2>Resto del torneo: probabilidades por equipo</h2>
      <p class="muted">Probabilidades agregadas de llegar a cada ronda y ganar el torneo.</p>
      <div class="toolbar">
        <input id="teamSearch" placeholder="Filtrar equipo...">
      </div>
      <div class="table-wrap">{_render_tournament_table(dashboard)}</div>
    </section>
  </main>
  <script>
    function wireFilter(inputId, tableId) {{
      const input = document.getElementById(inputId);
      const table = document.getElementById(tableId);
      if (!input || !table) return;
      input.addEventListener('input', () => {{
        const q = input.value.toLowerCase();
        for (const row of table.querySelectorAll('tbody tr')) {{
          row.style.display = row.innerText.toLowerCase().includes(q) ? '' : 'none';
        }}
      }});
    }}
    wireFilter('matchSearch', 'matchesTable');
    wireFilter('teamSearch', 'teamsTable');
  </script>
</body>
</html>
"""
    output_path = Path(output_file) if output_file else outputs_path / "worldcup_report.html"
    output_path.write_text(html_text, encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an external HTML report for the World Cup simulator.")
    parser.add_argument("--outputs-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--output-file", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = build_worldcup_html_report(args.outputs_dir, args.output_file)
    print(f"Reporte generado: {output_path}")


if __name__ == "__main__":
    main()

