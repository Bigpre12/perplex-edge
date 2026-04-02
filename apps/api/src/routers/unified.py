from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from datetime import datetime
import asyncio
import logging

router = APIRouter(tags=["unified"])
logger = logging.getLogger(__name__)

@router.post("/compute")
async def trigger_unified_compute(
    sport: str = Query("basketball_nba"),
    db: AsyncSession = Depends(get_db)
):
    """
    Unified Backend Compute Trigger.
    Orchestrates EV, Sharp, Arbitrage, and Prop scoring in parallel.
    """
    from routers.ev import trigger_ev_compute
    from routers.props import trigger_props_compute
    from routers.sharp import trigger_sharp_compute
    from routers.arbitrage import trigger_arb_compute
    
    logger.info(f"🚀 [UNIFIED COMPUTE] Starting full intelligence cycle for {sport}...")
    
    # We call the functions directly to avoid network overhead
    tasks = [
        trigger_ev_compute(sport=sport, db=db),
        trigger_sharp_compute(sport=sport, db=db),
        trigger_arb_compute(sport=sport),
        trigger_props_compute(sport=sport, db=db)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    summary = {
        "ev": "ok" if not isinstance(results[0], Exception) else str(results[0]),
        "sharp": "ok" if not isinstance(results[1], Exception) else str(results[1]),
        "arb": "ok" if not isinstance(results[2], Exception) else str(results[2]),
        "props": "ok" if not isinstance(results[3], Exception) else str(results[3]),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return {
        "status": "ok",
        "message": f"Unified compute cycle completed for {sport}",
        "results": summary
    }
