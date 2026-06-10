from __future__ import annotations

import pandas as pd


MATCHUP_ADVANTAGES = {
    ("pressing", "direct"): 0.05,
    ("high_press", "direct_play"): 0.04,
    ("direct", "possession"): 0.04,
    ("counterattack", "high_press"): 0.06,
    ("possession", "low_block"): -0.03,
    ("possession", "pressing"): -0.04,
    ("balanced", "balanced"): 0.0,
}


def tactical_matchup_modifier(team: pd.Series, opponent: pd.Series, config: dict | None = None) -> float:
    style = str(team.get("tactical_style", "balanced"))
    opponent_style = str(opponent.get("tactical_style", "balanced"))
    base_advantage = MATCHUP_ADVANTAGES.get((style, opponent_style), 0.0)
    pressing_gap = float(team.get("pressing_intensity", 0.6)) - float(opponent.get("pressing_intensity", 0.6))
    advantage = base_advantage + pressing_gap * 0.03
    return round(max(0.90, min(1.10, 1.0 + advantage)), 4)

