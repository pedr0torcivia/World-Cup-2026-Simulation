import pandas as pd

from src.simulation.tie_breakers import sort_best_thirds, sort_group_table


def test_sort_group_table_uses_points_goal_difference_and_goals():
    table = pd.DataFrame(
        [
            {"team_id": "A", "team_name": "A", "group": "A", "points": 6, "goal_difference": 2, "goals_for": 3, "fair_play": 2, "elo_rating": 1800, "fifa_ranking": 10},
            {"team_id": "B", "team_name": "B", "group": "A", "points": 6, "goal_difference": 4, "goals_for": 5, "fair_play": 3, "elo_rating": 1750, "fifa_ranking": 20},
            {"team_id": "C", "team_name": "C", "group": "A", "points": 3, "goal_difference": 0, "goals_for": 2, "fair_play": 1, "elo_rating": 1700, "fifa_ranking": 30},
        ]
    )
    ranked = sort_group_table(table)
    assert ranked.iloc[0]["team_id"] == "B"
    assert list(ranked["rank"]) == [1, 2, 3]


def test_sort_best_thirds_returns_strongest_third_place_rows_first():
    thirds = pd.DataFrame(
        [
            {"team_id": "A", "points": 4, "goal_difference": 0, "goals_for": 3, "fair_play": 2, "elo_rating": 1700, "fifa_ranking": 20},
            {"team_id": "B", "points": 4, "goal_difference": 1, "goals_for": 2, "fair_play": 4, "elo_rating": 1600, "fifa_ranking": 30},
            {"team_id": "C", "points": 2, "goal_difference": 3, "goals_for": 6, "fair_play": 1, "elo_rating": 1900, "fifa_ranking": 5},
        ]
    )
    ranked = sort_best_thirds(thirds)
    assert ranked.iloc[0]["team_id"] == "B"

