from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class UserOut(BaseModel):
    id: str
    email: str
    role: str
    tier: str
    created_at: datetime

    model_config = {"from_attributes": True}

class SystemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class SystemOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
