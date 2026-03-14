import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app_core.sgo_sport_constants import SGO_SPORTS, get_sgo_sport_display

def test_sgo_sport_mapping():
    print("Testing SportsGameOdds Sport Mapping...")
    
    # 1. Test specific lookups
    test_cases = [
        ("MMA", "MMA"),
        ("AUSSIE_RULES_FOOTBALL", "Aussie Rules"),
        ("BASKETBALL", "Basketball"),
        ("ESPORTS", "ESports"),
    ]
    
    for s_id, expected_name in test_cases:
        name = get_sgo_sport_display(s_id)
        if name == expected_name:
            print(f"SUCCESS: {s_id} -> {name}")
        else:
            print(f"FAIL: {s_id} -> Got {name}, Expected {expected_name}")

    # 2. Total stats
    print(f"\nTotal SGO Sports Mapped: {len(SGO_SPORTS)}")

if __name__ == "__main__":
    test_sgo_sport_mapping()
