from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MarketBase(BaseModel):
    sport_id: int
    market_type: str
    stat_type: Optional[str] = None
    description: Optional[str] = None


class MarketCreate(MarketBase):
    pass


class MarketRead(MarketBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class MarketList(BaseModel):
    items: list[MarketRead]
    total: int
