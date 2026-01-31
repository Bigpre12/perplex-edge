"""Pydantic schemas for personal bet tracking."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class BetStatusEnum(str, Enum):
    """Bet status options."""
    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    PUSH = "push"
    VOID = "void"


# =============================================================================
# Request Schemas
# =============================================================================

class BetCreate(BaseModel):
    """Schema for creating a new bet."""
    
    sport_id: int = Field(..., description="Sport ID")
    game_id: Optional[int] = Field(None, description="Game ID (optional)")
    player_id: Optional[int] = Field(None, description="Player ID for props (optional)")
    
    market_type: str = Field(..., description="Market type (spread, total, player_points, etc.)")
    side: str = Field(..., description="Side (over, under, home, away)")
    line_value: Optional[float] = Field(None, description="Line value (e.g., 24.5 for points)")
    
    sportsbook: str = Field(..., description="Sportsbook name (FanDuel, DraftKings, etc.)")
    opening_odds: int = Field(..., description="American odds when bet was placed")
    stake: float = Field(1.0, description="Stake in units (default 1)")
    
    notes: Optional[str] = Field(None, description="Optional user notes")
    model_pick_id: Optional[int] = Field(None, description="Link to model pick if applicable")
    
    placed_at: Optional[datetime] = Field(None, description="When bet was placed (defaults to now)")


class BetSettle(BaseModel):
    """Schema for settling a bet."""
    
    status: BetStatusEnum = Field(..., description="Final status (won, lost, push, void)")
    actual_value: Optional[float] = Field(None, description="Actual stat value for props")
    closing_odds: Optional[int] = Field(None, description="Closing odds at game start")
    closing_line: Optional[float] = Field(None, description="Closing line at game start")


class BetUpdate(BaseModel):
    """Schema for updating a bet."""
    
    notes: Optional[str] = None
    stake: Optional[float] = None
    # Can't change most fields after creation to maintain audit trail


# =============================================================================
# Response Schemas
# =============================================================================

class BetResponse(BaseModel):
    """Full bet response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    sport_id: int
    sport_name: Optional[str] = None
    game_id: Optional[int]
    player_id: Optional[int]
    player_name: Optional[str] = None
    
    market_type: str
    side: str
    line_value: Optional[float]
    
    sportsbook: str
    opening_odds: int
    stake: float
    
    status: str
    actual_value: Optional[float]
    closing_odds: Optional[int]
    closing_line: Optional[float]
    clv_cents: Optional[float]
    profit_loss: Optional[float]
    
    placed_at: datetime
    settled_at: Optional[datetime]
    notes: Optional[str]
    model_pick_id: Optional[int]
    
    created_at: datetime
    updated_at: datetime


class BetList(BaseModel):
    """List of bets with pagination."""
    
    items: list[BetResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# Stats Schemas
# =============================================================================

class ROIByCategory(BaseModel):
    """ROI breakdown for a single category."""
    
    category: str  # The category value (e.g., "player_points", "FanDuel", "LeBron James")
    total_bets: int
    won: int
    lost: int
    pushed: int
    win_rate: float  # Won / (Won + Lost)
    total_stake: float  # Sum of stakes
    total_profit_loss: float  # Sum of P/L
    roi: float  # Total P/L / Total Stake * 100


class CLVStats(BaseModel):
    """CLV analysis stats."""
    
    total_bets_with_clv: int
    avg_clv_cents: float  # Average CLV across all bets
    positive_clv_count: int  # Bets that beat the close
    positive_clv_pct: float  # % of bets that beat the close
    total_clv_cents: float  # Sum of all CLV (positive = overall sharp)


class BetStatsResponse(BaseModel):
    """Comprehensive betting statistics."""
    
    # Summary
    total_bets: int
    settled_bets: int
    pending_bets: int
    
    # Overall performance
    total_stake: float
    total_profit_loss: float
    overall_roi: float  # Total P/L / Total Stake * 100
    overall_win_rate: float  # Won / (Won + Lost)
    
    # Record
    won: int
    lost: int
    pushed: int
    voided: int
    
    # CLV analysis
    clv_stats: CLVStats
    
    # Breakdowns
    by_market: list[ROIByCategory]
    by_sportsbook: list[ROIByCategory]
    by_sport: list[ROIByCategory]
    
    # Top performers
    top_players: list[ROIByCategory]  # Players with best ROI (min 5 bets)
    worst_players: list[ROIByCategory]  # Players with worst ROI (min 5 bets)


class CLVHistoryPoint(BaseModel):
    """Single data point for CLV over time."""
    
    date: str  # Date string
    cumulative_clv: float
    rolling_clv_7d: Optional[float]
    bet_count: int


class CLVHistoryResponse(BaseModel):
    """CLV history for charting."""
    
    data_points: list[CLVHistoryPoint]
    total_clv: float
    avg_clv: float


# =============================================================================
# Filter Schemas
# =============================================================================

class BetFilters(BaseModel):
    """Filters for bet queries."""
    
    sport_id: Optional[int] = None
    sportsbook: Optional[str] = None
    market_type: Optional[str] = None
    status: Optional[BetStatusEnum] = None
    player_id: Optional[int] = None
    
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    min_stake: Optional[float] = None
    max_stake: Optional[float] = None
    
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=200)


# =============================================================================
# Quick Log Schemas (for logging from UI picks)
# =============================================================================

class QuickBetFromPick(BaseModel):
    """Quick bet log from a model pick."""
    
    pick_id: int = Field(..., description="Model pick ID to log bet from")
    sportsbook: str = Field(..., description="Which sportsbook you bet on")
    stake: float = Field(1.0, description="Stake in units")
    actual_odds: Optional[int] = Field(None, description="Actual odds if different from pick")
    notes: Optional[str] = None
