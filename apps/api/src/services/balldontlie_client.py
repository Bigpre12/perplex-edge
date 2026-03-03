"""
BallDontLie API Client — Free, No Expiry (~30 req/min)

Fetches: NBA player game logs, season averages, schedules
Used for: player stats to feed ML model/projections

Docs: https://www.balldontlie.io
"""
import os
import httpx
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class BallDontLieClient:
    BASE_URL = "https://api.balldontlie.io/v1"

    def __init__(self):
        self.api_key = os.getenv("BALLDONTLIE_API_KEY", "")
        self._cache: Dict[str, dict] = {}
        self.default_ttl = 900  # 15 minutes
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

    async def get_nba_games(self, date: str = None) -> List[Dict]:
        """Fetch NBA games for a specific date (YYYY-MM-DD)."""
        if not self.available:
            return []

        if not date:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        cache_key = f"bdl_games_{date}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/games"
        params = {"dates[]": date}
        headers = {"Authorization": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                raw = resp.json()

            games = self._normalize_games(raw)
            self._set_cache(cache_key, games)
            logger.info(f"BallDontLie: Fetched {len(games)} NBA games for {date}")
            return games

        except Exception as e:
            logger.error(f"BallDontLie games error: {e}")
            return []

    def _normalize_games(self, raw: dict) -> List[Dict]:
        """Normalize BallDontLie response to our game format."""
        games = []
        for game in raw.get("data", []):
            try:
                home = game.get("home_team", {})
                away = game.get("visitor_team", {})

                start_str = game.get("date", "")
                try:
                    start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                except Exception:
                    start_time = datetime.now(timezone.utc)

                games.append({
                    "id": str(game.get("id", "")),
                    "sport_key": "basketball_nba",
                    "start_time": start_time,
                    "home_team_name": home.get("full_name", "Home"),
                    "away_team_name": away.get("full_name", "Away"),
                    "home_team_id": home.get("id"),
                    "away_team_id": away.get("id"),
                    "home_score": game.get("home_team_score"),
                    "away_score": game.get("visitor_team_score"),
                    "status": game.get("status", "Scheduled"),
                    "venue": "",
                    "source": "balldontlie",
                })
            except Exception as e:
                logger.debug(f"BallDontLie: Skipping game: {e}")
                continue

        return games

    async def get_player_stats(self, player_name: str) -> Optional[Dict]:
        """Search for a player and get their season averages."""
        if not self.available:
            return None

        cache_key = f"bdl_player_{player_name}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        headers = {"Authorization": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Search player
                resp = await client.get(
                    f"{self.BASE_URL}/players",
                    params={"search": player_name},
                    headers=headers,
                )
                resp.raise_for_status()
                players = resp.json().get("data", [])

                if not players:
                    return None

                player = players[0]
                player_id = player.get("id")

                # Get season averages
                avg_resp = await client.get(
                    f"{self.BASE_URL}/season_averages",
                    params={"player_ids[]": player_id, "season": 2025},
                    headers=headers,
                )
                avg_resp.raise_for_status()
                averages = avg_resp.json().get("data", [])

                result = {
                    "player": player,
                    "season_averages": averages[0] if averages else {},
                }
                self._set_cache(cache_key, result, ttl=3600)  # 1 hour
                return result

        except Exception as e:
            logger.error(f"BallDontLie player stats error: {e}")
            return None


# Singleton
balldontlie_client = BallDontLieClient()
