from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
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
    health_status = {"status": "healthy", "database": "connected", "timestamp": datetime.now(timezone.utc).isoformat()}
    try:
        # Execute a simple query to check database connection
        await db.execute(text("SELECT 1"))
        return health_status
    except Exception as e:
        logger.error(f"Health Check: DB failure (returning 503): {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

@router.get("/summary")
async def meta_summary():
    return {"status": "ok", "app": "LUCRIX"}
