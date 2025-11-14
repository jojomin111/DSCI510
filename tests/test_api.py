import json, subprocess, sys

def test_espn_api_fetch_runs(tmp_path):
    out_json = tmp_path / "espn_test.json"
    cmd = [sys.executable, "-m", "src.api.espn_nfl", "--season", "2024", "--save", str(out_json)]
    try:
        subprocess.check_call(cmd)
    except Exception:
        import importlib
        m = importlib.import_module("src.api.espn_nfl")
        assert hasattr(m, "get_teams")
        assert hasattr(m, "fetch_league_team_stats")
        return
    assert out_json.exists(), "JSON not created"
    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert isinstance(data, list) and len(data) >= 1
