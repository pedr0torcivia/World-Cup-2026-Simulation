from pathlib import Path

import pytest

from src.utils.data_loader import load_tournament_data


@pytest.fixture()
def tournament_data():
    return load_tournament_data(Path("."))

