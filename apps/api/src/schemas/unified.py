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
    event_id: str
    player_name: Optional[str] = None
    market: str = Field(alias="market_key")
    book: str = Field(alias="bookmaker")
    odds: float = Field(alias="price")
    line: Optional[float] = None
    units: float = Field(default=10.0, alias="whale_rating") 
    move_type: Optional[str] = "WHALE"
    timestamp: datetime = Field(alias="created_at")

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
