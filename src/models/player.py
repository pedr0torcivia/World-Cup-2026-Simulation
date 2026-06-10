from dataclasses import dataclass


@dataclass(slots=True)
class Player:
    player_id: str
    player_name: str
    team_id: str
    position: str
    age: int
    overall_rating: float
    importance: float
    starter_probability: float
    stamina: float
    injury_proneness: float
    penalty_skill: float
    yellow_card_risk: float
    red_card_risk: float
    minutes_played: int
    is_injured: bool
    injury_days_remaining: int
    is_suspended: bool
    yellow_cards: int

