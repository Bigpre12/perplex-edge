"""
Real Data Connector for Sports Betting System

Routes requests to the appropriate external API client (e.g. The Odds API)
and formats the raw JSON into the normalized structures expected by our
internal analytics engines (Monte Carlo, CLV, EV).
"""
import asyncio
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import logging

from app.services.odds_api_client import odds_api

logger = logging.getLogger(__name__)

class RealDataConnector:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def fetch_nba_games(self) -> List[Dict]:
        """Fetch live NBA games from The Odds API"""
        try:
            # Get from The Odds API (basketball_nba)
            raw_games = await odds_api.get_live_odds("basketball_nba", markets="h2h,spreads,totals")
            if not raw_games:
                return []
                
            formatted = []
            for game in raw_games:
                # Parse start time
                start_dt = datetime.fromisoformat(game.get("commence_time", "").replace("Z", "+00:00"))
                status = "scheduled" if start_dt > datetime.now(timezone.utc) else "in_progress"
                
                # Extract main market lines from the first bookmaker (usually DraftKings or FanDuel is best)
                bookmakers = game.get("bookmakers", [])
                
                formatted.append({
                    "id": game.get("id"),  # Using the external string ID temporarily for internal mapping
                    "sport_id": 30, # Internal NBA ID
                    "external_game_id": game.get("id"),
                    "home_team_name": game.get("home_team"),
                    "away_team_name": game.get("away_team"),
                    "sport_name": "NBA",
                    "start_time": start_dt,
                    "status": status,
                    "bookmakers_count": len(bookmakers),
                    "raw_bookmakers_data": bookmakers # Keep for prop extraction later
                })
                
            return formatted
            
        except Exception as e:
            logger.error(f"Error fetching real NBA games: {e}")
            return []
    
    async def fetch_nfl_games(self) -> List[Dict]:
        """Fetch live NFL games from The Odds API"""
        try:
            # Get from The Odds API (americanfootball_nfl)
            raw_games = await odds_api.get_live_odds("americanfootball_nfl", markets="h2h,spreads,totals")
            if not raw_games:
                return []
                
            formatted = []
            for game in raw_games:
                start_dt = datetime.fromisoformat(game.get("commence_time", "").replace("Z", "+00:00"))
                status = "scheduled" if start_dt > datetime.now(timezone.utc) else "in_progress"
                
                formatted.append({
                    "id": game.get("id"), 
                    "sport_id": 1, # Internal NFL ID
                    "external_game_id": game.get("id"),
                    "home_team_name": game.get("home_team"),
                    "away_team_name": game.get("away_team"),
                    "sport_name": "NFL",
                    "start_time": start_dt,
                    "status": status
                })
                
            return formatted
            
        except Exception as e:
            logger.error(f"Error fetching real NFL games: {e}")
            return []
    
    async def fetch_player_props(self, sport_key: str, game_id: str, market: str = "player_points") -> List[Dict]:
        """
        Fetch real player props for a specific game and market from The Odds API.
        Formats them securely for the Monte Carlo analysis engine.
        """
        try:
            raw_events = await odds_api.get_player_props(sport_key, game_id, markets=market)
            if not raw_events or not isinstance(raw_events, list) or len(raw_events) == 0:
                logger.warning(f"No props found for game {game_id} and market {market}")
                return []
                
            # The API returns an array with 1 item for the specific event ID we requested
            event = raw_events[0]
            bookmakers = event.get("bookmakers", [])
            
            props = []
            
            # Extract consensus lines across all books
            for book in bookmakers:
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
                                
                        if line > 0:
                            props.append({
                                "game_id": game_id,
                                "player_name": player,
                                "stat_type": market.replace("player_", ""),
                                "line": line,
                                "over_odds": over_odds,
                                "under_odds": under_odds,
                                "sportsbook": book_name,
                                "updated_at": datetime.now(timezone.utc)
                            })
                            
            return props
            
        except Exception as e:
            logger.error(f"Error fetching real player props: {e}")
            return []

# Global instances
real_data_connector = RealDataConnector()
