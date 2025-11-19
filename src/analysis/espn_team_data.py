"""
Utilities for loading ESPN NFL team stats (2000–2024).

Assumes JSON files created by src/api/espn_nfl.py like:
  data/espn_team_stats_2000.json
  data/espn_team_stats_2001.json
  ...
Each JSON is a list of dicts, one per team, with keys like:
  - id, name, abbrev, season
  - record: {"wins": ..., "losses": ...}
  - stats: {"offense_rushing_yards": ..., "offense_passing_yards": ...}
"""

import json
import os
import re
from glob import glob
from typing import Dict, List, Any

import pandas as pd

DATA_DIR = "data"
PATTERN = os.path.join(DATA_DIR, "espn_team_stats_*.json")

YEAR_RE = re.compile(r"espn_team_stats_(\d{4})\.json$")


def _load_one_json(path: str) -> List[Dict[str, Any]]:
    """
    Load a single espn_team_stats_YYYY.json file and return a list of flat dicts.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    rows: List[Dict[str, Any]] = []

    for team in raw:
        flat: Dict[str, Any] = {}

        flat["team_id"] = team.get("id")
        flat["team_name"] = team.get("name")
        flat["team_abbrev"] = team.get("abbrev")
        flat["season"] = team.get("season")

        rec = team.get("record") or {}
        flat["wins"] = rec.get("wins")
        flat["losses"] = rec.get("losses")

        stats = team.get("stats") or {}
        flat["offense_rushing_yards"] = stats.get("offense_rushing_yards")
        flat["offense_passing_yards"] = stats.get("offense_passing_yards")

        rows.append(flat)

    return rows


def load_all_espn_team_stats() -> pd.DataFrame:
    """
    Load all espn_team_stats_YYYY.json files into a single DataFrame.

    Returns DataFrame with columns such as:
      team_id, team_name, team_abbrev, season (as Year),
      wins, losses,
      offense_rushing_yards, offense_passing_yards
    """
    files = sorted(glob(PATTERN))
    if not files:
        raise FileNotFoundError(f"No files matched {PATTERN}")

    all_rows: List[Dict[str, Any]] = []
    for path in files:
        m = YEAR_RE.search(os.path.basename(path))
        file_year = int(m.group(1)) if m else None

        rows = _load_one_json(path)
        for r in rows:
            if not r.get("season") and file_year is not None:
                r["season"] = file_year
            all_rows.append(r)

    df = pd.DataFrame(all_rows)

    df["season"] = pd.to_numeric(df["season"], errors="coerce").astype("Int64")
    for col in ["wins", "losses", "offense_rushing_yards", "offense_passing_yards"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["games"] = df["wins"] + df["losses"]
    df["win_pct"] = df["wins"] / df["games"]

    df = df.rename(columns={"season": "Year"})

    return df


if __name__ == "__main__":
    df = load_all_espn_team_stats()
    print(df.head())
    print()
    print("Shape:", df.shape)
    print("Years:", df["Year"].dropna().unique())
