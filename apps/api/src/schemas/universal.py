from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

T = TypeVar("T")


class PerplexEdgeErrorBody(BaseModel):
    """Standard error envelope for API clients (Perplex Edge)."""
    code: str = "error"
    message: str
    request_id: Optional[str] = None
    details: Optional[Any] = None


class PerplexEdgeErrorResponse(BaseModel):
    error: PerplexEdgeErrorBody

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
