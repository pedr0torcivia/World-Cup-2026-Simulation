from __future__ import annotations

from pathlib import Path

import pandas as pd


def save_champion_chart(champion_probabilities: pd.DataFrame, output_path: Path) -> None:
    import matplotlib.pyplot as plt

    top = champion_probabilities.head(10).sort_values("probability")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(top["team"], top["probability"])
    ax.set_xlabel("Probability")
    ax.set_title("Top champion probabilities")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)

