import asyncio
from app.services.real_sports_api import real_data_connector

async def debug_games():
    games = await real_data_connector.get_nba_games()
    print(f"Games found: {len(games)}")
    for g in games:
        print(f"ID: {g.get('id') or g.get('game_id')}")
        print(f"  Home: {g.get('home_team') or g.get('home_team_name')}")
        print(f"  Away: {g.get('away_team') or g.get('away_team_name')}")

if __name__ == "__main__":
    asyncio.run(debug_games())
