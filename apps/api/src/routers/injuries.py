from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.session import get_db
from models.injury import Injury
from schemas.injury import InjuryOut

router = APIRouter()

@router.get("")
async def news(
    sport: str = Query("basketball_nba"),
    db: Session = Depends(get_db),
):
    return (
        db.query(Injury)
        .filter(Injury.sport == sport)
        .order_by(Injury.created_at.desc())
        .all()
    )
