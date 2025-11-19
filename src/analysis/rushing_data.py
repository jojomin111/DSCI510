"""
Utilities for loading and working with NFL rushing data (2001–2024).

Assumes:
- data/rushing_cleaned.csv       (2001–2023, PFR-derived)
- data/rb_rushing_2024.csv       (your cleaned 2024 table)
"""

import os
from typing import List

import pandas as pd

DATA_DIR = "data"
HISTORICAL_FILE = os.path.join(DATA_DIR, "rushing_cleaned.csv")
R2024_FILE = os.path.join(DATA_DIR, "rb_rushing_2024.csv")


def _load_single(path: str) -> pd.DataFrame:
    """
    Load a single CSV, drop any 'Unnamed: ...' index columns, return DataFrame.
    """
    df = pd.read_csv(path)

    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    df.columns = [c.strip() for c in df.columns]

    return df


def load_all_rushing() -> pd.DataFrame:
    """
    Load rushing_cleaned (2001–2023) + 2024 file into a single DataFrame.

    Returns:
        DataFrame with columns like:
        Player, Age, G, GS, rAtt, rYds, rTD, r1D, rLng, rY/A, rY/g, Fmb, Year
    """
    frames: List[pd.DataFrame] = []

    if os.path.exists(HISTORICAL_FILE):
        frames.append(_load_single(HISTORICAL_FILE))
    else:
        raise FileNotFoundError(f"Missing {HISTORICAL_FILE}")

    if os.path.exists(R2024_FILE):
        frames.append(_load_single(R2024_FILE))
    else:
        print(f"[WARN] {R2024_FILE} not found; loading only 2001–2023.")

    full = pd.concat(frames, ignore_index=True)

    if "Year" in full.columns:
        full["Year"] = pd.to_numeric(full["Year"], errors="coerce").astype("Int64")

    for col in ["Age", "G", "GS", "rAtt", "rYds", "rTD", "r1D", "rLng", "rY/A", "rY/g", "Fmb"]:
        if col in full.columns:
            full[col] = pd.to_numeric(full[col], errors="coerce")

    return full


if __name__ == "__main__":
    df = load_all_rushing()
    print(df.head())
    print()
    print("Shape:", df.shape)
    print("Years:", df["Year"].dropna().unique())
