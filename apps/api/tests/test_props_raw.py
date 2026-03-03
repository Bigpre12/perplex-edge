import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from services.odds_api_client import odds_api
from real_data_connector import real_data_connector

async def test():
    print("Testing odds_api player props directly...")
    games = await real_data_connector.fetch_games_by_sport('basketball_nba')
    if games:
        game_id = games[0]['id']
        print(f"Fetching props for game {game_id}")
        
        # Test direct call to odds_api to see structure
        raw_events = await odds_api.get_player_props('basketball_nba', game_id, markets='player_points')
        print(f"Raw type: {type(raw_events)}")
        print(f"Raw data: {raw_events}")

if __name__ == "__main__":
    asyncio.run(test())
