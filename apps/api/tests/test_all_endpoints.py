"""
Full project endpoint verification — corrected paths.
"""
import requests
import sys

base = "http://localhost:8000"

clv_body = {
    "odds": -110, "model_probability": 0.58,
    "odds_history": [{"odds": -105, "line_value": 24.5}, {"odds": -120, "line_value": 25.5}],
    "odds_by_book": {"DraftKings": -110, "FanDuel": -105}, "public_pct": 62
}
mc_prop_body = {"mean": 25.3, "std_dev": 5.2, "line": 24.5, "side": "over", "simulations": 500, "distribution": "normal"}
mc_parlay_body = {
    "legs": [
        {"player_name": "Curry", "stat_type": "pts", "mean": 29.5, "std_dev": 6.1, "line": 28.5, "side": "over", "odds": -112},
        {"player_name": "LeBron", "stat_type": "pts", "mean": 25.8, "std_dev": 5.5, "line": 25.5, "side": "over", "odds": -108}
    ], "simulations": 500
}
bankroll_body = {
    "picks": [{"win_probability": 0.55, "odds": -110}, {"win_probability": 0.52, "odds": -105}],
    "kelly_fraction": 0.25, "initial_bankroll": 1000.0, "simulations": 200
}
kelly_body = {"win_probability": 0.55, "odds": -110}

tests = [
    ("Root",                              "GET",  "/",                                       None),
    ("Health",                            "GET",  "/health",                                 None),
    # Immediate router
    ("Immediate - Player Props",          "GET",  "/immediate/working-player-props",          None),
    ("Immediate - Brain Metrics",         "GET",  "/immediate/brain-metrics",                 None),
    ("Immediate - Brain Decisions",       "GET",  "/immediate/brain-decisions",               None),
    ("Immediate - Brain Health",          "GET",  "/immediate/brain-health-status",            None),
    ("Immediate - Brain Learning",        "GET",  "/immediate/brain-learning-events",          None),
    ("Immediate - Picks",                 "GET",  "/immediate/picks",                         None),
    ("Immediate - High EV",              "GET",  "/immediate/picks/high-ev",                 None),
    ("Immediate - Lines",                "GET",  "/immediate/lines",                         None),
    ("Immediate - Games",                "GET",  "/immediate/games",                         None),
    ("Immediate - Injuries",             "GET",  "/immediate/injuries",                      None),
    ("Immediate - Odds Snapshots",       "GET",  "/immediate/odds-snapshots",                None),
    # Validation router
    ("Validation - Picks",               "GET",  "/validation/picks",                        None),
    ("Validation - Performance",         "GET",  "/validation/performance",                  None),
    ("Validation - Track Record",        "GET",  "/validation/track-record",                 None),
    # Track Record router
    ("Track Record - Transparent",       "GET",  "/track-record/transparent",                None),
    ("Track Record - Performance",       "GET",  "/track-record/performance",                None),
    ("Track Record - Recent Picks",      "GET",  "/track-record/recent-picks",               None),
    ("Track Record - Bookmaker Perf",    "GET",  "/track-record/bookmaker-performance",      None),
    # Status router
    ("Model Status",                     "GET",  "/status/model-status",                     None),
    # Parlays router
    ("Parlays - Working",                "GET",  "/parlays/working-parlays",                 None),
    ("Parlays - MC Sim",                 "GET",  "/parlays/monte-carlo-simulation",           None),
    # Picks router
    ("Picks - Stats",                    "GET",  "/picks/stats",                             None),
    ("Picks - High EV",                  "GET",  "/picks/high-ev",                           None),
    ("Picks - Search",                   "GET",  "/picks/search?query=curry",                None),
    # Analysis router (NEW)
    ("Analysis - CLV Compute",           "POST", "/analysis/clv/compute",                    clv_body),
    ("Analysis - CLV Summary",           "GET",  "/analysis/clv/summary",                    None),
    ("Analysis - CLV Leaderboard",       "GET",  "/analysis/clv/leaderboard",                None),
    ("Analysis - MC Prop Sim",           "POST", "/analysis/monte-carlo/simulate-prop",       mc_prop_body),
    ("Analysis - MC Parlay Sim",         "POST", "/analysis/monte-carlo/simulate-parlay",     mc_parlay_body),
    ("Analysis - MC Bankroll",           "POST", "/analysis/monte-carlo/bankroll",            bankroll_body),
    ("Analysis - Kelly",                 "POST", "/analysis/kelly",                          kelly_body),
]

print("=" * 70)
print("FULL PROJECT ENDPOINT TEST")
print("=" * 70)

passed = 0
failed = 0
errors = []

for name, method, path, body in tests:
    try:
        if method == "POST" and body:
            r = requests.post(base + path, json=body, timeout=15)
        else:
            r = requests.get(base + path, timeout=15)

        status = r.status_code
        ok = status == 200

        if ok:
            passed += 1
            tag = "PASS"
        else:
            failed += 1
            err_text = r.text[:80].replace("\n", " ")
            errors.append("{}: {} - {}".format(name, status, err_text))
            tag = "FAIL"

        print("  {} [{}] {}".format(tag, status, name))
    except Exception as e:
        failed += 1
        errors.append("{}: {}".format(name, str(e)[:80]))
        print("  FAIL [ERR] {} - {}".format(name, str(e)[:50]))

print()
print("=" * 70)
print("Results: {} passed, {} failed out of {}".format(passed, failed, passed + failed))

if errors:
    print()
    print("FAILURES:")
    for e in errors:
        print("  - {}".format(e))
else:
    print()
    print("ALL ENDPOINTS WORKING - NO ERRORS!")

print("=" * 70)
sys.exit(0 if failed == 0 else 1)
