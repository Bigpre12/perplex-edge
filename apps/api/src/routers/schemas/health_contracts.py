from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DependencyStatus(BaseModel):
    status: str
    error: Optional[str] = None


class DegradationStatus(BaseModel):
    level: str
    reasons: List[str]
    user_message: str


class HealthResponse(BaseModel):
    status: str
    dependencies: Dict[str, DependencyStatus]
    database: str
    odds_api: str
    kalshi: str
    sportmonks: str
    odds_api_all_keys_cooldown: bool
    cache: str
    inference_status: str
    pipeline_status: str
    odds_stream: str
    system_status: str
    version: str
    timestamp: str
    last_odds_update: Optional[str] = None
    last_ev_update: Optional[str] = None
    props_count: int
    odds_quota: Dict[str, Any]
    last_odds_sync: Optional[str] = None
    last_ev_sync: Optional[str] = None
    last_grade_sync: Optional[str] = None


class HealthDepsResponse(BaseModel):
    status: str
    dependencies: Dict[str, DependencyStatus]
    overall: str
    system_status: str
    degradation: DegradationStatus
    freshness: Dict[str, Optional[str]]
    components: Dict[str, Any]
    timestamp: str
    version: str
    sync: Dict[str, Optional[str]]

