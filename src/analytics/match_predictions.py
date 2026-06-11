from __future__ import annotations

from collections import Counter, defaultdict

import pandas as pd


def record_match_prediction(accumulator: dict, simulation_id: int, result) -> None:
    key = (result.match_id, result.stage, result.team_a, result.team_b)
    entry = accumulator.setdefault(
        key,
        {
            "simulations": set(),
            "score_counter": Counter(),
            "winner_counter": Counter(),
            "goals_a": 0.0,
            "goals_b": 0.0,
            "xg_a": 0.0,
            "xg_b": 0.0,
            "extra_time": 0,
            "penalties": 0,
        },
    )
    entry["simulations"].add(simulation_id)
    entry["score_counter"][(int(result.goals_a), int(result.goals_b))] += 1
    if result.goals_a > result.goals_b:
        entry["winner_counter"]["team_a"] += 1
    elif result.goals_b > result.goals_a:
        entry["winner_counter"]["team_b"] += 1
    else:
        entry["winner_counter"]["draw"] += 1
    entry["goals_a"] += float(result.goals_a)
    entry["goals_b"] += float(result.goals_b)
    entry["xg_a"] += float(result.expected_goals_a)
    entry["xg_b"] += float(result.expected_goals_b)
    entry["extra_time"] += int(bool(result.went_to_extra_time))
    entry["penalties"] += int(bool(result.went_to_penalties))


def build_match_predictions(accumulator: dict, teams: pd.DataFrame) -> pd.DataFrame:
    team_names = dict(zip(teams["team_id"], teams["team_name"]))
    rows = []
    for (match_id, stage, team_a, team_b), entry in accumulator.items():
        sample_size = len(entry["simulations"])
        if sample_size <= 0:
            continue
        (score_a, score_b), score_count = entry["score_counter"].most_common(1)[0]
        rows.append(
            {
                "match_id": match_id,
                "stage": stage,
                "team_a": team_names.get(team_a, team_a),
                "team_b": team_names.get(team_b, team_b),
                "team_a_id": team_a,
                "team_b_id": team_b,
                "samples": sample_size,
                "most_likely_score": f"{score_a}-{score_b}",
                "most_likely_score_probability": score_count / sample_size,
                "average_goals_a": entry["goals_a"] / sample_size,
                "average_goals_b": entry["goals_b"] / sample_size,
                "average_xg_a": entry["xg_a"] / sample_size,
                "average_xg_b": entry["xg_b"] / sample_size,
                "team_a_win_probability": entry["winner_counter"]["team_a"] / sample_size,
                "draw_probability_90": entry["winner_counter"]["draw"] / sample_size,
                "team_b_win_probability": entry["winner_counter"]["team_b"] / sample_size,
                "extra_time_probability": entry["extra_time"] / sample_size,
                "penalty_shootout_probability": entry["penalties"] / sample_size,
            }
        )
    if not rows:
        return pd.DataFrame()
    stage_order = defaultdict(lambda: 99, {"group": 1, "round_of_32": 2, "round_of_16": 3, "quarter_final": 4, "semi_final": 5, "third_place": 6, "final": 7})
    output = pd.DataFrame(rows)
    output["_stage_order"] = output["stage"].map(stage_order)
    output = output.sort_values(["_stage_order", "match_id", "samples"], ascending=[True, True, False]).drop(columns=["_stage_order"])
    return output.reset_index(drop=True)

