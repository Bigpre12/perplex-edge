from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from services.dvp_service import get_dvp_rating, get_dvp_for_prop_card

router = APIRouter(prefix="/dvp", tags=["dvp"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/team/{team}/{position}/{prop_type}")
def team_dvp(team: str, position: str, prop_type: str, db: Session = Depends(get_db)):
    """How many times has this team allowed this prop to be hit by this position."""
    return get_dvp_rating(team, position, prop_type, db)

@router.get("/player/{player_id}")
def player_dvp(player_id: str, db: Session = Depends(get_db)):
    """Get DvP context ready to drop onto a prop card."""
    return get_dvp_for_prop_card(player_id, db)
