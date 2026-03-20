from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from models.prop import Prop # Using Prop as proxy for PropLine if not exists
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{player_id}")
async def player_streaks(
    player_id: str,
    prop_type: str = Query("points"),
    db: AsyncSession = Depends(get_db)
):
    """Market Streak Engine (Fix #10: player_id string cast)"""
    try:
        # Cast player_id to string to match DB type (Fix #10)
        result = await db.execute(
            select(Prop)
            .where(
                Prop.player_name == str(player_id), 
                Prop.sport.is_not(None) # Generic filter
            )
            .limit(10)
        )
        lines = result.scalars().all()
        
        return {
            "player_id": player_id,
            "prop_type": prop_type,
            "streaks": lines,
            "status": "active"
        }
    except Exception as e:
        logger.error(f"Error in streaks: {e}")
        return {"error": str(e)}
