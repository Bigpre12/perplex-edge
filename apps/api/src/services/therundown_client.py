"""
TheRundown API Client — Free Tier (20,000 data points/day, 3 books)

Fetches: pre-match odds, game schedules, scores
Used as: backup odds source when The Odds API credits run low

Docs: https://therundown.io/api
"""
import os
import httpx
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# TheRundown sport IDs
SPORT_ID_MAP = {
    "basketball_nba": 4,
    "americanfootball_nfl": 2,
    "icehockey_nhl": 6,
    "baseball_mlb": 3,
    "basketball_ncaab": 5,
    "americanfootball_ncaaf": 1,
}


class TheRundownClient:
    BASE_URL = "https://api.therundown.io/v2"

    def __init__(self):
        self.api_key = os.getenv("THERUNDOWN_API_KEY", "")
        self._cache: Dict[str, dict] = {}
        self.default_ttl = 600  # 10 minutes — conserve quota
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

    async def get_games(self, sport_key: str) -> List[Dict]:
        """Fetch today's games for a sport from TheRundown."""
        if not self.available:
            return []

        sport_id = SPORT_ID_MAP.get(sport_key)
        if not sport_id:
            return []

        cache_key = f"rundown_games_{sport_key}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        url = f"{self.BASE_URL}/sports/{sport_id}/events/{today}"
        headers = {"x-rapidapi-key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                raw = resp.json()

            games = self._normalize_games(raw, sport_key)
            self._set_cache(cache_key, games)
            logger.info(f"TheRundown: Fetched {len(games)} games for {sport_key}")
            return games

        except Exception as e:
            logger.error(f"TheRundown error for {sport_key}: {e}")
            return []

    def _normalize_games(self, raw: Any, sport_key: str) -> List[Dict]:
        """Normalize TheRundown response into our game format."""
        if not isinstance(raw, dict):
            return []

        games = []
        events = raw.get("events", [])

        for event in events:
            try:
                teams = event.get("teams_normalized", event.get("teams", []))
                home = next((t for t in teams if t.get("is_home")), {})
                away = next((t for t in teams if not t.get("is_home")), {})

                start_str = event.get("event_date", "")
                try:
                    start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                except Exception:
                    start_time = datetime.now(timezone.utc)

                game = {
                    "id": str(event.get("event_id", "")),
                    "sport_key": sport_key,
                    "start_time": start_time,
                    "home_team_name": home.get("name", "Home"),
                    "away_team_name": away.get("name", "Away"),
                    "home_team_id": home.get("team_id"),
                    "away_team_id": away.get("team_id"),
                    "home_score": event.get("score", {}).get("score_home"),
                    "away_score": event.get("score", {}).get("score_away"),
                    "status": event.get("score", {}).get("event_status", "STATUS_SCHEDULED"),
                    "venue": event.get("venue_name", ""),
                    "source": "therundown",
                }
                games.append(game)
            except Exception as e:
                logger.debug(f"TheRundown: Skipping event: {e}")
                continue

        return games


# Singleton
therundown_client = TheRundownClient()
