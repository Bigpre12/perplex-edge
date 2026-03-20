from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from models.saved_system import SavedSystem
from schemas.user import SystemCreate, SystemOut
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("", response_model=SystemOut)
async def create_system(body: SystemCreate, db: AsyncSession = Depends(get_db)):
    """Institutional Neural System Builder (Fix #2: Async)"""
    try:
        system = SavedSystem(**body.model_dump())
        db.add(system)
        await db.commit()
        await db.refresh(system)
        return system
    except Exception as e:
        logger.error(f"Error creating system: {e}")
        raise

@router.get("", response_model=list[SystemOut])
async def list_systems(db: AsyncSession = Depends(get_db)):
    stmt = select(SavedSystem).order_by(SavedSystem.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()
