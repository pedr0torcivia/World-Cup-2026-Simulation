from dataclasses import dataclass, field


@dataclass(slots=True)
class MatchResult:
    match_id: str
    stage: str
    team_a: str
    team_b: str
    goals_a: int
    goals_b: int
    expected_goals_a: float
    expected_goals_b: float
    winner: str | None = None
    draw: bool = False
    went_to_extra_time: bool = False
    went_to_penalties: bool = False
    penalty_score_a: int = 0
    penalty_score_b: int = 0
    yellow_cards: dict[str, int] = field(default_factory=dict)
    red_cards: dict[str, int] = field(default_factory=dict)
    injuries: list[dict] = field(default_factory=list)
    fatigue_added: dict[str, float] = field(default_factory=dict)
    events: list[str] = field(default_factory=list)
    probability_summary: dict[str, float | str] = field(default_factory=dict)
