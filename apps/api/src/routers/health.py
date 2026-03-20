from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone
import logging

from db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("")
@router.get("/")
async def health_check(
    db: AsyncSession = Depends(get_db)
):
    """
    Health check endpoint. Always returns 200 so Railway marks deployment
    as healthy. DB connectivity status is reported in the response body.
    """
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
        logger.info("Health Check: DB connection OK")
    except Exception as e:
        db_status = "disconnected"
        logger.error(f"Health Check: DB failure: {e}")

    return {
        "status": "ok",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/summary")
async def meta_summary():
    return {"status": "ok", "app": "LUCRIX"}
