from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TeamBase(BaseModel):
    sport_id: int
    external_team_id: str
    name: str
    abbreviation: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class TeamList(BaseModel):
    items: list[TeamRead]
    total: int
