from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class InjuryOut(BaseModel):
    id: int
    sport: str
    player: str
    team: str
    status: str
    note: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class InjuryImpactSchema(BaseModel):
    id: int
    player_name: str
    sport: str
    team: Optional[str] = None
    impact_score: float
    created_at: datetime

    model_config = {"from_attributes": True}
