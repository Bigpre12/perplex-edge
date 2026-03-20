from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()

@router.get("/")
@router.get("")
async def health_check():
    from db.session import AsyncSessionLocal
    from sqlalchemy import text
    db_ok = False
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_ok = True
    except Exception as e:
        import logging
        logging.error(f"Health Check: DB failure: {e}")
        db_ok = False
    
    return {
        "status": "ok" if db_ok else "degraded",
        "db": "connected" if db_ok else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/summary")
async def meta_summary():
    return {"status": "ok", "app": "LUCRIX"}
