"""
Results API Service - Fetch actual game results for pick grading
Uses OddsPapi for real game results and player statistics
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from app.services.oddspapi_provider import oddspapi_provider

logger = logging.getLogger(__name__)

@dataclass
class GameResult:
    """Game result data structure."""
    game_id: int
    fixture_id: str  # OddsPapi fixture ID
    final_score: Dict[str, int]
    player_stats: Dict[int, Dict[str, float]]
    game_time: datetime
    status: str

class ResultsAPI:
    """Service for fetching actual game results from OddsPapi."""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600
    
    async def fetch_game_results(self, game_id: int, fixture_id: str = None) -> Optional[Dict[str, Any]]:
        """Fetch actual results for a specific game from OddsPapi."""
        try:
            # Check cache
            cache_key = f"game_result_{game_id}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if (datetime.now(timezone.utc) - timestamp).seconds < self.cache_ttl:
                    return cached_data
            
            # If no fixture_id provided, we can't fetch from OddsPapi
            if not fixture_id:
                logger.warning(f"[results_api] No fixture_id for game {game_id}, cannot fetch results")
                return None
            
            # Fetch from OddsPapi
            result = await self._fetch_from_oddspapi(fixture_id)
            
            if result:
                self.cache[cache_key] = (result, datetime.now(timezone.utc))
            
            return result
            
        except Exception as e:
            logger.error(f"[results_api] Error fetching game {game_id}: {e}")
            return None
    
    async def _fetch_from_oddspapi(self, fixture_id: str) -> Optional[Dict[str, Any]]:
        """Fetch actual results from OddsPapi API."""
        try:
            # Fetch settlements (game results)
            settlements = await oddspapi_provider.fetch_settlements(fixture_id)
            
            if not settlements:
                logger.warning(f"[results_api] No settlements found for fixture {fixture_id}")
                return None
            
            # Fetch scores for detailed stats
            scores = await oddspapi_provider.fetch_scores(fixture_id)
            
            # Parse the results
            result = {
                "fixture_id": fixture_id,
                "status": "FINAL",
                "settlements": settlements,
                "scores": scores,
                "game_time": datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"[results_api] Error fetching from OddsPapi: {e}")
            return None
    
    async def get_player_stat_from_settlements(self, settlements: Dict, player_name: str, stat_type: str) -> Optional[float]:
        """Extract player stat from OddsPapi settlements data."""
        try:
            # OddsPapi settlements contain player prop results
            # This would need to be implemented based on actual API response structure
            # For now, return None to indicate we need the actual implementation
            logger.info(f"[results_api] Would extract {stat_type} for {player_name} from settlements")
            return None
            
        except Exception as e:
            logger.error(f"[results_api] Error extracting player stat: {e}")
            return None
    
    async def is_game_completed(self, game_id: int, fixture_id: str = None) -> bool:
        """Check if a game is completed using OddsPapi data."""
        try:
            if not fixture_id:
                return False
            
            settlements = await oddspapi_provider.fetch_settlements(fixture_id)
            return settlements is not None and len(settlements) > 0
            
        except Exception as e:
            logger.error(f"[results_api] Error checking game completion: {e}")
            return False

# Global results API instance
results_api = ResultsAPI()
