from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class InjuryBase(BaseModel):
    sport_id: int
    player_id: int
    status: str
    status_detail: Optional[str] = None
    is_starter_flag: Optional[bool] = None
    probability: Optional[float] = None
    source: Optional[str] = None


class InjuryCreate(InjuryBase):
    updated_at: datetime


class InjuryRead(InjuryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    updated_at: datetime


class InjuryWithPlayer(InjuryRead):
    player_name: str
    team_name: Optional[str] = None
    position: Optional[str] = None


class InjuryList(BaseModel):
    items: list[InjuryWithPlayer]
    total: int
