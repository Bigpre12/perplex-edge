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
from services.sportsgameodds_client import sportsgameodds_client

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

# Sport-specific provider routing — determines which fallback chain to use per sport
STATS_PROVIDER = {
    "basketball_nba": ["balldontlie", "mysportsfeeds", "espn", "thesportsdb"],
    "americanfootball_nfl": ["balldontlie", "mysportsfeeds", "espn", "thesportsdb"],
    "baseball_mlb": ["balldontlie", "mysportsfeeds", "espn", "thesportsdb"],
    "icehockey_nhl": ["balldontlie", "mysportsfeeds", "espn", "thesportsdb"],
    "basketball_ncaab": ["balldontlie", "espn", "thesportsdb"],
    "americanfootball_ncaaf": ["balldontlie", "espn", "thesportsdb"],
    "basketball_wnba": ["balldontlie", "espn", "thesportsdb"],
    "tennis_atp": ["espn", "thesportsdb"],
    "tennis_wta": ["espn", "thesportsdb"],
    "golf_pga": ["espn", "thesportsdb"],
    "mma_mixed_martial_arts": ["thesportsdb", "sportsgameodds"],
    "soccer_epl": ["espn", "thesportsdb"],
    "soccer_usa_mls": ["espn", "thesportsdb"],
}

ODDS_PROVIDER = {
    "basketball_nba": ["the_odds_api", "therundown", "sportsgameodds"],
    "americanfootball_nfl": ["the_odds_api", "therundown", "sportsgameodds"],
    "baseball_mlb": ["the_odds_api", "therundown", "sportsgameodds"],
    "icehockey_nhl": ["the_odds_api", "therundown", "sportsgameodds"],
    "basketball_ncaab": ["the_odds_api", "sportsgameodds"],
    "americanfootball_ncaaf": ["the_odds_api", "sportsgameodds"],
    "basketball_wnba": ["the_odds_api", "sportsgameodds"],
    "tennis_atp": ["the_odds_api"],
    "tennis_wta": ["the_odds_api"],
    "golf_pga": ["the_odds_api"],
    "mma_mixed_martial_arts": ["sportsgameodds"],  # Only free option for UFC odds
    "soccer_epl": ["the_odds_api"],
    "soccer_usa_mls": ["the_odds_api"],
}

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
            
    async def fetch_games_by_sport(self, sport_key: str) -> list:
        """Fetch live games via full waterfall: Odds API → ESPN → TheSportsDB → TheRundown → BallDontLie → MySportsFeeds → SportsGameOdds"""
        # === Provider 1: The Odds API (burns credits, has full odds) ===
        try:
            # Requesting common player props along with team markets for better discovery
            player_markets = "player_points,player_rebounds,player_assists,player_threes,player_pass_tds,player_pass_yds,player_rush_yds,player_rec_yds,player_anytime_td,pitcher_strikeouts,batter_hits"
            raw_games = await odds_api.get_live_odds(sport_key, markets=f"h2h,spreads,totals,{player_markets}")
            if raw_games:
                formatted = []
                for game in raw_games:
                    start_dt = datetime.fromisoformat(game.get("commence_time", "").replace("Z", "+00:00"))
                    status = "scheduled" if start_dt > datetime.now(timezone.utc) else "in_progress"
                    display_name = sport_key.split("_")[1].upper() if "_" in sport_key else sport_key.upper()
                    formatted.append({
                        "id": game.get("id"),
                        "sport_id": get_sport_id_local(sport_key) or 0,
                        "external_game_id": game.get("id"),
                        "home_team": game.get("home_team"),
                        "away_team": game.get("away_team"),
                        "home_team_name": game.get("home_team"),
                        "away_team_name": game.get("away_team"),
                        "sport_name": display_name,
                        "start_time": start_dt,
                        "status": status,
                        "bookmakers_count": len(game.get("bookmakers", [])),
                        "raw_bookmakers_data": game.get("bookmakers", []),
                        "source": "odds_api",
                    })
                logger.info(f"Waterfall: {len(formatted)} games from Odds API for {sport_key}")
                return formatted
        except Exception as e:
            logger.warning(f"Waterfall: Odds API failed for {sport_key}: {e}")

        # === Provider 2: ESPN (free, no key, unlimited, ALL sports) ===
        try:
            espn_games = await espn_client.get_scoreboard(sport_key)
            if espn_games:
                logger.info(f"Waterfall: {len(espn_games)} games from ESPN for {sport_key}")
                return espn_games  # type: ignore
        except Exception as e:
            logger.warning(f"Waterfall: ESPN failed for {sport_key}: {e}")

        # === Provider 3: TheSportsDB (free, ALL sports incl. UFC) ===
        try:
            tsdb_games = await thesportsdb_client.get_events_by_day(sport_key)
            if tsdb_games:
                logger.info(f"Waterfall: {len(tsdb_games)} games from TheSportsDB for {sport_key}")
                return tsdb_games  # type: ignore
        except Exception as e:
            logger.warning(f"Waterfall: TheSportsDB failed for {sport_key}: {e}")

        # === Provider 4: TheRundown (20k pts/day, major sports) ===
        try:
            rundown_games = await therundown_client.get_games(sport_key)
            if rundown_games:
                logger.info(f"Waterfall: {len(rundown_games)} games from TheRundown for {sport_key}")
                return rundown_games  # type: ignore
        except Exception as e:
            logger.warning(f"Waterfall: TheRundown failed for {sport_key}: {e}")

        # === Provider 5: BallDontLie (NBA only) ===
        if "nba" in sport_key:
            try:
                bdl_games = await balldontlie_client.get_nba_games()
                if bdl_games:
                    logger.info(f"Waterfall: {len(bdl_games)} games from BallDontLie")
                    return bdl_games  # type: ignore
            except Exception as e:
                logger.warning(f"Waterfall: BallDontLie failed: {e}")

        # === Provider 6: MySportsFeeds (NFL/NBA/MLB/NHL) ===
        try:
            msf_games = await mysportsfeeds_client.get_daily_games(sport_key)
            if msf_games:
                logger.info(f"Waterfall: {len(msf_games)} games from MySportsFeeds for {sport_key}")
                return msf_games  # type: ignore
        except Exception as e:
            logger.warning(f"Waterfall: MySportsFeeds failed for {sport_key}: {e}")

        # === Provider 7: SportsGameOdds (UFC + alt lines, 1k/mo) ===
        try:
            sgo_games = await sportsgameodds_client.get_events(sport_key)
            if sgo_games:
                logger.info(f"Waterfall: {len(sgo_games)} games from SportsGameOdds for {sport_key}")
                return sgo_games  # type: ignore
        except Exception as e:
            logger.warning(f"Waterfall: SportsGameOdds failed for {sport_key}: {e}")

        logger.warning(f"Waterfall: All 7 providers exhausted for {sport_key}")
        return []
        
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
