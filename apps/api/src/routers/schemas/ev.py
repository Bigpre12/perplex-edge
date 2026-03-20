# routers/schemas/ev.py
from datetime import datetime
from pydantic import BaseModel

class EvEdge(BaseModel):
    sport: str
    league: str
    game_id: str
    game_start_time: datetime

    player_id: str
    player_name: str
    team: str

    market_key: str
    market_label: str
    line: float

    book: str
    side: str
    odds: int

    model_prob: float
    implied_prob: float
    edge_pct: float
    snapshot_at: datetime
