import os
from typing import Set

import pandas as pd

DATA_DIR = "data"

NAMES_FILE = os.path.join(DATA_DIR, "rb_rushing_2001_2024_rb70_names.csv")
OTC_RAW_FILE = os.path.join(DATA_DIR, "otc_rb_contracts_raw.csv")

OTC_FILTERED_FILE = os.path.join(DATA_DIR, "otc_rb_contracts_rb70.csv")


def _normalize_name(s: str) -> str:
    if s is None:
        return ""
    return str(s).strip().lower()


def load_rb70_name_set() -> Set[str]:
    if not os.path.exists(NAMES_FILE):
        raise FileNotFoundError(f"Missing {NAMES_FILE}")

    df = pd.read_csv(NAMES_FILE)
    if "Player" not in df.columns:
        raise KeyError(f"'Player' column not found in {NAMES_FILE}")

    names = {_normalize_name(p) for p in df["Player"].dropna().unique()}
    print(f"Loaded {len(names)} unique RB names from {NAMES_FILE}")
    return names


def filter_otc_for_rb70() -> pd.DataFrame:
    if not os.path.exists(OTC_RAW_FILE):
        raise FileNotFoundError(f"Missing {OTC_RAW_FILE}")

    names = load_rb70_name_set()

    df = pd.read_csv(OTC_RAW_FILE)

    candidate_cols = [c for c in df.columns if c.lower() == "player"]
    if not candidate_cols:
        raise KeyError("Could not find a 'player' column in OverTheCap data.")
    player_col = candidate_cols[0]

    df["player_norm"] = df[player_col].apply(_normalize_name)

    before = len(df)
    df_filtered = df[df["player_norm"].isin(names)].copy()
    after = len(df_filtered)

    print(f"Filtered OverTheCap contracts: {before} -> {after} rows")

    df_filtered.drop(columns=["player_norm"], inplace=True)

    return df_filtered


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    df_filtered = filter_otc_for_rb70()
    df_filtered.to_csv(OTC_FILTERED_FILE, index=False)
    print(f"Saved filtered RB70 contracts to {OTC_FILTERED_FILE}")


if __name__ == "__main__":
    main()
