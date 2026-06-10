from __future__ import annotations

import pandas as pd


def set_piece_xg_share(team: pd.Series) -> float:
    attack = float(team.get("attack_rating", 75.0))
    aerial = float(team.get("experience", 75.0))
    return round(max(0.12, min(0.34, 0.18 + (attack + aerial - 150.0) * 0.002)), 4)

