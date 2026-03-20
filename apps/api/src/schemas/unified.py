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
    line: float
    book: str
    odds_over: Optional[float] = None
    odds_under: Optional[float] = None
    implied_over: Optional[float] = None
    implied_under: Optional[float] = None
    last_updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class PropHistorySchema(BaseModel):
    snapshot_at: datetime
    line: float
    odds_over: Optional[float] = None
    odds_under: Optional[float] = None
    
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
    market_key: str
    player_name: Optional[str] = None
    bookmaker: str
    price: float
    line: Optional[float] = None
    move_type: str
    created_at: datetime

    model_config = {"from_attributes": True}

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
