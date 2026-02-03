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
    key: str


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
    sport_id: int  # Actual sport_id from the database
    sport_key: str  # Sport key (e.g., "americanfootball_nfl") for reliable label mapping
    
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
    
    # Line movement tracking
    opening_line: Optional[float] = None  # Original line when first posted
    opening_odds: Optional[int] = None  # Original odds
    line_movement: Optional[float] = None  # current_line - opening_line (positive = moved up)
    odds_movement: Optional[int] = None  # current_odds - opening_odds (negative = sharpened)
    movement_direction: Optional[str] = None  # "sharp_up", "sharp_down", "steam", "reverse", "stable"


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
    team_abbr: Optional[str] = None
    opponent_team: str
    opponent_abbr: Optional[str] = None
    
    # Prop details
    stat_type: str
    line: float
    side: str
    odds: int
    sportsbook: Optional[str] = None
    
    # Hit rate stats
    hit_rate_season: Optional[float] = None
    games_season: int = 0
    hit_rate_last_10: Optional[float] = None
    games_last_10: int = 0
    hit_rate_last_5: Optional[float] = None
    games_last_5: int = 0
    
    # Flags
    is_100_season: bool = False
    is_100_last_10: bool = False
    is_100_last_5: bool = False
    
    # Model outputs
    model_probability: float = 0.0
    expected_value: float = 0.0
    confidence_score: float = 0.0
    
    # Game info
    game_id: int
    game_start_time: Optional[str] = None  # ISO format string, None if not available


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


class PlatformViolation(BaseModel):
    """A platform rule violation for a parlay."""
    
    type: str  # "player_limit_exceeded" or "game_limit_exceeded"
    severity: str  # "HIGH" or "CRITICAL"
    message: str  # Human-readable description
    player_id: Optional[int] = None
    game_id: Optional[int] = None
    count: int  # How many props violated the rule
    max_allowed: int  # Max allowed by the platform


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
    
    # Platform-specific validity
    valid_platforms: list[str] = []  # Platforms where this parlay is valid
    platform_violations: list[PlatformViolation] = []  # Rule violations by platform
    is_universally_valid: bool = True  # True if valid on all platforms


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


class AutoGenerateSlipsResponse(BaseModel):
    """Response for auto-generated optimal slips."""
    
    slips: list[ParlayRecommendation]  # Non-overlapping optimal parlays
    slip_count: int
    leg_count: int
    platform: str
    total_candidates: int
    filters: dict
    # Summary stats
    avg_slip_ev: float
    avg_slip_probability: float
    total_suggested_units: float
    slate_quality: str  # "STRONG", "GOOD", "THIN", "PASS"


# =============================================================================
# Real-Time Parlay Quote
# =============================================================================

class QuoteLegRequest(BaseModel):
    """Single leg specification for quote request."""
    
    game_id: int
    player_id: Optional[int] = None
    stat_type: Optional[str] = None
    line_value: Optional[float] = None
    side: str  # "over", "under", "home", "away"
    model_odds: Optional[int] = None  # Original odds from model pick
    model_prob: Optional[float] = None  # Model probability


class QuoteRequest(BaseModel):
    """Request for real-time parlay quote."""
    
    legs: list[QuoteLegRequest]
    use_cache: bool = True  # Use cached odds when available


class OddsMovement(BaseModel):
    """Odds movement information."""
    
    direction: str  # "up", "down", "stable"
    magnitude: float  # Percentage change
    old_odds: int
    new_odds: int
    display: Optional[str]  # "Odds: +140 → +130"
    favorable: bool  # True if movement is favorable to bettor


class QuotedLeg(BaseModel):
    """Single leg with real-time odds."""
    
    index: int
    game_id: int
    player_id: Optional[int]
    player_name: Optional[str]
    stat_type: Optional[str]
    line_value: Optional[float]
    side: str
    sportsbook: str
    current_odds: int
    decimal_odds: float
    implied_prob: float
    model_odds: Optional[int]
    model_prob: float
    edge: float
    movement: Optional[OddsMovement]
    is_stale: bool
    last_update: Optional[str]
    found: bool  # Whether odds were found in database


class QuoteResponse(BaseModel):
    """Real-time parlay quote response."""
    
    legs: list[QuotedLeg]
    leg_count: int
    parlay_odds: int  # American odds
    parlay_decimal: float
    parlay_probability: float  # Model probability
    implied_probability: float  # Market implied probability
    parlay_ev: float  # Expected value
    has_movement: bool  # Whether any leg odds moved
    stale_legs: int  # Count of stale legs
    all_fresh: bool  # All legs have fresh odds
    quoted_at: str  # ISO timestamp


class OddsFreshnessResponse(BaseModel):
    """Odds data freshness status."""
    
    status: str  # "healthy", "degraded", "stale", "no_data"
    total_lines: int
    fresh_lines: int
    stale_lines: int
    freshness_pct: float
    oldest_update: Optional[str]
    newest_update: Optional[str]
    stale_threshold_minutes: int
    checked_at: str


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


# =============================================================================
# Tonight Summary (What's On Tonight Dashboard)
# =============================================================================

class SportTonightSummary(BaseModel):
    """Summary of a sport's slate for tonight."""
    sport_id: int
    sport_name: str
    sport_key: str
    games_count: int
    props_count: int
    best_ev: Optional[float] = None  # Best EV available in this sport
    avg_ev: Optional[float] = None   # Average EV across all props
    slate_quality: str  # "loaded", "normal", "thin", "empty"


class TonightSummaryResponse(BaseModel):
    """Response for tonight's slate summary across all sports."""
    date: str  # Date in YYYY-MM-DD format
    timezone: str  # "US/Eastern"
    sports: list[SportTonightSummary]
    total_games: int
    total_props: int
    overall_best_ev: Optional[float] = None
    slate_quality: str  # Overall slate quality
