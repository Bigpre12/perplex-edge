from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.session import get_db
from models.line_move import LineMove
from schemas.line_move import LineMoveOut

router = APIRouter()

@router.get("", response_model=list[LineMoveOut])
async def line_movement(
    sport: str = Query("basketball_nba"),
    db: Session = Depends(get_db),
):
    return (
        db.query(LineMove)
        .filter(LineMove.sport == sport)
        .order_by(LineMove.created_at.desc())
        .all()
    )
