from dataclasses import dataclass


@dataclass(slots=True)
class Venue:
    venue_id: str
    venue_name: str
    city: str
    country: str
    altitude: float
    expected_temperature: float
    expected_humidity: float
    travel_difficulty: float
    home_team_bonus: float

