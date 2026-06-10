from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class TournamentData:
    teams: object
    players: object
    fixtures: object
    venues: object
    referees: object
    config: dict
    project_root: Path

