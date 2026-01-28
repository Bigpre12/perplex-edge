from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SportBase(BaseModel):
    name: str
    league_code: str


class SportCreate(SportBase):
    pass


class SportRead(SportBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class SportList(BaseModel):
    items: list[SportRead]
    total: int
