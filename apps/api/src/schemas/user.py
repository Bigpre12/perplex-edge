from datetime import datetime
from pydantic import BaseModel

class UserOut(BaseModel):
    id: str
    email: str
    role: str
    tier: str
    created_at: datetime

    model_config = {"from_attributes": True}
