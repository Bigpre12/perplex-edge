import asyncio
import os
import sys
from datetime import datetime
# Add current directory to path
sys.path.append(os.getcwd())

# Mock environment if needed
if not os.getenv("THE_ODDS_API_KEY"):
    os.environ["THE_ODDS_API_KEY"] = "534f28df45cd7fc2d3af6be2d23b6315"

from services.odds_api_client import odds_api

async def test_api():
    print(f"Testing Odds API with key: {os.getenv('THE_ODDS_API_KEY')[:5]}...")
    try:
        # 1. Test Sports
        sports = await odds_api.get_active_sports()
        print(f"Active sports count: {len(sports)}")
        
        # 2. Test NBA Odds
        res = await odds_api.get_live_odds('basketball_nba')
        print(f"NBA live games: {len(res)}")
        if res:
            print(f"Sample game: {res[0].get('home_team')} vs {res[0].get('away_team')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
