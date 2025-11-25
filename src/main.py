"""
Main entrypoint for the NFL Running Back Value project.

This script ties together the main data collection pieces:

1. Fetch NFL team stats from the ESPN API for a given season.
2. Scrape RB contract history from OverTheCap.
3. Optionally save both datasets into the data/ directory.

"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.api.espn_nfl import fetch_league_team_stats
from src.scrapers.otc_rb_contracts import fetch_otc_rb_contracts

DEFAULT_SEASON = 2024  # default season if none selected


def run_pipeline(season: int, save_espn: str | None, save_otc: str | None) -> None:
    """
    Run the basic data collection:

    """

    print(f"Running data pipeline for season {season}")

    # --- 1) ESPN team stats ---
    print("[1/2] Fetching NFL team stats from ESPN")
    team_stats: List[Dict[str, Any]] = fetch_league_team_stats(season, throttle=0.0)
    print(f"  Retrieved stats for {len(team_stats)} teams.")

    if save_espn:
        save_path = Path(save_espn)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with save_path.open("w", encoding="utf-8") as f:
            json.dump(team_stats, f, indent=2)
        print(f"  Saved ESPN team stats to {save_path}")

    # --- 2) OverTheCap RB contracts ---
    print("[2/2] Scraping RB contract history from OverTheCap")
    otc_df: pd.DataFrame = fetch_otc_rb_contracts()
    print(f"  Retrieved {len(otc_df)} RB contract rows.")

    if save_otc:
        save_path = Path(save_otc)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        otc_df.to_csv(save_path, index=False)
        print(f"  Saved OverTheCap contracts to {save_path}")

    print("=== Pipeline complete ===")


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for the main pipeline.

    Returns:
        argparse.Namespace with attributes:
        - season (int)
        - save_espn (str | None)
        - save_otc (str | None)
    """
    parser = argparse.ArgumentParser(
        description="Run the NFL RB Value data pipeline "
                    "(ESPN team stats + OverTheCap RB contracts)."
    )
    parser.add_argument(
        "--season",
        type=int,
        default=DEFAULT_SEASON,
        help=f"NFL season year to fetch from ESPN (default: {DEFAULT_SEASON}).",
    )
    parser.add_argument(
        "--save-espn",
        type=str,
        default="",
        help="Optional path to save ESPN team stats JSON "
             '(e.g. "data/espn_team_stats_2024.json").',
    )
    parser.add_argument(
        "--save-otc",
        type=str,
        default="",
        help="Optional path to save OverTheCap RB contract CSV "
             '(e.g. "data/otc_rb_contracts_raw.csv").',
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    save_espn = args.save_espn or None
    save_otc = args.save_otc or None
    run_pipeline(args.season, save_espn, save_otc)
