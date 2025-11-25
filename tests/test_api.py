"""
Basic tests for the NFL Running Back Value.

1. The ESPN team stats API returns data in the expected format.
2. The OverTheCap RB contract scraper returns a non-empty DataFrame
   with the expected cleaned columns.
3. The money/percentage cleaning helper functions behave as expected.

Activate your virtual environment, then from the project root run:

    pytest

or,

    python -m pytest
"""

from typing import Any, Dict, List

import pandas as pd

from src.api.espn_nfl import fetch_league_team_stats
from src.scrapers.otc_rb_contracts import (
    fetch_otc_rb_contracts,
    _clean_money,
    _clean_pct,
)


def test_clean_money_basic() -> None:
    """_clean_money should convert '$1,234,567' to 1234567.0 and handle blanks."""
    assert _clean_money("$1,234,567") == 1234567.0
    assert _clean_money(" $250 ") == 250.0
    assert _clean_money("-") is None
    assert _clean_money("—") is None
    assert _clean_money("") is None


def test_clean_pct_basic() -> None:
    """_clean_pct should convert '15.8%' to 15.8 and handle blanks."""
    assert _clean_pct("15.8%") == 15.8
    assert _clean_pct(" 3.0 % ") == 3.0
    assert _clean_pct("-") is None
    assert _clean_pct("") is None


def test_otc_contracts_structure() -> None:
    """
    OverTheCap RB contract scraper should return a non-empty DataFrame
    with the expected key columns and numeric types.
    """
    df: pd.DataFrame = fetch_otc_rb_contracts()

    # Basic shape check
    assert not df.empty, "OverTheCap contracts DataFrame is unexpectedly empty."

    # Required columns
    required_cols = {
        "player",
        "team",
        "year_signed",
        "years",
        "total_value",
        "apy",
        "guaranteed",
        "apy_cap_pct",
        "inflated_value",
        "inflated_apy",
        "inflated_guaranteed",
    }
    missing = required_cols.difference(df.columns)
    assert not missing, f"Missing expected columns from OverTheCap data: {missing}"

    # Spot check numeric columns are numeric (float or int)
    for col in [
        "total_value",
        "apy",
        "guaranteed",
        "inflated_value",
        "inflated_apy",
        "inflated_guaranteed",
        "year_signed",
        "years",
        "apy_cap_pct",
    ]:
        assert df[col].dtype.kind in "fi", f"Column {col} is not numeric."


def test_espn_fetch_league_team_stats() -> None:
    """
    ESPN team stats fetcher should return ~32 records with
    basic fields present for each team.
    """
    season = 2024
    data: List[Dict[str, Any]] = fetch_league_team_stats(season, throttle=0.0)

    # There should be at least 30 records (32 teams in the NFL).
    assert len(data) >= 30, f"Expected at least 30 teams, got {len(data)}."

    # Check the structure of the first record
    first = data[0]
    for key in ("id", "name", "abbrev", "season", "record", "stats"):
        assert key in first, f"Key '{key}' missing from ESPN team stats record."

    # Season field should match what we requested
    assert first["season"] == season
