from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def meta_health():
    return {
        "status": "healthy",
        "service": "meta",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@router.get("/summary")
async def meta_summary():
    return {
        "status": "ok",
        "app": "Perplex Edge",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@router.get("/username")
async def meta_username():
    return {"username": "demo-user"}
