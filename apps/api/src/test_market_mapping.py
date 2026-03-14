import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from services.sportsgameodds_client import sportsgameodds_client
from app_core.market_constants import SGO_STAT_IDS, SGO_PERIOD_IDS, get_period_display

def test_market_mapping():
    print("Testing Market Mapping...")
    
    # 1. Test Parse Logic
    test_ids = [
        "points-away-game-ml-away",
        "points-PLAYER_ID-game-ou-over",
        "threePointersMade-PLAYER_ID-game-ou-under",
        "assists-PLAYER_ID-1q-ou-over"
    ]
    
    for oid in test_ids:
        parsed = sportsgameodds_client.parse_odd_id(oid)
        if parsed:
            print(f"SUCCESS: Parsed {oid}")
            print(f"  - Stat: {parsed['stat_id']}")
            print(f"  - Entity: {parsed['stat_entity_id']}")
            print(f"  - Period: {parsed['period_id']} ({get_period_display(parsed['period_id'])})")
            print(f"  - Bet: {parsed['bet_type_id']}")
            print(f"  - Side: {parsed['side_id']}")
        else:
            print(f"FAIL: Could not parse {oid}")

    # 2. Test Stat Mappings
    if "threePointersMade" in SGO_STAT_IDS:
        print(f"SUCCESS: 'threePointersMade' mapping exists -> {SGO_STAT_IDS['threePointersMade']}")
    else:
        print("FAIL: 'threePointersMade' mapping missing")

if __name__ == "__main__":
    test_market_mapping()
