import argparse
import json
import time
from typing import Any, Dict, List, Tuple

import requests

# ESPN endpoints
TEAM_LIST_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
TEAM_RECORD_URL = (
    "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl"
    "/seasons/{season}/types/2/teams/{team_id}/record"
)
TEAM_STATS_URL = (
    "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl"
    "/seasons/{season}/types/2/teams/{team_id}/statistics"
)


def list_teams() -> List[Dict[str, str]]:
    resp = requests.get(TEAM_LIST_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    teams: List[Dict[str, str]] = []
    sport = data.get("sports", [{}])[0]
    league = sport.get("leagues", [{}])[0]

    for t in league.get("teams", []):
        team = t.get("team", {})
        teams.append(
            {
                "id": team.get("id"),
                "name": team.get("displayName"),
                "abbrev": team.get("abbreviation"),
            }
        )
    return teams


def get_record(team_id: str, season: int) -> Dict[str, int]:

    url = TEAM_RECORD_URL.format(season=season, team_id=team_id)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    d = resp.json()

    wins = losses = None

    # Typical shape:
    # {
    #   "items": [
    #     {
    #       "stats": [
    #         {"name": "wins", "value": 10},
    #         {"name": "losses", "value": 7},
    #         ...
    #       ]
    #     }
    #   ]
    # }
    for item in d.get("items", []):
        for stat in item.get("stats", []):
            name = stat.get("name")
            val = stat.get("value")
            if name == "wins":
                try:
                    wins = int(val)
                except Exception:
                    wins = None
            elif name == "losses":
                try:
                    losses = int(val)
                except Exception:
                    losses = None

    return {"wins": wins, "losses": losses}


def _extract_yards_from_stats(payload: Any) -> Tuple[float, float]:

    rushing = None
    passing = None

    def walk(obj: Any) -> None:
        nonlocal rushing, passing

        if isinstance(obj, dict):
            name = obj.get("name")
            value = obj.get("value")

            # These names are based on how ESPN typically labels team stats.
            if name in ("rushingYards", "rushingYardsNet", "teamRushingYards"):
                if isinstance(value, (int, float)):
                    rushing = float(value)

            if name in ("netPassingYards", "passingYards", "teamPassingYards"):
                if isinstance(value, (int, float)):
                    passing = float(value)

            for v in obj.values():
                walk(v)

        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(payload)
    return rushing, passing


def get_offense_yards(team_id: str, season: int) -> Dict[str, float]:

    url = TEAM_STATS_URL.format(season=season, team_id=team_id)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    stats_json = resp.json()

    rushing, passing = _extract_yards_from_stats(stats_json)

    return {
        "offense_rushing_yards": rushing,
        "offense_passing_yards": passing,
    }


def get_team_summary(team: Dict[str, str], season: int) -> Dict[str, Any]:
 
    tid = team["id"]
    out: Dict[str, Any] = {
        "id": tid,
        "name": team["name"],
        "abbrev": team["abbrev"],
        "season": season,
        "record": None,
        "stats": {},
    }

    # Record (wins/losses)
    try:
        out["record"] = get_record(tid, season)
    except Exception as e:
        out["record"] = {"wins": None, "losses": None, "error": str(e)}

    # Offense yards
    try:
        yards = get_offense_yards(tid, season)
        out["stats"].update(yards)
    except Exception as e:
        out["stats"]["error"] = str(e)

    return out


def fetch_league_team_stats(season: int, throttle: float = 0.3) -> List[Dict[str, Any]]:

    teams = list_teams()
    all_stats: List[Dict[str, Any]] = []

    for t in teams:
        if not t.get("id"):
            continue

        print(f"Fetching {t['abbrev']} ({t['id']}) for {season}...")
        all_stats.append(get_team_summary(t, season))

        # Be a bit gentle with ESPN's servers
        if throttle > 0:
            time.sleep(throttle)

    return all_stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, required=True, help="NFL season year")
    parser.add_argument(
        "--save",
        type=str,
        default="",
        help="Path to save JSON output (e.g., data/espn_team_stats_2024.json)",
    )
    args = parser.parse_args()

    data = fetch_league_team_stats(args.season)

    if args.save:
        with open(args.save, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved {len(data)} team records to {args.save}")
    else:
        # Just preview the first couple of teams
        print(json.dumps(data[:2], indent=2))


if __name__ == "__main__":
    main()
