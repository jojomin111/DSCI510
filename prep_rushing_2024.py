import os
import pandas as pd

RAW_PATH = "data/rb_rushing_2024_raw.csv"
OUT_PATH = "data/rb_rushing_2024.csv"


def main():
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(
            f"Expected raw 2024 file at {RAW_PATH}. "
            "Make sure you saved your pasted table there."
        )

    df = pd.read_csv(RAW_PATH)

    df = df.dropna(subset=["Player"])
    df = df[df["Player"] != "Player"]
    df = df[df["Rk"].astype(str) != "Rk"]

    df = df.rename(
        columns={
            "Att": "rAtt",
            "Yds": "rYds",
            "TD": "rTD",
            "1D": "r1D",
            "Lng": "rLng",
            "Y/A": "rY/A",
            "Y/G": "rY/g",
        }
    )

    df["Year"] = 2024
    cols = [
        "Player",
        "Age",
        "G",
        "GS",
        "rAtt",
        "rYds",
        "rTD",
        "r1D",
        "rLng",
        "rY/A",
        "rY/g",
        "Fmb",
        "Year",
    ]
    df = df[cols]

    os.makedirs("data", exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote normalized 2024 rushing file to {OUT_PATH}")
    print(f"Rows: {len(df)}")


if __name__ == "__main__":
    main()
