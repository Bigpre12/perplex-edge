from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class LineBase(BaseModel):
    game_id: int
    market_id: int
    player_id: Optional[int] = None
    sportsbook: str
    line_value: Optional[float] = None
    odds: float
    side: str
    is_current: bool = True


class LineCreate(LineBase):
    fetched_at: datetime


class LineRead(LineBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fetched_at: datetime


class LineWithDetails(LineRead):
    market_type: str
    stat_type: Optional[str] = None
    player_name: Optional[str] = None


class LineList(BaseModel):
    items: list[LineRead]
    total: int


class BookmakerLine(BaseModel):
    sportsbook: str
    odds: float
    line_value: Optional[float] = None


class LineComparison(BaseModel):
    """Compare lines across sportsbooks for the same market."""
    game_id: int
    market_type: str
    side: str
    stat_type: Optional[str] = None
    player_name: Optional[str] = None
    lines: list[BookmakerLine]
    best_odds: float
    best_sportsbook: str
    consensus_line: Optional[float] = None
