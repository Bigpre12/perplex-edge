"""
Merged RealDataConnector (Waterfall Logic + Production Fixes)
FIX #6: betstack URL fixed. FIX #8: dynamic dates. FIX #17: connection safety.
Routes requests through a PRIORITY WATERFALL of free API providers.
"""
import asyncio
import os
import httpx
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

# Adjusting imports to match new app structure
from app.services.odds_api_client import odds_api
from services.espn_client import espn_client
from services.therundown_client import therundown_client
from services.balldontlie_client import balldontlie_client
from services.thesportsdb_client import thesportsdb_client
from services.mysportsfeeds_client import mysportsfeeds_client
from services.sportsgameodds_client import sportsgameodds_client

from config import settings

logger = logging.getLogger(__name__)

# Sport Key to ID mapping (duplicated from app_core to avoid import issues)
SPORT_KEY_TO_ID = {
    "basketball_nba": 30,
    "americanfootball_nfl": 31,
    "baseball_mlb": 32,
    "icehockey_nhl": 33,
    "basketball_ncaab": 39,
    "americanfootball_ncaaf": 41,
    "tennis_atp": 42,
    "tennis_wta": 43,
    "basketball_wnba": 53,
    "mma_mixed_martial_arts": 54,
    "boxing_boxing": 55,
}

def get_sport_id_local(sport_key: str) -> Optional[int]:
    if not sport_key: return None
    return SPORT_KEY_TO_ID.get(sport_key.lower())

class RealDataConnector:
    def __init__(self):
        self.betstack_api_key = os.getenv("BETSTACK_API_KEY")
        self.odds_api_key     = settings.ODDS_API_KEY
        self.ai_api_key       = settings.GROQ_API_KEY

        # FIX #6: Correct domain — api.betstack.dev
        self.betstack_base_url = "https://api.betstack.dev"
        self.odds_api_base_url = "https://api.the-odds-api.com/v4"
        self.groq_base_url     = "https://api.groq.com/openai/v1"
        
        self.seasons = {
            "basketball_nba": {"start": 10, "end": 6},
            "americanfootball_nfl": {"start": 8, "end": 2},
            "baseball_mlb": {"start": 2, "end": 11},
            "icehockey_nhl": {"start": 10, "end": 6},
        }

    async def get_nba_games(self) -> List[Dict]:
        """Fetch NBA slate for the current calendar window."""
        # Try waterfall first
        games = await self.fetch_games_by_sport("basketball_nba")
        if games:
            return games
            
        # If waterfall yields nothing, we might be in a UTC transition.
        # Try fetching using espn directly as it's the most reliable fallback
        return await espn_client.get_scoreboard("basketball_nba")

    async def fetch_props_from_betstack(self, sport: str = "nba") -> Any:
        """FIX #6: fetch props from the correct BetStack endpoint."""
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(
                    f"{self.betstack_base_url}/sports/{sport}/props",
                    headers={"X-API-Key": self.betstack_api_key} if self.betstack_api_key else {},
                    timeout=10.0,
                )
                r.raise_for_status()
                return r.json()
            except Exception as e:
                logger.error(f"BetStack error: {e}")
                return None

    async def generate_ai_analysis(self, prompt: str) -> Optional[Dict]:
        """Fix for AI analysis using Groq."""
        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(
                    f"{self.groq_base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.ai_api_key}",
                             "Content-Type": "application/json"},
                    json={"model": "llama-3.3-70b-versatile",
                          "messages": [
                              {"role": "system", "content": "You are a sports betting analytics expert."},
                              {"role": "user",   "content": prompt},
                          ],
                          "temperature": 0.7, "max_tokens": 500},
                    timeout=30.0,
                )
                r.raise_for_status()
                return r.json()
            except Exception as e:
                logger.error(f"Groq error: {e}")
                return None

    # --- WATERFALL LOGIC FROM ORIGINAL real_data_connector.py ---
    
    async def fetch_games_by_sport(self, sport_key: str) -> List[Dict]:
        providers = [
            ("odds_api", lambda: odds_api.get_live_odds(sport_key, markets="h2h,spreads,totals")),
            ("espn", lambda: espn_client.get_scoreboard(sport_key)),
            ("thesportsdb", lambda: thesportsdb_client.get_events_by_day(sport_key)),
            ("therundown", lambda: therundown_client.get_games(sport_key)),
        ]
        
        for name, fetch_func in providers:
            try:
                data = await fetch_func()
                if data:
                    logger.info(f"Waterfall: Successfully fetched {sport_key} from {name}")
                    return self._normalize_game_data(data, sport_key, name)
            except Exception as e:
                logger.warning(f"Waterfall: {name} failed for {sport_key}: {e}")
        return []

    def _normalize_game_data(self, data: Any, sport_key: str, source: str) -> List[Dict]:
        # Implementation from existing real_data_connector logic (simplified for length)
        normalized = []
        if source == "odds_api":
            for g in data:
                start_dt = datetime.fromisoformat(g.get("commence_time", "").replace("Z", "+00:00"))
                normalized.append({
                    "id": g.get("id"),
                    "sport_id": get_sport_id_local(sport_key) or 0,
                    "home_team": g.get("home_team") or g.get("home_team_name"),
                    "away_team": g.get("away_team") or g.get("away_team_name"),
                    "home_team_name": g.get("home_team") or g.get("home_team_name"),
                    "away_team_name": g.get("away_team") or g.get("away_team_name"),
                    "start_time": start_dt,
                    "status": "scheduled" if start_dt > datetime.now(timezone.utc) else "live",
                    "source": source
                })
        else:
            return data # Already normalized by clients usually
        return normalized

    async def fetch_player_props(self, sport_key: str, game_id: str, market: str = "player_points") -> List[Dict]:
        """Fetch props cascading from Odds API."""
        try:
            raw = await odds_api.get_player_props(sport_key, game_id, markets=market)
            if not raw: return []
            bookmakers = raw.get("bookmakers", [])
            props = []
            for book in bookmakers:
                for mkt in book.get("markets", []):
                    if mkt.get("key") != market: continue
                    for out in mkt.get("outcomes", []):
                        player = out.get("description", "Unknown")
                        side = out.get("name", "Over").lower()
                        props.append({
                            "game_id": game_id,
                            "player_name": player,
                            "stat_type": market,
                            "line": out.get("point"),
                            "side": side,
                            "odds": out.get("price"),
                            "sportsbook": book.get("title")
                        })
            return props
        except Exception as e:
            logger.error(f"Prop fetch failed: {e}")
            return []

real_data_connector = RealDataConnector()
