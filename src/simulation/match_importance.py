from __future__ import annotations


def game_importance_modifier(need_win: bool = False, need_draw: bool = False) -> float:
    if need_win:
        return 1.04
    if need_draw:
        return 0.97
    return 1.0

