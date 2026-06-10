from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from src.models.tournament import TournamentData
from src.utils.validation import validate_tournament_data


def read_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}
    return config


def load_tournament_data(project_root: Path | str = ".") -> TournamentData:
    root = Path(project_root)
    data_dir = root / "data"
    teams = pd.read_csv(data_dir / "teams.csv")
    players = pd.read_csv(data_dir / "players.csv")
    fixtures = pd.read_csv(data_dir / "fixtures.csv")
    venues = pd.read_csv(data_dir / "venues.csv")
    referees_path = data_dir / "referees.csv"
    referees = pd.read_csv(referees_path) if referees_path.exists() else pd.DataFrame()
    config = read_config(data_dir / "config.yaml")

    validate_tournament_data(teams, players, fixtures, venues)
    return TournamentData(
        teams=teams,
        players=players,
        fixtures=fixtures,
        venues=venues,
        referees=referees,
        config=config,
        project_root=root,
    )

