"""
The Unified Odds API REST Client

Standardized production-grade client for The Odds API (V4).
Consolidates logic from legacy clients and ensures:
1. Robust Key Rotation across multiple API keys.
2. Daily Call Capping to protect quotas (~100k/mo).
3. Intelligent Caching (Redis + Memory fallback).
4. Consistent Interface for all ingestion and analytic services.

Methods:
    - get_active_sports(): List of in-season sports.
    - get_events(sport): Game schedule only (cheap, no odds).
    - get_live_odds(sport, markets): Real-time odds for games.
    - get_player_props(sport, event_id, markets): Deep player markets.
"""
import os
import time
import httpx
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from core.config import settings
from services.cache import cache

logger = logging.getLogger(__name__)

class OddsApiClient:
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    def __init__(self):
        # Load keys from centralized settings
        self.api_keys = settings.ODDS_API_KEYS
        self.current_key_idx = 0
        
        # Security logging: Show hint of active keys
        safe_keys = [f"{k[:4]}****" for k in self.api_keys if k]
        logger.info(f"OddsApiClient initialized with {len(self.api_keys)} keys: {', '.join(safe_keys)}")
        
        self.default_ttl = 300  # 5 min — standard odds
        self.long_ttl = 3600    # 1 hour — sports/metadata
        self.timeout = 15.0
        
        # Limit per day (approx 100k/mo tier)
        self.max_daily_calls = int(os.getenv("THE_ODDS_API_MAX_CALLS_PER_DAY", 10000))

    def _get_api_key(self) -> str:
        if not self.api_keys:
            return ""
        return self.api_keys[self.current_key_idx % len(self.api_keys)]

    def _rotate_key(self) -> bool:
        if len(self.api_keys) <= 1:
            return False
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
        logger.warning(f"🔄 Rotated to Odds API key index {self.current_key_idx}")
        return True

    async def _get_today_count(self) -> int:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        key = f"odds_api_usage:{today}"
        count = await cache.get(key)
        return int(count) if count else 0

    async def _increment_count(self):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        key = f"odds_api_usage:{today}"
        count = await self._get_today_count()
        await cache.set(key, str(count + 1), ttl=86400)

    async def _request(self, endpoint: str, params: Dict = None, use_cache: bool = True, ttl: int = None) -> Any:
        # 1. Check Daily Limit
        count = await self._get_today_count()
        if count >= self.max_daily_calls and not settings.DEVELOPMENT_MODE:
            logger.warning(f"🚨 Odds API daily limit ({self.max_daily_calls}) reached. Aborting.")
            return None

        params = params.copy() if params else {}
        ttl = ttl if ttl is not None else self.default_ttl
        
        # 2. Check Cache
        cache_key = f"odds_api_v4:{endpoint}:{str(sorted(params.items()))}"
        if use_cache:
            cached = await cache.get_json(cache_key)
            if cached:
                return cached

        # 3. Execute Request with Rotation
        for attempt in range(len(self.api_keys) or 1):
            key = self._get_api_key()
            if not key:
                logger.error("No Odds API key available.")
                return None

            p = params.copy()
            p["apiKey"] = key
            url = f"{self.BASE_URL}{endpoint}"
            
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(url, params=p)
                    
                    # Log quota headers
                    used = resp.headers.get("x-requests-used")
                    rem = resp.headers.get("x-requests-remaining")
                    if rem:
                        logger.info(f"✅ OddsAPI Quota: {rem} left (Used: {used}) | Path: {endpoint}")
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        await self._increment_count()
                        if use_cache:
                            await cache.set_json(cache_key, data, ttl=ttl)
                        return data
                    
                    elif resp.status_code in (401, 403, 429):
                        logger.error(f"❌ Key index {self.current_key_idx} failure ({resp.status_code}). Rotating...")
                        if self._rotate_key():
                            continue # Try next key
                        else:
                            break # No more keys
                    else:
                        logger.error(f"❌ Odds API error {resp.status_code}: {resp.text[:200]}")
                        return None
            except Exception as e:
                logger.error(f"Odds API connection error: {e}")
                return None
        
        return None

    # --- Core API Methods ---

    async def get_active_sports(self) -> List[Dict]:
        """Fetch all currently active sports."""
        return await self._request("/sports", use_cache=True, ttl=self.long_ttl) or []

    async def get_events(self, sport: str) -> List[Dict]:
        """Fetch game schedules (cheap, no odds results)."""
        return await self._request(f"/sports/{sport}/events", use_cache=True) or []

    async def get_live_odds(self, sport: str, regions: str = "us", markets: str = "h2h,spreads") -> List[Dict]:
        """Fetch real-time odds for games."""
        params = {
            "regions": regions,
            "markets": markets,
            "oddsFormat": "american",
            "dateFormat": "iso"
        }
        return await self._request(f"/sports/{sport}/odds", params=params) or []

    async def get_player_props(self, sport: str, event_id: str, markets: str, regions: str = "us") -> Dict:
        """Fetch specific player props for an event."""
        params = {
            "regions": regions,
            "markets": markets,
            "oddsFormat": "american",
            "dateFormat": "iso"
        }
        # Note: endpoint returns a dict for single event ID if passed as path param
        return await self._request(f"/sports/{sport}/events/{event_id}/odds", params=params) or {}

    # --- Compatibility Aliases ---
    async def get_odds(self, sport: str, regions: str = "us", markets: str = "h2h,spreads") -> List[Dict]:
        return await self.get_live_odds(sport, regions, markets)

    async def fetch_odds(self, sport: str, regions: str = "us", markets: str = "h2h,spreads") -> List[Dict]:
        return await self.get_live_odds(sport, regions, markets)

    async def fetch_events(self, sport: str) -> List[Dict]:
        return await self.get_events(sport)

    async def fetch_player_props(self, sport: str, event_id: str, markets: str, regions: str = "us") -> Dict:
        return await self.get_player_props(sport, event_id, markets, regions)

# --- Global Singletons ---
odds_api_client = OddsApiClient()
odds_api = odds_api_client
