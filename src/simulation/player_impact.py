from __future__ import annotations

import pandas as pd


POSITION_WEIGHTS = {
    "GK": 0.85,
    "DF": 0.95,
    "MF": 1.00,
    "FW": 1.05,
}


def player_impact_score(player: pd.Series, tactical_style: str = "balanced") -> float:
    position = str(player.get("position", "MF"))
    position_weight = POSITION_WEIGHTS.get(position, 1.0)
    if tactical_style in {"direct", "counterattack"} and position == "FW":
        position_weight += 0.08
    if tactical_style in {"possession", "pressing"} and position == "MF":
        position_weight += 0.07
    availability = 1.0 if bool(player.get("is_available", not bool(player.get("is_injured", False)))) else 0.0
    return round(
        float(player.get("overall_rating", 70.0))
        * float(player.get("importance", 0.5))
        * float(player.get("starter_probability", 0.5))
        * position_weight
        * availability,
        4,
    )

