"""Season-related Pydantic schemas."""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# =============================================================================
# Season Schemas
# =============================================================================

class SeasonBase(BaseModel):
    sport_id: int
    season_year: int
    label: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False


class SeasonCreate(SeasonBase):
    pass


class SeasonRead(SeasonBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class SeasonList(BaseModel):
    items: List[SeasonRead]
    total: int


# =============================================================================
# Season Roster Schemas
# =============================================================================

class SeasonRosterBase(BaseModel):
    season_id: int
    team_id: int
    player_id: int
    jersey_number: Optional[str] = None
    position: Optional[str] = None
    is_active: bool = True


class SeasonRosterCreate(SeasonRosterBase):
    pass


class SeasonRosterRead(SeasonRosterBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Nested Response Schemas (for API responses)
# =============================================================================

class TeamInfo(BaseModel):
    """Simplified team info for nested responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    sport_id: int
    name: str
    abbreviation: Optional[str] = None


class PlayerInfo(BaseModel):
    """Simplified player info for nested responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    sport_id: int
    team_id: Optional[int] = None
    name: str
    position: Optional[str] = None


class RosterPlayerOut(BaseModel):
    """Player with roster info for team roster endpoint."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    position: Optional[str] = None
    jersey_number: Optional[str] = None
    is_active: bool


class GameOut(BaseModel):
    """Game with nested team info."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    sport_id: int
    season_id: Optional[int] = None
    home_team: TeamInfo
    away_team: TeamInfo
    start_time: datetime
    status: str


class GamePlayerStats(BaseModel):
    """Player stats for a game - supports all sports."""
    model_config = ConfigDict(from_attributes=True)
    
    # Common stats
    minutes: Optional[float] = None
    
    # Basketball stats
    points: Optional[float] = None
    rebounds: Optional[float] = None
    assists: Optional[float] = None
    steals: Optional[float] = None
    blocks: Optional[float] = None
    turnovers: Optional[float] = None
    three_pointers_made: Optional[float] = None
    
    # Football stats
    passing_yards: Optional[float] = None
    passing_touchdowns: Optional[float] = None
    rushing_yards: Optional[float] = None
    rushing_touchdowns: Optional[float] = None
    receiving_yards: Optional[float] = None
    receptions: Optional[float] = None
    
    # Hockey stats
    goals: Optional[float] = None
    assists_hockey: Optional[float] = None
    shots: Optional[float] = None
    saves: Optional[float] = None
    
    # Baseball stats
    hits: Optional[float] = None
    runs: Optional[float] = None
    rbis: Optional[float] = None
    strikeouts: Optional[float] = None
    innings_pitched: Optional[float] = None


class GamePlayerOut(BaseModel):
    """Player with stats for a specific game."""
    player: PlayerInfo
    team: TeamInfo
    stats: GamePlayerStats
