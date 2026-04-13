# apps/api/src/schemas/props.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal

class PropRecord(BaseModel):
    """Normalized prop record for internal processing and persistence."""
    sport: str
    league: Optional[str] = None
    game_id: str
    game_start_time: Optional[datetime] = None
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    team: Optional[str] = None
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    market_key: str
    market_label: Optional[str] = None
    line: Optional[Decimal] = None
    book: str
    odds_over: Optional[Decimal] = None
    odds_under: Optional[Decimal] = None
    implied_over: Optional[Decimal] = None
    implied_under: Optional[Decimal] = None
    source_ts: datetime
    ingested_ts: datetime = Field(default_factory=datetime.now)
    is_best_over: bool = False
    is_best_under: bool = False
    is_soft_book: bool = False
    is_sharp_book: bool = False
    confidence: Optional[float] = None

    class Config:
        from_attributes = True
