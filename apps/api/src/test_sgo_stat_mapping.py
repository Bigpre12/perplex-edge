import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app_core.sgo_stat_constants import SGO_STATS, get_sgo_stat_display

def test_sgo_stat_mapping():
    print("Testing SportsGameOdds Stat Mapping...")
    
    # 1. Test points mapping (The special one)
    test_points = [
        ("BASEBALL", "Runs"),
        ("SOCCER", "Goals"),
        ("GOLF", "To Par"),
        ("TENNIS", "Sets"),
        ("MMA", "Fight Winner"),
    ]
    
    print("\n--- Testing 'points' statID ---")
    for sport, expected in test_points:
        actual = get_sgo_stat_display(sport, "points")
        if actual == expected:
            print(f"SUCCESS: {sport} points -> {actual}")
        else:
            print(f"FAIL: {sport} points -> Got {actual}, Expected {expected}")

    # 2. Test sport-specific stats
    test_specifics = [
        ("BASKETBALL", "threePointersMade", "Three Pointers Made"),
        ("FOOTBALL", "passing_yards", "Passing Yards"),
        ("HOCKEY", "goalie_saves", "Saves"),
        ("MMA", "significant_strikes", "Significant Strikes"),
        ("SOCCER", "yellowCards", "Yellow Cards"),
    ]
    
    print("\n--- Testing Sport-Specific statIDs ---")
    for sport, stat, expected in test_specifics:
        actual = get_sgo_stat_display(sport, stat)
        if actual == expected:
            print(f"SUCCESS: {sport} {stat} -> {actual}")
        else:
            print(f"FAIL: {sport} {stat} -> Got {actual}, Expected {expected}")

    # 3. Total stats
    total_stats = sum(len(stats) for stats in SGO_STATS.values())
    print(f"\nTotal SGO Stats Mapped: {total_stats}")

if __name__ == "__main__":
    test_sgo_stat_mapping()
