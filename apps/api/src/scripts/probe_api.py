import asyncio
import os
import json
from dotenv import load_dotenv

# MUST LOAD DOTENV BEFORE INITIALIZING THE CLIENT
load_dotenv()

from services.odds_api_client import odds_api

async def main():
    print("--- Environment Check ---")
    key = os.getenv("THE_ODDS_API_KEY")
    print(f"API Key present: {'Yes' if key else 'No'}")
    if key:
        print(f"Key starts with: {key[:5]}...")
    
    print("\n--- Probing NBA Games ---")
    nba_games = await odds_api.get_live_odds("basketball_nba")
    print(f"NBA Games Found: {len(nba_games)}")
    if nba_games:
        # Sort by time to see if anything is live
        print(f"Sample NBA Game: {nba_games[0].get('home_team')} vs {nba_games[0].get('away_team')}")
        eid = nba_games[0].get('id')
        print(f"Probing props for {eid}...")
        props = await odds_api.get_player_props("basketball_nba", eid, "player_points")
        print(f"NBA Props Found: {len(props)}")
    else:
        # Check active sports to see if it's even in season
        sports = await odds_api.get_active_sports()
        nba_active = any(s.get('key') == 'basketball_nba' for s in sports)
        print(f"Is basketball_nba in active sports? {'Yes' if nba_active else 'No'}")

    print("\n--- Probing NFL Games ---")
    nfl_games = await odds_api.get_live_odds("americanfootball_nfl")
    print(f"NFL Games Found: {len(nfl_games)}")

if __name__ == "__main__":
    asyncio.run(main())
