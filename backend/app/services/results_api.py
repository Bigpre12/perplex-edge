"""
Results API Service - Fetch actual game results for pick grading
Uses NBA Stats API (free, official) for player statistics
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

@dataclass
class GameResult:
    """Game result data structure."""
    game_id: int
    player_stats: Dict[int, Dict[str, float]]
    game_time: datetime
    status: str

class NBAStatsAPI:
    """Service for fetching actual player stats from NBA Stats API (free, official)."""
    
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
        self.cache = {}
        self.cache_ttl = 3600
    
    async def fetch_player_game_stats(self, player_name: str, game_date: str) -> Optional[Dict[str, Any]]:
        """
        Fetch player stats from NBA Stats API for a specific game.
        
        Args:
            player_name: Player name (e.g., "Derrick White")
            game_date: Game date in YYYY-MM-DD format
        
        Returns:
            Player stats dict with PTS, REB, AST, etc.
        """
        try:
            # Get player ID from name
            player_id = await self._get_player_id(player_name)
            if not player_id:
                logger.warning(f"[nba_stats] Could not find player ID for {player_name}")
                return None
            
            # Get game log for player
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
                
                # Parse game logs to find game for specific date
                result_sets = data.get("resultSets", [])
                if not result_sets:
                    return None
                
                game_logs = result_sets[0].get("rowSet", [])
                headers = result_sets[0].get("headers", [])
                
                # Find game for specific date
                for game in game_logs:
                    game_dict = dict(zip(headers, game))
                    if game_date in game_dict.get("GAME_DATE", ""):
                        return {
                            "player_id": player_id,
                            "player_name": player_name,
                            "game_date": game_dict.get("GAME_DATE"),
                            "team": game_dict.get("TEAM_ABBREVIATION"),
                            "pts": game_dict.get("PTS", 0),
                            "reb": game_dict.get("REB", 0),
                            "ast": game_dict.get("AST", 0),
                            "stl": game_dict.get("STL", 0),
                            "blk": game_dict.get("BLK", 0),
                            "tov": game_dict.get("TOV", 0),
                            "fgm": game_dict.get("FGM", 0),
                            "fga": game_dict.get("FGA", 0),
                            "fg3m": game_dict.get("FG3M", 0),
                            "fg3a": game_dict.get("FG3A", 0),
                            "ftm": game_dict.get("FTM", 0),
                            "fta": game_dict.get("FTA", 0),
                            "min": game_dict.get("MIN", 0),
                        }
                
                logger.warning(f"[nba_stats] No game found for {player_name} on {game_date}")
                return None
                
        except Exception as e:
            logger.error(f"[nba_stats] Error fetching stats for {player_name}: {e}")
            return None
    
    async def _get_player_id(self, player_name: str) -> Optional[int]:
        """Get NBA player ID from name."""
        try:
            # Check cache
            cache_key = f"player_id_{player_name.lower().replace(' ', '_')}"
            if cache_key in self.cache:
                cached_id, timestamp = self.cache[cache_key]
                if (datetime.now(timezone.utc) - timestamp).seconds < self.cache_ttl:
                    return cached_id
            
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
                
                # Find player by name
                player_name_lower = player_name.lower()
                for player in players:
                    player_dict = dict(zip(headers, player))
                    full_name = f"{player_dict.get('FIRST_NAME', '')} {player_dict.get('LAST_NAME', '')}".strip().lower()
                    
                    if player_name_lower in full_name or full_name in player_name_lower:
                        player_id = player_dict.get("PERSON_ID")
                        # Cache result
                        self.cache[cache_key] = (player_id, datetime.now(timezone.utc))
                        return player_id
                
                return None
                
        except Exception as e:
            logger.error(f"[nba_stats] Error finding player ID for {player_name}: {e}")
            return None
    
    async def is_game_completed(self, game_date: str) -> bool:
        """Check if games for a date are completed."""
        try:
            # For now, assume games are completed if they're from yesterday or earlier
            from datetime import datetime, timedelta
            game_dt = datetime.strptime(game_date, "%Y-%m-%d")
            today = datetime.now()
            return game_dt.date() < today.date()
        except:
            return False

async def fetch_game_results(game_id: int, sport_id: int) -> Optional[GameResult]:
    """
    Fetch game results for grading picks.
    
    Args:
        game_id: The game ID
        sport_id: The sport ID
        
    Returns:
        GameResult with player stats or None if not available
    """
    try:
        # For now, return a placeholder result
        # In production, this would fetch actual results from the appropriate API
        logger.info(f"Fetching results for game {game_id}, sport {sport_id}")
        
        # TODO: Implement actual result fetching based on sport_id
        # - NBA: Use NBA Stats API
        # - NFL: Use NFL API
        # - MLB: Use MLB API
        
        return GameResult(
            game_id=game_id,
            player_stats={},
            game_time=datetime.now(timezone.utc),
            status="completed"
        )
    except Exception as e:
        logger.error(f"Error fetching game results: {e}")
        return None

# Global NBA Stats API instance
nba_stats_api = NBAStatsAPI()

# Alias for backward compatibility
results_api = nba_stats_api
