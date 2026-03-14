import logging
from fastapi import APIRouter, HTTPException
from jobs.ingestion_service import ingest_all_odds

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/picks")
async def sync_picks():
    """Manual trigger to sync picks from external providers (Odds API)."""
    try:
        logger.info("Manual sync triggered via /api/sync/picks")
        await ingest_all_odds()
        return {"status": "success", "message": "Ingestion cycle completed."}
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
