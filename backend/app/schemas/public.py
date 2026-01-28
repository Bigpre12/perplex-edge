"""Public API Pydantic schemas for consumer-facing endpoints."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# =============================================================================
# Sports
# =============================================================================

class PublicSport(BaseModel):
    """Public sport response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    league_code: str


class PublicSportList(BaseModel):
    """List of sports."""
    items: list[PublicSport]
    total: int


# =============================================================================
# Games
# =============================================================================

class PublicGame(BaseModel):
    """Public game response with team details."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    external_game_id: str
    home_team: str
    home_team_abbr: Optional[str]
    away_team: str
    away_team_abbr: Optional[str]
    start_time: datetime
    status: str


class PublicGameList(BaseModel):
    """List of games."""
    items: list[PublicGame]
    total: int


# =============================================================================
# Markets
# =============================================================================

class PublicMarket(BaseModel):
    """Public market response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    market_type: str
    stat_type: Optional[str]
    description: Optional[str]


class PublicMarketList(BaseModel):
    """List of markets."""
    items: list[PublicMarket]
    total: int


# =============================================================================
# Player Prop Picks
# =============================================================================

class PlayerPropPick(BaseModel):
    """Player prop pick with all details for the cheat sheet."""
    
    # Pick identification
    pick_id: int
    
    # Player info
    player_name: str
    player_id: int
    team: str
    team_abbr: Optional[str]
    opponent_team: str
    opponent_abbr: Optional[str]
    
    # Prop details
    stat_type: str
    line: float
    side: str  # "over" or "under"
    odds: int
    sportsbook: Optional[str] = None
    
    # Model outputs
    model_probability: float
    implied_probability: float
    expected_value: float
    hit_rate_30d: Optional[float]
    hit_rate_10g: Optional[float]
    confidence_score: float
    
    # Game info
    game_id: int
    game_start_time: datetime


class PlayerPropPickList(BaseModel):
    """List of player prop picks."""
    items: list[PlayerPropPick]
    total: int
    filters: dict  # Echo back applied filters


# =============================================================================
# Game Line Picks
# =============================================================================

class GameLinePick(BaseModel):
    """Game line pick (spread/total/moneyline) for the cheat sheet."""
    
    # Pick identification
    pick_id: int
    
    # Game info
    game_id: int
    home_team: str
    home_team_abbr: Optional[str]
    away_team: str
    away_team_abbr: Optional[str]
    game_start_time: datetime
    
    # Line details
    market_type: str  # "spread", "total", "moneyline"
    line: Optional[float]  # Spread value or total, null for moneyline
    side: str  # "home", "away", "over", "under"
    odds: int
    sportsbook: Optional[str] = None
    
    # Model outputs
    model_probability: float
    implied_probability: float
    expected_value: float
    confidence_score: float


class GameLinePickList(BaseModel):
    """List of game line picks."""
    items: list[GameLinePick]
    total: int
    filters: dict  # Echo back applied filters
