import os
from typing import Tuple

import pandas as pd

DATA_DIR = "data"
HISTORICAL_FILE = os.path.join(DATA_DIR, "rushing_cleaned.csv")   # 2001–2023
R2024_FILE = os.path.join(DATA_DIR, "rb_rushing_2024.csv")        # 2024

OUT_FULL = os.path.join(DATA_DIR, "rb_rushing_2001_2024_full.csv")
OUT_FILTERED = os.path.join(DATA_DIR, "rb_rushing_2001_2024_rb70.csv")
OUT_NAMES = os.path.join(DATA_DIR, "rb_rushing_2001_2024_rb70_names.csv")


def _load_csv(path: str) -> pd.DataFrame:
    """Load a CSV and drop any Unnamed index columns."""
    df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    df.columns = [c.strip() for c in df.columns]  # strip spaces
    return df


def _detect_attempts_column(df: pd.DataFrame) -> str:
    """
    Detect the rushing attempts column name.
    Prefer 'rAtt' (your cleaned schema), but fall back to 'Att' if needed.
    """
    if "rAtt" in df.columns:
        return "rAtt"
    if "Att" in df.columns:
        return "Att"
    raise KeyError("Could not find a rushing attempts column ('rAtt' or 'Att').")


def load_and_merge_rushing() -> pd.DataFrame:
    """
    Load rushing_cleaned.csv (2001–2023) and rb_rushing_2024.csv,
    merge into a single DataFrame, and standardize basic types.
    """
    if not os.path.exists(HISTORICAL_FILE):
        raise FileNotFoundError(f"Missing {HISTORICAL_FILE}")
    if not os.path.exists(R2024_FILE):
        raise FileNotFoundError(f"Missing {R2024_FILE}")

    df_hist = _load_csv(HISTORICAL_FILE)
    df_2024 = _load_csv(R2024_FILE)

    # Concatenate
    full = pd.concat([df_hist, df_2024], ignore_index=True)

    # Ensure Year is numeric
    if "Year" in full.columns:
        full["Year"] = pd.to_numeric(full["Year"], errors="coerce").astype("Int64")

    # Standardize obvious numeric columns if present
    numeric_cols = ["Age", "G", "GS", "rAtt", "Att",
                    "rYds", "rTD", "r1D", "rLng", "rY/A", "rY/g", "Fmb"]
    for col in numeric_cols:
        if col in full.columns:
            full[col] = pd.to_numeric(full[col], errors="coerce")

    return full


def filter_rb_70_plus(full: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    From the combined table, return:
      - filtered DataFrame: only RBs (if Pos column exists) and 70+ rushing attempts
      - names DataFrame: unique Player-Year pairs for those RBs (for OverTheCap work)

    If 'Pos' is not present, we assume the dataset is already RB-only.
    """
    df = full.copy()

    # Filter by position if available
    if "Pos" in df.columns:
        df = df[df["Pos"] == "RB"]

    # Filter by attempts (>= 70)
    att_col = _detect_attempts_column(df)
    df = df[df[att_col] >= 70]

    # Build names list for OverTheCap (Player + Year)
    if "Year" in df.columns:
        names_df = (
            df[["Player", "Year"]]
            .dropna()
            .drop_duplicates()
            .sort_values(["Year", "Player"])
            .reset_index(drop=True)
        )
    else:
        # Fallback: just unique names
        names_df = (
            df[["Player"]]
            .dropna()
            .drop_duplicates()
            .sort_values("Player")
            .reset_index(drop=True)
        )

    return df, names_df


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print("Loading and merging rushing data (2001–2024)...")
    full = load_and_merge_rushing()
    print(f"Combined shape: {full.shape}")

    # Save full merged table
    full.to_csv(OUT_FULL, index=False)
    print(f"Saved full merged dataset to {OUT_FULL}")

    print("Filtering to RBs with >= 70 rushing attempts...")
    filtered_df, names_df = filter_rb_70_plus(full)

    filtered_df.to_csv(OUT_FILTERED, index=False)
    print(f"Saved filtered RB >=70 dataset to {OUT_FILTERED}")
    print(f"Filtered shape: {filtered_df.shape}")

    names_df.to_csv(OUT_NAMES, index=False)
    print(f"Saved OverTheCap names list to {OUT_NAMES}")
    print(f"Names rows: {names_df.shape[0]}")


if __name__ == "__main__":
    main()
