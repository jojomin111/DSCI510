import os
import pandas as pd

DATA_DIR = "data"

HIST = os.path.join(DATA_DIR, "rushing_cleaned.csv")
R2024 = os.path.join(DATA_DIR, "rb_rushing_2024.csv")
OUT_RB70 = os.path.join(DATA_DIR, "rb_rushing_2001_2024_rb70.csv")
OUT_NAMES = os.path.join(DATA_DIR, "rb_rushing_2001_2024_rb70_names.csv")


def normalize_name(s: str) -> str:
    if s is None:
        return ""
    return str(s).strip().lower()


def detect_attempts_column(df):
    """Return which column stores rushing attempts."""
    for c in ["rAtt", "Att", "ATT"]:
        if c in df.columns:
            return c
    raise KeyError("No rushing attempts column found (rAtt or Att).")


def load_and_combine():
    df_hist = pd.read_csv(HIST)
    df_2024 = pd.read_csv(R2024)

    for df in (df_hist, df_2024):
        df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")], inplace=True)

    if "Team" not in df_hist.columns:
        raise KeyError("Team column missing from rushing_cleaned.csv")

    if "Team" not in df_2024.columns:
        raise KeyError("Team column missing from rb_rushing_2024.csv")

    df = pd.concat([df_hist, df_2024], ignore_index=True)

    df["player_norm"] = df["Player"].apply(normalize_name)
    df["Team"] = df["Team"].astype(str).str.upper().str.strip()

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")

    return df


def filter_rb70(df):
    """Filter RBs with >= 70 rushing attempts."""

    if "Pos" in df.columns:
        df = df[df["Pos"] == "RB"]

    att_col = detect_attempts_column(df)
    df = df[df[att_col] >= 70]

    names = (
        df[["Player", "Year"]]
        .dropna()
        .drop_duplicates()
        .sort_values(["Year", "Player"])
        .reset_index(drop=True)
    )

    return df, names


def main():
    print("Loading rushing datasets...")
    df = load_and_combine()
    print(f"Combined shape: {df.shape}")

    print("Filtering to RBs >=70 carries...")
    rb70, names = filter_rb70(df)
    print(f"RB70 shape: {rb70.shape}")

    rb70.to_csv(OUT_RB70, index=False)
    names.to_csv(OUT_NAMES, index=False)

    print(f"Saved RB70 dataset: {OUT_RB70}")
    print(f"Saved RB70 names list: {OUT_NAMES}")


if __name__ == "__main__":
    main()
