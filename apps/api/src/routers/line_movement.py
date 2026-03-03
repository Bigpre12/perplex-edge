from fastapi import APIRouter, Query
from services.line_movement_service import line_movement_service
from typing import Optional

router = APIRouter(prefix="/line-movement", tags=["intelligence"])

@router.get("/velocity")
async def market_velocity(market_id: str = Query(...)):
    """
    Returns the speed of line movement (odds change per hour).
    """
    velocity = line_movement_service.get_velocity(market_id)
    return {"market_id": market_id, "velocity": velocity}

@router.get("/steam")
async def market_steam(market_id: str = Query(...)):
    """
    Detects if there is active 'Steam' or 'Sharp Action' on a market.
    """
    steam = line_movement_service.detect_steam(market_id)
    return {"market_id": market_id, "steam": steam}
