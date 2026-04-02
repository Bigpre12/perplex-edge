import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from sqlalchemy import text
from db.session import get_db
from api_utils.tier_guards import require_tier
from models.user import User

router = APIRouter(tags=["ev"])
logger = logging.getLogger(__name__)

@router.get("")
@router.get("/")
async def get_ev_signals(
    sport: Optional[str] = Query(None),
    limit: int = Query(50),
    db=Depends(get_db),
    current_user: User = Depends(require_tier("pro"))
):
    # 1. Try ev_signals table first
    try:
        sql = """
            SELECT *, edge_percent as ev_percentage, true_prob as fair_prob 
            FROM ev_signals 
            WHERE created_at > NOW() - INTERVAL '24 hours'
        """
        params = {"limit": limit}
        if sport:
            sql += " AND sport = :sport"
            params["sport"] = sport
            
        sql += " ORDER BY edge_percent DESC NULLS LAST LIMIT :limit"
        
        result = await db.execute(text(sql), params)
        rows = result.mappings().all()
        if rows:
            return {
                "props": [dict(r) for r in rows],
                "count": len(rows),
                "updated": datetime.utcnow().isoformat() + "Z",
                "source": "ev_signals"
            }
    except Exception as e:
        logger.warning(f"Error reading ev_signals (fallback next): {e}")
        try:
            await db.rollback()
        except Exception:
            pass

    # 2. Fallback: pull from props_live with on-the-fly EV calc
    try:
        query = """
            SELECT
                player_name,
                market_key,
                sport,
                book,
                line,
                odds_over,
                odds_under,
                implied_over,
                implied_under,
                confidence,
                home_team,
                away_team,
                last_updated_at
            FROM props_live
            WHERE last_updated_at > NOW() - INTERVAL '24 hours'
            AND implied_over IS NOT NULL
            AND implied_over > 0
            AND implied_over < 1
            AND implied_under IS NOT NULL
            AND implied_under > 0
            AND implied_under < 1
            AND (implied_over + implied_under) BETWEEN 0.85 AND 1.15
        """
        params: dict = {"limit": limit}
        if sport:
            query += " AND sport = :sport"
            params["sport"] = sport
            
        query += " ORDER BY confidence DESC LIMIT :limit"

        result = await db.execute(text(query), params)
        rows = result.mappings().all()

        # Compute EV in Python — normalize to no-vig fair probs first
        edges = []
        for r in rows:
            row = dict(r)
            try:
                total_implied = row['implied_over'] + row['implied_under']
                fair_over = row['implied_over'] / total_implied
                fair_under = row['implied_under'] / total_implied
                dec_over = 1 / row['implied_over'] if row['implied_over'] > 0 else 0
                dec_under = 1 / row['implied_under'] if row['implied_under'] > 0 else 0
                ev_over = round((fair_over * dec_over - 1) * 100, 2)
                ev_under = round((fair_under * dec_under - 1) * 100, 2)
                best_ev = max(ev_over, ev_under)
                recommendation = 'OVER' if ev_over >= ev_under else 'UNDER'
                # Only keep edges in the 2–20% range (noise filter)
                if 2.0 <= best_ev <= 20.0:
                    row['ev_pct'] = best_ev
                    row['recommendation'] = recommendation
                    edges.append(row)
            except Exception:
                continue

        return {
            "props": edges,
            "count": len(edges),
            "status": "ok" if edges else "no_data",
            "updated": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        try:
            await db.rollback()
        except Exception:
            pass
        return {"props": [], "count": 0, "error": str(e), 
                "status": "error",
                "updated": datetime.utcnow().isoformat() + "Z"}

@router.get("/ev-top")
async def get_ev_top(
    limit: int = Query(20), 
    db=Depends(get_db),
    current_user: User = Depends(require_tier("pro"))
):
    # Reuse the same logic, higher threshold
    return await get_ev_signals(sport=None, limit=limit, db=db, current_user=current_user)

@router.get("/{sport_path}")
async def get_ev_by_sport(
    sport_path: str, 
    limit: int = Query(50), 
    db=Depends(get_db),
    current_user: User = Depends(require_tier("pro"))
):
    return await get_ev_signals(sport=sport_path, limit=limit, db=db, current_user=current_user)

@router.post("/compute")
async def trigger_ev_compute(
    sport: str = Query("basketball_nba"),
    db: AsyncSession = Depends(get_db)
):
    """Trigger the EV scoring engine for a specific sport."""
    from services.ev_service import ev_service
    from services.heartbeat_service import HeartbeatService
    try:
        await ev_service.run_ev_cycle(sport)
        await HeartbeatService.log_heartbeat(db, f"ev_grader_{sport}")
        return {"status": "ok", "message": f"EV computation triggered for {sport}", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"EV Compute Trigger Failed: {e}")
        return {"status": "error", "message": str(e)}
