import argparse, json, time, requests
from typing import Dict, List

ESPN_TEAMS_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
ESPN_TEAM_DETAIL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}"

def get_teams() -> List[Dict]:
    """Return list of NFL teams with ids and display info."""
    resp = requests.get(ESPN_TEAMS_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("sports", [])[0].get("leagues", [])[0].get("teams", [])

def get_team_stats(team_id: str, season: int) -> Dict:
    """Get team detail (including stats) for a given season."""
    url = f"{ESPN_TEAM_DETAIL.format(team_id=team_id)}?enable=stats&season={season}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    d = resp.json()
    out = {
        "id": d.get("team", {}).get("id"),
        "name": d.get("team", {}).get("displayName"),
        "abbrev": d.get("team", {}).get("abbreviation"),
        "season": season,
        "record": None,
        "stats": {}
    }
    rec = d.get("team", {}).get("record", {}).get("items", [])
    if rec:
        summary = rec[0].get("summary", "")
        if "-" in summary:
            try:
                wins, losses = summary.split("-")[:2]
                out["record"] = {"wins": int(wins), "losses": int(losses)}
            except Exception:
                out["record"] = {"wins": None, "losses": None}

    for c in d.get("team", {}).get("teamStats", {}).get("splits", []):
        for stat in c.get("stats", []):
            name, val = stat.get("name"), stat.get("value")
            if name:
                out["stats"][name] = val
    return out

def fetch_league_team_stats(season: int, throttle: float = 1.0):
    teams = get_teams()
    all_stats = []
    for t in teams:
        tid = t.get("team", {}).get("id")
        if tid:
            try:
                all_stats.append(get_team_stats(tid, season))
                time.sleep(throttle)
            except Exception as e:
                all_stats.append({"id": tid, "season": season, "error": str(e)})
    return all_stats

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--save", type=str, default="")
    args = parser.parse_args()

    data = fetch_league_team_stats(args.season)
    if args.save:
        with open(args.save, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved {len(data)} records to {args.save}")
    else:
        print(json.dumps(data[:2], indent=2))

if __name__ == "__main__":
    main()
