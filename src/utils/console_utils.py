from __future__ import annotations

import math
import unicodedata

import pandas as pd


def normalize_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(character for character in text if not unicodedata.combining(character))
    return " ".join(text.casefold().split())


def format_percentage(value: object) -> str:
    if value is None or value == "No disponible":
        return "No disponible"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "No disponible"
    if math.isnan(number):
        return "No disponible"
    return f"{number * 100:.1f}%"


def format_decimal(value: object, digits: int = 2, signed: bool = False) -> str:
    if value is None or value == "No disponible":
        return "No disponible"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "No disponible"
    if math.isnan(number):
        return "No disponible"
    sign = "+" if signed and number > 0 else ""
    return f"{sign}{number:.{digits}f}"


def safe_get(row: pd.Series | dict, column: str, default: object = "No disponible") -> object:
    if isinstance(row, pd.Series):
        if column not in row or pd.isna(row[column]):
            return default
        return row[column]
    value = row.get(column, default)
    if pd.isna(value):
        return default
    return value


def print_separator(width: int = 100) -> None:
    print("=" * width)

