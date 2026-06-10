from __future__ import annotations

from collections import Counter, defaultdict

import pandas as pd

from src.analytics.uncertainty import add_probability_uncertainty


ROUND_COLUMNS = [
    "round_of_32",
    "round_of_16",
    "quarter_final",
    "semi_final",
    "final",
    "champion",
]


def build_probability_tables(teams: pd.DataFrame, simulation_records: list[dict], group_position_records: list[dict]) -> dict[str, pd.DataFrame]:
    total = max(1, len(simulation_records))
    team_names = dict(zip(teams["team_id"], teams["team_name"]))
    champion_counts = Counter(record["champion"] for record in simulation_records)
    round_counts: dict[str, Counter] = {round_name: Counter() for round_name in ROUND_COLUMNS}
    for record in simulation_records:
        for round_name in ROUND_COLUMNS:
            for team_id in record.get(round_name, []):
                round_counts[round_name][team_id] += 1

    champion_rows = [
        {
            "team": team_names[team_id],
            "championships": champion_counts[team_id],
            "probability": champion_counts[team_id] / total,
        }
        for team_id in teams["team_id"]
    ]

    qualification_rows = []
    for team_id in teams["team_id"]:
        round_of_32 = round_counts["round_of_32"][team_id] / total
        qualification_rows.append(
            {
                "team": team_names[team_id],
                "group_stage_exit_probability": 1.0 - round_of_32,
                "round_of_32_probability": round_of_32,
                "round_of_16_probability": round_counts["round_of_16"][team_id] / total,
                "quarter_final_probability": round_counts["quarter_final"][team_id] / total,
                "semi_final_probability": round_counts["semi_final"][team_id] / total,
                "final_probability": round_counts["final"][team_id] / total,
                "champion_probability": round_counts["champion"][team_id] / total,
            }
        )

    positions: dict[str, Counter] = defaultdict(Counter)
    qualifies = Counter()
    for row in group_position_records:
        positions[row["team_id"]][int(row["rank"])] += 1
        if row["qualified"]:
            qualifies[row["team_id"]] += 1
    group_rows = []
    for team_id in teams["team_id"]:
        group_rows.append(
            {
                "team": team_names[team_id],
                "probability_1st": positions[team_id][1] / total,
                "probability_2nd": positions[team_id][2] / total,
                "probability_3rd": positions[team_id][3] / total,
                "probability_4th": positions[team_id][4] / total,
                "probability_qualify": qualifies[team_id] / total,
            }
        )

    return {
        "champion_probabilities": add_probability_uncertainty(
            pd.DataFrame(champion_rows).sort_values("probability", ascending=False),
            ["probability"],
            total,
        ),
        "qualification_probabilities": add_probability_uncertainty(
            pd.DataFrame(qualification_rows).sort_values("champion_probability", ascending=False),
            [
                "group_stage_exit_probability",
                "round_of_32_probability",
                "round_of_16_probability",
                "quarter_final_probability",
                "semi_final_probability",
                "final_probability",
                "champion_probability",
            ],
            total,
        ),
        "group_probabilities": add_probability_uncertainty(
            pd.DataFrame(group_rows).sort_values("probability_qualify", ascending=False),
            ["probability_1st", "probability_2nd", "probability_3rd", "probability_4th", "probability_qualify"],
            total,
        ),
    }
