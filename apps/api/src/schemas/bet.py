from datetime import datetime
from pydantic import BaseModel

class BetCreate(BaseModel):
    user_id: str
    player: str
    market: str
    pick: str
    line: float
    odds: int
    stake: float

class BetOut(BaseModel):
    id: int
    user_id: str
    player: str
    market: str
    pick: str
    line: float
    odds: int
    stake: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
