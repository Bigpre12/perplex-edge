"""
ESPN Public API Client — Free, No API Key Required

Uses ESPN's public `site.api.espn.com` endpoints to fetch:
- Live scoreboard (games in progress + upcoming)
- Team schedules
- Game statuses and scores

This is the highest-priority fallback since it costs $0 forever and has
no rate limit for reasonable usage (~1 req/5s).

Endpoints used:
  Scoreboard: https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard
"""
import httpx
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# ESPN sport/league mapping for The Odds API sport keys
SPORT_MAP = {
    "basketball_nba": ("basketball", "nba"),
    "basketball_wnba": ("basketball", "wnba"),
    "basketball_ncaab": ("basketball", "mens-college-basketball"),
    "americanfootball_nfl": ("football", "nfl"),
    "americanfootball_ncaaf": ("football", "college-football"),
    "icehockey_nhl": ("hockey", "nhl"),
    "baseball_mlb": ("baseball", "mlb"),
    "soccer_epl": ("soccer", "eng.1"),
    "soccer_usa_mls": ("soccer", "usa.1"),
    "soccer_uefa_champs_league": ("soccer", "uefa.champions_league"),
    "rugby_league_nrl": ("rugby-league", "nrl"),
    "aussie_rules_afl": ("australian-football", "afl"),
    "mma_mixed_martial_arts": None,
}


class ESPNClient:
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

    def __init__(self):
        self._cache: Dict[str, dict] = {}
        self.default_ttl = 300  # 5 minutes
        self.timeout = 10.0

    def _cache_key(self, endpoint: str) -> str:
        return endpoint

    def _get_cached(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry and time.time() < entry["expires_at"]:
            return entry["data"]
        return None

    def invalidate_cache(self, key: str) -> None:
        self._cache.pop(key, None)

    def _set_cache(self, key: str, data: Any, ttl: int = None):
        self._cache[key] = {
            "data": data,
            "expires_at": time.time() + (ttl or self.default_ttl),
        }

    async def get_scoreboard(self, sport_key: str, force_refresh: bool = False) -> List[Dict]:
        """
        Fetch today's scoreboard for a sport. Returns normalized game objects
        compatible with the real_data_connector format.
        """
        if SPORT_MAP.get(sport_key) is None:
            return []

        mapping = SPORT_MAP.get(sport_key)
        if not mapping:
            logger.warning(f"ESPN: No mapping for sport_key '{sport_key}'")
            return []

        sport, league = mapping
        endpoint = f"/{sport}/{league}/scoreboard"
        cache_key = self._cache_key(endpoint)

        if force_refresh:
            self.invalidate_cache(cache_key)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                raw = resp.json()

            games = self._normalize_scoreboard(raw, sport_key)
            self._set_cache(cache_key, games, ttl=300)
            logger.info(f"ESPN: Fetched {len(games)} games for {sport_key}")
            return games

        except Exception as e:
            logger.error(f"ESPN scoreboard error for {sport_key}: {e}")
            return []

    def _normalize_scoreboard(self, raw: dict, sport_key: str) -> List[Dict]:
        """Convert ESPN scoreboard JSON to our normalized game format."""
        games = []
        events = raw.get("events", [])

        for event in events:
            try:
                competitions = event.get("competitions", [{}])
                comp = competitions[0] if competitions else {}
                competitors = comp.get("competitors", [])

                home = next((c for c in competitors if c.get("homeAway") == "home"), {})
                away = next((c for c in competitors if c.get("homeAway") == "away"), {})

                home_team = home.get("team", {})
                away_team = away.get("team", {})

                # Parse start time
                start_str = event.get("date", "")
                try:
                    start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                except Exception:
                    start_time = datetime.now(timezone.utc)

                status_type = comp.get("status", {}).get("type", {})
                status_name = status_type.get("name", "STATUS_SCHEDULED")

                game = {
                    "id": event.get("id", ""),
                    "sport_key": sport_key,
                    "start_time": start_time,
                    "home_team_name": home_team.get("displayName", home_team.get("name", "Home")),
                    "away_team_name": away_team.get("displayName", away_team.get("name", "Away")),
                    "home_team_id": home_team.get("id"),
                    "away_team_id": away_team.get("id"),
                    "home_score": int(home.get("score", 0)) if home.get("score") else None,
                    "away_score": int(away.get("score", 0)) if away.get("score") else None,
                    "status": status_name,
                    "venue": comp.get("venue", {}).get("fullName", ""),
                    "broadcast": ", ".join(
                        b.get("names", [""])[0]
                        for b in comp.get("broadcasts", [])
                        if b.get("names")
                    ),
                    "source": "espn",
                }
                games.append(game)
            except Exception as e:
                logger.debug(f"ESPN: Skipping event parse error: {e}")
                continue

        return games

    async def fetch_injuries(self, sport_key: str) -> List[Dict]:
        """Fetch latest injury data for a given sport from ESPN's public API."""
        if SPORT_MAP.get(sport_key) is None:
            return []
        mapping = SPORT_MAP.get(sport_key)
        if not mapping:
            return []
        
        sport, league = mapping
        # site.api.espn.com/apis/site/v2/sports/{sport}/{league}/injuries
        url = f"{self.BASE_URL}/{sport}/{league}/injuries"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                # ESPN nested structure: { injuries: [ { displayName: 'Team X', injuries: [...] } ] }
                return data.get("injuries", [])
        except Exception as e:
            logger.error(f"ESPN: Injuries fetch failed for {sport_key}: {e}")
            return []

    async def fetch_news(self, sport_key: str) -> List[Dict]:
        """Fetch latest news articles for a given sport from ESPN's public API."""
        if SPORT_MAP.get(sport_key) is None:
            return []
        mapping = SPORT_MAP.get(sport_key)
        if not mapping:
            return []
        
        sport, league = mapping
        # site.api.espn.com/apis/site/v2/sports/{sport}/{league}/news
        url = f"{self.BASE_URL}/{sport}/{league}/news"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                return data.get("articles", [])
        except Exception as e:
            logger.error(f"ESPN: News fetch failed for {sport_key}: {e}")
            return []

    async def get_injuries(self, sport_key: str) -> List[Dict]:
        """Legacy compatibility method mapping to fetch_injuries."""
        return await self.fetch_injuries(sport_key)


# Singleton
espn_client = ESPNClient()
