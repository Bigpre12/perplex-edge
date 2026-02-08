"""
Results API Service - Fetch actual game results for pick grading
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GameResult:
    """Game result data structure."""
    game_id: int
    final_score: Dict[str, int]  # {team_id: points}
    player_stats: Dict[int, Dict[str, float]]  # {player_id: {stat_type: value}}
    game_time: datetime
    status: str  # "FINAL", "IN_PROGRESS", etc.

class ResultsAPI:
    """Service for fetching actual game results."""
    
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 3600  # 1 hour cache
    
    async def fetch_game_results(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch actual results for a specific game.
        
        Args:
            game_id: Game ID to fetch results for
        
        Returns:
            Game results data or None if not found
        """
        try:
            # Check cache first
            cache_key = f"game_result_{game_id}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if (datetime.now(timezone.utc) - timestamp).seconds < self.cache_ttl:
                    return cached_data
            
            # Fetch from data source
            # This would integrate with your actual data provider
            # For now, return mock data for testing
            result = await self._fetch_from_data_source(game_id)
            
            # Cache the result
            self.cache[cache_key] = (result, datetime.now(timezone.utc))
            
            return result
            
        except Exception as e:
            logger.error(f"[results_api] Error fetching game {game_id}: {e}")
            return None
    
    async def _fetch_from_data_source(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch from actual data source.
        
        This is a placeholder - implement based on your data provider.
        """
        try:
            # Mock data for testing - replace with actual API call
            mock_results = {
                "game_id": game_id,
                "status": "FINAL",
                "final_score": {
                    "team_1": 110,
                    "team_2": 105
                },
                "player_stats": {
                    12345: {  # Player ID
                        "PTS": 25.5,
                        "REB": 8.2,
                        "AST": 7.1,
                        "STL": 2.3,
                        "BLK": 1.1,
                        "TO": 3.4,
                        "FGM": 10.2,
                        "FGA": 22.1,
                        "3PM": 3.1,
                        "3PA": 8.2
                    },
                    12346: {
                        "PTS": 22.3,
                        "REB": 9.1,
                        "AST": 6.8,
                        "STL": 1.9,
                        "BLK": 0.8,
                        "TO": 2.9,
                        "FGM": 9.3,
                        "FGA": 20.4,
                        "3PM": 2.8,
                        "3PA": 7.9
                    }
                },
                "game_time": datetime.now(timezone.utc).isoformat()
            }
            
            return mock_results
            
        except Exception as e:
            logger.error(f"[results_api] Error in data source fetch: {e}")
            return None
    
    async def fetch_multiple_game_results(self, game_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Fetch results for multiple games.
        
        Args:
            game_ids: List of game IDs
        
        Returns:
            Dictionary mapping game_id to results
        """
        results = {}
        
        # Fetch in parallel
        tasks = [self.fetch_game_results(game_id) for game_id in game_ids]
        fetched_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(fetched_results):
            game_id = game_ids[i]
            if isinstance(result, Exception):
                logger.error(f"[results_api] Error fetching game {game_id}: {result}")
                continue
            if result:
                results[game_id] = result
        
        return results
    
    async def get_player_stat(self, game_id: int, player_id: int, stat_type: str) -> Optional[float]:
        """
        Get a specific player stat from game results.
        
        Args:
            game_id: Game ID
            player_id: Player ID
            stat_type: Stat type (PTS, REB, etc.)
        
        Returns:
            Stat value or None if not found
        """
        try:
            game_results = await self.fetch_game_results(game_id)
            if not game_results:
                return None
            
            player_stats = game_results.get("player_stats", {})
            player_data = player_stats.get(player_id, {})
            
            return player_data.get(stat_type)
            
        except Exception as e:
            logger.error(f"[results_api] Error getting player stat: {e}")
            return None
    
    async def is_game_completed(self, game_id: int) -> bool:
        """
        Check if a game is completed and results are available.
        
        Args:
            game_id: Game ID to check
        
        Returns:
            True if game is completed, False otherwise
        """
        try:
            game_results = await self.fetch_game_results(game_id)
            if not game_results:
                return False
            
            status = game_results.get("status", "").upper()
            return status in ["FINAL", "COMPLETED", "FINISHED"]
            
        except Exception as e:
            logger.error(f"[results_api] Error checking game completion: {e}")
            return False

# Global results API instance
results_api = ResultsAPI()
