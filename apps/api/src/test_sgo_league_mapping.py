import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app_core.sgo_league_constants import SGO_LEAGUES, get_sgo_league_name, get_sgo_league_sport

def test_sgo_league_mapping():
    print("Testing SportsGameOdds League Mapping...")
    
    # 1. Test specific lookups
    test_cases = [
        ("UFC", "UFC", "MMA"),
        ("NBA", "NBA", "BASKETBALL"),
        ("EPL", "Premier League", "SOCCER"),
        ("UEFA_CHAMPIONS_LEAGUE", "Champions League", "SOCCER"),
        ("NCAAB", "College Basketball", "BASKETBALL"),
    ]
    
    for l_id, expected_name, expected_sport in test_cases:
        name = get_sgo_league_name(l_id)
        sport = get_sgo_league_sport(l_id)
        if name == expected_name and sport == expected_sport:
            print(f"SUCCESS: {l_id} -> {name} ({sport})")
        else:
            print(f"FAIL: {l_id} -> Got {name} ({sport}), Expected {expected_name} ({expected_sport})")

    # 2. Total stats
    print(f"\nTotal SGO Leagues Mapped: {len(SGO_LEAGUES)}")

if __name__ == "__main__":
    test_sgo_league_mapping()
