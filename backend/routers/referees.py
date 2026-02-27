from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from services.referee_service import get_ref_tendencies, get_game_refs

router = APIRouter(prefix="/referees", tags=["intelligence"])

@router.get("/tendencies")
async def referee_tendencies(
    crew: str = Query(..., description="Comma-separated referee names"),
    db: Session = Depends(get_db)
):
    """
    Returns referee-specific tendencies (foul rate, pace impact).
    """
    ref_list = crew.split(",") if crew else []
    return get_ref_tendencies(ref_list, db)

@router.get("/game/{game_id}")
async def game_referees(game_id: str, db: Session = Depends(get_db)):
    """
    Returns the referee crew for a specific game and their associated tendencies.
    """
    crew = get_game_refs(game_id, db)
    if not crew:
        return {"message": "No referee data available for this game"}
    return get_ref_tendencies(crew, db)
