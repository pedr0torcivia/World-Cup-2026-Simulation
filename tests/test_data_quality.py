from src.analytics.data_quality import build_data_quality_report


def test_data_quality_reports_player_fallback_warning(tournament_data):
    report = build_data_quality_report(tournament_data.teams, tournament_data.players, tournament_data.venues)
    assert not report.empty
    assert report["team_data_quality_score"].between(0.0, 1.0).all()
    assert report["warning"].str.contains("player-level data missing").any()

