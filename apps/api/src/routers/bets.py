from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from models.bets import Bet
from schemas.bet import BetOut, BetCreate

router = APIRouter()

@router.get("", response_model=list[BetOut])
async def list_bets(db: Session = Depends(get_db)):
    return db.query(Bet).order_by(Bet.created_at.desc()).all()

@router.post("", response_model=BetOut)
async def create_bet(payload: BetCreate, db: Session = Depends(get_db)):
    bet = Bet(**payload.model_dump(), status="open")
    db.add(bet)
    db.commit()
    db.refresh(bet)
    return bet

@router.delete("/{bet_id}")
async def delete_bet(bet_id: int, db: Session = Depends(get_db)):
    bet = db.query(Bet).filter(Bet.id == bet_id).first()
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    db.delete(bet)
    db.commit()
    return {"success": True}
