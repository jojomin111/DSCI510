"""
Scrape OverTheCap running back contract history into a CSV.

Source page:
https://overthecap.com/contract-history/running-back
"""

import argparse
import re
from typing import List

import pandas as pd
import requests

OTC_RB_CONTRACT_HISTORY_URL = "https://overthecap.com/contract-history/running-back"


def _clean_money(x: str) -> float | None:
    """
    Convert strings like '$32,700,000' to float 32700000.0.
    Return None if the value is missing or not parseable.
    """
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)

    s = str(x).strip()
    if s in ("", "-", "—", "–"):
        return None

    s = s.replace("$", "").replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def _clean_pct(x: str) -> float | None:
    """
    Convert strings like '15.8%' to float 15.8.
    """
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)

    s = str(x).strip()
    if s in ("", "-", "—", "–"):
        return None

    s = s.replace("%", "")
    try:
        return float(s)
    except ValueError:
        return None


def fetch_otc_rb_contracts() -> pd.DataFrame:
    """
    Download the OverTheCap RB contract history page and parse the table
    into a pandas DataFrame.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0 Safari/537.36"
        )
    }
    resp = requests.get(OTC_RB_CONTRACT_HISTORY_URL, headers=headers, timeout=30)
    resp.raise_for_status()

    tables: List[pd.DataFrame] = pd.read_html(resp.text)

    if not tables:
        raise RuntimeError("No tables found on OverTheCap RB contract history page.")

    df = tables[0].copy()

    df.columns = [str(c).strip() for c in df.columns]

    rename_map = {
        "Player": "player",
        "Team": "team",
        "Year Signed": "year_signed",
        "Years": "years",
        "Value": "total_value",
        "APY": "apy",
        "Guaranteed": "guaranteed",
        "APY as % Of Cap At Signing": "apy_cap_pct",
        "Inflated Value": "inflated_value",
        "Inflated APY": "inflated_apy",
        "Inflated Guaranteed": "inflated_guaranteed",
    }

    for old, new in rename_map.items():
        if old in df.columns:
            df.rename(columns={old: new}, inplace=True)

    if "player" in df.columns:
        df = df[~df["player"].isna() & (df["player"].astype(str).str.strip() != "")]

    money_cols = [
        "total_value",
        "apy",
        "guaranteed",
        "inflated_value",
        "inflated_apy",
        "inflated_guaranteed",
    ]
    for col in money_cols:
        if col in df.columns:
            df[col] = df[col].apply(_clean_money)

    if "apy_cap_pct" in df.columns:
        df["apy_cap_pct"] = df["apy_cap_pct"].apply(_clean_pct)

    for col in ("year_signed", "years"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape OverTheCap RB contract history into a CSV."
    )
    parser.add_argument(
        "--save",
        type=str,
        required=True,
        help="Output CSV path, e.g. data/otc_rb_contracts_raw.csv",
    )
    args = parser.parse_args()

    df = fetch_otc_rb_contracts()
    print(f"Fetched {len(df)} contract rows from OverTheCap.")

    df.to_csv(args.save, index=False)
    print(f"Saved to {args.save}")


if __name__ == "__main__":
    main()
