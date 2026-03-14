import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app_core.bookmaker_constants import BOOKMAKERS, DFS_BOOKMAKERS, get_bookmaker_name, get_bookmaker_type

def test_bookmaker_mapping():
    print("Testing Bookmaker Mapping...")
    
    # 1. Test specific lookups
    test_cases = [
        ("draftkings", "Draft Kings", "sportsbook"),
        ("prizepicks", "PrizePicks", "dfs"),
        ("kalshi", "Kalshi", "exchange"),
        ("underdog", "Underdog Fantasy", "dfs"),
    ]
    
    for b_id, expected_name, expected_type in test_cases:
        name = get_bookmaker_name(b_id)
        b_type = get_bookmaker_type(b_id)
        if name == expected_name and b_type == expected_type:
            print(f"SUCCESS: {b_id} -> {name} ({b_type})")
        else:
            print(f"FAIL: {b_id} -> Got {name} ({b_type}), Expected {expected_name} ({expected_type})")

    # 2. Test DFS Set
    expected_dfs = {"prizepicks", "underdog", "sleeper", "parlayplay", "hotstreak"}
    actual_dfs = DFS_BOOKMAKERS
    
    missing = expected_dfs - actual_dfs
    if not missing:
        print(f"SUCCESS: DFS set contains all expected platforms. Total DFS: {len(actual_dfs)}")
    else:
        print(f"FAIL: DFS set missing: {missing}")

    # 3. Total stats
    print(f"\nTotal Bookmakers Mapped: {len(BOOKMAKERS)}")

if __name__ == "__main__":
    test_bookmaker_mapping()
