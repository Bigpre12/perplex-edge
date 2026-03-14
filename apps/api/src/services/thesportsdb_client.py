"""
TheSportsDB Client — Free Public Key, All Sports Including UFC

Fetches: schedules, team info, player data across every sport.
The only free API that covers UFC/MMA fighter data.

Free key: "1" (public test key) or sign up at https://www.thesportsdb.com/
Docs: https://www.thesportsdb.com/api.php
"""
import os
import httpx
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# TheSportsDB league IDs
LEAGUE_MAP = {
    "basketball_nba": "4387",
    "americanfootball_nfl": "4391",
    "baseball_mlb": "4424",
    "icehockey_nhl": "4380",
    "basketball_wnba": "4388",
    "basketball_ncaab": "4607",
    "soccer_epl": "4328",
    "soccer_usa_mls": "4346",
    "mma_mixed_martial_arts": "4443",  # UFC
    "tennis_atp": "4464",
    "tennis_wta": "4465",
}


class TheSportsDBClient:
    BASE_URL = "https://www.thesportsdb.com/api/v1/json"

    def __init__(self):
        # "1" is the free public test key, or use your own
        self.api_key = os.getenv("THESPORTSDB_KEY", "1")
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

    async def get_events_by_day(self, sport_key: str, date: str = None) -> List[Dict]:
        """Fetch events/games for a league on a specific date."""
        league_id = LEAGUE_MAP.get(sport_key)
        if not league_id:
            return []

        if not date:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        cache_key = f"tsdb_events_{sport_key}_{date}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/{self.api_key}/eventsday.php"
        params = {"d": date, "l": league_id}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                raw = resp.json()

            games = self._normalize_events(raw, sport_key)
            self._set_cache(cache_key, games)
            logger.info(f"TheSportsDB: {len(games)} events for {sport_key} on {date}")
            return games

        except Exception as e:
            logger.error(f"TheSportsDB error for {sport_key}: {e}")
            return []

    def _normalize_events(self, raw: dict, sport_key: str) -> List[Dict]:
        """Convert TheSportsDB events to our normalized format."""
        events = raw.get("events") or []
        games = []

        for event in events:
            try:
                start_str = f"{event.get('dateEvent', '')}T{event.get('strTime', '00:00:00')}+00:00"
                try:
                    start_time = datetime.fromisoformat(start_str)
                except Exception:
                    start_time = datetime.now(timezone.utc)

                games.append({
                    "id": str(event.get("idEvent", "")),
                    "sport_key": sport_key,
                    "start_time": start_time,
                    "home_team_name": event.get("strHomeTeam", "Home"),
                    "away_team_name": event.get("strAwayTeam", "Away"),
                    "home_score": event.get("intHomeScore"),
                    "away_score": event.get("intAwayScore"),
                    "status": event.get("strStatus", "Scheduled"),
                    "venue": event.get("strVenue", ""),
                    "source": "thesportsdb",
                })
            except Exception as e:
                logger.debug(f"TheSportsDB: Skipping event: {e}")
                continue

        return games

    async def get_player_details(self, player_name: str) -> Optional[Dict]:
        """Search for a player by name — works for UFC fighters too."""
        cache_key = f"tsdb_player_{player_name}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/{self.api_key}/searchplayers.php"
        params = {"p": player_name}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                raw = resp.json()

            players = raw.get("player") or []
            if players:
                result = players[0]
                self._set_cache(cache_key, result, ttl=3600)
                return result
            return None

        except Exception as e:
            logger.error(f"TheSportsDB player search error: {e}")
            return None

    async def search_teams(self, team_name: str) -> List[Dict]:
        """Search for teams by name."""
        cache_key = f"tsdb_teams_{team_name}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/{self.api_key}/searchteams.php"
        params = {"t": team_name}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                raw = resp.json()

            teams = raw.get("teams") or []
            self._set_cache(cache_key, teams, ttl=3600 * 24)
            return teams

        except Exception as e:
            logger.error(f"TheSportsDB team search error: {e}")
            return []

    async def lookup_event(self, event_id: str) -> Optional[Dict]:
        """Look up details for a specific event/game."""
        cache_key = f"tsdb_event_{event_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/{self.api_key}/lookupevent.php"
        params = {"id": event_id}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                raw = resp.json()

            events = raw.get("events") or []
            if events:
                result = events[0]
                self._set_cache(cache_key, result, ttl=3600 * 12)
                return result
            return None

        except Exception as e:
            logger.error(f"TheSportsDB event lookup error for {event_id}: {e}")
            return None


# Singleton
thesportsdb_client = TheSportsDBClient()
