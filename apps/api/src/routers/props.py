from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.session import get_db
from models.props import Prop
from schemas.prop import PropOut, PropsScoredResponse

router = APIRouter()

@router.get("", response_model=list[PropOut])
async def list_props(
    sport: str = Query("basketball_nba"),
    limit: int = Query(25, le=100),
    db: Session = Depends(get_db),
):
    return (
        db.query(Prop)
        .filter(Prop.sport == sport)
        .order_by(Prop.created_at.desc())
        .limit(limit)
        .all()
    )

@router.get("/scored", response_model=PropsScoredResponse)
async def scored_props(
    sport: str = Query("basketball_nba"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    items = (
        db.query(Prop)
        .filter(Prop.sport == sport, Prop.is_scored.is_(True))
        .order_by(Prop.created_at.desc())
        .limit(limit)
        .all()
    )
    return {"count": len(items), "items": items}
