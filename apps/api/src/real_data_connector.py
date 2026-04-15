"""
Real Data Connector for Sports Betting System

Routes requests through a PRIORITY WATERFALL of free API providers:
  1. The Odds API     (primary — 500 credits/month, has odds + props)
  2. ESPN Free API    (no key needed — games, scores, schedules — ALL sports)
  3. TheRundown       (20k data points/day — backup odds, 3 books)
  4. BallDontLie      (free forever — NBA/NFL/MLB/NHL/NCAAB stats)
  5. TheSportsDB      (free $0 key — ALL sports incl. UFC/MMA)
  6. MySportsFeeds    (free personal — deep NFL/NBA/MLB/NHL stats)
  7. SportsGameOdds   (1k objects/mo — UFC odds + alt lines)

If the primary provider fails (401/429/timeout), we cascade to the next.
All providers use in-memory caching to minimize API calls.
"""
import asyncio
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import logging

from services.odds_api_client import odds_api
from services.espn_client import espn_client
from services.therundown_client import therundown_client
from services.balldontlie_client import balldontlie_client
from services.thesportsdb_client import thesportsdb_client
from services.mysportsfeeds_client import mysportsfeeds_client
from services.sportsgameodds_client import sportsgameodds_client
from services.api_sports_client import api_sports_client
from services.sportmonks_client import sportmonks_client
from services.isports_client import isports_client
from services.statsbomb_client import statsbomb_client
from core.waterfall_config import get_provider_chain

logger = logging.getLogger(__name__)

# Sport Key to ID mapping (duplicated from app_core to avoid import issues)
SPORT_KEY_TO_ID = {
    "basketball_nba": 30,
    "americanfootball_nfl": 31,
    "baseball_mlb": 40,
    "icehockey_nhl": 22,
    "basketball_ncaab": 39,
    "americanfootball_ncaaf": 41,
    "tennis_atp": 42,
    "tennis_wta": 43,
    "basketball_wnba": 53,
    "mma_mixed_martial_arts": 54,
    "boxing_boxing": 55,
}

def get_sport_id_local(sport_key: str) -> Optional[int]:
    """Local helper to get sport ID."""
    if not sport_key:
        return None
    return SPORT_KEY_TO_ID.get(sport_key.lower())

# Branched Waterfall Logic (Recommended Architecture 2026-04-07)
# 🏀 US Sports: NBA, NFL, MLB, NHL, NCAAF, NCAAB, WNBA, NCAAW
# ⚽ Soccer: EPL, MLS, UEFA, etc.
# 🥊 MMA: UFC, etc.

US_SPORTS = ["basketball_nba", "americanfootball_nfl", "baseball_mlb", "icehockey_nhl", 
             "basketball_ncaab", "americanfootball_ncaaf", "basketball_wnba", "basketball_ncaaw"]
SOCCER_SPORTS = ["soccer_epl", "soccer_usa_mls", "soccer_uefa_champions_league"]
MMA_SPORTS = ["mma_mixed_martial_arts"]

class RealDataConnector:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        # Define seasonal boundaries (simplified for logic demo)
        self.seasons = {
            "basketball_nba": {"start": 10, "end": 6},  # Oct to June
            "basketball_wnba": {"start": 5, "end": 10}, # May to Oct
            "americanfootball_nfl": {"start": 8, "end": 2}, # Aug to Feb
            "icehockey_nhl": {"start": 10, "end": 6}, # Oct to June
            "baseball_mlb": {"start": 2, "end": 11}, # Feb to Nov
            "tennis_atp": {"start": 1, "end": 11}, # Jan to Nov
            "boxing_boxing": {"start": 1, "end": 12}, # Year-round
            "mma_mixed_martial_arts": {"start": 1, "end": 12}, # Year-round
            "soccer_epl": {"start": 8, "end": 5}, # Aug to May
        }

    def is_sport_active(self, sport_key: str) -> bool:
        """Check if a sport is currently in season based on month."""
        now = datetime.now(timezone.utc)
        month = now.month
        season = self.seasons.get(sport_key)
        if not season:
            return True # Default to active if unknown
            
        start, end = season["start"], season["end"]
        if sport_key == "basketball_nba":
            return True # ALWAYS ACTIVE FOR TICKER NEWS
        if start <= end:
            return start <= month <= end
        else:
            # Wraps around year (e.g., NBA Oct-June)
            return month >= start or month <= end
            
    def get_waterfall_chain(self, sport_key: str, data_type: str = "stats") -> List[str]:
        """
        Returns the branched waterfall chain based on sport and data type.
        Delegates to ``core.waterfall_config`` (single source of truth).
        """
        return get_provider_chain(sport_key, data_type)

    async def fetch_games_by_sport(self, sport_key: str) -> list:
        """
        [UNIFIED] Delegated to WaterfallRouter (Branched Orchestrator).
        """
        from services.waterfall_router import waterfall_router
        return await waterfall_router.get_data(sport_key, data_type="stats")

    async def fetch_games_by_sport_OLD(self, sport_key: str) -> list:
        """[DEPRECATED] Standard linear waterfall."""
        
    async def fetch_nba_games(self) -> List[Dict]:
        """Fetch NBA games via waterfall — always returns data if any provider works."""
        games = await self.fetch_games_by_sport("basketball_nba")
        # Enrich with NBA-specific fields
        for g in games:
            g.setdefault("sport_id", 30)
            g.setdefault("sport_name", "NBA")
        return games
    
    async def fetch_nfl_games(self) -> List[Dict]:
        """Fetch NFL games via waterfall."""
        games = await self.fetch_games_by_sport("americanfootball_nfl")
        for g in games:
            g.setdefault("sport_id", 31)
            g.setdefault("sport_name", "NFL")
        return games
    
    async def fetch_player_props(self, sport_key: str, game_id: str, market: str = "player_points") -> List[Dict]:
        """
        Fetch real player props for a specific game and market from The Odds API.
        Formats them securely for the Monte Carlo analysis engine.
        """
        try:
            raw_events = await odds_api.get_player_props(sport_key, game_id, markets=market)
            if not raw_events or not isinstance(raw_events, dict):
                logger.warning(f"No props found for game {game_id} and market {market}")
                return []
                
            # The API returns a dictionary object for the specific event ID requested
            bookmakers = raw_events.get("bookmakers", [])
            
            props = []
            
            # Extract lines across all books
            for book in bookmakers:
                book_key = book.get("key")
                book_name = book.get("title")
                markets_data = book.get("markets", [])
                
                for mkt in markets_data:
                    if mkt.get("key") != market:
                        continue
                        
                    outcomes = mkt.get("outcomes", [])
                    
                    # Group outcomes by description (player name)
                    player_outcomes = {}
                    for outcome in outcomes:
                        player = outcome.get("description", "Unknown")
                        if player not in player_outcomes:
                            player_outcomes[player] = []
                        player_outcomes[player].append(outcome)
                        
                    # Build standard format
                    for player, outs in player_outcomes.items():
                        over_odds = -110
                        under_odds = -110
                        line = 0.0
                        
                        for out in outs:
                            name = out.get("name", "").lower()
                            if "over" in name:
                                over_odds = out.get("price")
                                line = out.get("point", line)
                            elif "under" in name:
                                under_odds = out.get("price")
                                line = out.get("point", line)
                                
                        if float(line) > 0:
                            props.append({
                                "game_id": game_id,
                                "player_name": player,
                                "stat_type": market.replace("player_", ""),
                                "line": line,
                                "over_odds": over_odds,
                                "under_odds": under_odds,
                                "sportsbook": book_name,
                                "sportsbook_key": book_key,
                                "updated_at": datetime.now(timezone.utc)
                            })
                            
            return props
            
        except Exception as e:
            logger.error(f"Error fetching real player props: {e}")
            return []

    async def fetch_active_games(self) -> List[Dict]:
        """Fetch games for all currently active sports."""
        active_games = []
        
        # Check NBA
        nba = await self.fetch_nba_games()
        if nba:
            active_games.extend(nba)
            
        # Check NHL
        nhl = await self.fetch_nhl_games()
        if nhl:
            active_games.extend(nhl)
            
        # Check NFL
        nfl = await self.fetch_nfl_games()
        if nfl:
            active_games.extend(nfl)
            
        return active_games

    async def fetch_nhl_games(self) -> List[Dict]:
        """Fetch NHL games via waterfall."""
        games = await self.fetch_games_by_sport("icehockey_nhl")
        for g in games:
            g.setdefault("sport_id", 22)
            g.setdefault("sport_name", "NHL")
        return games

    async def fetch_dfs_props(self, sport_key: str, game_id: str, market: str = "player_points") -> List[Dict]:
        """
        Specific fetch for DFS platforms (PrizePicks, Underdog).
        Tailored for Texas users who primarily use Pickem apps.
        """
        # DFS_BOOKMAKERS is now imported here to prevent circularity
        DFS_BOOKMAKERS = ["draftkings", "fanduel", "prizepicks", "underdog_fantasy"]
        try:
            raw_events = await odds_api.get_player_props(sport_key, game_id, markets=market)
            if not raw_events or not isinstance(raw_events, dict):
                return []
                
            bookmakers = raw_events.get("bookmakers", [])
            
            dfs_props = []
            for book in bookmakers:
                book_key = book.get("key", "").lower()
                if book_key not in DFS_BOOKMAKERS:
                    continue
                    
                book_title = book.get("title")
                markets_data = book.get("markets", [])
                
                for mkt in markets_data:
                    if mkt.get("key") != market:
                        continue
                        
                    outcomes = mkt.get("outcomes", [])
                    player_outcomes = {}
                    for outcome in outcomes:
                        player = outcome.get("description", "Unknown")
                        if player not in player_outcomes:
                            player_outcomes[player] = []
                        player_outcomes[player].append(outcome)
                        
                    for player, outs in player_outcomes.items():
                        line = 0.0
                        over_odds = -119 # Default DFS implied odds
                        
                        for out in outs:
                            line = out.get("point", line)
                            if "over" in out.get("name", "").lower():
                                over_odds = out.get("price", over_odds)

                        if float(line) > 0:
                            dfs_props.append({
                                "game_id": game_id,
                                "player_name": player,
                                "stat_type": market.replace("player_", ""),
                                "line": line,
                                "over_odds": over_odds,
                                "under_odds": over_odds,
                                "sportsbook": book_title,
                                "platform_key": book_key,
                                "is_dfs": True,
                                "updated_at": datetime.now(timezone.utc)
                            })
                            
            return dfs_props
        except Exception as e:
            logger.error(f"Error fetching DFS props: {e}")
            return []

# Global instances
real_data_connector = RealDataConnector()
