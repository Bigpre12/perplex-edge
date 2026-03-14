import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app_core.sgo_bet_type_constants import SGO_BET_TYPES, get_sgo_bet_type_name, get_sgo_side_name

def test_sgo_bet_type_mapping():
    print("Testing SportsGameOdds Bet Type and Side Mapping...")
    
    # 1. Test bet types
    print("\n--- Testing Bet Type Display ---")
    test_types = [
        ("ml", "Moneyline"),
        ("sp", "Spread"),
        ("ou", "Over/Under"),
        ("ml3way", "3-Way Moneyline"),
    ]
    for bt_id, expected in test_types:
        actual = get_sgo_bet_type_name(bt_id)
        if actual == expected:
            print(f"SUCCESS: {bt_id} -> {actual}")
        else:
            print(f"FAIL: {bt_id} -> Got {actual}, Expected {expected}")

    # 2. Test sides
    print("\n--- Testing Side Display ---")
    test_sides = [
        ("ml", "home", "Home"),
        ("ou", "over", "Over"),
        ("ml3way", "away+draw", "Away/Draw"),
        ("prop", "side1", "Option 1"),
    ]
    for bt_id, s_id, expected in test_sides:
        actual = get_sgo_side_name(bt_id, s_id)
        if actual == expected:
            print(f"SUCCESS: {bt_id}:{s_id} -> {actual}")
        else:
            print(f"FAIL: {bt_id}:{s_id} -> Got {actual}, Expected {expected}")

    # 3. Total stats
    print(f"\nTotal SGO Bet Types Mapped: {len(SGO_BET_TYPES)}")

if __name__ == "__main__":
    test_sgo_bet_type_mapping()
