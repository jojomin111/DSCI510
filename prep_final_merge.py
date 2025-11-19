import os
import pandas as pd

DATA_DIR = "data"

RB70_FILE = os.path.join(DATA_DIR, "rb70_stats_with_contract.csv")
OTC_FILE = os.path.join(DATA_DIR, "otc_rb_contracts_rb70.csv")

OUT_FINAL = os.path.join(DATA_DIR, "rb_analysis_master.csv")


def normalize_name(s: str) -> str:
    """Make player names lowercase stripped strings."""
    if s is None:
        return ""
    return str(s).strip().lower()


def load_rb70():
    df = pd.read_csv(RB70_FILE)
    df.columns = [c.strip() for c in df.columns]

    if "Player" not in df.columns:
        raise KeyError("The RB70 dataset must contain a 'Player' column.")

    df["player_norm"] = df["Player"].apply(normalize_name)

    return df


def load_otc():
    df = pd.read_csv(OTC_FILE)
    df.columns = [c.strip() for c in df.columns]

    candidate = [c for c in df.columns if c.lower() == "player"]
    if not candidate:
        raise KeyError("The OTC file must contain a 'Player' column.")
    player_col = candidate[0]

    df["player_norm"] = df[player_col].apply(normalize_name)

    money_cols = ["apy", "guaranteed", "total_value"]
    for c in money_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


def merge_final():
    df_rb = load_rb70()
    df_otc = load_otc()

    merged = df_rb.merge(
        df_otc,
        how="left",
        on="player_norm",
        suffixes=("", "_contract")
    )

    merged.drop(columns=["player_norm"], inplace=True, errors="ignore")

    return merged


def main():
    merged = merge_final()
    print(f"Final merged shape: {merged.shape}")

    merged.to_csv(OUT_FINAL, index=False)
    print(f"Saved final analysis dataset to:\n{OUT_FINAL}")


if __name__ == "__main__":
    main()
