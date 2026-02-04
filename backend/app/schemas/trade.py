"""Trade-related Pydantic schemas."""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# =============================================================================
# Trade Detail Schemas
# =============================================================================

class TradeDetailBase(BaseModel):
    """Base schema for trade detail."""
    player_id: Optional[int] = None
    from_team_id: int
    to_team_id: int
    asset_type: str  # "player", "pick", "cash", "rights"
    asset_description: Optional[str] = None
    player_name: Optional[str] = None


class TradeDetailCreate(TradeDetailBase):
    """Schema for creating a trade detail."""
    pass


class TradeDetailRead(TradeDetailBase):
    """Schema for reading a trade detail."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    trade_id: int
    created_at: datetime


class TradeDetailWithTeams(TradeDetailRead):
    """Trade detail with team names included."""
    from_team_name: Optional[str] = None
    from_team_abbr: Optional[str] = None
    to_team_name: Optional[str] = None
    to_team_abbr: Optional[str] = None


# =============================================================================
# Trade Schemas
# =============================================================================

class TradeBase(BaseModel):
    """Base schema for trade."""
    trade_date: date
    season_year: int
    description: Optional[str] = None
    headline: Optional[str] = None
    source_url: Optional[str] = None
    source: Optional[str] = "nba.com"


class TradeCreate(TradeBase):
    """Schema for creating a trade with details."""
    details: List[TradeDetailCreate]


class TradeRead(TradeBase):
    """Schema for reading a trade."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_applied: bool
    created_at: datetime
    updated_at: datetime


class TradeWithDetails(TradeRead):
    """Trade with all its details."""
    details: List[TradeDetailWithTeams]
    
    # Summary fields
    teams_involved: Optional[List[str]] = None
    players_moved: Optional[List[str]] = None


class TradeList(BaseModel):
    """Paginated list of trades."""
    items: List[TradeWithDetails]
    total: int


# =============================================================================
# Trade Apply Schemas
# =============================================================================

class TradeApplyRequest(BaseModel):
    """Request to apply a trade (update player teams)."""
    update_rosters: bool = True  # Also update SeasonRoster entries


class TradeApplyResult(BaseModel):
    """Result of applying a trade."""
    trade_id: int
    players_updated: int
    roster_entries_created: int
    roster_entries_deactivated: int
    details: List[dict]


# =============================================================================
# Bulk Trade Create Schema
# =============================================================================

class BulkTradeItem(BaseModel):
    """Single trade for bulk import."""
    trade_date: date
    headline: str
    description: Optional[str] = None
    source_url: Optional[str] = None
    players: List[dict]  # {"name": "James Harden", "from": "Clippers", "to": "Cavaliers"}
    picks: Optional[List[dict]] = None  # {"description": "2027 1st", "from": "Team A", "to": "Team B"}


class BulkTradeCreate(BaseModel):
    """Schema for bulk creating trades."""
    season_year: int
    trades: List[BulkTradeItem]
    auto_apply: bool = False  # Automatically apply trades to update player teams


class BulkTradeResult(BaseModel):
    """Result of bulk trade creation."""
    trades_created: int
    details_created: int
    players_updated: int
    errors: List[str]
