from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

from src.analytics.data_quality import build_data_quality_report
from src.analytics.probabilities import build_probability_tables
from src.analytics.reports import write_outputs
from src.analytics.team_dashboard import build_team_dashboard_stats
from src.simulation.fatigue import initialize_team_fatigue
from src.simulation.group_stage import simulate_group_stage
from src.simulation.knockout_stage import simulate_knockout_stage
from src.utils.random_utils import create_rng


def _match_results_to_rows(simulation_id: int, results: list) -> list[dict]:
    rows = []
    for result in results:
        rows.append(
            {
                "simulation_id": simulation_id,
                "match_id": result.match_id,
                "stage": result.stage,
                "team_a": result.team_a,
                "team_b": result.team_b,
                "goals_a": result.goals_a,
                "goals_b": result.goals_b,
                "winner": result.winner or "",
                "went_to_extra_time": result.went_to_extra_time,
                "went_to_penalties": result.went_to_penalties,
                "expected_goals_a": result.expected_goals_a,
                "expected_goals_b": result.expected_goals_b,
                "probability_team_a_win": result.probability_summary.get("probability_team_a_win", 0.0),
                "probability_draw_90": result.probability_summary.get("probability_draw_90", 0.0),
                "probability_team_b_win": result.probability_summary.get("probability_team_b_win", 0.0),
                "probability_over_2_5": result.probability_summary.get("probability_over_2_5", 0.0),
                "probability_both_teams_score": result.probability_summary.get("probability_both_teams_score", 0.0),
                "most_likely_score": result.probability_summary.get("most_likely_score", ""),
            }
        )
    return rows


def run_monte_carlo(tournament_data, simulations: int | None = None, seed: int | None = None, output_dir: Path | None = None) -> dict:
    config = dict(tournament_data.config)
    simulation_count = int(simulations or config.get("number_of_simulations", 1000))
    base_seed = int(seed if seed is not None else config.get("random_seed", 123))
    teams = tournament_data.teams.copy()
    output_path = output_dir or tournament_data.project_root / "outputs"

    simulation_records: list[dict] = []
    group_position_records: list[dict] = []
    match_sample_rows: list[dict] = []
    injury_counter = Counter()
    serious_injury_counter = Counter()
    position_counter: dict[str, Counter] = defaultdict(Counter)
    total_goals = 0
    total_matches = 0
    total_penalty_matches = 0
    total_injuries = 0

    for simulation_id in range(1, simulation_count + 1):
        rng = create_rng(base_seed + simulation_id - 1)
        players = tournament_data.players.copy()
        team_fatigue = initialize_team_fatigue(teams)
        group_table, qualifiers, group_results = simulate_group_stage(
            teams,
            players,
            tournament_data.fixtures,
            tournament_data.venues,
            rng,
            config,
            team_fatigue,
        )
        champion, reached, knockout_results = simulate_knockout_stage(
            teams,
            players,
            qualifiers,
            tournament_data.venues,
            rng,
            config,
            team_fatigue,
            tournament_data.project_root,
        )
        qualified_ids = set(qualifiers["team_id"])
        for _, row in group_table.iterrows():
            group_position_records.append({"team_id": row["team_id"], "rank": row["rank"], "qualified": row["team_id"] in qualified_ids})

        all_results = group_results + knockout_results
        if simulation_id <= int(config.get("sample_simulations_to_store", 5)):
            match_sample_rows.extend(_match_results_to_rows(simulation_id, all_results))

        injuries = [injury for result in all_results for injury in result.injuries]
        for injury in injuries:
            injury_counter[injury["team_id"]] += 1
            position_counter[injury["team_id"]][injury["position"]] += 1
            if injury["injury_type"] in {"moderate", "severe"}:
                serious_injury_counter[injury["team_id"]] += 1

        total_injuries += len(injuries)
        total_goals += sum(result.goals_a + result.goals_b for result in all_results)
        total_matches += len(all_results)
        total_penalty_matches += sum(1 for result in all_results if result.went_to_penalties)
        record = {**reached, "champion": champion}
        simulation_records.append(record)

    probability_tables = build_probability_tables(teams, simulation_records, group_position_records)
    data_quality_report = build_data_quality_report(teams, tournament_data.players, tournament_data.venues)
    team_names = dict(zip(teams["team_id"], teams["team_name"]))
    injuries_summary = pd.DataFrame(
        [
            {
                "team": team_names[team_id],
                "average_injuries": injury_counter[team_id] / simulation_count,
                "serious_injury_probability": serious_injury_counter[team_id] / simulation_count,
                "most_affected_position": position_counter[team_id].most_common(1)[0][0] if position_counter[team_id] else "",
            }
            for team_id in teams["team_id"]
        ]
    ).sort_values("average_injuries", ascending=False)
    match_sample = pd.DataFrame(match_sample_rows)
    metadata = {
        "simulations": simulation_count,
        "seed": base_seed,
        "average_goals_per_match": total_goals / max(1, total_matches),
        "average_injuries": total_injuries / max(1, simulation_count),
        "penalty_rate": total_penalty_matches / max(1, total_matches),
    }
    write_outputs(output_path, probability_tables, injuries_summary, match_sample, data_quality_report, metadata)
    dashboard_stats = build_team_dashboard_stats(output_path)
    if not dashboard_stats.empty:
        dashboard_stats.to_csv(output_path / "team_dashboard_stats.csv", index=False)
    return {
        "tables": probability_tables,
        "injuries": injuries_summary,
        "match_sample": match_sample,
        "data_quality": data_quality_report,
        "dashboard": dashboard_stats,
        "metadata": metadata,
    }
