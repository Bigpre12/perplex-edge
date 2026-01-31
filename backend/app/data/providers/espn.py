"""
ESPN API Provider.

ESPN's public API (unofficial/undocumented) provides:
- Schedules and scoreboards
- Box scores and game details
- Team and player stats
- Injury information

No API key required - free to use but may change without notice.

Usage:
    async with ESPNProvider() as provider:
        games = await provider.fetch_scoreboard("basketball_nba", date(2026, 1, 31))
        boxscore = await provider.fetch_boxscore("basketball_nba", "401584711")
"""

import logging
from datetime import date, datetime, timezone
from typing import Any, Optional

from app.data.base import BaseProvider

logger = logging.getLogger(__name__)


class ESPNProvider(BaseProvider):
    """
    ESPN API client for schedules, scores, and stats.
    
    Features:
    - Free (no API key required)
    - Good coverage of NBA, NCAAB, NFL
    - Provides schedules, scores, box scores, injuries
    
    Limitations:
    - Unofficial/undocumented API
    - No odds data
    - May change without notice
    """
    
    name = "espn"
    base_url = "https://site.api.espn.com/apis/site/v2/sports"
    
    # Sport paths in ESPN's API
    SPORT_PATHS = {
        "basketball_nba": "basketball/nba",
        "basketball_ncaab": "basketball/mens-college-basketball",
        "americanfootball_nfl": "football/nfl",
        "americanfootball_ncaaf": "football/college-football",
        "baseball_mlb": "baseball/mlb",
        "icehockey_nhl": "hockey/nhl",
    }
    
    def __init__(self):
        super().__init__(api_key=None)  # No API key needed
    
    def _get_sport_path(self, sport_key: str) -> str:
        """Get ESPN sport path from standard sport key."""
        return self.SPORT_PATHS.get(sport_key, sport_key.replace("_", "/"))
    
    async def health_check(self) -> bool:
        """Check if ESPN API is accessible."""
        try:
            await self._request("GET", "/basketball/nba/scoreboard")
            return True
        except Exception as e:
            logger.warning(f"[{self.name}] Health check failed: {e}")
            return False
    
    async def fetch_scoreboard(
        self,
        sport_key: str,
        game_date: Optional[date] = None,
    ) -> dict[str, Any]:
        """
        Fetch scoreboard (schedule) for a sport.
        
        Args:
            sport_key: Standard sport key (e.g., "basketball_nba")
            game_date: Date to fetch (default: today)
        
        Returns:
            Scoreboard data with events/games
        """
        sport_path = self._get_sport_path(sport_key)
        params = {}
        
        if game_date:
            params["dates"] = game_date.strftime("%Y%m%d")
        
        data = await self._request("GET", f"/{sport_path}/scoreboard", params=params)
        return data if isinstance(data, dict) else {}
    
    async def fetch_games(
        self,
        sport_key: str,
        game_date: Optional[date] = None,
    ) -> list[dict]:
        """
        Fetch games for a sport, normalized to standard format.
        
        Args:
            sport_key: Standard sport key
            game_date: Date to fetch (default: today)
        
        Returns:
            List of normalized game objects
        """
        scoreboard = await self.fetch_scoreboard(sport_key, game_date)
        events = scoreboard.get("events", [])
        
        games = []
        for event in events:
            try:
                # Extract teams
                competitions = event.get("competitions", [{}])
                if not competitions:
                    continue
                
                competition = competitions[0]
                competitors = competition.get("competitors", [])
                
                home_team = next((c for c in competitors if c.get("homeAway") == "home"), None)
                away_team = next((c for c in competitors if c.get("homeAway") == "away"), None)
                
                if not home_team or not away_team:
                    continue
                
                # Parse start time
                start_time_str = event.get("date")
                start_time = None
                if start_time_str:
                    try:
                        start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
                    except ValueError:
                        pass
                
                games.append({
                    "id": event.get("id"),
                    "sport_key": sport_key,
                    "sport_title": sport_key.split("_")[-1].upper(),
                    "commence_time": start_time.isoformat() if start_time else None,
                    "home_team": home_team.get("team", {}).get("displayName"),
                    "away_team": away_team.get("team", {}).get("displayName"),
                    "status": event.get("status", {}).get("type", {}).get("name"),
                    "home_score": home_team.get("score"),
                    "away_score": away_team.get("score"),
                    # ESPN-specific data
                    "espn_id": event.get("id"),
                    "venue": competition.get("venue", {}).get("fullName"),
                })
            except Exception as e:
                logger.warning(f"[{self.name}] Error parsing event: {e}")
                continue
        
        return games
    
    async def fetch_boxscore(
        self,
        sport_key: str,
        event_id: str,
    ) -> dict[str, Any]:
        """
        Fetch box score for a specific game.
        
        Args:
            sport_key: Standard sport key
            event_id: ESPN event ID
        
        Returns:
            Box score data with player stats
        """
        sport_path = self._get_sport_path(sport_key)
        data = await self._request("GET", f"/{sport_path}/summary", params={"event": event_id})
        return data if isinstance(data, dict) else {}
    
    async def fetch_injuries(
        self,
        sport_key: str,
    ) -> list[dict]:
        """
        Fetch injury report for a sport.
        
        Args:
            sport_key: Standard sport key
        
        Returns:
            List of injury entries
        """
        sport_path = self._get_sport_path(sport_key)
        
        try:
            data = await self._request("GET", f"/{sport_path}/injuries")
            return data.get("injuries", []) if isinstance(data, dict) else []
        except Exception as e:
            logger.warning(f"[{self.name}] Failed to fetch injuries: {e}")
            return []
    
    async def fetch_teams(
        self,
        sport_key: str,
    ) -> list[dict]:
        """
        Fetch teams for a sport.
        
        Args:
            sport_key: Standard sport key
        
        Returns:
            List of team objects
        """
        sport_path = self._get_sport_path(sport_key)
        data = await self._request("GET", f"/{sport_path}/teams")
        
        teams = []
        sports_data = data.get("sports", []) if isinstance(data, dict) else []
        
        for sport in sports_data:
            for league in sport.get("leagues", []):
                for team in league.get("teams", []):
                    team_info = team.get("team", {})
                    teams.append({
                        "id": team_info.get("id"),
                        "name": team_info.get("displayName"),
                        "abbreviation": team_info.get("abbreviation"),
                        "location": team_info.get("location"),
                        "logo": team_info.get("logos", [{}])[0].get("href") if team_info.get("logos") else None,
                    })
        
        return teams
