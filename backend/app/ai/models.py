"""Pydantic models for AI integration request/response payloads."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================

class RiskProfile(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class ConfidenceLabel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SignalSource(str, Enum):
    """Distinguishes model-only vs AI-assisted signals."""
    MODEL = "model"
    AI_ASSISTED = "ai_assisted"


# =============================================================================
# Input Models
# =============================================================================

class PropLine(BaseModel):
    """A single prop line to analyze."""
    game_id: int
    player_name: str
    player_id: Optional[int] = None
    team: Optional[str] = None
    opponent: Optional[str] = None
    stat_type: str  # PTS, REB, AST, 3PM, etc.
    line: float
    side: str  # over / under
    odds: Optional[int] = None  # American odds, e.g. -110
    implied_probability: Optional[float] = None
    model_probability: Optional[float] = None
    model_ev: Optional[float] = None
    confidence: Optional[float] = None
    book: Optional[str] = None
    game_time: Optional[str] = None


class AIContext(BaseModel):
    """Context passed alongside props for AI analysis."""
    sport: str  # e.g. "NBA", "NFL"
    league: str  # e.g. "basketball_nba"
    date: str  # ISO date YYYY-MM-DD
    risk_profile: RiskProfile = RiskProfile.MODERATE
    min_ev_threshold: float = Field(default=0.03, ge=0.0, le=1.0)
    max_legs_in_parlay: int = Field(default=3, ge=2, le=10)
    books: Optional[list[str]] = None
    injuries: Optional[list[str]] = None
    notes: Optional[str] = None


class AIRequestPayload(BaseModel):
    """Full payload sent to the AI provider."""
    props: list[PropLine]
    context: AIContext
    prompt_template: Optional[str] = None


# =============================================================================
# Output Models
# =============================================================================

class AIRecommendation(BaseModel):
    """A single AI-generated recommendation."""
    player_name: str
    stat_type: str
    line: float
    side: str
    book: Optional[str] = None
    odds: Optional[int] = None
    model_projection: Optional[float] = None
    edge_pct: Optional[float] = None
    confidence_label: ConfidenceLabel = ConfidenceLabel.MEDIUM
    reasoning: Optional[str] = None
    signal_source: SignalSource = SignalSource.AI_ASSISTED
    suggested_bet_size_pct: Optional[float] = None


class ParlayLegRecommendation(BaseModel):
    """A single leg within a parlay recommendation."""
    player_name: str
    stat_type: str
    line: float
    side: str
    odds: Optional[int] = None
    edge_pct: Optional[float] = None
    confidence_label: ConfidenceLabel = ConfidenceLabel.MEDIUM


class ParlayRecommendation(BaseModel):
    """An AI-generated parlay recommendation."""
    legs: list[ParlayLegRecommendation]
    combined_odds: Optional[int] = None
    combined_ev: Optional[float] = None
    confidence_label: ConfidenceLabel = ConfidenceLabel.MEDIUM
    reasoning: Optional[str] = None


class AIRecommendationsResponse(BaseModel):
    """Full response from the AI analysis layer."""
    sport: str
    league: str
    date: str
    individual: list[AIRecommendation] = Field(default_factory=list)
    parlays: list[ParlayRecommendation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    total_recommendations: int = 0
    ai_model: Optional[str] = None
    generated_at: Optional[str] = None
