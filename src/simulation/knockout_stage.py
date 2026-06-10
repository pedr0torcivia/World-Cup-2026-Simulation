from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.models.match import MatchResult
from src.simulation.match_engine import simulate_match


ROUND_SEQUENCE = [
    ("round_of_32", 32),
    ("round_of_16", 16),
    ("quarter_final", 8),
    ("semi_final", 4),
    ("final", 2),
]


def seed_qualifiers(qualifiers: pd.DataFrame) -> list[str]:
    ordered = qualifiers.sort_values(
        by=["rank", "points", "goal_difference", "goals_for", "elo_rating"],
        ascending=[True, False, False, False, False],
        kind="mergesort",
    )
    return [str(team_id) for team_id in ordered["team_id"].head(32)]


def pair_seeded_teams(team_ids: list[str]) -> list[tuple[str, str]]:
    return [(team_ids[index], team_ids[-index - 1]) for index in range(len(team_ids) // 2)]


def load_bracket_pairs(project_root: Path, seeded_ids: list[str]) -> list[tuple[str, str]]:
    rules_path = project_root / "data" / "bracket_rules.csv"
    if not rules_path.exists():
        return pair_seeded_teams(seeded_ids)

    rules = pd.read_csv(rules_path)
    if not {"slot_a", "slot_b"}.issubset(rules.columns):
        raise ValueError("bracket_rules.csv must include slot_a and slot_b columns")
    pairs = []
    for _, row in rules.iterrows():
        pairs.append((seeded_ids[int(row["slot_a"]) - 1], seeded_ids[int(row["slot_b"]) - 1]))
    return pairs


def simulate_knockout_stage(
    teams: pd.DataFrame,
    players: pd.DataFrame,
    qualifiers: pd.DataFrame,
    venues: pd.DataFrame,
    rng: np.random.Generator,
    config: dict,
    team_fatigue: dict[str, float],
    project_root: Path,
) -> tuple[str, dict[str, list[str]], list[MatchResult]]:
    seeded_ids = seed_qualifiers(qualifiers)
    current_pairs = load_bracket_pairs(project_root, seeded_ids)
    reached: dict[str, list[str]] = {"round_of_32": seeded_ids.copy()}
    results: list[MatchResult] = []
    venue_cycle = venues.reset_index(drop=True)

    for round_index, (round_name, _) in enumerate(ROUND_SEQUENCE):
        winners: list[str] = []
        for match_index, (team_a_id, team_b_id) in enumerate(current_pairs, start=1):
            team_a = teams.loc[teams["team_id"] == team_a_id].iloc[0]
            team_b = teams.loc[teams["team_id"] == team_b_id].iloc[0]
            venue = venue_cycle.iloc[(round_index + match_index) % len(venue_cycle)]
            result = simulate_match(
                f"{round_name}_{match_index}",
                round_name,
                team_a,
                team_b,
                venue,
                players,
                rng,
                config,
                team_fatigue,
                knockout=True,
            )
            results.append(result)
            winners.append(str(result.winner))
        if round_name != "final":
            next_round = ROUND_SEQUENCE[round_index + 1][0]
            reached[next_round] = winners.copy()
            current_pairs = [(winners[index], winners[index + 1]) for index in range(0, len(winners), 2)]
        else:
            reached["champion"] = winners.copy()
            return winners[0], reached, results

    raise RuntimeError("Knockout stage ended without a champion")

