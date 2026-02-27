from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from services.h2h_service import get_h2h_splits, check_back_to_back, get_home_away_splits

router = APIRouter(prefix="/h2h", tags=["intelligence"])

@router.get("/splits")
async def player_h2h_splits(
    player_id: str = Query(...),
    opponent: str = Query(...),
    stat: str = Query("points"),
    seasons: int = Query(3),
    db: Session = Depends(get_db)
):
    """
    Returns head-to-head historical performance for a specific player against an opponent.
    """
    return get_h2h_splits(player_id, opponent, stat, db, seasons)

@router.get("/fatigue")
async def player_fatigue(
    player_id: str = Query(...),
    date: str = Query(..., description="ISO date YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    Calculates fatigue risk based on B2B or 3-in-4 game schedules.
    """
    return check_back_to_back(player_id, date, db)

@router.get("/home-away")
async def player_home_away(
    player_id: str = Query(...),
    stat: str = Query("points"),
    db: Session = Depends(get_db)
):
    """
    Returns Home vs Away performance splits.
    """
    return get_home_away_splits(player_id, stat, db)
