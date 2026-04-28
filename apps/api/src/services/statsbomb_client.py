import httpx
from services.api_telemetry import InstrumentedAsyncClient
import logging
import json
from typing import Dict, List, Optional, Any
from services.db import db

logger = logging.getLogger(__name__)

class StatsBombClient:
    """
    Lazy-Fetcher for StatsBomb Open Data.
    Caches historical data permanently in Supabase.
    """
    BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/"

    async def _get_cached_data(self, key: str) -> Optional[Any]:
        """Check Supabase for permanently cached data."""
        query = "SELECT data FROM statsbomb_cache WHERE key = :key"
        try:
            result = await db.fetch_all(query, {"key": key})
            if result:
                return json.loads(result[0]["data"])
        except Exception as e:
            logger.error(f"StatsBomb cache read error: {e}")
        return None

    async def _set_cached_data(self, key: str, data: Any):
        """Store data in Supabase permanently."""
        query = """
            INSERT INTO statsbomb_cache (key, data)
            VALUES (:key, :data)
            ON CONFLICT (key) DO UPDATE SET data = EXCLUDED.data
        """
        try:
            await db.executemany(query, [{"key": key, "data": json.dumps(data)}])
        except Exception as e:
            logger.error(f"StatsBomb cache write error: {e}")

    async def _fetch_from_github(self, path: str) -> Optional[Any]:
        """Fetch data from GitHub Raw API."""
        url = f"{self.BASE_URL}{path}"
        try:
            async with InstrumentedAsyncClient(provider="statsbomb", timeout=15.0) as client:
                logger.info(f"🌐 StatsBomb: Fetching {url}")
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.json()
                else:
                    logger.error(f"❌ StatsBomb GitHub error {resp.status_code}")
                    return None
        except Exception as e:
            logger.error(f"StatsBomb connection failed: {e}")
            return None

    async def get_competitions(self) -> List[Dict]:
        """Fetch all competitions."""
        key = "competitions"
        data = await self._get_cached_data(key)
        if not data:
            data = await self._fetch_from_github("competitions.json")
            if data: await self._set_cached_data(key, data)
        return data or []

    async def get_matches(self, competition_id: int, season_id: int) -> List[Dict]:
        """Fetch matches for a competition and season."""
        key = f"matches:{competition_id}:{season_id}"
        data = await self._get_cached_data(key)
        if not data:
            data = await self._fetch_from_github(f"matches/{competition_id}/{season_id}.json")
            if data: await self._set_cached_data(key, data)
        return data or []

    async def get_events(self, match_id: int) -> List[Dict]:
        """Fetch match event data."""
        key = f"events:{match_id}"
        data = await self._get_cached_data(key)
        if not data:
            data = await self._fetch_from_github(f"events/{match_id}.json")
            if data: await self._set_cached_data(key, data)
        return data or []

statsbomb_client = StatsBombClient()
