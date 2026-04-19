from fastapi import APIRouter, Depends, Query
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from services.props_live_query import props_live_game_time_window
from db.session import get_async_db
from models.brain import PropLive, PropHistory, HitRateModel
from schemas.unified import PropHistorySchema
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter(tags=["hero"])

@router.get("")
@router.get("/")
async def get_player_hero_stats(
    name: str = Query(..., description="Player name"),
    sport: str = Query("basketball_nba"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Returns consolidated Hero view data for a specific player.
    Matches frontend API.hero() call.
    """
    try:
        # 1. Get current live line
        stmt = select(PropLive).where(
            PropLive.player_name == name,
            PropLive.sport == sport,
            props_live_game_time_window(PropLive.game_start_time),
        ).order_by(desc(PropLive.last_updated_at)).limit(1)
        
        res = await db.execute(stmt)
        current = res.scalar_one_or_none()
        
        # 2. Get Historical Heatmap/Trend
        hist_stmt = select(PropHistory).where(
            PropHistory.player_name == name,
            PropHistory.sport == sport
        ).order_by(desc(PropHistory.snapshot_at)).limit(20)
        
        hist_res = await db.execute(hist_stmt)
        history_rows = hist_res.scalars().all()
        
        # 3. Get Hit Rate Stats from pre-computed model if available
        hr_stmt = select(HitRateModel).where(
            HitRateModel.player_name == name
        ).limit(1)
        
        hr_res = await db.execute(hr_stmt)
        hr_model = hr_res.scalar_one_or_none()
        
        # Basic stats calculation if model is missing
        l5_hit = hr_model.l5_hit_rate if hr_model else 0.0
        l10_hit = hr_model.l10_hit_rate if hr_model else 0.0
        
        return {
            "status": "success",
            "player": name,
            "sport": sport,
            "current": {
                "line": current.line if current else None,
                "market": current.market_key if current else None,
                "odds_over": float(current.odds_over) if current and current.odds_over else None,
                "odds_under": float(current.odds_under) if current and current.odds_under else None,
            },
            "stats": {
                "l5_hit": l5_hit,
                "l10_hit": l10_hit,
                "season_avg": 0.0 # To be populated by aggregation service
            },
            "history": [PropHistorySchema.model_validate(h) for h in history_rows]
        }
    except Exception as e:
        logger.error(f"Hero stats error for {name}: {e}")
        return {"status": "error", "message": str(e)}
