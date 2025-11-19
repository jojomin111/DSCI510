"""
PLANNED Scraper for Pro-Football-Reference yearly rushing stats. This was NOT used due to the fact that PFR has bot and bulk blockers. I had utilized manual copy and paste and csv cleaning as seen in prep_rushin_2024.py

"""

import csv
import time
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

PFR_RUSHING_URL = "https://www.pro-football-reference.com/years/{season}/rushing.htm"


def _clean_number(value: str):
    if value is None:
        return None
    s = value.strip()
    if s == "" or s == "--":
        return None
    s = s.replace(",", "")
    try:
        if "." in s:
            return float(s)
        return int(s)
    except Exception:
        return None


def fetch_rushing_html(season: int) -> str:
    """
    Download the raw HTML for the given season's rushing stats page.

    NOTE: If Pro-Football-Reference returns 403 (forbidden), this will raise
    a clear error telling you to download the data manually instead of scraping.
    """
    url = PFR_RUSHING_URL.format(season=season)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    resp = requests.get(url, headers=headers, timeout=30)

    if resp.status_code == 403:
        raise RuntimeError(
            f"PFR returned 403 Forbidden for {url}. "
            "They are blocking automated requests. "
            "Please use the browser 'Get table as CSV' export and load that file locally."
        )

    resp.raise_for_status()
    time.sleep(1.0)
    return resp.text


def parse_rushing_table(html: str, season: int) -> List[Dict]:

    soup = BeautifulSoup(html, "lxml")

    table = soup.find("table", id="rushing")
    if table is None:
        for tbl in soup.find_all("table"):
            tid = tbl.get("id", "")
            if "rushing" in tid:
                table = tbl
                break
    if table is None:
        raise RuntimeError("Could not find rushing table on PFR page")

    thead = table.find("thead")
    header_row = thead.find_all("tr")[-1]
    headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

    tbody = table.find("tbody")
    rows: List[Dict] = []

    for tr in tbody.find_all("tr"):
        if "class" in tr.attrs and "thead" in tr["class"]:
            continue

        cells = tr.find_all(["th", "td"])
        if not cells:
            continue

        values = [c.get_text(strip=True) for c in cells]

        if values[0] == "Player" or values[0] == "":
            continue

        row_dict = dict(zip(headers, values))
        row_dict["Season"] = season
        rows.append(row_dict)

    numeric_cols = [
        "Age", "G", "GS",
        "Att", "Yds", "TD", "Y/A", "Y/G",
        "Rec", "Yds.1", "Y/R",
        "Y/Tch", "YScm", "RRTD", "Fmb"
    ]

    for row in rows:
        for col in numeric_cols:
            if col in row:
                row[col] = _clean_number(row[col])

    return rows


def fetch_rushing_stats(season: int) -> List[Dict]:
    html = fetch_rushing_html(season)
    return parse_rushing_table(html, season)


def save_rushing_csv(records: List[Dict], season: int, path: str) -> None:
    if not records:
        raise ValueError(f"No records to save for season {season}")

    fieldnames = list(records[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)


if __name__ == "__main__":
    test_season = 2023
    data = fetch_rushing_stats(test_season)
    print(f"Fetched {len(data)} player records for {test_season}")
