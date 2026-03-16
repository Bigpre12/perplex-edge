import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from clients.odds_client import odds_api_client
from config import settings

async def check():
    print(f"Primary key: {settings.ODDS_API_KEY_PRIMARY}")
    print(f"Backup key: {settings.ODDS_API_KEY_BACKUP}")
    print(f"All keys: {odds_api_client.api_keys}")
    
    print("\nFetching active sports...")
    try:
        sports = await odds_api_client.fetch_sports()
        print(f"Found {len(sports)} sports.")
        print("Sample keys:", [s['key'] for s in sports[:10]])
        
        # Check NBA specifically
        nba = [s for s in sports if s['key'] == 'basketball_nba']
        print(f"NBA active: {len(nba) > 0}")
        if nba:
            print(f"NBA title: {nba[0]['title']}")
            
        print("\nFetching events for NBA...")
        events = await odds_api_client.fetch_events("basketball_nba")
        print(f"NBA events found: {len(events)}")
        if events:
            print(f"Sample event: {events[0]['id']} - {events[0]['home_team']} vs {events[0]['away_team']}")
            
    except Exception as e:
        print(f"Check failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check())
