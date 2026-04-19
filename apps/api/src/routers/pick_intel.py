"""
Pick Intel — ranked, enriched player-prop edges from props_live (post-grader fields).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_db
from models.brain import PropLive
from services.props_live_query import props_live_game_time_window

logger = logging.getLogger(__name__)

router = APIRouter(tags=["pick-intel"])

TEAM_MARKETS = ("h2h", "spreads", "totals")


def _f(val: Any) -> float:
    try:
        if val is None:
            return 0.0
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def _market_clause(market: str):
    """Return SQLAlchemy boolean expression for market filter, or None for ALL."""
    m = (market or "ALL").strip().upper()
    if m == "ALL" or not m:
        return None
    mk = PropLive.market_key
    ml = PropLive.market_label
    if m == "POINTS":
        return or_(mk.ilike("%points%"), ml.ilike("%points%"))
    if m == "ASSISTS":
        return or_(mk.ilike("%assist%"), ml.ilike("%assist%"))
    if m == "REBOUNDS":
        return or_(mk.ilike("%rebound%"), ml.ilike("%rebound%"))
    if m == "THREES":
        return or_(
            mk.ilike("%three%"),
            mk.ilike("%3pt%"),
            ml.ilike("%three%"),
            ml.ilike("%3pt%"),
        )
    return or_(mk.ilike(f"%{m.lower()}%"), ml.ilike(f"%{m.lower()}%"))


def build_reasoning(p: PropLive, side: str, ev: float, tags: List[str]) -> str:
    parts: List[str] = []
    if "STEAM" in tags:
        parts.append("Sharp money moving this line")
    if "WHALE" in tags:
        parts.append("Large-volume action detected")
    if "SHARP BOOK" in tags:
        parts.append(f"Pinned by sharp book ({p.book})")
    if ev >= 8:
        parts.append(f"{ev:.1f}% edge vs market implied probability")
    elif ev >= 3:
        parts.append(f"Positive EV at {ev:.1f}% above fair value")
    if p.is_best_over and side == "OVER":
        parts.append("Best available over price across books")
    if p.is_best_under and side == "UNDER":
        parts.append("Best available under price across books")
    if "SHARP" in tags and "Sharp vs soft book disagreement" not in parts:
        parts.append("Sharp vs soft book disagreement detected")
    return " · ".join(parts) if parts else "Model edge identified"


def enrich_prop(p: PropLive) -> Dict[str, Any]:
    implied_over = _f(p.implied_over)
    implied_under = _f(p.implied_under)
    recommended_side = "OVER" if implied_over >= implied_under else "UNDER"
    recommended_odds = _f(p.odds_over) if recommended_side == "OVER" else _f(p.odds_under)

    ev = _f(p.ev_percentage)
    if ev >= 8:
        ev_tier = "Strong edge"
    elif ev >= 3:
        ev_tier = "Positive EV"
    else:
        ev_tier = "Marginal"

    tags: List[str] = []
    if p.steam_signal:
        tags.append("STEAM")
    if p.whale_signal:
        tags.append("WHALE")
    if p.sharp_conflict:
        tags.append("SHARP")
    if p.is_best_over or p.is_best_under:
        tags.append("BEST LINE")
    if p.is_sharp_book:
        tags.append("SHARP BOOK")
    if ev >= 8:
        tags.append("HIGH EV")

    conf01 = _f(p.confidence) if p.confidence is not None else 0.0
    if conf01 > 1.0:
        conf01 = conf01 / 100.0
    conf_pct = round(conf01 * 100, 1) if conf01 <= 1.0 else round(conf01, 1)

    implied_prob_raw = implied_over if recommended_side == "OVER" else implied_under
    implied_pct = round(implied_prob_raw * 100, 1) if implied_prob_raw <= 1.0 else round(implied_prob_raw, 1)

    away = (p.away_team or "").strip()
    home = (p.home_team or "").strip()
    matchup = f"{away} @ {home}" if away and home else (away or home or "Matchup")

    gst = p.game_start_time
    gst_iso = gst.astimezone(timezone.utc).isoformat() if gst else None

    action_score = round(ev * (conf01 if conf01 else 0.5), 2)

    reasoning = build_reasoning(p, recommended_side, ev, tags)

    return {
        "id": p.id,
        "player_name": p.player_name or "",
        "team": p.team or "",
        "matchup": matchup,
        "market_label": p.market_label or p.market_key or "",
        "market_key": p.market_key,
        "line": _f(p.line),
        "recommended_side": recommended_side,
        "recommended_odds": recommended_odds,
        "best_book": p.book,
        "ev_percentage": round(ev, 2),
        "ev_tier": ev_tier,
        "confidence": conf_pct,
        "implied_prob": implied_pct,
        "tags": tags,
        "reasoning": reasoning,
        "steam_signal": bool(p.steam_signal),
        "whale_signal": bool(p.whale_signal),
        "sharp_conflict": bool(p.sharp_conflict),
        "is_best_line": bool(p.is_best_over or p.is_best_under),
        "game_start_time": gst_iso,
        "sport": p.sport,
        "action_score": action_score,
        "game_id": p.game_id,
    }


@router.get("/pick-intel")
async def get_pick_intel(
    sport: str = Query("basketball_nba"),
    min_ev: float = Query(2.0, ge=-100.0, le=100.0),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),
    market: Optional[str] = Query(None, description="ALL | POINTS | ASSISTS | REBOUNDS | THREES"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
) -> List[Dict[str, Any]]:
    """
    Brain-ranked player props from props_live (ev_percentage, confidence, signals).
    Returns a JSON array for simple client consumption.
    """
    score_expr = func.coalesce(PropLive.ev_percentage, 0.0) * func.coalesce(PropLive.confidence, 0.5)
    conf_filter = func.coalesce(PropLive.confidence, 0.5) >= min_confidence

    wheres = [
        PropLive.sport == sport,
        func.coalesce(PropLive.ev_percentage, 0.0) >= min_ev,
        conf_filter,
        PropLive.player_name.isnot(None),
        PropLive.player_name != "",
        PropLive.market_key.notin_(TEAM_MARKETS),
        props_live_game_time_window(PropLive.game_start_time),
    ]
    mclause = _market_clause(market or "ALL")
    if mclause is not None:
        wheres.append(mclause)

    stmt = (
        select(PropLive)
        .where(*wheres)
        .order_by(desc(score_expr), desc(func.coalesce(PropLive.ev_percentage, 0.0)))
        .limit(limit)
    )

    try:
        result = await db.execute(stmt)
        rows = result.scalars().all()
        return [enrich_prop(p) for p in rows]
    except Exception as e:
        logger.exception("pick-intel query failed: %s", e)
        return []
