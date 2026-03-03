import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))
load_dotenv()

async def inspect():
    import httpx
    api_key = "b94144c89048238eff1856d83c383d9a"
    
    # 1. Get Events
    print("--- Fetching NBA Events ---")
    events_url = "https://api.the-odds-api.com/v4/sports/basketball_nba/events"
    async with httpx.AsyncClient() as client:
        r = await client.get(events_url, params={"apiKey": api_key})
        if r.status_code != 200:
            print(f"Failed to fetch events: {r.text}")
            return
        events = r.json()
        if not events:
            print("No active NBA events found.")
            return
        
        event_id = events[0]['id']
        print(f"Found event: {events[0]['home_team']} vs {events[0]['away_team']} (ID: {event_id})")

        # 2. Get Markets for this event
        print(f"--- Fetching ALL Markets for Event {event_id} ---")
        # To see all, we can try a few standard ones or look at documentation
        # But we really want to know what this KEY can do.
        odds_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/events/{event_id}/odds"
        r = await client.get(odds_url, params={
            "apiKey": api_key,
            "regions": "us",
            "markets": "h2h,player_points,player_rebounds", # Try mix
            "oddsFormat": "american"
        })
        print(f"Status: {r.status_code}")
        print(f"Body: {r.text}")

if __name__ == "__main__":
    asyncio.run(inspect())
