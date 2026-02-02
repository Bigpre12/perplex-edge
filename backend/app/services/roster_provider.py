"""Roster provider for fetching current team rosters from external APIs."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.core.config import get_settings
from app.core.rate_limiter import get_roster_api_limiter

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

class RosterPlayerData:
    """Normalized roster player data structure."""
    
    def __init__(
        self,
        external_player_id: str,
        first_name: str,
        last_name: str,
        team_id: int,
        team_name: str,
        team_abbreviation: str,
        position: Optional[str] = None,
        jersey_number: Optional[str] = None,
        height: Optional[str] = None,
        weight: Optional[str] = None,
    ):
        self.external_player_id = external_player_id
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = f"{first_name} {last_name}"
        self.team_id = team_id
        self.team_name = team_name
        self.team_abbreviation = team_abbreviation
        self.position = position
        self.jersey_number = jersey_number
        self.height = height
        self.weight = weight
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "external_player_id": self.external_player_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "team_id": self.team_id,
            "team_name": self.team_name,
            "team_abbreviation": self.team_abbreviation,
            "position": self.position,
            "jersey_number": self.jersey_number,
            "height": self.height,
            "weight": self.weight,
        }


class TeamData:
    """Normalized team data structure."""
    
    def __init__(
        self,
        external_team_id: int,
        name: str,
        full_name: str,
        abbreviation: str,
        city: str,
        conference: str,
        division: str,
    ):
        self.external_team_id = external_team_id
        self.name = name
        self.full_name = full_name
        self.abbreviation = abbreviation
        self.city = city
        self.conference = conference
        self.division = division
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "external_team_id": self.external_team_id,
            "name": self.name,
            "full_name": self.full_name,
            "abbreviation": self.abbreviation,
            "city": self.city,
            "conference": self.conference,
            "division": self.division,
        }


# =============================================================================
# Team Name Mappings (balldontlie.io format to standard format)
# =============================================================================

TEAM_NAME_MAPPING = {
    "Hawks": "Atlanta Hawks",
    "Celtics": "Boston Celtics",
    "Nets": "Brooklyn Nets",
    "Hornets": "Charlotte Hornets",
    "Bulls": "Chicago Bulls",
    "Cavaliers": "Cleveland Cavaliers",
    "Mavericks": "Dallas Mavericks",
    "Nuggets": "Denver Nuggets",
    "Pistons": "Detroit Pistons",
    "Warriors": "Golden State Warriors",
    "Rockets": "Houston Rockets",
    "Pacers": "Indiana Pacers",
    "Clippers": "Los Angeles Clippers",
    "Lakers": "Los Angeles Lakers",
    "Grizzlies": "Memphis Grizzlies",
    "Heat": "Miami Heat",
    "Bucks": "Milwaukee Bucks",
    "Timberwolves": "Minnesota Timberwolves",
    "Pelicans": "New Orleans Pelicans",
    "Knicks": "New York Knicks",
    "Thunder": "Oklahoma City Thunder",
    "Magic": "Orlando Magic",
    "76ers": "Philadelphia 76ers",
    "Suns": "Phoenix Suns",
    "Trail Blazers": "Portland Trail Blazers",
    "Kings": "Sacramento Kings",
    "Spurs": "San Antonio Spurs",
    "Raptors": "Toronto Raptors",
    "Jazz": "Utah Jazz",
    "Wizards": "Washington Wizards",
}


# =============================================================================
# Roster Provider
# =============================================================================

class RosterProvider:
    """
    Provider for fetching roster data from external APIs.
    
    Uses balldontlie.io API for NBA roster data.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        use_stubs: bool = False,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.roster_api_key
        self.base_url = base_url or settings.roster_api_base_url
        self.use_stubs = use_stubs
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self) -> "RosterProvider":
        self._client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()
    
    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        return self._client
    
    async def _request(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a request to the roster API."""
        # Enforce rate limiting before making request
        await get_roster_api_limiter().wait()
        
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        # balldontlie.io requires API key in Authorization header
        if self.api_key:
            headers["Authorization"] = self.api_key
        
        response = await self.client.get(url, params=params, headers=headers)
        
        # Handle HTTP errors gracefully
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 422:
                # 422 typically means validation error - log and return empty
                logger.warning(
                    f"Roster API returned 422 for {endpoint}: {e.response.text[:500]}"
                )
                return []
            elif e.response.status_code == 429:
                # Rate limited
                logger.warning(f"Roster API rate limited: {e.response.text[:200]}")
                return []
            elif e.response.status_code == 404:
                # Resource not found - not necessarily an error
                logger.info(f"Roster API resource not found: {endpoint}")
                return []
            else:
                # Re-raise other errors
                logger.error(f"Roster API error {e.response.status_code}: {e.response.text[:500]}")
                raise
        
        return response.json()
    
    # =========================================================================
    # Public API Methods
    # =========================================================================
    
    async def fetch_teams(self) -> list[TeamData]:
        """
        Fetch all NBA teams.
        
        Returns:
            List of TeamData objects
        """
        if self.use_stubs:
            raw_data = self._stub_teams_response()
        else:
            raw_data = await self._request("/teams")
        
        return self._parse_teams(raw_data)
    
    async def fetch_players(
        self,
        team_ids: Optional[list[int]] = None,
        search: Optional[str] = None,
        per_page: int = 100,
        cursor: Optional[int] = None,
    ) -> tuple[list[RosterPlayerData], Optional[int]]:
        """
        Fetch players, optionally filtered by team or search query.
        
        Args:
            team_ids: Filter by team IDs
            search: Search by player name
            per_page: Number of results per page (max 100)
            cursor: Cursor for pagination
        
        Returns:
            Tuple of (list of RosterPlayerData, next_cursor or None)
        """
        if self.use_stubs:
            raw_data = self._stub_players_response(team_ids, search)
            return self._parse_players(raw_data), None
        
        params: dict[str, Any] = {"per_page": per_page}
        
        if team_ids:
            params["team_ids[]"] = team_ids
        if search:
            params["search"] = search
        if cursor:
            params["cursor"] = cursor
        
        raw_data = await self._request("/players", params)
        
        # Parse next cursor from meta
        next_cursor = None
        if isinstance(raw_data, dict) and "meta" in raw_data:
            next_cursor = raw_data["meta"].get("next_cursor")
        
        return self._parse_players(raw_data), next_cursor
    
    async def fetch_all_players_for_team(
        self,
        team_id: int,
    ) -> list[RosterPlayerData]:
        """
        Fetch all players for a specific team (handles pagination).
        
        Args:
            team_id: Team ID to fetch players for
        
        Returns:
            List of all RosterPlayerData for the team
        """
        all_players: list[RosterPlayerData] = []
        cursor = None
        
        while True:
            players, next_cursor = await self.fetch_players(
                team_ids=[team_id],
                cursor=cursor,
            )
            all_players.extend(players)
            
            if not next_cursor:
                break
            cursor = next_cursor
        
        return all_players
    
    async def fetch_player_by_name(
        self,
        player_name: str,
    ) -> Optional[RosterPlayerData]:
        """
        Search for a player by name.
        
        Args:
            player_name: Player name to search for
        
        Returns:
            RosterPlayerData if found, None otherwise
        """
        players, _ = await self.fetch_players(search=player_name, per_page=25)
        
        # Try exact match first
        for player in players:
            if player.full_name.lower() == player_name.lower():
                return player
        
        # Try partial match
        for player in players:
            if player_name.lower() in player.full_name.lower():
                return player
        
        return None
    
    # =========================================================================
    # Parsing Methods
    # =========================================================================
    
    def _parse_teams(self, raw_data: dict[str, Any] | list[dict[str, Any]]) -> list[TeamData]:
        """Parse teams from API response."""
        teams = []
        
        # Handle both list and dict (with 'data' key) responses
        if isinstance(raw_data, dict):
            data = raw_data.get("data", [])
        else:
            data = raw_data
        
        for entry in data:
            full_name = entry.get("full_name", "")
            name = entry.get("name", "")
            
            teams.append(TeamData(
                external_team_id=entry["id"],
                name=name,
                full_name=full_name,
                abbreviation=entry.get("abbreviation", ""),
                city=entry.get("city", ""),
                conference=entry.get("conference", ""),
                division=entry.get("division", ""),
            ))
        
        return teams
    
    def _parse_players(self, raw_data: dict[str, Any] | list[dict[str, Any]]) -> list[RosterPlayerData]:
        """Parse players from API response."""
        players = []
        
        # Handle both list and dict (with 'data' key) responses
        if isinstance(raw_data, dict):
            data = raw_data.get("data", [])
        else:
            data = raw_data
        
        for entry in data:
            team = entry.get("team", {})
            if not team:
                continue
            
            # Get standardized team name
            team_name = team.get("name", "")
            full_team_name = TEAM_NAME_MAPPING.get(team_name, team.get("full_name", team_name))
            
            players.append(RosterPlayerData(
                external_player_id=str(entry["id"]),
                first_name=entry.get("first_name", ""),
                last_name=entry.get("last_name", ""),
                team_id=team.get("id", 0),
                team_name=full_team_name,
                team_abbreviation=team.get("abbreviation", ""),
                position=entry.get("position", None),
                jersey_number=entry.get("jersey_number", None),
                height=entry.get("height", None),
                weight=entry.get("weight", None),
            ))
        
        return players
    
    # =========================================================================
    # Stub Methods for Testing
    # =========================================================================
    
    def _stub_teams_response(self) -> dict[str, Any]:
        """Return realistic stub team data for testing."""
        return {
            "data": [
                {"id": 1, "abbreviation": "ATL", "city": "Atlanta", "conference": "East", "division": "Southeast", "full_name": "Atlanta Hawks", "name": "Hawks"},
                {"id": 2, "abbreviation": "BOS", "city": "Boston", "conference": "East", "division": "Atlantic", "full_name": "Boston Celtics", "name": "Celtics"},
                {"id": 3, "abbreviation": "BKN", "city": "Brooklyn", "conference": "East", "division": "Atlantic", "full_name": "Brooklyn Nets", "name": "Nets"},
                {"id": 4, "abbreviation": "CHA", "city": "Charlotte", "conference": "East", "division": "Southeast", "full_name": "Charlotte Hornets", "name": "Hornets"},
                {"id": 5, "abbreviation": "CHI", "city": "Chicago", "conference": "East", "division": "Central", "full_name": "Chicago Bulls", "name": "Bulls"},
                {"id": 6, "abbreviation": "CLE", "city": "Cleveland", "conference": "East", "division": "Central", "full_name": "Cleveland Cavaliers", "name": "Cavaliers"},
                {"id": 7, "abbreviation": "DAL", "city": "Dallas", "conference": "West", "division": "Southwest", "full_name": "Dallas Mavericks", "name": "Mavericks"},
                {"id": 8, "abbreviation": "DEN", "city": "Denver", "conference": "West", "division": "Northwest", "full_name": "Denver Nuggets", "name": "Nuggets"},
                {"id": 9, "abbreviation": "DET", "city": "Detroit", "conference": "East", "division": "Central", "full_name": "Detroit Pistons", "name": "Pistons"},
                {"id": 10, "abbreviation": "GSW", "city": "Golden State", "conference": "West", "division": "Pacific", "full_name": "Golden State Warriors", "name": "Warriors"},
                {"id": 11, "abbreviation": "HOU", "city": "Houston", "conference": "West", "division": "Southwest", "full_name": "Houston Rockets", "name": "Rockets"},
                {"id": 12, "abbreviation": "IND", "city": "Indiana", "conference": "East", "division": "Central", "full_name": "Indiana Pacers", "name": "Pacers"},
                {"id": 13, "abbreviation": "LAC", "city": "Los Angeles", "conference": "West", "division": "Pacific", "full_name": "Los Angeles Clippers", "name": "Clippers"},
                {"id": 14, "abbreviation": "LAL", "city": "Los Angeles", "conference": "West", "division": "Pacific", "full_name": "Los Angeles Lakers", "name": "Lakers"},
                {"id": 15, "abbreviation": "MEM", "city": "Memphis", "conference": "West", "division": "Southwest", "full_name": "Memphis Grizzlies", "name": "Grizzlies"},
                {"id": 16, "abbreviation": "MIA", "city": "Miami", "conference": "East", "division": "Southeast", "full_name": "Miami Heat", "name": "Heat"},
                {"id": 17, "abbreviation": "MIL", "city": "Milwaukee", "conference": "East", "division": "Central", "full_name": "Milwaukee Bucks", "name": "Bucks"},
                {"id": 18, "abbreviation": "MIN", "city": "Minnesota", "conference": "West", "division": "Northwest", "full_name": "Minnesota Timberwolves", "name": "Timberwolves"},
                {"id": 19, "abbreviation": "NOP", "city": "New Orleans", "conference": "West", "division": "Southwest", "full_name": "New Orleans Pelicans", "name": "Pelicans"},
                {"id": 20, "abbreviation": "NYK", "city": "New York", "conference": "East", "division": "Atlantic", "full_name": "New York Knicks", "name": "Knicks"},
                {"id": 21, "abbreviation": "OKC", "city": "Oklahoma City", "conference": "West", "division": "Northwest", "full_name": "Oklahoma City Thunder", "name": "Thunder"},
                {"id": 22, "abbreviation": "ORL", "city": "Orlando", "conference": "East", "division": "Southeast", "full_name": "Orlando Magic", "name": "Magic"},
                {"id": 23, "abbreviation": "PHI", "city": "Philadelphia", "conference": "East", "division": "Atlantic", "full_name": "Philadelphia 76ers", "name": "76ers"},
                {"id": 24, "abbreviation": "PHX", "city": "Phoenix", "conference": "West", "division": "Pacific", "full_name": "Phoenix Suns", "name": "Suns"},
                {"id": 25, "abbreviation": "POR", "city": "Portland", "conference": "West", "division": "Northwest", "full_name": "Portland Trail Blazers", "name": "Trail Blazers"},
                {"id": 26, "abbreviation": "SAC", "city": "Sacramento", "conference": "West", "division": "Pacific", "full_name": "Sacramento Kings", "name": "Kings"},
                {"id": 27, "abbreviation": "SAS", "city": "San Antonio", "conference": "West", "division": "Southwest", "full_name": "San Antonio Spurs", "name": "Spurs"},
                {"id": 28, "abbreviation": "TOR", "city": "Toronto", "conference": "East", "division": "Atlantic", "full_name": "Toronto Raptors", "name": "Raptors"},
                {"id": 29, "abbreviation": "UTA", "city": "Utah", "conference": "West", "division": "Northwest", "full_name": "Utah Jazz", "name": "Jazz"},
                {"id": 30, "abbreviation": "WAS", "city": "Washington", "conference": "East", "division": "Southeast", "full_name": "Washington Wizards", "name": "Wizards"},
            ]
        }
    
    def _stub_players_response(
        self,
        team_ids: Optional[list[int]] = None,
        search: Optional[str] = None,
    ) -> dict[str, Any]:
        """Return realistic stub player data for testing - January 2026 rosters."""
        all_players = [
            # Dallas Mavericks (id: 7) - Now have AD, Kyrie, Klay, D'Lo
            {"id": 1001, "first_name": "Anthony", "last_name": "Davis", "position": "F-C", "team": {"id": 7, "abbreviation": "DAL", "name": "Mavericks", "full_name": "Dallas Mavericks"}},
            {"id": 1002, "first_name": "Kyrie", "last_name": "Irving", "position": "G", "team": {"id": 7, "abbreviation": "DAL", "name": "Mavericks", "full_name": "Dallas Mavericks"}},
            {"id": 1003, "first_name": "Klay", "last_name": "Thompson", "position": "G", "team": {"id": 7, "abbreviation": "DAL", "name": "Mavericks", "full_name": "Dallas Mavericks"}},
            {"id": 1004, "first_name": "D'Angelo", "last_name": "Russell", "position": "G", "team": {"id": 7, "abbreviation": "DAL", "name": "Mavericks", "full_name": "Dallas Mavericks"}},
            {"id": 1005, "first_name": "P.J.", "last_name": "Washington", "position": "F", "team": {"id": 7, "abbreviation": "DAL", "name": "Mavericks", "full_name": "Dallas Mavericks"}},
            
            # Los Angeles Lakers (id: 14) - Now have Luka, LeBron, Ayton, Smart
            {"id": 2001, "first_name": "LeBron", "last_name": "James", "position": "F", "team": {"id": 14, "abbreviation": "LAL", "name": "Lakers", "full_name": "Los Angeles Lakers"}},
            {"id": 2002, "first_name": "Luka", "last_name": "Doncic", "position": "G", "team": {"id": 14, "abbreviation": "LAL", "name": "Lakers", "full_name": "Los Angeles Lakers"}},
            {"id": 2003, "first_name": "Austin", "last_name": "Reaves", "position": "G", "team": {"id": 14, "abbreviation": "LAL", "name": "Lakers", "full_name": "Los Angeles Lakers"}},
            {"id": 2004, "first_name": "Deandre", "last_name": "Ayton", "position": "C", "team": {"id": 14, "abbreviation": "LAL", "name": "Lakers", "full_name": "Los Angeles Lakers"}},
            {"id": 2005, "first_name": "Marcus", "last_name": "Smart", "position": "G", "team": {"id": 14, "abbreviation": "LAL", "name": "Lakers", "full_name": "Los Angeles Lakers"}},
            
            # Golden State Warriors (id: 10) - Now have Curry, Butler, Draymond, Horford
            {"id": 3001, "first_name": "Stephen", "last_name": "Curry", "position": "G", "team": {"id": 10, "abbreviation": "GSW", "name": "Warriors", "full_name": "Golden State Warriors"}},
            {"id": 3002, "first_name": "Jimmy", "last_name": "Butler", "position": "F", "team": {"id": 10, "abbreviation": "GSW", "name": "Warriors", "full_name": "Golden State Warriors"}},
            {"id": 3003, "first_name": "Draymond", "last_name": "Green", "position": "F", "team": {"id": 10, "abbreviation": "GSW", "name": "Warriors", "full_name": "Golden State Warriors"}},
            {"id": 3004, "first_name": "Al", "last_name": "Horford", "position": "C", "team": {"id": 10, "abbreviation": "GSW", "name": "Warriors", "full_name": "Golden State Warriors"}},
            {"id": 3005, "first_name": "Jonathan", "last_name": "Kuminga", "position": "F", "team": {"id": 10, "abbreviation": "GSW", "name": "Warriors", "full_name": "Golden State Warriors"}},
            
            # Houston Rockets (id: 11) - Now have Durant, Sengun, VanVleet
            {"id": 4001, "first_name": "Kevin", "last_name": "Durant", "position": "F", "team": {"id": 11, "abbreviation": "HOU", "name": "Rockets", "full_name": "Houston Rockets"}},
            {"id": 4002, "first_name": "Alperen", "last_name": "Sengun", "position": "C", "team": {"id": 11, "abbreviation": "HOU", "name": "Rockets", "full_name": "Houston Rockets"}},
            {"id": 4003, "first_name": "Fred", "last_name": "VanVleet", "position": "G", "team": {"id": 11, "abbreviation": "HOU", "name": "Rockets", "full_name": "Houston Rockets"}},
            {"id": 4004, "first_name": "Clint", "last_name": "Capela", "position": "C", "team": {"id": 11, "abbreviation": "HOU", "name": "Rockets", "full_name": "Houston Rockets"}},
            
            # Oklahoma City Thunder (id: 21) - 2025 Champions
            {"id": 5001, "first_name": "Shai", "last_name": "Gilgeous-Alexander", "position": "G", "team": {"id": 21, "abbreviation": "OKC", "name": "Thunder", "full_name": "Oklahoma City Thunder"}},
            {"id": 5002, "first_name": "Chet", "last_name": "Holmgren", "position": "C", "team": {"id": 21, "abbreviation": "OKC", "name": "Thunder", "full_name": "Oklahoma City Thunder"}},
            {"id": 5003, "first_name": "Jalen", "last_name": "Williams", "position": "G-F", "team": {"id": 21, "abbreviation": "OKC", "name": "Thunder", "full_name": "Oklahoma City Thunder"}},
            {"id": 5004, "first_name": "Alex", "last_name": "Caruso", "position": "G", "team": {"id": 21, "abbreviation": "OKC", "name": "Thunder", "full_name": "Oklahoma City Thunder"}},
            
            # San Antonio Spurs (id: 27) - Now have Fox and Wembanyama
            {"id": 6001, "first_name": "Victor", "last_name": "Wembanyama", "position": "C", "team": {"id": 27, "abbreviation": "SAS", "name": "Spurs", "full_name": "San Antonio Spurs"}},
            {"id": 6002, "first_name": "De'Aaron", "last_name": "Fox", "position": "G", "team": {"id": 27, "abbreviation": "SAS", "name": "Spurs", "full_name": "San Antonio Spurs"}},
            {"id": 6003, "first_name": "Stephon", "last_name": "Castle", "position": "G", "team": {"id": 27, "abbreviation": "SAS", "name": "Spurs", "full_name": "San Antonio Spurs"}},
            
            # Denver Nuggets (id: 8)
            {"id": 7001, "first_name": "Nikola", "last_name": "Jokic", "position": "C", "team": {"id": 8, "abbreviation": "DEN", "name": "Nuggets", "full_name": "Denver Nuggets"}},
            {"id": 7002, "first_name": "Jamal", "last_name": "Murray", "position": "G", "team": {"id": 8, "abbreviation": "DEN", "name": "Nuggets", "full_name": "Denver Nuggets"}},
            {"id": 7003, "first_name": "Cameron", "last_name": "Johnson", "position": "F", "team": {"id": 8, "abbreviation": "DEN", "name": "Nuggets", "full_name": "Denver Nuggets"}},
            
            # New York Knicks (id: 20) - Now have KAT, Bridges, Brunson
            {"id": 8001, "first_name": "Jalen", "last_name": "Brunson", "position": "G", "team": {"id": 20, "abbreviation": "NYK", "name": "Knicks", "full_name": "New York Knicks"}},
            {"id": 8002, "first_name": "Karl-Anthony", "last_name": "Towns", "position": "C", "team": {"id": 20, "abbreviation": "NYK", "name": "Knicks", "full_name": "New York Knicks"}},
            {"id": 8003, "first_name": "Mikal", "last_name": "Bridges", "position": "F", "team": {"id": 20, "abbreviation": "NYK", "name": "Knicks", "full_name": "New York Knicks"}},
            {"id": 8004, "first_name": "OG", "last_name": "Anunoby", "position": "F", "team": {"id": 20, "abbreviation": "NYK", "name": "Knicks", "full_name": "New York Knicks"}},
            
            # Miami Heat (id: 16) - Now have Wiggins instead of Butler
            {"id": 9001, "first_name": "Bam", "last_name": "Adebayo", "position": "C", "team": {"id": 16, "abbreviation": "MIA", "name": "Heat", "full_name": "Miami Heat"}},
            {"id": 9002, "first_name": "Tyler", "last_name": "Herro", "position": "G", "team": {"id": 16, "abbreviation": "MIA", "name": "Heat", "full_name": "Miami Heat"}},
            {"id": 9003, "first_name": "Andrew", "last_name": "Wiggins", "position": "F", "team": {"id": 16, "abbreviation": "MIA", "name": "Heat", "full_name": "Miami Heat"}},
            {"id": 9004, "first_name": "Terry", "last_name": "Rozier", "position": "G", "team": {"id": 16, "abbreviation": "MIA", "name": "Heat", "full_name": "Miami Heat"}},
        ]
        
        # Filter by team_ids if provided
        if team_ids:
            all_players = [p for p in all_players if p["team"]["id"] in team_ids]
        
        # Filter by search if provided
        if search:
            search_lower = search.lower()
            all_players = [
                p for p in all_players
                if search_lower in f"{p['first_name']} {p['last_name']}".lower()
            ]
        
        return {"data": all_players, "meta": {"next_cursor": None}}
