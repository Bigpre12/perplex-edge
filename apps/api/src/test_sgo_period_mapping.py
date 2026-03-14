import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app_core.sgo_period_constants import SGO_PERIODS, get_sgo_period_display, is_deprecated_period

def test_sgo_period_mapping():
    print("Testing SportsGameOdds Period Mapping...")
    
    # 1. Test basic segments
    print("\n--- Testing Segment Display ---")
    test_cases = [
        ("game", "Full Event"),
        ("1h", "1st Half"),
        ("1q", "1st Quarter"),
        ("1ix3", "1st 3 Innings"),
        ("1rx2", "1st 2 Rounds"),
        ("reg", "Regulation"),
    ]
    
    for p_id, expected in test_cases:
        actual = get_sgo_period_display(p_id)
        if actual == expected:
            print(f"SUCCESS: {p_id} -> {actual}")
        else:
            print(f"FAIL: {p_id} -> Got {actual}, Expected {expected}")

    # 2. Test Deprecation
    print("\n--- Testing Deprecation ---")
    if is_deprecated_period("1ix5"):
        print("SUCCESS: '1ix5' is correctly flagged as deprecated.")
    else:
        print("FAIL: '1ix5' not flagged as deprecated.")

    # 3. Total stats
    print(f"\nTotal SGO Periods Mapped: {len(SGO_PERIODS)}")

if __name__ == "__main__":
    test_sgo_period_mapping()
