"""
MySportsFeeds Client — Free for Personal/Private Use

Fetches: deep stats for NFL, NBA, MLB, NHL (player logs, DFS, injuries)
Free tier: personal use, requires sign-up at mysportsfeeds.com

Docs: https://www.mysportsfeeds.com/data-feeds/api-docs
"""
import os
import httpx
from services.api_telemetry import InstrumentedAsyncClient
import logging
import time
import base64
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

SPORT_SLUG = {
    "basketball_nba": "nba",
    "americanfootball_nfl": "nfl",
    "baseball_mlb": "mlb",
    "icehockey_nhl": "nhl",
}


class MySportsFeedsClient:
    BASE_URL = "https://api.mysportsfeeds.com/v2.1/pull"

    def __init__(self):
        self.api_key = os.getenv("MYSPORTSFEEDS_API_KEY", "")
        self.password = os.getenv("MYSPORTSFEEDS_PASSWORD", "MYSPORTSFEEDS")
        self._cache: Dict[str, dict] = {}
        self.default_ttl = 900  # 15 min
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

    def _auth_header(self) -> Dict[str, str]:
        token = base64.b64encode(f"{self.api_key}:{self.password}".encode()).decode()
        return {"Authorization": f"Basic {token}"}

    async def get_daily_games(self, sport_key: str, date: str = None) -> List[Dict]:
        """Fetch today's games for a sport."""
        if not self.available:
            return []

        slug = SPORT_SLUG.get(sport_key)
        if not slug:
            return []

        if not date:
            date = datetime.now(timezone.utc).strftime("%Y%m%d")
        else:
            date = date.replace("-", "")

        cache_key = f"msf_games_{slug}_{date}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        season = "current"
        url = f"{self.BASE_URL}/{slug}/{season}/date/{date}/games.json"

        try:
            async with InstrumentedAsyncClient(provider="mysportsfeeds", timeout=self.timeout) as client:
                resp = await client.get(url, headers=self._auth_header())
                resp.raise_for_status()
                raw = resp.json()

            games = self._normalize_games(raw, sport_key)
            self._set_cache(cache_key, games)
            logger.info(f"MySportsFeeds: {len(games)} games for {sport_key}")
            return games

        except Exception as e:
            logger.error(f"MySportsFeeds error for {sport_key}: {e}")
            return []

    def _normalize_games(self, raw: dict, sport_key: str) -> List[Dict]:
        """Convert MySportsFeeds response to our format."""
        games_list = raw.get("games", [])
        games = []

        for entry in games_list:
            try:
                game = entry.get("schedule", {})
                home = game.get("homeTeam", {})
                away = game.get("awayTeam", {})

                start_str = game.get("startTime", "")
                try:
                    start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                except Exception:
                    start_time = datetime.now(timezone.utc)

                score = entry.get("score", {})

                games.append({
                    "id": str(game.get("id", "")),
                    "sport_key": sport_key,
                    "start_time": start_time,
                    "home_team_name": home.get("name", "Home"),
                    "away_team_name": away.get("name", "Away"),
                    "home_team_id": home.get("id"),
                    "away_team_id": away.get("id"),
                    "home_score": score.get("homeScoreTotal"),
                    "away_score": score.get("awayScoreTotal"),
                    "status": game.get("playedStatus", "UNPLAYED"),
                    "venue": game.get("venue", {}).get("name", ""),
                    "source": "mysportsfeeds",
                })
            except Exception as e:
                logger.debug(f"MySportsFeeds: Skipping game: {e}")
                continue

        return games

    async def get_player_game_logs(self, sport_key: str, player_name: str, limit: int = 10) -> List[Dict]:
        """Get recent game logs for a player — useful for projections."""
        if not self.available:
            return []

        slug = SPORT_SLUG.get(sport_key)
        if not slug:
            return []

        cache_key = f"msf_logs_{slug}_{player_name}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/{slug}/current/player_gamelogs.json"
        params = {"player": player_name, "limit": limit, "sort": "game.starttime.D"}

        try:
            async with InstrumentedAsyncClient(provider="mysportsfeeds", timeout=self.timeout) as client:
                resp = await client.get(url, headers=self._auth_header(), params=params)
                resp.raise_for_status()
                raw = resp.json()

            logs = raw.get("gamelogs", [])
            self._set_cache(cache_key, logs, ttl=1800)
            return logs

        except Exception as e:
            logger.error(f"MySportsFeeds game logs error: {e}")
            return []


# Singleton
mysportsfeeds_client = MySportsFeedsClient()
