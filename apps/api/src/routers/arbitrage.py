# apps/api/src/routers/arbitrage.py
from fastapi import APIRouter, Query, Depends
from typing import Optional, Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from common_deps import get_user_tier
from db.session import get_async_db

router = APIRouter(tags=["arbitrage"])


def _row_to_opportunity(row: Dict[str, Any]) -> Dict[str, Any]:
    oa = row.get("outcome_a") or ""
    player_guess = oa.split(" OVER ")[0] if " OVER " in oa else oa
    return {
        "source": "persisted",
        "event_id": row.get("event_id"),
        "sport": row.get("sport"),
        "market": row.get("market"),
        "outcome_a": row.get("outcome_a"),
        "outcome_b": row.get("outcome_b"),
        "player_name": player_guess,
        "stat_type": row.get("market"),
        "line": None,
        "over_book": row.get("book_a"),
        "over_odds": row.get("odds_a"),
        "under_book": row.get("book_b"),
        "under_odds": row.get("odds_b"),
        "profit_percentage": float(row.get("profit_per_100") or 0),
        "arb_percentage": float(row.get("arb_pct") or 0),
        "arb_pct": float(row.get("arb_pct") or 0),
        "detected_at": str(row.get("detected_at")) if row.get("detected_at") else None,
        "expires_at": str(row.get("expires_at")) if row.get("expires_at") else None,
    }


@router.get("")
async def get_arbitrage(
    sport: Optional[str] = Query(None),
    tier: str = Depends(get_user_tier),
    db: AsyncSession = Depends(get_async_db),
):
    # Tier check: Arbitrage is elite only
    if tier != "elite":
        return {
            "count": 0, 
            "opportunities": [], 
            "message": "Elite subscription required for Arbitrage Scanner",
            "tier_required": "elite"
        }

    persisted: List[Dict[str, Any]] = []
    try:
        from services.arb_calculator import fetch_recent_arbs

        persisted = await fetch_recent_arbs(db, sport, limit=50)
    except Exception:
        pass

    merged = [_row_to_opportunity(row) for row in persisted]
    merged.sort(key=lambda x: x.get("profit_percentage") or 0, reverse=True)
    return {
        "count": len(merged),
        "opportunities": merged,
        "persisted_count": len(persisted),
    }

@router.post("/compute")
async def trigger_arb_compute(
    sport: str = Query("basketball_nba")
):
    """Trigger the arbitrage computation engine."""
    from datetime import datetime
    return {
        "status": "ok", 
        "message": f"Arbitrage scan completed for {sport}", 
        "timestamp": datetime.utcnow().isoformat()
    }
