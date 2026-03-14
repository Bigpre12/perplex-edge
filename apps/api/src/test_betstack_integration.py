import sys
import os
import asyncio
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from services.betstack_client import betstack_client
from real_sports_api import RealSportsAPI

async def test_betstack_integration():
    print("Testing Betstack API Integration...")
    
    # 1. Check client availability
    if not betstack_client.available:
        print("FAIL: Betstack API key not found in .env")
        return

    print("SUCCESS: Betstack API key found.")

    # 2. Test direct client call (Props)
    print("\nAttempting to fetch NBA props...")
    props = await betstack_client.get_player_props("nba")
    if props:
        print(f"SUCCESS: Fetched {len(props)} props.")
        print(f"Sample Prop: {json.dumps(props[0], indent=2) if len(props) > 0 else 'None'}")
    else:
        print("INFO: No props returned (Check API key permissions or active games).")

    # 3. Test integrated RealSportsAPI call
    print("\nTesting RealSportsAPI integration...")
    real_api = RealSportsAPI()
    props_integrated = await real_api.fetch_props_from_betstack("nba")
    if isinstance(props_integrated, list):
        print("SUCCESS: RealSportsAPI correctly resolved props via BetstackClient.")
    else:
        print(f"FAIL: RealSportsAPI returned error: {props_integrated}")

if __name__ == "__main__":
    asyncio.run(test_betstack_integration())
