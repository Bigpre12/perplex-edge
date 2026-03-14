import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from services.therundown_client import therundown_client

async def test_integration():
    print("Testing Therundown Integration...")
    
    # 1. Test Client Availability
    if not therundown_client.available:
        print("FAIL: Therundown API key not found in environment.")
        return

    print(f"SUCCESS: API Key found: {therundown_client.api_key[:4]}...")

    # 2. Test Fetching NBA Games (Sport ID 4)
    print("\nTesting NBA Games Fetch (Sport ID 4)...")
    try:
        games = await therundown_client.get_games("basketball_nba")
        if games:
            print(f"SUCCESS: Fetched {len(games)} NBA games via Therundown")
            for i, g in enumerate(games[:3]):
                print(f"  - {g['away_team_name']} @ {g['home_team_name']} ({g['status']})")
        else:
            print("FAIL: No games returned or API error. Check key/plan.")
    except Exception as e:
        print(f"ERROR during fetch: {e}")

if __name__ == "__main__":
    # Ensure env is loaded
    load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
    asyncio.run(test_integration())
