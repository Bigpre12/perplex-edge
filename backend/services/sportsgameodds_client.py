"""
SportsGameOdds Client — Free Tier (1,000 objects/month, 10 req/min)

The only free API that covers UFC/MMA odds + alternate lines.
Used sparingly for: UFC odds, alt lines on high-confidence props.

Docs: https://sportsgameodds.com/docs/v1/
"""
import os
import httpx
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

SPORT_SLUG = {
    "mma_mixed_martial_arts": "MMA",
    "basketball_nba": "NBA",
    "americanfootball_nfl": "NFL",
    "baseball_mlb": "MLB",
    "icehockey_nhl": "NHL",
    "tennis_atp": "TENNIS",
}


class SportsGameOddsClient:
    BASE_URL = "https://api.sportsgameodds.com/v1"

    def __init__(self):
        self.api_key = os.getenv("SPORTSGAMEODDS_KEY", "")
        self._cache: Dict[str, dict] = {}
        self.default_ttl = 1800  # 30 min — conserve the 1k/mo quota
        self.timeout = 10.0

    def _get_cached(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry and time.time() < entry["expires_at"]:
            return entry["data"]
        return None

    def _set_cache(self, key: str, data: Any, ttl: int = None):
        self._cache[key] = {
            "data": data,
            "expires_at": time.time() + (ttl or self.default_ttl),
        }

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    async def get_events(self, sport_key: str) -> List[Dict]:
        """Fetch upcoming events for a sport. Use sparingly (1k objects/mo)."""
        if not self.available:
            return []

        slug = SPORT_SLUG.get(sport_key)
        if not slug:
            return []

        cache_key = f"sgo_events_{sport_key}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/events"
        params = {"sport": slug, "status": "upcoming"}
        headers = {"x-api-key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                raw = resp.json()

            events = self._normalize_events(raw, sport_key)
            self._set_cache(cache_key, events)
            logger.info(f"SportsGameOdds: {len(events)} events for {sport_key}")
            return events

        except Exception as e:
            logger.error(f"SportsGameOdds error for {sport_key}: {e}")
            return []

    def _normalize_events(self, raw: Any, sport_key: str) -> List[Dict]:
        """Convert SGO response to our format."""
        items = raw.get("data", []) if isinstance(raw, dict) else []
        games = []

        for event in items:
            try:
                teams = event.get("teams", {})
                home = teams.get("home", {})
                away = teams.get("away", {})

                start_str = event.get("startTime", "")
                try:
                    start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                except Exception:
                    start_time = datetime.now(timezone.utc)

                games.append({
                    "id": str(event.get("id", "")),
                    "sport_key": sport_key,
                    "start_time": start_time,
                    "home_team_name": home.get("name", event.get("homeTeam", "Home")),
                    "away_team_name": away.get("name", event.get("awayTeam", "Away")),
                    "home_score": None,
                    "away_score": None,
                    "status": event.get("status", "upcoming"),
                    "source": "sportsgameodds",
                })
            except Exception as e:
                logger.debug(f"SportsGameOdds: Skipping event: {e}")
                continue

        return games

    async def get_odds(self, event_id: str, include_alt_lines: bool = False) -> Optional[Dict]:
        """Get odds for a specific event. Set include_alt_lines=True for alt lines."""
        if not self.available:
            return None

        cache_key = f"sgo_odds_{event_id}_{include_alt_lines}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/events/{event_id}/odds"
        params = {}
        if include_alt_lines:
            params["includeAltLines"] = "true"
        headers = {"x-api-key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            self._set_cache(cache_key, data)
            return data

        except Exception as e:
            logger.error(f"SportsGameOdds odds error: {e}")
            return None


# Singleton
sportsgameodds_client = SportsGameOddsClient()
