import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from real_data_connector import real_data_connector
from datetime import datetime, timezone, timedelta

async def test():
    print("Testing real data connector...")
    games = await real_data_connector.fetch_games_by_sport('basketball_nba')
    if games:
        print(f"Success! Got {len(games)} games from real_data_connector.")
        print(games[0])
        now = datetime.now(timezone.utc)
        slate_limit = now + timedelta(hours=48)
        active_slate = [g for g in games if g["start_time"] <= slate_limit]
        print(f"Active slate length: {len(active_slate)}")
    else:
        print("Failed or empty list.")

if __name__ == "__main__":
    asyncio.run(test())
