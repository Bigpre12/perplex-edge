from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends
from db.session import get_db, get_async_db
from models.brain import BrainSystemState, ModelPick
try:
    from core.state import state
except ImportError:
    class _State:
        system_online = True
        last_updated = None
        def get_summary(self): return "active (fallback)"
    state = _State()
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

from common_deps import require_pro, get_user_tier
from services.brain_advanced_service import brain_advanced_service

router = APIRouter(tags=["Brain Intelligence"])
user_router = APIRouter()

@user_router.get("/decisions")
async def get_prop_score(sport: str = "basketball_nba", db: AsyncSession = Depends(get_db), tier: str = Depends(get_user_tier)):
    if tier not in ("pro", "elite"): return []
    try:
        results = await brain_advanced_service.get_prop_score(sport, db)
        return {"items": results, "decisions": results}
    except Exception as e:
        logger.error(f"Error in prop-score: {e}")
        return {"items": [], "decisions": []}

@user_router.get("/parlay-builder")
async def get_parlay_builder(sport: str = "basketball_nba", legs: int = 3, min_score: int = 65, db: AsyncSession = Depends(get_async_db), tier: str = Depends(get_user_tier)):
    if tier not in ("pro", "elite"): return {"legs": [], "sport": sport, "message": "Pro or Elite subscription required"}
    try:
        res = await brain_advanced_service.build_parlay(sport, legs, min_score, db)
        if not res or not isinstance(res, list) or not res[0].get("legs"):
            return {"legs": [], "sport": sport, "message": "No high-confidence props qualify right now"}
        return res[0] # Return the first parlay object instead of a list containing one object
    except Exception as e:
        logger.error(f"Error in parlay-builder: {e}")
        return {"legs": [], "sport": sport, "message": "No high-confidence props qualify right now", "error": str(e)}

@user_router.get("/live-analysis")
async def get_live_analysis(sport: str = "basketball_nba", tier: str = Depends(get_user_tier)):
    if tier not in ("pro", "elite"): return []
    try:
        return await brain_advanced_service.analyze_live_games(sport)
    except Exception as e:
        logger.error(f"Error in live-analysis: {e}")
        return []

@user_router.get("/injury-impact")
async def get_injury_impact(sport: str = "basketball_nba", tier: str = Depends(get_user_tier)):
    if tier not in ("pro", "elite"): return []
    try:
        return await brain_advanced_service.analyze_injuries(sport)
    except Exception as e:
        logger.error(f"Error in injury-impact: {e}")
        return []

@user_router.get("/steam-alerts")
async def get_steam_alerts(sport: str = "basketball_nba", db: AsyncSession = Depends(get_async_db), tier: str = Depends(get_user_tier)):
    if tier not in ("pro", "elite"): return []
    try:
        return await brain_advanced_service.check_steam_moves(sport, db)
    except Exception as e:
        logger.error(f"Error in steam-alerts: {e}")
        return []

@user_router.get("/insights")
async def get_reasoning_feed(sport: str = "basketball_nba", limit: int = 20, db: AsyncSession = Depends(get_async_db), tier: str = Depends(get_user_tier)):
    if tier not in ("pro", "elite"): return []
    try:
        return await brain_advanced_service.get_reasoning_feed(sport, limit, db)
    except Exception as e:
        logger.error(f"Error in reasoning-feed: {e}")
        return []

@user_router.get("/heatmap")
async def get_heatmap(sport: str = "basketball_nba", db: AsyncSession = Depends(get_async_db), tier: str = Depends(get_user_tier)):
    if tier not in ("pro", "elite"): return []
    try:
        return await brain_advanced_service.get_heatmap(sport, db)
    except Exception as e:
        logger.error(f"Error in heatmap: {e}")
        return []

@user_router.get("/metrics")
async def get_dashboard_metrics(db: AsyncSession = Depends(get_async_db), tier: str = Depends(get_user_tier)):
    if tier not in ("pro", "elite"): return {"status": "limited", "message": "Pro required"}
    try:
        return await brain_advanced_service.get_dashboard_metrics(db)
    except Exception as e:
        logger.error(f"Error in dashboard-metrics: {e}")
        return {}

# Attach user_router to the main exported router
router.include_router(user_router)

@router.get("/brain-status")
async def get_brain_health():
    try:
        return {
            "status": "healthy",
            "core_state": state.get_summary() if hasattr(state, 'get_summary') else "active",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Brain Health Error: {e}")
        return {"status": "error", "detail": str(e)}

@router.post("/analyze")
async def run_brain_analysis(payload: dict | None = None):
    return {
        "status": "success",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.post("/metrics/dashboard")
async def get_brain_metrics_post(db: AsyncSession = Depends(get_async_db)):
    try:
        from sqlalchemy import select
        stmt = select(ModelPick).where(ModelPick.clv_percentage != None).limit(5)
        res = await db.execute(stmt)
        stats = res.scalars().all()
        return {
            "clv_active": True,
            "metrics_available": len(stats) > 0,
            "sample_stats": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Brain Metrics Error: {e}")
        return {"status": "warming_up", "note": str(e)}

@router.post("")
@router.post("/")
async def brain_query(payload: dict, db: AsyncSession = Depends(get_async_db)):
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Missing SQL query")
    
    if not query.lower().startswith("select"):
        raise HTTPException(status_code=403, detail="Only SELECT queries allowed")
        
    try:
        from sqlalchemy import text
        result = await db.execute(text(query))
        rows = result.fetchall()
        return {"results": [dict(row._mapping) for row in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
