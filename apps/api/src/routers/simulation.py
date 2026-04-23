from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from common_deps import get_async_db
from services.monte_carlo_results_store import list_latest_by_sport

router = APIRouter(tags=["simulation"])


@router.get("/{sport}")
async def list_monte_carlo_results(sport: str, db: AsyncSession = Depends(get_async_db)):
    rows = await list_latest_by_sport(db, sport, 50)
    return {"sport": sport, "count": len(rows), "results": rows}
