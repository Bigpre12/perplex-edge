# apps/api/src/clients/espn_client.py
import logging
from typing import List, Dict, Any
from .base_client import ResilientBaseClient

logger = logging.getLogger(__name__)

class ESPNClient(ResilientBaseClient):
    """
    ESPN scraper — no API key required.
    Used for: injuries, news, scores, rosters, game schedules.
    """

    def __init__(self):
        super().__init__(
            name="ESPN",
            base_url="https://site.api.espn.com/apis/site/v2/sports",
            timeout=15,
            max_retries=2
        )

    def _map_sport(self, sport: str) -> tuple:
        """Map Odds API sport string to ESPN (category, league)"""
        mapping = {
            "basketball_nba": ("basketball", "nba"),
            "americanfootball_nfl": ("football", "nfl"),
            "baseball_mlb": ("baseball", "mlb"),
            "icehockey_nhl": ("hockey", "nhl"),
            "soccer_usa_mls": ("soccer", "usa.1"),
            "soccer_epl": ("soccer", "eng.1"),
            "soccer_uefa_champs_league": ("soccer", "uefa.champions"),
            "mma_mixed_martial_arts": ("mma", "ufc"),
            "mmamixedmartialarts": ("mma", "ufc"),
            "mma_mma": ("mma", "ufc"),
            "mixed_martial_arts": ("mma", "ufc"),
            "basketball_ncaab": ("basketball", "mens-college-basketball"),
            "americanfootball_ncaaf": ("football", "college-football"),
            "rugbyleague_nrl": ("rugby-league", "nrl"),
            "rugby_league_nrl": ("rugby-league", "nrl"),
            "soccer_uefachampsleague": ("soccer", "uefa.champions"),
        }
        sk = (sport or "").strip().lower().replace("-", "_")
        return mapping.get(sk, ("unknown", "unknown"))

    async def fetch_injuries(self, sport: str) -> list:
        """ESPN injury feed per sport"""
        cat, league = self._map_sport(sport)
        if cat == "unknown": return []
        
        path = f"/{cat}/{league}/injuries"
        res = await self.request("GET", path)
        return res.get("injuries", [])

    async def fetch_news(self, sport: str) -> list:
        """ESPN headlines for sport"""
        cat, league = self._map_sport(sport)
        if cat == "unknown": return []
        
        path = f"/{cat}/{league}/news"
        res = await self.request("GET", path)
        return res.get("articles", [])

    async def fetch_scoreboard(self, sport: str) -> list:
        """Live + today's game scores"""
        cat, league = self._map_sport(sport)
        if cat == "unknown": return []
        
        path = f"/{cat}/{league}/scoreboard"
        res = await self.request("GET", path)
        return res.get("events", [])

    async def fetch_roster(self, sport: str, team_id: str) -> list:
        """Team roster for player matching"""
        cat, league = self._map_sport(sport)
        if cat == "unknown": return []
        
        path = f"/{cat}/{league}/teams/{team_id}/roster"
        res = await self.request("GET", path)
        return res.get("athletes", [])

    async def fetch_game_odds(self, sport: str) -> list:
        """ESPN game lines (backup to Odds API)"""
        events = await self.fetch_scoreboard(sport)
        odds_list = []
        for event in events:
            for comp in event.get("competitions", []):
                if "odds" in comp:
                    odds_list.append({
                        "event_id": event.get("id"),
                        "odds": comp.get("odds")
                    })
        return odds_list

espn_client = ESPNClient()
