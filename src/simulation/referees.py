from __future__ import annotations

import pandas as pd


def average_referee() -> pd.Series:
    return pd.Series(
        {
            "referee_id": "AVG",
            "referee_name": "Average referee",
            "strictness": 1.0,
            "yellow_tendency": 1.0,
            "red_tendency": 1.0,
            "penalty_award_rate": 1.0,
            "var_intervention_rate": 1.0,
        }
    )

