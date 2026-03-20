from fastapi import APIRouter, Depends, Response, status
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
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    health_status = {"status": "healthy", "database": "connected"}
    try:
        # Execute a simple query to check database connection
        await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Health Check: DB failure: {e}")
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    # Add timestamp to the response
    health_status["timestamp"] = datetime.now(timezone.utc).isoformat()
    
    return health_status

@router.get("/summary")
async def meta_summary():
    return {"status": "ok", "app": "LUCRIX"}
