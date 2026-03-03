import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()

from services.odds_api_client import odds_api
from real_data_connector import real_data_connector

async def test():
    games = await real_data_connector.fetch_games_by_sport('basketball_nba')
    if games:
        game_id = games[0]['id']
        raw_events = await odds_api.get_player_props('basketball_nba', game_id, markets='player_points')
        with open('raw_props.json', 'w') as f:
            json.dump(raw_events, f, indent=2)

if __name__ == "__main__":
    asyncio.run(test())
