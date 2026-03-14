
import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "apps", "api", "src"))

async def test_waterfall():
    from real_data_connector import real_data_connector
    from services.props_service import props_service
    
    print("--- Testing Waterfall Games (NBA) ---")
    games = await real_data_connector.fetch_games_by_sport("basketball_nba")
    print(f"Found {len(games)} games")
    if games:
        print(f"First game: {games[0].get('home_team')} vs {games[0].get('away_team')} (Status: {games[0].get('status')})")
        
        game_id = games[0].get("id")
        print(f"\n--- Testing Waterfall Props for Game {game_id} ---")
        props = await real_data_connector.fetch_player_props("basketball_nba", game_id)
        print(f"Found {len(props)} props")
        if props:
            print(f"First prop: {props[0].get('player_name')} - {props[0].get('line')} {props[0].get('stat_type')}")
        else:
            print("No props found (Normal if no markets available yet)")
    else:
        print("No games found. Waterfall might be empty or API keys exhausted.")

if __name__ == "__main__":
    asyncio.run(test_waterfall())
