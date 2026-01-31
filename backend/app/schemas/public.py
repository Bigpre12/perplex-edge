"""Public API Pydantic schemas for consumer-facing endpoints."""

from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, ConfigDict, PlainSerializer


# Custom serializer to ensure datetime is formatted with Z suffix for UTC
def serialize_datetime_utc(dt: datetime) -> str:
    """Serialize datetime to ISO format with Z suffix for UTC."""
    if dt is None:
        return None
    # Format as ISO and append Z to indicate UTC
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# Type alias for UTC datetime that serializes with Z suffix
UTCDatetime = Annotated[datetime, PlainSerializer(serialize_datetime_utc)]


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
    start_time: UTCDatetime
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
# Book-Specific Lines (for per-sportsbook comparison)
# =============================================================================

class BookLine(BaseModel):
    """Line from a specific sportsbook."""
    sportsbook: str
    line: Optional[float]
    odds: int
    ev: Optional[float] = None  # EV for this specific book


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
    hit_rate_5g: Optional[float]
    hit_rate_3g: Optional[float]
    confidence_score: float
    
    # Game info
    game_id: int
    game_start_time: UTCDatetime
    
    # Per-book comparison (new fields for market visibility)
    book_lines: Optional[list[BookLine]] = None  # All sportsbooks for this prop
    best_book: Optional[str] = None  # Which book has best EV
    line_variance: Optional[float] = None  # Max line difference across books (flag if >0.5)
    
    # Kelly sizing (bet size recommendation)
    kelly_units: Optional[float] = None  # Suggested bet size in units (0-5)
    kelly_edge_pct: Optional[float] = None  # Edge percentage
    kelly_risk_level: Optional[str] = None  # "NO_BET", "SMALL", "STANDARD", "CONFIDENT", "STRONG", "MAX"


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
    game_start_time: UTCDatetime
    
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


# =============================================================================
# 100% Hit Rate Props
# =============================================================================

class HundredPercentProp(BaseModel):
    """Prop with 100% hit rate over a time window."""
    
    pick_id: int
    player_name: str
    player_id: int
    team: str
    team_abbr: Optional[str]
    opponent_team: str
    opponent_abbr: Optional[str]
    
    # Prop details
    stat_type: str
    line: float
    side: str
    odds: int
    sportsbook: Optional[str] = None
    
    # Hit rate stats
    hit_rate_season: Optional[float]
    games_season: int
    hit_rate_last_10: Optional[float]
    games_last_10: int
    hit_rate_last_5: Optional[float]
    games_last_5: int
    
    # Flags
    is_100_season: bool
    is_100_last_10: bool
    is_100_last_5: bool
    
    # Model outputs
    model_probability: float
    expected_value: float
    confidence_score: float
    
    # Game info
    game_id: int
    game_start_time: UTCDatetime


class HundredPercentPropList(BaseModel):
    """List of 100% hit rate props."""
    items: list[HundredPercentProp]
    total: int
    window: str  # "season", "last_10", "last_5"


# =============================================================================
# Parlay Builder
# =============================================================================

class ParlayLeg(BaseModel):
    """Single leg of a parlay."""
    
    pick_id: int
    player_name: str
    player_id: Optional[int] = None  # For correlation detection
    team_abbr: Optional[str]
    game_id: Optional[int] = None  # For correlation detection
    stat_type: str
    line: float
    side: str
    odds: int
    
    # Grading
    grade: str  # "A", "B", "C", "D", "F"
    win_prob: float
    edge: float
    
    # Hit rate context
    hit_rate_5g: Optional[float]
    is_100_last_5: bool


class CorrelationWarning(BaseModel):
    """Warning about correlated legs in a parlay."""
    
    type: str  # "same_game", "same_player", "stat_ladder", "opposing_sides"
    severity: str  # "high", "medium", "low"
    legs: list[int]  # Indices of correlated legs (1-indexed for display)
    message: str  # Human-readable warning


class KellySizing(BaseModel):
    """Kelly criterion bet sizing recommendation."""
    
    full_kelly_pct: float  # Full Kelly percentage
    kelly_fraction: float  # Adjusted Kelly fraction
    suggested_units: float  # Suggested bet size in units
    edge_pct: float  # Edge percentage
    risk_level: str  # "NO_BET", "SMALL", "STANDARD", "CONFIDENT", "STRONG", "MAX"


class ParlayRecommendation(BaseModel):
    """A recommended parlay with grading."""
    
    legs: list[ParlayLeg]
    leg_count: int
    
    # Parlay math
    total_odds: int  # American odds
    decimal_odds: float
    parlay_probability: float
    parlay_ev: float
    
    # Grading
    overall_grade: str  # "A", "B", "C", "D", "F"
    label: str  # "LOCK", "PLAY", "SKIP"
    
    # Risk metrics
    min_leg_prob: float  # Lowest individual leg probability
    avg_edge: float
    
    # Correlation warnings
    correlations: list[CorrelationWarning] = []  # Any detected correlations
    correlation_risk: float = 0.0  # 0-1 risk score
    correlation_risk_label: str = "LOW"  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    
    # Kelly sizing
    kelly: Optional[KellySizing] = None  # Kelly criterion recommendation


class ParlayBuilderRequest(BaseModel):
    """Request for parlay builder."""
    
    leg_count: int = 3  # Number of legs (2-15)
    include_100_pct: bool = False  # Require at least 1 100% hit rate leg
    min_leg_grade: str = "C"  # Minimum grade for each leg
    max_results: int = 5  # Number of parlays to return
    block_correlated: bool = True  # Block high-correlation parlays (same-game, stat ladders)
    max_correlation_risk: str = "MEDIUM"  # Max allowed: "LOW", "MEDIUM", "HIGH", "CRITICAL"


class ParlayBuilderResponse(BaseModel):
    """Response from parlay builder."""
    
    parlays: list[ParlayRecommendation]
    total_candidates: int  # Total legs available
    leg_count: int
    filters_applied: dict


# =============================================================================
# Alt-Line Explorer
# =============================================================================

class AltLine(BaseModel):
    """Single alternate line option."""
    
    line: float
    over_odds: Optional[int]
    under_odds: Optional[int]
    over_prob: Optional[float]  # Model probability for over
    under_prob: Optional[float]  # Model probability for under
    over_ev: Optional[float]  # EV for over at these odds
    under_ev: Optional[float]  # EV for under at these odds
    over_fair_odds: Optional[int]  # Fair odds based on model prob
    under_fair_odds: Optional[int]  # Fair odds based on model prob
    is_main_line: bool = False  # Is this the primary market line


class AltLineExplorerResponse(BaseModel):
    """Response with all alternate lines for a prop."""
    
    player_name: str
    player_id: int
    team_abbr: Optional[str]
    stat_type: str
    game_id: int
    opponent_abbr: Optional[str]
    game_start_time: UTCDatetime
    
    # Model projection
    model_projection: float  # Expected value from model
    projection_std: Optional[float]  # Standard deviation if available
    
    # Alternate lines
    alt_lines: list[AltLine]
    
    # Recommendations
    best_over_line: Optional[AltLine]  # Highest EV over
    best_under_line: Optional[AltLine]  # Highest EV under
    
    # Hit rate context
    hit_rate_5g: Optional[float]
    season_avg: Optional[float]
