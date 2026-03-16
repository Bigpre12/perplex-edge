from datetime import datetime
from pydantic import BaseModel

class InjuryOut(BaseModel):
    id: int
    sport: str
    player: str
    team: str
    status: str
    note: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
