from datetime import datetime
from pydantic import BaseModel

class PropOut(BaseModel):
    id: int
    sport: str
    player: str
    team: str | None = None
    market: str
    line: float
    odds: int
    book: str
    projection: float | None = None
    edge: float | None = None
    ev: float | None = None
    result: str | None = None
    actual: float | None = None
    is_scored: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class PropsScoredResponse(BaseModel):
    count: int
    items: list[PropOut]
