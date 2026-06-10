from src.simulation.fatigue import calculate_match_fatigue, fatigue_performance_modifier, recover_fatigue


def test_fatigue_performance_modifier_declines_with_fatigue():
    assert fatigue_performance_modifier(0.8) < fatigue_performance_modifier(0.1)


def test_recover_fatigue_clamps_to_zero():
    assert recover_fatigue(0.2, days_rest=10, recovery_per_day=0.1) == 0.0


def test_hot_humid_extra_time_increases_fatigue():
    mild = calculate_match_fatigue(90, 0.2, 22, 55, 0.5)
    stressful = calculate_match_fatigue(120, 0.7, 33, 78, 0.8)
    assert stressful > mild

