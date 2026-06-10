from __future__ import annotations

import pandas as pd


def empty_group_table(teams: pd.DataFrame) -> pd.DataFrame:
    table = teams[["team_id", "team_name", "group", "fifa_ranking", "elo_rating"]].copy()
    for column in ["points", "played", "wins", "draws", "losses", "goals_for", "goals_against", "goal_difference", "fair_play"]:
        table[column] = 0
    return table


def sort_group_table(table: pd.DataFrame, head_to_head: pd.DataFrame | None = None) -> pd.DataFrame:
    sorted_table = table.copy()
    sorted_table = sorted_table.sort_values(
        by=["points", "goal_difference", "goals_for", "fair_play", "elo_rating", "fifa_ranking"],
        ascending=[False, False, False, True, False, True],
        kind="mergesort",
    )
    sorted_table["rank"] = range(1, len(sorted_table) + 1)
    return sorted_table.reset_index(drop=True)


def sort_best_thirds(third_place_rows: pd.DataFrame) -> pd.DataFrame:
    best = third_place_rows.copy()
    best = best.sort_values(
        by=["points", "goal_difference", "goals_for", "fair_play", "elo_rating", "fifa_ranking"],
        ascending=[False, False, False, True, False, True],
        kind="mergesort",
    )
    best["third_rank"] = range(1, len(best) + 1)
    return best.reset_index(drop=True)

