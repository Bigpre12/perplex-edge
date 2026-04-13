from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel
from datetime import datetime

T = TypeVar("T")

class ResponseMeta(BaseModel):
    source: Optional[str] = None
    db_rows: Optional[int] = None
    last_sync: Optional[datetime] = None
    request_id: Optional[str] = None

class UniversalResponse(BaseModel, Generic[T]):
    status: str  # "ok", "no_data", "upstream_error", "pipeline_error"
    message: Optional[str] = None
    meta: Optional[ResponseMeta] = None
    data: List[T] = []
