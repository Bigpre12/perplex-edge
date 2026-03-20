from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any

router = APIRouter()

@router.get("/ev-top")
async def get_ev_top(
    sport: str = Query(...),
    limit: int = Query(10),
) -> List[Dict[str, Any]]:
    """Returns top EV signals for the intel dashboard."""
    # This is a placeholder that will be expanded with real EVEngine queries.
    return []
