from datetime import datetime
from pydantic import BaseModel

class LineMoveOut(BaseModel):
    id: int
    sport: str
    player: str
    market: str
    open_line: float
    current_line: float
    direction: str
    book: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
