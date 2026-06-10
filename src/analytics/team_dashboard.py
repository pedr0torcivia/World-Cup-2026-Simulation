from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.simulation.expected_goals import attack_strength, defense_strength, goalkeeper_strength, team_strength
from src.utils.console_utils import normalize_text
from src.utils.data_loader import read_config


DASHBOARD_COLUMNS = [
    "team",
    "rank",
    "champion_probability",
    "champion_ci_low",
    "champion_ci_high",
    "final_probability",
    "semifinal_probability",
    "quarterfinal_probability",
    "round_of_16_probability",
    "round_of_32_probability",
    "group_qualification_probability",
    "group_exit_probability",
    "group_winner_probability",
    "group_runner_up_probability",
    "third_place_probability",
    "fourth_place_probability",
    "average_points",
    "average_goal_difference",
    "average_goals_for",
    "average_goals_against",
    "average_xg_for",
    "average_xg_against",
    "clean_sheet_probability",
    "failed_to_score_probability",
    "average_yellow_cards",
    "average_red_cards",
    "red_card_probability",
    "suspension_probability",
    "average_injuries",
    "severe_injury_probability",
    "key_player_injury_probability",
    "most_affected_position",
    "performance_loss_due_to_injuries",
    "average_fatigue",
    "high_fatigue_probability",
    "extra_time_probability",
    "penalty_shootout_probability",
    "shootout_win_rate",
    "penalty_conversion_rate",
    "team_strength",
    "attack_strength",
    "defense_strength",
    "goalkeeper_strength",
    "squad_depth_index",
    "recent_form_index",
    "dark_horse_index",
    "upset_victim_probability",
    "data_quality_score",
    "simulations_used",
]


TEAM_ALIASES = {
    "usa": "united states",
    "eeuu": "united states",
    "estados unidos": "united states",
    "espana": "spain",
    "costa de marfil": "ivory coast",
    "ir iran": "ir iran",
    "iran": "ir iran",
    "rd congo": "dr congo",
    "republica democratica del congo": "dr congo",
}


def _read_optional_csv(path: Path) -> tuple[pd.DataFrame, str | None]:
    if not path.exists():
        return pd.DataFrame(), f"Missing {path.name}. Run a simulation first for complete data."
    return pd.read_csv(path), None


def _merge_if_available(left: pd.DataFrame, right: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if right.empty or "team" not in right.columns:
        return left
    available = ["team"] + [column for column in columns if column in right.columns and column not in left.columns]
    if len(available) == 1:
        return left
    return left.merge(right[available], on="team", how="left")


def _build_match_sample_stats(outputs_dir: Path) -> pd.DataFrame:
    matches, _ = _read_optional_csv(outputs_dir / "match_results_sample.csv")
    if matches.empty:
        return pd.DataFrame(columns=["team"])
    rows = []
    for _, match in matches.iterrows():
        rows.append(
            {
                "team_id": match["team_a"],
                "goals_for": match["goals_a"],
                "goals_against": match["goals_b"],
                "xg_for": match.get("expected_goals_a", 0.0),
                "xg_against": match.get("expected_goals_b", 0.0),
                "clean_sheet": int(match["goals_b"] == 0),
                "failed_to_score": int(match["goals_a"] == 0),
                "extra_time": int(bool(match.get("went_to_extra_time", False))),
                "penalties": int(bool(match.get("went_to_penalties", False))),
            }
        )
        rows.append(
            {
                "team_id": match["team_b"],
                "goals_for": match["goals_b"],
                "goals_against": match["goals_a"],
                "xg_for": match.get("expected_goals_b", 0.0),
                "xg_against": match.get("expected_goals_a", 0.0),
                "clean_sheet": int(match["goals_a"] == 0),
                "failed_to_score": int(match["goals_b"] == 0),
                "extra_time": int(bool(match.get("went_to_extra_time", False))),
                "penalties": int(bool(match.get("went_to_penalties", False))),
            }
        )
    expanded = pd.DataFrame(rows)
    stats = expanded.groupby("team_id", as_index=False).agg(
        average_goals_for=("goals_for", "mean"),
        average_goals_against=("goals_against", "mean"),
        average_xg_for=("xg_for", "mean"),
        average_xg_against=("xg_against", "mean"),
        clean_sheet_probability=("clean_sheet", "mean"),
        failed_to_score_probability=("failed_to_score", "mean"),
        extra_time_probability=("extra_time", "mean"),
        penalty_shootout_probability=("penalties", "mean"),
    )
    teams_path = outputs_dir.parent / "data" / "teams.csv"
    if teams_path.exists():
        teams = pd.read_csv(teams_path)[["team_id", "team_name"]]
        stats = stats.merge(teams, on="team_id", how="left").rename(columns={"team_name": "team"})
    return stats


def _model_indices(outputs_dir: Path) -> pd.DataFrame:
    teams_path = outputs_dir.parent / "data" / "teams.csv"
    config_path = outputs_dir.parent / "data" / "config.yaml"
    if not teams_path.exists() or not config_path.exists():
        return pd.DataFrame(columns=["team"])
    teams = pd.read_csv(teams_path)
    config = read_config(config_path)
    rows = []
    for _, team in teams.iterrows():
        rows.append(
            {
                "team": team["team_name"],
                "team_strength": team_strength(team, config),
                "attack_strength": attack_strength(team, config),
                "defense_strength": defense_strength(team, config),
                "goalkeeper_strength": goalkeeper_strength(team),
                "squad_depth_index": max(0.0, min(1.0, (float(team.get("squad_depth", 75.0)) - 55.0) / 40.0)),
                "recent_form_index": max(0.0, min(1.0, (float(team.get("recent_form", 75.0)) - 55.0) / 40.0)),
            }
        )
    return pd.DataFrame(rows)


def build_team_dashboard_stats(outputs_dir: str | Path) -> pd.DataFrame:
    outputs_path = Path(outputs_dir)
    champion, _ = _read_optional_csv(outputs_path / "champion_probabilities.csv")
    qualification, _ = _read_optional_csv(outputs_path / "qualification_probabilities.csv")
    groups, _ = _read_optional_csv(outputs_path / "group_probabilities.csv")
    injuries, _ = _read_optional_csv(outputs_path / "injuries_summary.csv")
    quality, _ = _read_optional_csv(outputs_path / "data_quality_report.csv")

    if champion.empty:
        if not qualification.empty:
            base = qualification[["team"]].copy()
        elif not groups.empty:
            base = groups[["team"]].copy()
        else:
            return pd.DataFrame(columns=DASHBOARD_COLUMNS)
    else:
        champion_columns = ["team", "probability", "probability_ci_low", "probability_ci_high"]
        if "simulations_used" in champion.columns:
            champion_columns.append("simulations_used")
        base = champion[champion_columns].rename(
            columns={
                "probability": "champion_probability",
                "probability_ci_low": "champion_ci_low",
                "probability_ci_high": "champion_ci_high",
            }
        )

    base = _merge_if_available(
        base,
        qualification.rename(
            columns={
                "semi_final_probability": "semifinal_probability",
                "quarter_final_probability": "quarterfinal_probability",
                "round_of_32_probability": "round_of_32_probability",
                "round_of_16_probability": "round_of_16_probability",
            }
        ),
        [
            "group_stage_exit_probability",
            "round_of_32_probability",
            "round_of_16_probability",
            "quarterfinal_probability",
            "semifinal_probability",
            "final_probability",
            "champion_probability",
        ],
    )
    base = base.rename(columns={"group_stage_exit_probability": "group_exit_probability"})
    if "group_exit_probability" in base.columns:
        base["group_qualification_probability"] = 1.0 - base["group_exit_probability"].astype(float)

    base = _merge_if_available(
        base,
        groups.rename(
            columns={
                "probability_1st": "group_winner_probability",
                "probability_2nd": "group_runner_up_probability",
                "probability_3rd": "third_place_probability",
                "probability_4th": "fourth_place_probability",
                "probability_qualify": "group_qualification_probability",
            }
        ),
        [
            "group_winner_probability",
            "group_runner_up_probability",
            "third_place_probability",
            "fourth_place_probability",
            "group_qualification_probability",
        ],
    )
    base = _merge_if_available(
        base,
        injuries.rename(
            columns={
                "average_injuries": "average_injuries",
                "serious_injury_probability": "severe_injury_probability",
            }
        ),
        ["average_injuries", "severe_injury_probability", "most_affected_position"],
    )
    base = _merge_if_available(
        base,
        quality.rename(columns={"team_data_quality_score": "data_quality_score"}),
        ["data_quality_score"],
    )
    base = _merge_if_available(base, _build_match_sample_stats(outputs_path), [
        "average_goals_for",
        "average_goals_against",
        "average_xg_for",
        "average_xg_against",
        "clean_sheet_probability",
        "failed_to_score_probability",
        "extra_time_probability",
        "penalty_shootout_probability",
    ])
    base = _merge_if_available(base, _model_indices(outputs_path), [
        "team_strength",
        "attack_strength",
        "defense_strength",
        "goalkeeper_strength",
        "squad_depth_index",
        "recent_form_index",
    ])

    for column in DASHBOARD_COLUMNS:
        if column not in base.columns:
            base[column] = pd.NA

    base["champion_probability"] = pd.to_numeric(base["champion_probability"], errors="coerce").fillna(0.0)
    base = base.sort_values("champion_probability", ascending=False).reset_index(drop=True)
    base["rank"] = range(1, len(base) + 1)
    base["dark_horse_index"] = (
        pd.to_numeric(base["round_of_16_probability"], errors="coerce").fillna(0.0)
        * (1.0 - pd.to_numeric(base["champion_probability"], errors="coerce").fillna(0.0))
    )
    base["upset_victim_probability"] = (
        pd.to_numeric(base["team_strength"], errors="coerce").fillna(0.5)
        * pd.to_numeric(base["group_exit_probability"], errors="coerce").fillna(0.0)
    )
    base["performance_loss_due_to_injuries"] = pd.to_numeric(base["average_injuries"], errors="coerce").fillna(0.0) * 0.015
    base["average_goal_difference"] = (
        pd.to_numeric(base["average_goals_for"], errors="coerce")
        - pd.to_numeric(base["average_goals_against"], errors="coerce")
    )
    base["shootout_win_rate"] = pd.NA
    base["penalty_conversion_rate"] = pd.NA
    base["average_yellow_cards"] = pd.NA
    base["average_red_cards"] = pd.NA
    base["red_card_probability"] = pd.NA
    base["suspension_probability"] = pd.NA
    base["key_player_injury_probability"] = pd.NA
    base["average_fatigue"] = pd.NA
    base["high_fatigue_probability"] = pd.NA
    return base[DASHBOARD_COLUMNS]


def load_dashboard_data(outputs_dir: str | Path) -> pd.DataFrame:
    outputs_path = Path(outputs_dir)
    dashboard_path = outputs_path / "team_dashboard_stats.csv"
    if dashboard_path.exists():
        data = pd.read_csv(dashboard_path)
    else:
        data = build_team_dashboard_stats(outputs_path)
        if not data.empty:
            outputs_path.mkdir(parents=True, exist_ok=True)
            data.to_csv(dashboard_path, index=False)
    if data.empty:
        raise FileNotFoundError(
            f"No dashboard data found in {outputs_path}. Run `python -m src.main --simulations 100 --seed 123` first."
        )
    data["rank"] = pd.to_numeric(data["rank"], errors="coerce").fillna(0).astype(int)
    data = data.sort_values("champion_probability", ascending=False).reset_index(drop=True)
    data["rank"] = range(1, len(data) + 1)
    return data


def search_team(df: pd.DataFrame, query: str) -> list[int]:
    original_query = normalize_text(query)
    candidate_queries = {original_query, normalize_text(TEAM_ALIASES.get(original_query, original_query))}
    matches = []
    for index, row in df.iterrows():
        team_name = normalize_text(row["team"])
        if any(candidate in team_name or team_name in candidate for candidate in candidate_queries):
            matches.append(index)
    return matches
