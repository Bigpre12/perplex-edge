from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PlayerBase(BaseModel):
    sport_id: int
    team_id: Optional[int] = None
    external_player_id: str
    name: str
    position: Optional[str] = None


class PlayerCreate(PlayerBase):
    pass


class PlayerRead(PlayerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class PlayerWithTeam(PlayerRead):
    team_name: Optional[str] = None
    team_abbreviation: Optional[str] = None


class PlayerList(BaseModel):
    items: list[PlayerRead]
    total: int
