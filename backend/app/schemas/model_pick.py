from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ModelPickBase(BaseModel):
    sport_id: int
    game_id: int
    player_id: Optional[int] = None
    market_id: int
    side: str
    line_value: Optional[float] = None
    odds: float
    model_probability: float
    implied_probability: float
    expected_value: float
    hit_rate_30d: Optional[float] = None
    hit_rate_10g: Optional[float] = None
    confidence_score: float
    is_active: bool = True


class ModelPickCreate(ModelPickBase):
    pass


class ModelPickRead(ModelPickBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    generated_at: datetime


class ModelPickWithDetails(ModelPickRead):
    sport_name: str
    market_type: str
    stat_type: Optional[str] = None
    player_name: Optional[str] = None
    home_team: str
    away_team: str
    game_time: datetime


class ModelPickList(BaseModel):
    items: list[ModelPickWithDetails]
    total: int


class PickSummary(BaseModel):
    """Summary of model picks performance."""
    total_picks: int
    active_picks: int
    avg_ev: float
    avg_confidence: float
    high_confidence_picks: int  # confidence > 0.7
