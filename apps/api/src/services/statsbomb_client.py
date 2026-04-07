import logging
from typing import Dict, List, Optional, Any
from statsbombpy import sb
from services.cache import cache

logger = logging.getLogger(__name__)

class StatsBombClient:
    """
    Official StatsBomb Python Client Integration.
    Fetches/Parses StatsBomb Open Data using the statsbombpy library.
    """
    def __init__(self):
        # By default, statsbombpy uses the open-data repo if no credentials are provided.
        pass

    async def get_competitions(self) -> Any:
        """Fetch all available competitions."""
        cache_key = "statsbomb:competitions"
        cached = await cache.get_json(cache_key)
        if cached:
            return cached
            
        try:
            # sb.competitions() returns a pandas DataFrame, we convert to dict
            df = sb.competitions()
            data = df.to_dict(orient="records")
            await cache.set_json(cache_key, data, ttl=86400 * 7)
            return data
        except Exception as e:
            logger.error(f"StatsBomb Error (Competitions): {e}")
            return []

    async def get_matches(self, competition_id: int, season_id: int) -> Any:
        """Fetch matches for a specific competition and season."""
        cache_key = f"statsbomb:matches:{competition_id}:{season_id}"
        cached = await cache.get_json(cache_key)
        if cached:
            return cached
            
        try:
            df = sb.matches(competition_id=competition_id, season_id=season_id)
            data = df.to_dict(orient="records")
            await cache.set_json(cache_key, data, ttl=86400 * 7)
            return data
        except Exception as e:
            logger.error(f"StatsBomb Error (Matches): {e}")
            return []

    async def get_events(self, match_id: int) -> Any:
        """Fetch match event data."""
        cache_key = f"statsbomb:events:{match_id}"
        cached = await cache.get_json(cache_key)
        if cached:
            return cached
            
        try:
            # Note: sb.events returns a dict of dataframes (one per event type) 
            # if multiple types are requested, or a single df.
            # We'll fetch all and convert.
            events = sb.events(match_id=match_id)
            if hasattr(events, 'to_dict'):
                data = events.to_dict(orient="records")
            else:
                data = {k: v.to_dict(orient="records") for k, v in events.items()}
                
            await cache.set_json(cache_key, data, ttl=86400 * 7)
            return data
        except Exception as e:
            logger.error(f"StatsBomb Error (Events): {e}")
            return []

    async def get_lineups(self, match_id: int) -> Any:
        """Fetch lineups for a match."""
        cache_key = f"statsbomb:lineups:{match_id}"
        cached = await cache.get_json(cache_key)
        if cached:
            return cached
            
        try:
            lineups = sb.lineups(match_id=match_id)
            # lineups is a dict of dataframes {team_name: df}
            data = {k: v.to_dict(orient="records") for k, v in lineups.items()}
            await cache.set_json(cache_key, data, ttl=86400 * 7)
            return data
        except Exception as e:
            logger.error(f"StatsBomb Error (Lineups): {e}")
            return []

statsbomb_client = StatsBombClient()
