import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from services.balldontlie_client import balldontlie_client
from real_sports_api import RealSportsAPI

async def test_integration():
    print("Testing Balldontlie Integration...")
    
    # 1. Test Client Availability
    if not balldontlie_client.available:
        print("FAIL: Balldontlie API key not found in environment.")
        return

    print(f"SUCCESS: API Key found: {balldontlie_client.api_key[:5]}...")

    # 2. Test Player Search/Stats
    print("\nTesting Player Stats (LeBron James)...")
    lebron = await balldontlie_client.get_player_stats("LeBron James")
    if lebron:
        print(f"SUCCESS: Found player: {lebron['player'].get('first_name')} {lebron['player'].get('last_name')}")
        print(f"Stats (2024): {lebron.get('season_averages', {})}")
    else:
        print("FAIL: Could not fetch stats for LeBron James")

    # 3. Test Team Roster
    print("\nTesting Team Roster (Lakers)...")
    lakers_roster = await balldontlie_client.get_team_roster("Lakers")
    if lakers_roster:
        print(f"SUCCESS: Fetched {len(lakers_roster)} players for Lakers")
        for i, p in enumerate(lakers_roster[:5]):
            print(f"  - {p['player_name']} ({p['position']})")
    else:
        print("FAIL: Could not fetch roster for Lakers")

    # 4. Test RealSportsAPI Integration
    print("\nTesting RealSportsAPI.fetch_roster_data('Celtics')...")
    api = RealSportsAPI()
    celtics = await api.fetch_roster_data("Celtics")
    if celtics:
        # Check if it's mock or real (mock has "Star 1" etc)
        is_mock = any("Star" in p.get("player_name", "") for p in celtics)
        if not is_mock:
            print(f"SUCCESS: Fetched real roster data for Celtics ({len(celtics)} players)")
        else:
            print("WARNING: Fetched mock roster data for Celtics. Check API response.")
    else:
        print("FAIL: RealSportsAPI returned nothing for Celtics")

if __name__ == "__main__":
    # Ensure env is loaded
    load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
    asyncio.run(test_integration())
