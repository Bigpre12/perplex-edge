import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from services.thesportsdb_client import thesportsdb_client

async def test_integration():
    print("Testing TheSportsDB Integration...")
    
    # 1. Test Client key
    if not thesportsdb_client.api_key or thesportsdb_client.api_key == "1":
        print(f"WARNING: API Key is still default or not found: {thesportsdb_client.api_key}")
    else:
        print(f"SUCCESS: API Key found: {thesportsdb_client.api_key}")

    # 2. Test Search Teams (Arsenal)
    print("\nTesting Team Search (Arsenal)...")
    try:
        teams = await thesportsdb_client.search_teams("Arsenal")
        if teams:
            print(f"SUCCESS: Found {len(teams)} teams matching 'Arsenal'")
            for team in teams[:3]:
                print(f"  - {team.get('strTeam')} ({team.get('strLeague')})")
        else:
            print("FAIL: No teams returned or API error.")
    except Exception as e:
        print(f"ERROR during team search: {e}")

    # 3. Test Lookup Event (2052711)
    event_id = "2052711"
    print(f"\nTesting Event Lookup (ID {event_id})...")
    try:
        event = await thesportsdb_client.lookup_event(event_id)
        if event:
            print(f"SUCCESS: Found event: {event.get('strEvent')}")
            print(f"  - Date: {event.get('dateEvent')}")
            print(f"  - Teams: {event.get('strHomeTeam')} vs {event.get('strAwayTeam')}")
        else:
            print(f"FAIL: Event {event_id} not found or API error.")
    except Exception as e:
        print(f"ERROR during event lookup: {e}")

if __name__ == "__main__":
    # Ensure env is loaded
    load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
    asyncio.run(test_integration())
