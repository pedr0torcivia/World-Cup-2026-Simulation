import pandas as pd

from src.simulation.injuries import calculate_player_injury_probability


def test_injury_model_uses_age_stamina_fatigue_and_climate():
    player = pd.Series({"age": 34, "stamina": 65, "injury_proneness": 0.4})
    low = calculate_player_injury_probability(player, 0.01, 60, 0.1, 1.0, 22, 55)
    high = calculate_player_injury_probability(player, 0.01, 120, 0.8, 1.5, 34, 80)
    assert high > low

