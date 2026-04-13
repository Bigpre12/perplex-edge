# routers/schemas/props_history.py
from datetime import datetime
from pydantic import BaseModel

class PropLineSnapshot(BaseModel):
    snapshot_at: datetime
    sport: str
    league: str
    game_id: str
    player_id: str
    player_name: str
    team: str
    market_key: str
    market_label: str
    line: float
    book: str
    odds_over: int
    odds_under: int
