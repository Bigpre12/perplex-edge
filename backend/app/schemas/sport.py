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
    active: bool


class SportResponse(BaseModel):
    """Sport response model for API endpoints."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    league_code: str
    active: bool
    created_at: datetime
    updated_at: datetime


class SportList(BaseModel):
    items: list[SportResponse]
    total: int
