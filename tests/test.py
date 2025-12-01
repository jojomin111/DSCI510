"""
These tests avoid calling external APIs so that they are
fast and do not depend on network access.

"""

import math

from src.scrapers.otc_rb_contracts import _clean_money, _clean_pct

try:
    from src.api.espn_nfl import _extract_yards_from_stats
    HAS_EXTRACT_HELPER = True
except ImportError:
    HAS_EXTRACT_HELPER = False


def test_clean_money_parses_dollar_strings():
    """$-formatted strings should convert to floats."""
    assert _clean_money("$1,000,000") == 1_000_000.0
    assert _clean_money("$32,700,000") == 32_700_000.0


def test_clean_money_handles_blanks_and_dashes():
    """Blank or dash-like values should return None, not crash."""
    for val in ["", "-", "—", "–", None]:
        assert _clean_money(val) is None


def test_clean_pct_parses_percentage_strings():
    """Percent strings should map to float."""
    assert math.isclose(_clean_pct("15.8%"), 15.8, rel_tol=1e-9)
    assert math.isclose(_clean_pct("0.0%"), 0.0, rel_tol=1e-9)


def test_clean_pct_handles_invalid_values():
    """Invalid or empty percentage values should return None."""
    for val in ["", "-", "—", "–", None]:
        assert _clean_pct(val) is None


def test_extract_yards_from_stats_basic():
    """
    Test the ESPN stats helper on a small fake JSON payload.

    Only runs if _extract_yards_from_stats exists in src/api/espn_nfl.py.
    """
    if not HAS_EXTRACT_HELPER:
        return

    fake_payload = {
        "splits": [
            {
                "stats": [
                    {"name": "rushingYards", "value": 1200},
                    {"name": "netPassingYards", "value": 3800},
                ]
            }
        ]
    }

    rush, pas = _extract_yards_from_stats(fake_payload)

    assert rush == 1200.0
    assert pas == 3800.0
