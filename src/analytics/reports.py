from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_outputs(
    output_dir: Path,
    probability_tables: dict[str, pd.DataFrame],
    injuries_summary: pd.DataFrame,
    match_sample: pd.DataFrame,
    data_quality_report: pd.DataFrame,
    metadata: dict,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, table in probability_tables.items():
        table.to_csv(output_dir / f"{name}.csv", index=False)
    probability_tables["qualification_probabilities"].to_csv(output_dir / "knockout_probabilities.csv", index=False)
    injuries_summary.to_csv(output_dir / "injuries_summary.csv", index=False)
    data_quality_report.to_csv(output_dir / "data_quality_report.csv", index=False)
    match_sample.to_csv(output_dir / "match_results_sample.csv", index=False)
    (output_dir / "full_report.md").write_text(build_markdown_report(probability_tables, injuries_summary, data_quality_report, metadata), encoding="utf-8")


def build_markdown_report(probability_tables: dict[str, pd.DataFrame], injuries_summary: pd.DataFrame, data_quality_report: pd.DataFrame, metadata: dict) -> str:
    champions = probability_tables["champion_probabilities"].head(10)
    top = champions.iloc[0]
    lines = [
        "# World Cup 2026 Monte Carlo Report",
        "",
        f"- Simulations: {metadata['simulations']}",
        f"- Random seed: {metadata['seed']}",
        f"- Most likely champion: {top['team']} ({top['probability']:.2%})",
        f"- Average goals per match: {metadata['average_goals_per_match']:.2f}",
        f"- Average injuries per simulation: {metadata['average_injuries']:.2f}",
        f"- Penalty shootout rate: {metadata['penalty_rate']:.2%}",
        f"- Average team data quality score: {data_quality_report['team_data_quality_score'].mean():.2f}",
        "",
        "## Top 10 Candidates",
        "",
    ]
    for _, row in champions.iterrows():
        lines.append(f"- {row['team']}: {row['probability']:.2%}")

    early_risk = probability_tables["qualification_probabilities"].sort_values("group_stage_exit_probability", ascending=False).head(10)
    lines.extend(["", "## Early Exit Risk", ""])
    for _, row in early_risk.iterrows():
        lines.append(f"- {row['team']}: {row['group_stage_exit_probability']:.2%}")

    lines.extend(["", "## Injuries", ""])
    for _, row in injuries_summary.head(10).iterrows():
        lines.append(f"- {row['team']}: {row['average_injuries']:.2f} average injuries")

    lines.extend(["", "## Data Quality", ""])
    warnings = data_quality_report[data_quality_report["warning"] != ""].head(8)
    if warnings.empty:
        lines.append("- No major data quality warnings.")
    else:
        for _, row in warnings.iterrows():
            lines.append(f"- {row['team']}: {row['warning']} (score {row['team_data_quality_score']:.2f})")

    lines.extend(["", "## Sensitivity", ""])
    lines.append("Sensitivity CSVs can be generated with `run_sensitivity_analysis`; they report champion probability deltas when core assumptions move by +/-10%.")

    lines.extend(
        [
            "",
            "## Model Notes",
            "",
            "The simulator uses editable CSV/YAML inputs, Poisson goals, fatigue, injuries, cards, venue effects, penalties, group tie-breakers and a configurable knockout bracket.",
            "If `data/bracket_rules.csv` is absent, the round-of-32 bracket is an approximate seeded bracket that can be replaced when official mapping rules are loaded.",
        ]
    )
    return "\n".join(lines) + "\n"
