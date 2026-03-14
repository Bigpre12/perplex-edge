
import asyncio
import os
import sys
from datetime import datetime, timezone

# Add src to path
sys.path.append('c:/Users/preio/OneDrive/Documents/Untitled/perplex_engine/perplex-edge/apps/api/src')

try:
    from app.services.real_sports_api import real_data_connector
    from services.espn_client import espn_client
    from app.services.odds_api_client import odds_api
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def main():
    print("--- Diagnostic Script Start ---")
    
    print("\nTesting NBA Games...")
    games = await real_data_connector.get_nba_games()
    print(f"Found {len(games)} NBA games.")
    if games:
        for g in games[:2]:
            print(f"Game: {g.get('home_team_name')} vs {g.get('away_team_name')} | ID: {g.get('id') or g.get('game_id')}")
            
            game_id = g.get('id') or g.get('game_id')
            print(f"Testing Props for Game ID: {game_id}")
            props = await real_data_connector.fetch_player_props('basketball_nba', game_id)
            print(f"Found {len(props)} props for this game.")
    else:
        print("NO GAMES FOUND.")

    print("\nTesting ESPN Scoreboard directly...")
    espn_games = await espn_client.get_scoreboard('basketball_nba')
    print(f"ESPN found {len(espn_games)} games.")

    print("\nCheck Odds API Key...")
    print(f"THE_ODDS_API_KEY set: {bool(os.getenv('THE_ODDS_API_KEY'))}")

    print("--- Diagnostic Script End ---")

if __name__ == "__main__":
    asyncio.run(main())
