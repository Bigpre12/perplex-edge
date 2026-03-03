from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.saved_system import SavedSystem
from pydantic import BaseModel
from typing import Dict, Any, List

router = APIRouter(prefix="/systems", tags=["systems"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SystemCreate(BaseModel):
    user_id: str
    name: str
    filters: Dict[str, Any]

class SystemUpdate(BaseModel):
    won: bool
    odds: float = -110
    stake: float = 1.0

@router.post("/")
def create_system(body: SystemCreate, db: Session = Depends(get_db)):
    """Create a new saved system for a user."""
    system = SavedSystem(**body.model_dump())
    db.add(system)
    db.commit()
    db.refresh(system)
    return system

@router.get("/user/{user_id}")
def get_user_systems(user_id: str, db: Session = Depends(get_db)):
    """Fetch all saved systems for a specific user ID."""
    return db.query(SavedSystem).filter(SavedSystem.user_id == user_id).all()

@router.patch("/{system_id}/record")
def record_result(system_id: int, body: SystemUpdate, db: Session = Depends(get_db)):
    """Record a win/loss for a system and update its ROI and units profit."""
    system = db.query(SavedSystem).filter(SavedSystem.id == system_id).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    system.total_bets += 1
    if body.won:
        system.wins += 1
        # Calculate net profit based on odds
        # If -110: 1 unit wagered -> 0.91 profit
        # If +150: 1 unit wagered -> 1.5 profit
        if body.odds < 0:
            profit = body.stake * (100 / abs(body.odds))
        else:
            profit = body.stake * (body.odds / 100)
        system.units_profit += profit
    else:
        system.units_profit -= body.stake

    # ROI = (Net Profit / Total Wagered) * 100
    total_wagered = system.total_bets * body.stake
    if total_wagered > 0:
        system.roi = (system.units_profit / total_wagered) * 100
        
    db.commit()
    db.refresh(system)
    return system

@router.delete("/{system_id}")
def delete_system(system_id: int, db: Session = Depends(get_db)):
    """Delete a saved system."""
    system = db.query(SavedSystem).filter(SavedSystem.id == system_id).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    db.delete(system)
    db.commit()
    return {"ok": True}
