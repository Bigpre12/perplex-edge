"""
Standalone test for NBA Stats API - no heavy dependencies
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleNBAStatsAPI:
    """Simple version without heavy imports"""
    
    def __init__(self):
        self.base_url = "https://stats.nba.com/stats"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://stats.nba.com/",
        }
    
    async def fetch_player_game_stats(self, player_name: str, game_date: str):
        """Fetch player stats for a specific game."""
        try:
            player_id = await self._get_player_id(player_name)
            if not player_id:
                logger.error(f"Could not find player ID for {player_name}")
                return None
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/playergamelogs",
                    params={
                        "PlayerID": player_id,
                        "Season": "2025-26",
                        "SeasonType": "Regular Season"
                    },
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                result_sets = data.get("resultSets", [])
                if not result_sets:
                    return None
                
                game_logs = result_sets[0].get("rowSet", [])
                headers = result_sets[0].get("headers", [])
                
                for game in game_logs:
                    game_dict = dict(zip(headers, game))
                    if game_date in str(game_dict.get("GAME_DATE", "")):
                        return {
                            "player_id": player_id,
                            "player_name": player_name,
                            "game_date": game_dict.get("GAME_DATE"),
                            "pts": game_dict.get("PTS", 0),
                            "reb": game_dict.get("REB", 0),
                            "ast": game_dict.get("AST", 0),
                            "min": game_dict.get("MIN", 0),
                        }
                
                logger.warning(f"No game found for {player_name} on {game_date}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return None
    
    async def _get_player_id(self, player_name: str):
        """Get NBA player ID from name."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/commonallplayers",
                    params={
                        "LeagueID": "00",
                        "Season": "2025-26",
                        "IsOnlyCurrentSeason": 1
                    },
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                result_sets = data.get("resultSets", [])
                if not result_sets:
                    return None
                
                players = result_sets[0].get("rowSet", [])
                headers = result_sets[0].get("headers", [])
                
                player_name_lower = player_name.lower()
                for player in players:
                    player_dict = dict(zip(headers, player))
                    full_name = f"{player_dict.get('FIRST_NAME', '')} {player_dict.get('LAST_NAME', '')}".strip().lower()
                    
                    if player_name_lower in full_name or full_name in player_name_lower:
                        return player_dict.get("PERSON_ID")
                
                return None
                
        except Exception as e:
            logger.error(f"Error finding player: {e}")
            return None

async def test_nba_api():
    """Test the NBA Stats API."""
    print("=" * 60)
    print("TESTING NBA STATS API")
    print("=" * 60)
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    api = SimpleNBAStatsAPI()
    
    # Test with real players
    test_cases = [
        ("LeBron James", "2026-02-06"),
        ("Kevin Durant", "2026-02-06"),
        ("Stephen Curry", "2026-02-06"),
    ]
    
    success_count = 0
    
    for player_name, game_date in test_cases:
        print(f"Testing: {player_name} on {game_date}")
        
        try:
            stats = await api.fetch_player_game_stats(player_name, game_date)
            
            if stats:
                print(f"  [PASS] SUCCESS")
                print(f"     Points: {stats.get('pts')}")
                print(f"     Rebounds: {stats.get('reb')}")
                print(f"     Assists: {stats.get('ast')}")
                print(f"     Minutes: {stats.get('min')}")
                success_count += 1
            else:
                print(f"  [WARN] No stats found (game may not have been played)")
                
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
        
        print()
    
    print("=" * 60)
    print(f"RESULTS: {success_count}/{len(test_cases)} tests passed")
    print("=" * 60)
    
    if success_count == len(test_cases):
        print("[PASS] All tests passed! NBA API is working correctly.")
    elif success_count > 0:
        print("[WARN] Partial success. Some players found, others not.")
    else:
        print("[FAIL] All tests failed. Check NBA API availability.")
    
    print()
    print("Next steps:")
    print("1. If tests pass: Grading pipeline should work")
    print("2. If tests fail: Check rate limiting or API availability")

if __name__ == "__main__":
    asyncio.run(test_nba_api())
