from dataclasses import dataclass


@dataclass(slots=True)
class Team:
    team_id: str
    team_name: str
    confederation: str
    group: str
    fifa_ranking: int
    elo_rating: float
    attack_rating: float
    defense_rating: float
    midfield_rating: float
    goalkeeper_rating: float
    squad_depth: float
    recent_form: float
    experience: float
    penalty_rating: float
    discipline_rating: float
    pressing_intensity: float
    tactical_style: str
    home_advantage: float
    travel_fatigue_base: float

