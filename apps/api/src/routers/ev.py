import logging
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime
from db.session import get_db

router = APIRouter(tags=["ev"])
logger = logging.getLogger(__name__)

@router.get("")
@router.get("/")
async def get_ev_signals(
    sport: Optional[str] = Query(None),
    limit: int = Query(50),
    db=Depends(get_db)
):
    # 1. Try ev_signals table first
    try:
        rows = await db.fetch_all(
            """SELECT * FROM ev_signals 
               WHERE created_at > NOW() - INTERVAL '24 hours'
               ORDER BY ev_percentage DESC NULLS LAST
               LIMIT :limit""",
            {"limit": limit}
        )
        if rows:
            return {
                "props": [dict(r) for r in rows],
                "count": len(rows),
                "updated": datetime.utcnow().isoformat() + "Z",
                "source": "ev_signals"
            }
    except Exception:
        pass

    # 2. Fallback: pull from props_live with on-the-fly EV calc
    try:
        query = """
            SELECT *,
              ROUND(
                (CAST(1.0 AS NUMERIC) / NULLIF(implied_over, 0) - implied_over) * 100,
                2
              ) AS ev_pct
            FROM props_live
            WHERE last_updated_at > NOW() - INTERVAL '24 hours'
              AND implied_over IS NOT NULL
              AND implied_over > 0
              AND implied_over < 1
        """
        params = {"limit": limit}
        if sport:
            query += " AND sport = :sport"
            params["sport"] = sport
        query += " ORDER BY implied_over ASC LIMIT :limit"

        rows = await db.fetch_all(query, params)
        return {
            "props": [dict(r) for r in rows],
            "count": len(rows),
            "updated": datetime.utcnow().isoformat() + "Z",
            "source": "props_live_fallback",
            "fallback": "computed_live"
        }
    except Exception as e:
        return {"props": [], "count": 0, "error": str(e), 
                "updated": datetime.utcnow().isoformat() + "Z"}

@router.get("/ev-top")
async def get_ev_top(limit: int = Query(20), db=Depends(get_db)):
    # Reuse the same logic, higher threshold
    return await get_ev_signals(sport=None, limit=limit, db=db)

@router.get("/{sport_path}")
async def get_ev_by_sport(sport_path: str, limit: int = Query(50), db=Depends(get_db)):
    return await get_ev_signals(sport=sport_path, limit=limit, db=db)
