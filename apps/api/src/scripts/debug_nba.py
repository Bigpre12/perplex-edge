import asyncio, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv; load_dotenv()
from services.odds.the_odds_client import fetch_odds
from datetime import datetime, timezone

async def debug_events():
    events = await fetch_odds("/sports/basketball_nba/events")
    if not events:
        print("No events found for basketball_nba")
        return
    
    print(f"Found {len(events)} events")
    now = datetime.now(timezone.utc)
    for e in events[:5]:
        start_time = datetime.fromisoformat(e['commence_time'].replace('Z', '+00:00'))
        diff = (start_time - now).total_seconds()
        print(f"Game: {e['home_team']} vs {e['away_team']} | Start: {e['commence_time']} | Diff: {diff/3600:.1f} hours")

if __name__ == "__main__":
    asyncio.run(debug_events())
