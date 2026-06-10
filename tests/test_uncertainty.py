import pandas as pd

from src.analytics.uncertainty import add_probability_uncertainty, confidence_interval


def test_confidence_interval_contains_probability():
    se, low, high = confidence_interval(0.12, 10000)
    assert se > 0
    assert low < 0.12 < high


def test_add_probability_uncertainty_adds_columns():
    frame = add_probability_uncertainty(pd.DataFrame({"probability": [0.5]}), ["probability"], 100)
    assert "probability_ci_low" in frame.columns
    assert "probability_ci_high" in frame.columns
    assert "simulations_used" in frame.columns

