from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.session import get_db

router = APIRouter()

@router.get("/sharp-moves")
async def sharp_moves(
    sport: str = Query("basketball_nba"),
    db: Session = Depends(get_db),
):
    return {"sport": sport, "items": []}

@router.get("/freshness")
async def freshness(
    sport: str = Query("basketball_nba"),
):
    return {"sport": sport, "status": "fresh", "age_seconds": 0}
