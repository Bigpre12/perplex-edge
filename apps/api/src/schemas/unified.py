from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

class PropLiveSchema(BaseModel):
    id: int
    sport: str
    league: Optional[str] = None
    game_id: str
    game_start_time: Optional[datetime] = None
    player_name: Optional[str] = None
    market_key: str
    line: Optional[float] = None
    book: str
    odds_over: Optional[float] = None
    odds_under: Optional[float] = None
    implied_over: Optional[float] = None
    implied_under: Optional[float] = None
    team: Optional[str] = None
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    is_best_over: bool = False
    is_best_under: bool = False
    is_soft_book: bool = False
    is_sharp_book: bool = False
    confidence: Optional[float] = None

    model_config = {"from_attributes": True}

class PropHistorySchema(BaseModel):
    snapshot_at: datetime
    line: Optional[float] = None
    odds_over: Optional[float] = None
    odds_under: Optional[float] = None
    is_best_over: bool = False
    is_best_under: bool = False
    is_soft_book: bool = False
    is_sharp_book: bool = False
    confidence: Optional[float] = None
    
    model_config = {"from_attributes": True}

class EvEdgeSchema(BaseModel):
    id: int
    event_id: str
    market_key: str
    side: str
    player_name: Optional[str] = None
    bookmaker: str
    edge: float = Field(alias="edge_pct")
    price: float = Field(alias="odds")
    line: Optional[float] = None
    model_prob: Optional[float] = None
    implied_prob: float
    updated_at: datetime = Field(alias="snapshot_at")
    trend: List[float] = [] 

    model_config = {"from_attributes": True, "populate_by_name": True}

class WhaleEventSchema(BaseModel):
    id: int
    sport: str
    event_id: Optional[str] = None
    player_name: Optional[str] = None
    market: Optional[str] = Field(default=None, alias="market_key")
    book: Optional[str] = Field(default=None, alias="bookmaker")
    price_before: Optional[float] = None
    price_after: Optional[float] = None
    line: Optional[float] = None
    whale_rating: Optional[float] = Field(default=0.0)
    move_size: Optional[str] = None
    side: Optional[str] = None
    selection: Optional[str] = None
    move_type: Optional[str] = "WHALE"
    timestamp: Optional[datetime] = Field(default=None, alias="created_at")

    model_config = {"from_attributes": True, "populate_by_name": True}

class ClvTradeSchema(BaseModel):
    id: int
    player: str
    sport: str
    market: str
    open_line: float
    close_line: float
    clv_value: float
    beat: bool
    timestamp: datetime

    model_config = {"from_attributes": True}
