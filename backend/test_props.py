import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from real_data_connector import real_data_connector
from datetime import datetime, timezone, timedelta

async def test():
    print("Testing real data connector player props...")
    games = await real_data_connector.fetch_games_by_sport('basketball_nba')
    if games:
        print(f"Found {len(games)} games. Testing first game props...")
        for game in games[:3]:
            print(f"Testing game {game['home_team_name']} vs {game['away_team_name']} ({game['id']})")
            props = await real_data_connector.fetch_player_props('basketball_nba', game['id'], 'player_points')
            print(f"Found {len(props)} 'player_points' props.")
            
            if props:
                print(props[0])

if __name__ == "__main__":
    asyncio.run(test())
