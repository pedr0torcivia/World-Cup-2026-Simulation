from __future__ import annotations

import numpy as np
import pandas as pd

from src.models.match import MatchResult
from src.simulation.match_engine import simulate_match
from src.simulation.tie_breakers import empty_group_table, sort_best_thirds, sort_group_table


def update_group_table(table: pd.DataFrame, result: MatchResult) -> None:
    row_a = table["team_id"] == result.team_a
    row_b = table["team_id"] == result.team_b
    table.loc[row_a, "played"] += 1
    table.loc[row_b, "played"] += 1
    table.loc[row_a, "goals_for"] += result.goals_a
    table.loc[row_a, "goals_against"] += result.goals_b
    table.loc[row_b, "goals_for"] += result.goals_b
    table.loc[row_b, "goals_against"] += result.goals_a
    table.loc[row_a, "goal_difference"] = table.loc[row_a, "goals_for"] - table.loc[row_a, "goals_against"]
    table.loc[row_b, "goal_difference"] = table.loc[row_b, "goals_for"] - table.loc[row_b, "goals_against"]
    table.loc[row_a, "fair_play"] += result.yellow_cards.get(result.team_a, 0) + result.red_cards.get(result.team_a, 0) * 3
    table.loc[row_b, "fair_play"] += result.yellow_cards.get(result.team_b, 0) + result.red_cards.get(result.team_b, 0) * 3

    if result.goals_a > result.goals_b:
        table.loc[row_a, ["points", "wins"]] += [3, 1]
        table.loc[row_b, "losses"] += 1
    elif result.goals_b > result.goals_a:
        table.loc[row_b, ["points", "wins"]] += [3, 1]
        table.loc[row_a, "losses"] += 1
    else:
        table.loc[row_a, ["points", "draws"]] += [1, 1]
        table.loc[row_b, ["points", "draws"]] += [1, 1]


def simulate_group_stage(
    teams: pd.DataFrame,
    players: pd.DataFrame,
    fixtures: pd.DataFrame,
    venues: pd.DataFrame,
    rng: np.random.Generator,
    config: dict,
    team_fatigue: dict[str, float],
) -> tuple[pd.DataFrame, pd.DataFrame, list[MatchResult]]:
    group_fixtures = fixtures[fixtures["stage"].str.lower() == "group"].copy()
    results: list[MatchResult] = []
    ranked_tables: list[pd.DataFrame] = []

    for group_name, group_teams in teams.groupby("group", sort=True):
        table = empty_group_table(group_teams)
        matches = group_fixtures[group_fixtures["group"] == group_name].sort_values(["matchday", "match_id"])
        for _, fixture in matches.iterrows():
            team_a = teams.loc[teams["team_id"] == fixture["team_a"]].iloc[0]
            team_b = teams.loc[teams["team_id"] == fixture["team_b"]].iloc[0]
            venue = venues.loc[venues["venue_id"] == fixture["venue_id"]].iloc[0]
            result = simulate_match(
                str(fixture["match_id"]),
                "group",
                team_a,
                team_b,
                venue,
                players,
                rng,
                config,
                team_fatigue,
                knockout=False,
            )
            results.append(result)
            update_group_table(table, result)
        ranked_tables.append(sort_group_table(table))

    final_table = pd.concat(ranked_tables, ignore_index=True)
    top_two = final_table[final_table["rank"] <= 2]
    thirds = sort_best_thirds(final_table[final_table["rank"] == 3]).head(8)
    qualifiers = pd.concat([top_two, thirds], ignore_index=True)
    return final_table, qualifiers, results

