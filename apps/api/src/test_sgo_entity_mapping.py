import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app_core.sgo_entity_constants import SGO_ENTITIES, get_sgo_entity_display, get_fixed_sgo_entity, is_sgo_player_entity

def test_sgo_entity_mapping():
    print("Testing SportsGameOdds Entity Mapping...")
    
    # 1. Test basic display
    print("\n--- Testing Entity Display ---")
    test_displays = [
        ("home", "Home Team"),
        ("away", "Away Team"),
        ("all", "All / Combined"),
        ("LEBRON_JAMES_LA_LAKERS", "Lebron James La Lakers"),
    ]
    for e_id, expected in test_displays:
        actual = get_sgo_entity_display(e_id)
        if actual == expected:
            print(f"SUCCESS: {e_id} -> {actual}")
        else:
            print(f"FAIL: {e_id} -> Got {actual}, Expected {expected}")

    # 2. Test Fixed Entities
    print("\n--- Testing Fixed Entities ---")
    test_fixed = [
        (("ml", "home"), "home"),
        (("ml3way", "draw"), "all"),
        (("prop", "side1"), "side1"),
    ]
    for (bt, side), expected in test_fixed:
        actual = get_fixed_sgo_entity(bt, side)
        if actual == expected:
            print(f"SUCCESS: {bt}+{side} -> {actual}")
        else:
            print(f"FAIL: {bt}+{side} -> Got {actual}, Expected {expected}")

    # 3. Test Player Detection
    print("\n--- Testing Player Detection ---")
    if is_sgo_player_entity("LEBRON_JAMES") and not is_sgo_player_entity("home"):
        print("SUCCESS: Player detection logic is correct.")
    else:
        print("FAIL: Player detection logic is incorrect.")

if __name__ == "__main__":
    test_sgo_entity_mapping()
