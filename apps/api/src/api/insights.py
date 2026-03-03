from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from services.insight_engine import get_player_insights

router = APIRouter(prefix="/insights", tags=["insights"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/player/{player_id}/{prop_type}")
def player_insights(
    player_id: str, 
    prop_type: str, 
    line: float = Query(..., description="The prop line, e.g. 24.5"), 
    db: Session = Depends(get_db)
):
    """
    Returns hit rate trends (L5, L15) and 'heating_up'/'cooling_down' momentum signals.
    Used for the Deep Player Profile cards.
    """
    return get_player_insights(player_id, prop_type, line, db)
