from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from models.prop import PropLine

router = APIRouter(tags=["search"])

@router.get("")
@router.get("/")
async def search_props(q: str, db: AsyncSession = Depends(get_db)):
    if not q or len(q) < 3:
        return {"results": []}
        
    try:
        search_term = f"%{q}%"
        
        # Using PropLine as it's the current model for player props
        stmt = select(PropLine).filter(
            PropLine.is_settled == False,
            or_(
                PropLine.player_name.ilike(search_term),
                PropLine.team.ilike(search_term)
            )
        ).order_by(PropLine.steam_score.desc()).limit(10)
        
        res = await db.execute(stmt)
        props = res.scalars().all()
        
        return {"results": props}
    except Exception as e:
        import logging
        logging.error(f"Search error for {q}: {e}")
        return {"results": []}
