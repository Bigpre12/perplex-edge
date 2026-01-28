from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TeamInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    abbreviation: Optional[str] = None


class GameBase(BaseModel):
    sport_id: int
    external_game_id: str
    home_team_id: int
    away_team_id: int
    start_time: datetime
    status: str = "scheduled"


class GameCreate(GameBase):
    pass


class GameRead(GameBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class GameWithTeams(GameRead):
    home_team: TeamInfo
    away_team: TeamInfo


class OddsInfo(BaseModel):
    sportsbook: str
    market_type: str
    side: str
    line_value: Optional[float] = None
    odds: float


class GameWithOdds(GameWithTeams):
    odds: list[OddsInfo] = []


class GameList(BaseModel):
    items: list[GameWithTeams]
    total: int
