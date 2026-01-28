"""Injury provider for fetching injury status, availability, and lineup data."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Sport, Player, Injury

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

class InjuryData:
    """Normalized injury data structure."""
    
    # Injury status constants
    STATUS_OUT = "OUT"
    STATUS_DOUBTFUL = "DOUBTFUL"
    STATUS_QUESTIONABLE = "QUESTIONABLE"
    STATUS_PROBABLE = "PROBABLE"
    STATUS_GTD = "GTD"  # Game Time Decision
    STATUS_AVAILABLE = "AVAILABLE"
    
    def __init__(
        self,
        player_external_id: str,
        player_name: str,
        team_name: str,
        status: str,
        injury_detail: Optional[str] = None,
        probability: Optional[float] = None,
        is_starter: Optional[bool] = None,
        expected_return: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        source: Optional[str] = None,
    ):
        self.player_external_id = player_external_id
        self.player_name = player_name
        self.team_name = team_name
        self.status = status
        self.injury_detail = injury_detail
        self.probability = probability
        self.is_starter = is_starter
        self.expected_return = expected_return
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self.source = source
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "player_external_id": self.player_external_id,
            "player_name": self.player_name,
            "team_name": self.team_name,
            "status": self.status,
            "injury_detail": self.injury_detail,
            "probability": self.probability,
            "is_starter": self.is_starter,
            "expected_return": self.expected_return.isoformat() if self.expected_return else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "source": self.source,
        }


class LineupData:
    """Normalized lineup/starter data structure."""
    
    def __init__(
        self,
        player_external_id: str,
        player_name: str,
        team_name: str,
        position: str,
        is_starter: bool,
        is_confirmed: bool = False,
        updated_at: Optional[datetime] = None,
    ):
        self.player_external_id = player_external_id
        self.player_name = player_name
        self.team_name = team_name
        self.position = position
        self.is_starter = is_starter
        self.is_confirmed = is_confirmed
        self.updated_at = updated_at or datetime.now(timezone.utc)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "player_external_id": self.player_external_id,
            "player_name": self.player_name,
            "team_name": self.team_name,
            "position": self.position,
            "is_starter": self.is_starter,
            "is_confirmed": self.is_confirmed,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# =============================================================================
# Sport Key Mappings
# =============================================================================

SPORT_KEYS = {
    "NBA": "basketball_nba",
    "NFL": "americanfootball_nfl",
    "MLB": "baseball_mlb",
    "NHL": "icehockey_nhl",
    "NCAAB": "basketball_ncaab",
    "NCAAF": "americanfootball_ncaaf",
}


# =============================================================================
# Injury Provider
# =============================================================================

class InjuryProvider:
    """
    Provider for fetching injury and lineup data from external APIs.
    
    Fetches injury reports, expected availability, and starting lineups.
    Writes to the Injury table.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        use_stubs: bool = False,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.injury_api_key
        self.base_url = base_url or settings.injury_api_base_url
        self.use_stubs = use_stubs
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self) -> "InjuryProvider":
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
        """Make an authenticated request to the injury API."""
        if not self.api_key:
            raise ValueError("INJURY_API_KEY not configured")
        
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    # =========================================================================
    # Public API Methods
    # =========================================================================
    
    async def fetch_injuries(
        self,
        sport_key: str,
        team: Optional[str] = None,
    ) -> list[InjuryData]:
        """
        Fetch current injury reports for a sport.
        
        Args:
            sport_key: Sport identifier (e.g., 'basketball_nba')
            team: Optional team filter
        
        Returns:
            List of InjuryData objects
        """
        if self.use_stubs:
            raw_data = self._stub_injuries_response(sport_key, team)
        else:
            params = {}
            if team:
                params["team"] = team
            raw_data = await self._request(f"/sports/{sport_key}/injuries", params)
        
        return self._parse_injuries(raw_data)
    
    async def fetch_lineups(
        self,
        sport_key: str,
        external_game_id: Optional[str] = None,
    ) -> list[LineupData]:
        """
        Fetch expected starting lineups.
        
        Args:
            sport_key: Sport identifier
            external_game_id: Optional specific game
        
        Returns:
            List of LineupData objects
        """
        if self.use_stubs:
            raw_data = self._stub_lineups_response(sport_key, external_game_id)
        else:
            params = {}
            if external_game_id:
                params["game_id"] = external_game_id
            raw_data = await self._request(f"/sports/{sport_key}/lineups", params)
        
        return self._parse_lineups(raw_data)
    
    async def fetch_player_injury(
        self,
        external_player_id: str,
    ) -> Optional[InjuryData]:
        """
        Fetch injury status for a specific player.
        
        Args:
            external_player_id: External player ID
        
        Returns:
            InjuryData if player has injury status, None otherwise
        """
        if self.use_stubs:
            raw_data = self._stub_player_injury_response(external_player_id)
        else:
            try:
                raw_data = await self._request(f"/players/{external_player_id}/injury")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                raise
        
        if not raw_data:
            return None
        
        injuries = self._parse_injuries({"injuries": [raw_data]})
        return injuries[0] if injuries else None
    
    # =========================================================================
    # Database Write Methods
    # =========================================================================
    
    async def sync_injuries(
        self,
        db: AsyncSession,
        sport_id: int,
        injuries: list[InjuryData],
    ) -> dict[str, int]:
        """
        Sync injury data to the Injury table.
        
        Args:
            db: Database session
            sport_id: Internal sport ID
            injuries: List of InjuryData objects
        
        Returns:
            Dictionary with counts: {'created': n, 'updated': n, 'skipped': n}
        """
        counts = {"created": 0, "updated": 0, "skipped": 0}
        
        for injury_data in injuries:
            # Find the player
            result = await db.execute(
                select(Player).where(
                    Player.external_player_id == injury_data.player_external_id
                )
            )
            player = result.scalar_one_or_none()
            
            if not player:
                logger.warning(f"Player not found: {injury_data.player_external_id}")
                counts["skipped"] += 1
                continue
            
            # Check for existing injury record
            result = await db.execute(
                select(Injury).where(
                    Injury.sport_id == sport_id,
                    Injury.player_id == player.id,
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing record
                existing.status = injury_data.status
                existing.status_detail = injury_data.injury_detail
                existing.is_starter_flag = injury_data.is_starter
                existing.probability = injury_data.probability
                existing.source = injury_data.source
                existing.updated_at = injury_data.updated_at
                counts["updated"] += 1
            else:
                # Create new record
                injury = Injury(
                    sport_id=sport_id,
                    player_id=player.id,
                    status=injury_data.status,
                    status_detail=injury_data.injury_detail,
                    is_starter_flag=injury_data.is_starter,
                    probability=injury_data.probability,
                    source=injury_data.source,
                    updated_at=injury_data.updated_at,
                )
                db.add(injury)
                counts["created"] += 1
        
        await db.commit()
        return counts
    
    async def sync_sport_injuries(
        self,
        db: AsyncSession,
        sport_key: str,
    ) -> dict[str, int]:
        """
        Fetch and sync all injuries for a sport.
        
        Args:
            db: Database session
            sport_key: Sport identifier (e.g., 'basketball_nba')
        
        Returns:
            Sync counts dictionary
        """
        # Find sport
        league_code = sport_key.split("_")[-1].upper()
        result = await db.execute(
            select(Sport).where(Sport.league_code == league_code)
        )
        sport = result.scalar_one_or_none()
        
        if not sport:
            logger.warning(f"Sport not found: {league_code}")
            return {"created": 0, "updated": 0, "skipped": 0}
        
        # Fetch and sync
        injuries = await self.fetch_injuries(sport_key)
        return await self.sync_injuries(db, sport.id, injuries)
    
    async def update_starter_flags(
        self,
        db: AsyncSession,
        sport_id: int,
        lineups: list[LineupData],
    ) -> int:
        """
        Update is_starter_flag on existing injury records based on lineup data.
        
        Args:
            db: Database session
            sport_id: Internal sport ID
            lineups: List of LineupData objects
        
        Returns:
            Number of records updated
        """
        updated = 0
        
        for lineup in lineups:
            # Find player
            result = await db.execute(
                select(Player).where(
                    Player.external_player_id == lineup.player_external_id
                )
            )
            player = result.scalar_one_or_none()
            
            if not player:
                continue
            
            # Update injury record if exists
            result = await db.execute(
                select(Injury).where(
                    Injury.sport_id == sport_id,
                    Injury.player_id == player.id,
                )
            )
            injury = result.scalar_one_or_none()
            
            if injury:
                injury.is_starter_flag = lineup.is_starter
                injury.updated_at = lineup.updated_at
                updated += 1
        
        await db.commit()
        return updated
    
    # =========================================================================
    # Parsing Methods
    # =========================================================================
    
    def _parse_injuries(self, raw_data: dict[str, Any]) -> list[InjuryData]:
        """Parse injuries from API response."""
        injuries = []
        
        for entry in raw_data.get("injuries", []):
            # Map status to standardized values
            raw_status = entry.get("status", "").upper()
            status = self._normalize_status(raw_status)
            
            # Parse expected return date if present
            expected_return = None
            if entry.get("expected_return"):
                try:
                    expected_return = datetime.fromisoformat(
                        entry["expected_return"].replace("Z", "+00:00")
                    )
                except ValueError:
                    pass
            
            # Parse updated timestamp
            updated_at = datetime.now(timezone.utc)
            if entry.get("updated"):
                try:
                    updated_at = datetime.fromisoformat(
                        entry["updated"].replace("Z", "+00:00")
                    )
                except ValueError:
                    pass
            
            injuries.append(InjuryData(
                player_external_id=entry["player_id"],
                player_name=entry.get("player_name", ""),
                team_name=entry.get("team", ""),
                status=status,
                injury_detail=entry.get("injury"),
                probability=entry.get("probability"),
                is_starter=entry.get("is_starter"),
                expected_return=expected_return,
                updated_at=updated_at,
                source=entry.get("source", "injury_api"),
            ))
        
        return injuries
    
    def _parse_lineups(self, raw_data: dict[str, Any]) -> list[LineupData]:
        """Parse lineups from API response."""
        lineups = []
        
        for game in raw_data.get("games", []):
            for team_data in [game.get("home", {}), game.get("away", {})]:
                team_name = team_data.get("team", "")
                
                for player in team_data.get("lineup", []):
                    updated_at = datetime.now(timezone.utc)
                    if player.get("updated"):
                        try:
                            updated_at = datetime.fromisoformat(
                                player["updated"].replace("Z", "+00:00")
                            )
                        except ValueError:
                            pass
                    
                    lineups.append(LineupData(
                        player_external_id=player["player_id"],
                        player_name=player.get("player_name", ""),
                        team_name=team_name,
                        position=player.get("position", ""),
                        is_starter=player.get("is_starter", False),
                        is_confirmed=player.get("confirmed", False),
                        updated_at=updated_at,
                    ))
        
        return lineups
    
    def _normalize_status(self, raw_status: str) -> str:
        """Normalize injury status to standard values."""
        status_map = {
            "OUT": InjuryData.STATUS_OUT,
            "O": InjuryData.STATUS_OUT,
            "DOUBTFUL": InjuryData.STATUS_DOUBTFUL,
            "D": InjuryData.STATUS_DOUBTFUL,
            "QUESTIONABLE": InjuryData.STATUS_QUESTIONABLE,
            "Q": InjuryData.STATUS_QUESTIONABLE,
            "PROBABLE": InjuryData.STATUS_PROBABLE,
            "P": InjuryData.STATUS_PROBABLE,
            "GTD": InjuryData.STATUS_GTD,
            "GAME TIME DECISION": InjuryData.STATUS_GTD,
            "GAME-TIME DECISION": InjuryData.STATUS_GTD,
            "AVAILABLE": InjuryData.STATUS_AVAILABLE,
            "ACTIVE": InjuryData.STATUS_AVAILABLE,
            "HEALTHY": InjuryData.STATUS_AVAILABLE,
        }
        return status_map.get(raw_status.upper(), raw_status)
    
    # =========================================================================
    # Stub Methods for Testing
    # =========================================================================
    
    def _stub_injuries_response(
        self,
        sport_key: str,
        team: Optional[str] = None,
    ) -> dict[str, Any]:
        """Return realistic stub injury data for testing - January 2026 rosters."""
        injuries = []
        
        if "basketball" in sport_key:
            injuries = [
                # =================================================================
                # KEY STAR INJURIES
                # =================================================================
                {
                    "player_id": "nikola_jokic_001",
                    "player_name": "Nikola Jokic",
                    "team": "Denver Nuggets",
                    "status": "OUT",
                    "injury": "Knee",
                    "probability": 0.0,
                    "is_starter": None,
                    "expected_return": "2026-02-05T00:00:00Z",
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "jayson_tatum_002",
                    "player_name": "Jayson Tatum",
                    "team": "Boston Celtics",
                    "status": "OUT",
                    "injury": "Achilles",
                    "probability": 0.0,
                    "is_starter": None,
                    "expected_return": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "giannis_antetokounmpo_003",
                    "player_name": "Giannis Antetokounmpo",
                    "team": "Milwaukee Bucks",
                    "status": "OUT",
                    "injury": "Calf",
                    "probability": 0.0,
                    "is_starter": None,
                    "expected_return": "2026-02-20T00:00:00Z",
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "stephen_curry_004",
                    "player_name": "Stephen Curry",
                    "team": "Golden State Warriors",
                    "status": "DAY_TO_DAY",
                    "injury": "Knee",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "anthony_davis_005",
                    "player_name": "Anthony Davis",
                    "team": "Dallas Mavericks",
                    "status": "OUT",
                    "injury": "Hand",
                    "probability": 0.0,
                    "is_starter": None,
                    "expected_return": "2026-04-15T00:00:00Z",
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "jimmy_butler_006",
                    "player_name": "Jimmy Butler",
                    "team": "Golden State Warriors",
                    "status": "OUT",
                    "injury": "Knee - ACL (Season-ending)",
                    "probability": 0.0,
                    "is_starter": None,
                    "expected_return": "2026-10-01T00:00:00Z",
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "kyrie_irving_007",
                    "player_name": "Kyrie Irving",
                    "team": "Dallas Mavericks",
                    "status": "OUT",
                    "injury": "Knee",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "trae_young_008",
                    "player_name": "Trae Young",
                    "team": "Washington Wizards",
                    "status": "OUT",
                    "injury": "Undisclosed",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "ja_morant_009",
                    "player_name": "Ja Morant",
                    "team": "Memphis Grizzlies",
                    "status": "OUT",
                    "injury": "Elbow",
                    "probability": 0.0,
                    "is_starter": None,
                    "expected_return": "2026-02-20T00:00:00Z",
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "joel_embiid_010",
                    "player_name": "Joel Embiid",
                    "team": "Philadelphia 76ers",
                    "status": "DAY_TO_DAY",
                    "injury": "Rest",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # ATLANTA HAWKS
                # =================================================================
                {
                    "player_id": "kristaps_porzingis_011",
                    "player_name": "Kristaps Porzingis",
                    "team": "Atlanta Hawks",
                    "status": "OUT",
                    "injury": "Achilles",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "zaccharie_risacher_012",
                    "player_name": "Zaccharie Risacher",
                    "team": "Atlanta Hawks",
                    "status": "OUT",
                    "injury": "Knee",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "nfaly_dante_013",
                    "player_name": "N'Faly Dante",
                    "team": "Atlanta Hawks",
                    "status": "OUT",
                    "injury": "Knee (Season-ending)",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # BOSTON CELTICS
                # =================================================================
                {
                    "player_id": "neemias_queta_014",
                    "player_name": "Neemias Queta",
                    "team": "Boston Celtics",
                    "status": "DAY_TO_DAY",
                    "injury": "Illness",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "luka_garza_015",
                    "player_name": "Luka Garza",
                    "team": "Boston Celtics",
                    "status": "DAY_TO_DAY",
                    "injury": "Illness",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # BROOKLYN NETS
                # =================================================================
                {
                    "player_id": "haywood_highsmith_016",
                    "player_name": "Haywood Highsmith",
                    "team": "Brooklyn Nets",
                    "status": "OUT",
                    "injury": "Knee",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "tyrese_martin_017",
                    "player_name": "Tyrese Martin",
                    "team": "Brooklyn Nets",
                    "status": "DAY_TO_DAY",
                    "injury": "Knee",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "noah_clowney_018",
                    "player_name": "Noah Clowney",
                    "team": "Brooklyn Nets",
                    "status": "DAY_TO_DAY",
                    "injury": "Back",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # CHARLOTTE HORNETS
                # =================================================================
                {
                    "player_id": "mason_plumlee_019",
                    "player_name": "Mason Plumlee",
                    "team": "Charlotte Hornets",
                    "status": "OUT",
                    "injury": "Groin",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "kj_simpson_020",
                    "player_name": "KJ Simpson",
                    "team": "Charlotte Hornets",
                    "status": "DAY_TO_DAY",
                    "injury": "Hip",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # CHICAGO BULLS
                # =================================================================
                {
                    "player_id": "zach_collins_021",
                    "player_name": "Zach Collins",
                    "team": "Chicago Bulls",
                    "status": "OUT",
                    "injury": "Toe",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "tre_jones_022",
                    "player_name": "Tre Jones",
                    "team": "Chicago Bulls",
                    "status": "OUT",
                    "injury": "Hamstring",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "noa_essengue_023",
                    "player_name": "Noa Essengue",
                    "team": "Chicago Bulls",
                    "status": "OUT",
                    "injury": "Shoulder (Season-ending)",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "yuki_kawamura_024",
                    "player_name": "Yuki Kawamura",
                    "team": "Chicago Bulls",
                    "status": "OUT",
                    "injury": "Oblique",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # CLEVELAND CAVALIERS
                # =================================================================
                {
                    "player_id": "darius_garland_025",
                    "player_name": "Darius Garland",
                    "team": "Cleveland Cavaliers",
                    "status": "OUT",
                    "injury": "Foot/Toe",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "evan_mobley_026",
                    "player_name": "Evan Mobley",
                    "team": "Cleveland Cavaliers",
                    "status": "OUT",
                    "injury": "Calf",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "max_strus_027",
                    "player_name": "Max Strus",
                    "team": "Cleveland Cavaliers",
                    "status": "OUT",
                    "injury": "Foot",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "deandre_hunter_028",
                    "player_name": "De'Andre Hunter",
                    "team": "Cleveland Cavaliers",
                    "status": "DAY_TO_DAY",
                    "injury": "Knee",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "sam_merrill_029",
                    "player_name": "Sam Merrill",
                    "team": "Cleveland Cavaliers",
                    "status": "DAY_TO_DAY",
                    "injury": "Hand",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # DALLAS MAVERICKS
                # =================================================================
                {
                    "player_id": "dereck_lively_030",
                    "player_name": "Dereck Lively II",
                    "team": "Dallas Mavericks",
                    "status": "OUT",
                    "injury": "Foot (Season-ending)",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "dante_exum_031",
                    "player_name": "Dante Exum",
                    "team": "Dallas Mavericks",
                    "status": "OUT",
                    "injury": "Knee (Season-ending)",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "cooper_flagg_032",
                    "player_name": "Cooper Flagg",
                    "team": "Dallas Mavericks",
                    "status": "DAY_TO_DAY",
                    "injury": "Ankle",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "klay_thompson_033",
                    "player_name": "Klay Thompson",
                    "team": "Dallas Mavericks",
                    "status": "DAY_TO_DAY",
                    "injury": "Knee",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # DENVER NUGGETS
                # =================================================================
                {
                    "player_id": "aaron_gordon_034",
                    "player_name": "Aaron Gordon",
                    "team": "Denver Nuggets",
                    "status": "DAY_TO_DAY",
                    "injury": "Hamstring",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "cameron_johnson_035",
                    "player_name": "Cameron Johnson",
                    "team": "Denver Nuggets",
                    "status": "OUT",
                    "injury": "Knee",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "christian_braun_036",
                    "player_name": "Christian Braun",
                    "team": "Denver Nuggets",
                    "status": "DAY_TO_DAY",
                    "injury": "Ankle",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "jamal_murray_037",
                    "player_name": "Jamal Murray",
                    "team": "Denver Nuggets",
                    "status": "DAY_TO_DAY",
                    "injury": "Rest",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "tamar_bates_038",
                    "player_name": "Tamar Bates",
                    "team": "Denver Nuggets",
                    "status": "OUT",
                    "injury": "Foot",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # DETROIT PISTONS
                # =================================================================
                {
                    "player_id": "caris_levert_039",
                    "player_name": "Caris LeVert",
                    "team": "Detroit Pistons",
                    "status": "OUT",
                    "injury": "Illness",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # GOLDEN STATE WARRIORS
                # =================================================================
                {
                    "player_id": "draymond_green_040",
                    "player_name": "Draymond Green",
                    "team": "Golden State Warriors",
                    "status": "DAY_TO_DAY",
                    "injury": "Back",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "seth_curry_041",
                    "player_name": "Seth Curry",
                    "team": "Golden State Warriors",
                    "status": "OUT",
                    "injury": "Back",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "jonathan_kuminga_042",
                    "player_name": "Jonathan Kuminga",
                    "team": "Golden State Warriors",
                    "status": "OUT",
                    "injury": "Knee",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "al_horford_043",
                    "player_name": "Al Horford",
                    "team": "Golden State Warriors",
                    "status": "DAY_TO_DAY",
                    "injury": "Rest",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # HOUSTON ROCKETS
                # =================================================================
                {
                    "player_id": "fred_vanvleet_044",
                    "player_name": "Fred VanVleet",
                    "team": "Houston Rockets",
                    "status": "OUT",
                    "injury": "Knee/ACL",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "steven_adams_045",
                    "player_name": "Steven Adams",
                    "team": "Houston Rockets",
                    "status": "OUT",
                    "injury": "Ankle",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # INDIANA PACERS
                # =================================================================
                {
                    "player_id": "tyrese_haliburton_046",
                    "player_name": "Tyrese Haliburton",
                    "team": "Indiana Pacers",
                    "status": "OUT",
                    "injury": "Achilles (Season-ending)",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "obi_toppin_047",
                    "player_name": "Obi Toppin",
                    "team": "Indiana Pacers",
                    "status": "OUT",
                    "injury": "Foot",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "jarace_walker_048",
                    "player_name": "Jarace Walker",
                    "team": "Indiana Pacers",
                    "status": "DAY_TO_DAY",
                    "injury": "Foot",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # LA CLIPPERS
                # =================================================================
                {
                    "player_id": "kawhi_leonard_049",
                    "player_name": "Kawhi Leonard",
                    "team": "Los Angeles Clippers",
                    "status": "DAY_TO_DAY",
                    "injury": "Knee Management",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "bradley_beal_050",
                    "player_name": "Bradley Beal",
                    "team": "Los Angeles Clippers",
                    "status": "OUT",
                    "injury": "Hip",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "chris_paul_051",
                    "player_name": "Chris Paul",
                    "team": "Los Angeles Clippers",
                    "status": "OUT",
                    "injury": "Undisclosed",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "bogdan_bogdanovic_052",
                    "player_name": "Bogdan Bogdanovic",
                    "team": "Los Angeles Clippers",
                    "status": "OUT",
                    "injury": "Hamstring",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "derrick_jones_jr_053",
                    "player_name": "Derrick Jones Jr.",
                    "team": "Los Angeles Clippers",
                    "status": "OUT",
                    "injury": "Knee",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # LA LAKERS
                # =================================================================
                {
                    "player_id": "austin_reaves_054",
                    "player_name": "Austin Reaves",
                    "team": "Los Angeles Lakers",
                    "status": "OUT",
                    "injury": "Calf",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "adou_thiero_055",
                    "player_name": "Adou Thiero",
                    "team": "Los Angeles Lakers",
                    "status": "OUT",
                    "injury": "Undisclosed",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # MEMPHIS GRIZZLIES
                # =================================================================
                {
                    "player_id": "zach_edey_056",
                    "player_name": "Zach Edey",
                    "team": "Memphis Grizzlies",
                    "status": "OUT",
                    "injury": "Ankle",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "brandon_clarke_057",
                    "player_name": "Brandon Clarke",
                    "team": "Memphis Grizzlies",
                    "status": "OUT",
                    "injury": "Calf",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "scotty_pippen_jr_058",
                    "player_name": "Scotty Pippen Jr.",
                    "team": "Memphis Grizzlies",
                    "status": "OUT",
                    "injury": "Toe",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # MIAMI HEAT
                # =================================================================
                {
                    "player_id": "tyler_herro_059",
                    "player_name": "Tyler Herro",
                    "team": "Miami Heat",
                    "status": "OUT",
                    "injury": "Toe/Rib",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "davion_mitchell_060",
                    "player_name": "Davion Mitchell",
                    "team": "Miami Heat",
                    "status": "DAY_TO_DAY",
                    "injury": "Shoulder",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "kelel_ware_061",
                    "player_name": "Kel'el Ware",
                    "team": "Miami Heat",
                    "status": "DAY_TO_DAY",
                    "injury": "Hamstring",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # MILWAUKEE BUCKS
                # =================================================================
                {
                    "player_id": "taurean_prince_062",
                    "player_name": "Taurean Prince",
                    "team": "Milwaukee Bucks",
                    "status": "OUT",
                    "injury": "Neck",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "kevin_porter_jr_063",
                    "player_name": "Kevin Porter Jr.",
                    "team": "Milwaukee Bucks",
                    "status": "OUT",
                    "injury": "Oblique",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # MINNESOTA TIMBERWOLVES
                # =================================================================
                {
                    "player_id": "anthony_edwards_064",
                    "player_name": "Anthony Edwards",
                    "team": "Minnesota Timberwolves",
                    "status": "DAY_TO_DAY",
                    "injury": "Foot",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "leonard_miller_065",
                    "player_name": "Leonard Miller",
                    "team": "Minnesota Timberwolves",
                    "status": "DAY_TO_DAY",
                    "injury": "Back",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "terrence_shannon_jr_066",
                    "player_name": "Terrence Shannon Jr.",
                    "team": "Minnesota Timberwolves",
                    "status": "OUT",
                    "injury": "Foot",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # NEW ORLEANS PELICANS
                # =================================================================
                {
                    "player_id": "dejounte_murray_067",
                    "player_name": "Dejounte Murray",
                    "team": "New Orleans Pelicans",
                    "status": "OUT",
                    "injury": "Undisclosed",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # NEW YORK KNICKS
                # =================================================================
                {
                    "player_id": "mitchell_robinson_068",
                    "player_name": "Mitchell Robinson",
                    "team": "New York Knicks",
                    "status": "OUT",
                    "injury": "Rest/Ankle",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "miles_mcbride_069",
                    "player_name": "Miles McBride",
                    "team": "New York Knicks",
                    "status": "OUT",
                    "injury": "Ankle",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "josh_hart_070",
                    "player_name": "Josh Hart",
                    "team": "New York Knicks",
                    "status": "QUESTIONABLE",
                    "injury": "Ankle",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # OKLAHOMA CITY THUNDER
                # =================================================================
                {
                    "player_id": "jalen_williams_071",
                    "player_name": "Jalen Williams",
                    "team": "Oklahoma City Thunder",
                    "status": "OUT",
                    "injury": "Hamstring",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "isaiah_hartenstein_072",
                    "player_name": "Isaiah Hartenstein",
                    "team": "Oklahoma City Thunder",
                    "status": "OUT",
                    "injury": "Soleus",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "alex_caruso_073",
                    "player_name": "Alex Caruso",
                    "team": "Oklahoma City Thunder",
                    "status": "OUT",
                    "injury": "Adductor",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "nikola_topic_074",
                    "player_name": "Nikola Topic",
                    "team": "Oklahoma City Thunder",
                    "status": "OUT",
                    "injury": "Surgery",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "cason_wallace_075",
                    "player_name": "Cason Wallace",
                    "team": "Oklahoma City Thunder",
                    "status": "DAY_TO_DAY",
                    "injury": "Hip",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # ORLANDO MAGIC
                # =================================================================
                {
                    "player_id": "franz_wagner_076",
                    "player_name": "Franz Wagner",
                    "team": "Orlando Magic",
                    "status": "DAY_TO_DAY",
                    "injury": "Ankle",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "colin_castleton_077",
                    "player_name": "Colin Castleton",
                    "team": "Orlando Magic",
                    "status": "OUT",
                    "injury": "Undisclosed",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # PHILADELPHIA 76ERS
                # =================================================================
                {
                    "player_id": "paul_george_078",
                    "player_name": "Paul George",
                    "team": "Philadelphia 76ers",
                    "status": "DAY_TO_DAY",
                    "injury": "Rest",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "quentin_grimes_079",
                    "player_name": "Quentin Grimes",
                    "team": "Philadelphia 76ers",
                    "status": "DAY_TO_DAY",
                    "injury": "Ankle",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # PHOENIX SUNS
                # =================================================================
                {
                    "player_id": "devin_booker_080",
                    "player_name": "Devin Booker",
                    "team": "Phoenix Suns",
                    "status": "OUT",
                    "injury": "Ankle",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "jalen_green_081",
                    "player_name": "Jalen Green",
                    "team": "Phoenix Suns",
                    "status": "OUT",
                    "injury": "Hamstring",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "collin_gillespie_082",
                    "player_name": "Collin Gillespie",
                    "team": "Phoenix Suns",
                    "status": "DAY_TO_DAY",
                    "injury": "Hand",
                    "probability": 0.50,
                    "is_starter": False,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # PORTLAND TRAIL BLAZERS
                # =================================================================
                {
                    "player_id": "damian_lillard_083",
                    "player_name": "Damian Lillard",
                    "team": "Portland Trail Blazers",
                    "status": "OUT",
                    "injury": "Undisclosed",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "robert_williams_iii_084",
                    "player_name": "Robert Williams III",
                    "team": "Portland Trail Blazers",
                    "status": "DAY_TO_DAY",
                    "injury": "Rest",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "scoot_henderson_085",
                    "player_name": "Scoot Henderson",
                    "team": "Portland Trail Blazers",
                    "status": "OUT",
                    "injury": "Undisclosed",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "deni_avdija_086",
                    "player_name": "Deni Avdija",
                    "team": "Portland Trail Blazers",
                    "status": "DAY_TO_DAY",
                    "injury": "Rest",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # SACRAMENTO KINGS
                # =================================================================
                {
                    "player_id": "zach_lavine_087",
                    "player_name": "Zach LaVine",
                    "team": "Sacramento Kings",
                    "status": "OUT",
                    "injury": "Undisclosed",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "keegan_murray_088",
                    "player_name": "Keegan Murray",
                    "team": "Sacramento Kings",
                    "status": "OUT",
                    "injury": "Undisclosed",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "malik_monk_089",
                    "player_name": "Malik Monk",
                    "team": "Sacramento Kings",
                    "status": "OUT",
                    "injury": "Undisclosed",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # SAN ANTONIO SPURS
                # =================================================================
                {
                    "player_id": "devin_vassell_090",
                    "player_name": "Devin Vassell",
                    "team": "San Antonio Spurs",
                    "status": "OUT",
                    "injury": "Undisclosed",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "jeremy_sochan_091",
                    "player_name": "Jeremy Sochan",
                    "team": "San Antonio Spurs",
                    "status": "QUESTIONABLE",
                    "injury": "Quad",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # TORONTO RAPTORS
                # =================================================================
                {
                    "player_id": "jakob_poeltl_092",
                    "player_name": "Jakob Poeltl",
                    "team": "Toronto Raptors",
                    "status": "OUT",
                    "injury": "Lower Back (Indefinite)",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-25T12:00:00Z",
                    "source": "official",
                },
                # =================================================================
                # WASHINGTON WIZARDS
                # =================================================================
                {
                    "player_id": "khris_middleton_093",
                    "player_name": "Khris Middleton",
                    "team": "Washington Wizards",
                    "status": "DAY_TO_DAY",
                    "injury": "Rest",
                    "probability": 0.50,
                    "is_starter": True,
                    "updated": "2026-01-27T18:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "cam_whitmore_094",
                    "player_name": "Cam Whitmore",
                    "team": "Washington Wizards",
                    "status": "OUT",
                    "injury": "Undisclosed",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
            ]
        elif "football" in sport_key:
            injuries = [
                {
                    "player_id": "dak_prescott_404",
                    "player_name": "Dak Prescott",
                    "team": "Dallas Cowboys",
                    "status": "OUT",
                    "injury": "Ankle - Fracture",
                    "probability": 0.0,
                    "is_starter": None,
                    "updated": "2026-01-27T12:00:00Z",
                    "source": "official",
                },
                {
                    "player_id": "cmc_505",
                    "player_name": "Christian McCaffrey",
                    "team": "San Francisco 49ers",
                    "status": "QUESTIONABLE",
                    "injury": "Calf - Strain",
                    "probability": 0.55,
                    "is_starter": True,
                    "updated": "2026-01-27T14:00:00Z",
                    "source": "official",
                },
            ]
        
        # Filter by team if specified
        if team:
            injuries = [i for i in injuries if team.lower() in i["team"].lower()]
        
        return {"injuries": injuries}
    
    def _stub_lineups_response(
        self,
        sport_key: str,
        external_game_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Return realistic stub lineup data for January 28, 2026 games."""
        if "basketball" in sport_key:
            return {
                "games": [
                    # Lakers @ Cavaliers
                    {
                        "game_id": "game_lal_cle_20260128",
                        "home": {
                            "team": "Cleveland Cavaliers",
                            "lineup": [
                                {"player_id": "darius_garland_101", "player_name": "Darius Garland", "position": "PG", "is_starter": True, "confirmed": True},
                                {"player_id": "donovan_mitchell_102", "player_name": "Donovan Mitchell", "position": "SG", "is_starter": True, "confirmed": True},
                                {"player_id": "max_strus_103", "player_name": "Max Strus", "position": "SF", "is_starter": True, "confirmed": True},
                                {"player_id": "evan_mobley_104", "player_name": "Evan Mobley", "position": "PF", "is_starter": True, "confirmed": True},
                                {"player_id": "jarrett_allen_105", "player_name": "Jarrett Allen", "position": "C", "is_starter": True, "confirmed": True},
                            ],
                        },
                        "away": {
                            "team": "Los Angeles Lakers",
                            "lineup": [
                                {"player_id": "luka_doncic_201", "player_name": "Luka Doncic", "position": "PG", "is_starter": True, "confirmed": True},
                                {"player_id": "austin_reaves_202", "player_name": "Austin Reaves", "position": "SG", "is_starter": True, "confirmed": True},
                                {"player_id": "lebron_james_203", "player_name": "LeBron James", "position": "SF", "is_starter": True, "confirmed": True},
                                {"player_id": "rui_hachimura_204", "player_name": "Rui Hachimura", "position": "PF", "is_starter": True, "confirmed": True},
                                {"player_id": "deandre_ayton_205", "player_name": "Deandre Ayton", "position": "C", "is_starter": True, "confirmed": True},
                            ],
                        },
                    },
                    # Timberwolves @ Mavericks
                    {
                        "game_id": "game_min_dal_20260128",
                        "home": {
                            "team": "Dallas Mavericks",
                            "lineup": [
                                {"player_id": "dangelo_russell_301", "player_name": "D'Angelo Russell", "position": "PG", "is_starter": True, "confirmed": True},
                                {"player_id": "klay_thompson_302", "player_name": "Klay Thompson", "position": "SG", "is_starter": True, "confirmed": True},
                                {"player_id": "pj_washington_303", "player_name": "P.J. Washington", "position": "SF", "is_starter": True, "confirmed": True},
                                {"player_id": "anthony_davis_304", "player_name": "Anthony Davis", "position": "PF", "is_starter": True, "confirmed": False},
                                {"player_id": "dereck_lively_305", "player_name": "Dereck Lively II", "position": "C", "is_starter": True, "confirmed": True},
                            ],
                        },
                        "away": {
                            "team": "Minnesota Timberwolves",
                            "lineup": [
                                {"player_id": "mike_conley_401", "player_name": "Mike Conley", "position": "PG", "is_starter": True, "confirmed": True},
                                {"player_id": "anthony_edwards_402", "player_name": "Anthony Edwards", "position": "SG", "is_starter": True, "confirmed": True},
                                {"player_id": "jaden_mcdaniels_403", "player_name": "Jaden McDaniels", "position": "SF", "is_starter": True, "confirmed": True},
                                {"player_id": "julius_randle_404", "player_name": "Julius Randle", "position": "PF", "is_starter": True, "confirmed": True},
                                {"player_id": "rudy_gobert_405", "player_name": "Rudy Gobert", "position": "C", "is_starter": True, "confirmed": True},
                            ],
                        },
                    },
                    # Warriors @ Jazz
                    {
                        "game_id": "game_gsw_uta_20260128",
                        "home": {
                            "team": "Utah Jazz",
                            "lineup": [
                                {"player_id": "keyonte_george_501", "player_name": "Keyonte George", "position": "PG", "is_starter": True, "confirmed": True},
                                {"player_id": "kyle_anderson_502", "player_name": "Kyle Anderson", "position": "SG", "is_starter": True, "confirmed": True},
                                {"player_id": "lauri_markkanen_503", "player_name": "Lauri Markkanen", "position": "SF", "is_starter": True, "confirmed": True},
                                {"player_id": "walker_kessler_504", "player_name": "Walker Kessler", "position": "PF", "is_starter": True, "confirmed": True},
                                {"player_id": "jusuf_nurkic_505", "player_name": "Jusuf Nurkic", "position": "C", "is_starter": True, "confirmed": True},
                            ],
                        },
                        "away": {
                            "team": "Golden State Warriors",
                            "lineup": [
                                {"player_id": "stephen_curry_601", "player_name": "Stephen Curry", "position": "PG", "is_starter": True, "confirmed": True},
                                {"player_id": "brandin_podziemski_602", "player_name": "Brandin Podziemski", "position": "SG", "is_starter": True, "confirmed": True},
                                {"player_id": "jimmy_butler_603", "player_name": "Jimmy Butler", "position": "SF", "is_starter": True, "confirmed": True},
                                {"player_id": "draymond_green_604", "player_name": "Draymond Green", "position": "PF", "is_starter": True, "confirmed": True},
                                {"player_id": "al_horford_605", "player_name": "Al Horford", "position": "C", "is_starter": True, "confirmed": True},
                            ],
                        },
                    },
                ],
            }
        
        return {"games": []}
    
    def _stub_player_injury_response(
        self,
        external_player_id: str,
    ) -> Optional[dict[str, Any]]:
        """Return realistic stub player injury data for testing."""
        player_injuries = {
            "anthony_davis_456": {
                "player_id": "anthony_davis_456",
                "player_name": "Anthony Davis",
                "team": "Dallas Mavericks",
                "status": "QUESTIONABLE",
                "injury": "Knee - Soreness",
                "probability": 0.65,
                "is_starter": True,
                "updated": "2026-01-27T18:00:00Z",
            },
            "kawhi_leonard_789": {
                "player_id": "kawhi_leonard_789",
                "player_name": "Kawhi Leonard",
                "team": "Los Angeles Clippers",
                "status": "OUT",
                "injury": "Knee - Management",
                "probability": 0.0,
                "is_starter": None,
                "updated": "2026-01-27T15:30:00Z",
            },
            "klay_thompson_404": {
                "player_id": "klay_thompson_404",
                "player_name": "Klay Thompson",
                "team": "Dallas Mavericks",
                "status": "PROBABLE",
                "injury": "Knee - Maintenance",
                "probability": 0.90,
                "is_starter": True,
                "updated": "2026-01-27T16:00:00Z",
            },
        }
        
        return player_injuries.get(external_player_id)
