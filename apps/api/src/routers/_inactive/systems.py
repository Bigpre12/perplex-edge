class AsyncSession: pass
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from database import get_async_db
from models.saved_system import SavedSystem
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/systems", tags=["systems"])

class SystemCreate(BaseModel):
    user_id: str
    name: str # The user defined name
    filters: Dict[str, Any]

class SystemUpdate(BaseModel):
    won: bool
    odds: float = -110
    stake: float = 1.0

@router.post("")
async def create_system(body: SystemCreate, db: AsyncSession = Depends(get_async_db)):
    system = SavedSystem(**body.model_dump())
    db.add(system)
    await db.commit()
    await db.refresh(system)
    return system

@router.get("/user/{user_id}")
async def get_user_systems(user_id: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(SavedSystem).where(SavedSystem.user_id == user_id))
    return result.scalars().all()

@router.patch("/{system_id}/record")
async def record_result(system_id: int, body: SystemUpdate, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(SavedSystem).where(SavedSystem.id == system_id))
    system = result.scalar_one_or_none()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    system.total_bets += 1
    if body.won:
        system.wins += 1
        profit = body.stake * (100 / abs(body.odds)) if body.odds < 0 else body.stake * (body.odds / 100)
        system.units_profit += profit
    else:
        system.units_profit -= body.stake
    total_wagered = system.total_bets * body.stake
    if total_wagered > 0:
        system.roi = system.units_profit / total_wagered * 100
    await db.commit()
    await db.refresh(system)
    return system

@router.delete("/{system_id}")
async def delete_system(system_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(SavedSystem).where(SavedSystem.id == system_id))
    system = result.scalar_one_or_none()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    await db.delete(system)
    await db.commit()
    return {"ok": True}
