"""Persist and cache Monte Carlo parlay simulation results (Postgres)."""
from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import DATABASE_URL

logger = logging.getLogger(__name__)


def _is_sqlite() -> bool:
    return "sqlite" in (DATABASE_URL or "").lower()


def parlay_cache_keys(sport: str, legs: List[Dict[str, Any]]) -> tuple[str, str]:
    """(event_id, outcome_fingerprint) for cache lookup."""
    norm = json.dumps(legs, sort_keys=True, default=str)
    fp = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:64]
    first_eid = None
    for leg in legs:
        gid = leg.get("game_id") or leg.get("event_id")
        if gid:
            first_eid = str(gid)
            break
    event_id = first_eid or f"parlay:{fp[:16]}"
    return event_id, fp


async def fetch_cached_parlay(
    session: AsyncSession, sport: str, event_id: str, outcome_fp: str
) -> Optional[Dict[str, Any]]:
    if _is_sqlite():
        return None
    try:
        q = text(
            """
            SELECT id, event_id, sport, market, outcome, odds, true_prob, win_rate,
                   avg_roi, roi_std_dev, roi_p5, roi_p95, confidence_score, num_simulations, simulated_at
            FROM monte_carlo_results
            WHERE sport = :sport AND event_id = :eid AND outcome = :outcome
              AND simulated_at > NOW() - INTERVAL '30 minutes'
            ORDER BY simulated_at DESC
            LIMIT 1
            """
        )
        res = await session.execute(q, {"sport": sport, "eid": event_id, "outcome": outcome_fp})
        row = res.mappings().first()
        return dict(row) if row else None
    except Exception as e:
        logger.debug("monte_carlo cache read skipped: %s", e)
        return None


def cached_row_to_api_response(row: Dict[str, Any], leg_results: Optional[List] = None) -> Dict[str, Any]:
    wr = float(row.get("win_rate") or 0)
    ev = float(row.get("avg_roi") or 0)
    roi_pct = ev * 100.0
    edge = ev
    conf = float(row.get("confidence_score") or 0)
    return {
        "roi": roi_pct,
        "edge": edge,
        "win_rate": wr,
        "expected_value": edge,
        "true_probability": float(row.get("true_prob") or wr),
        "confidence": "high" if conf > 5.0 or edge > 0.05 else "medium",
        "max_drawdown": 0.15,
        "leg_results": leg_results or [],
        "cached": True,
        "monte_carlo_result_id": row.get("id"),
    }


async def save_parlay_result(
    session: AsyncSession,
    sport: str,
    event_id: str,
    outcome_fp: str,
    legs: List[Dict[str, Any]],
    n_sims: int,
    results: Dict[str, Any],
) -> None:
    if _is_sqlite():
        return
    combined = 1.0
    for leg in legs:
        o = leg.get("odds", -110)
        try:
            oi = int(o)
        except (TypeError, ValueError):
            oi = -110
        if oi > 0:
            combined *= 1 + (oi / 100.0)
        else:
            combined *= 1 + (100.0 / abs(oi))
    rep_odds = legs[0].get("odds", -110) if legs else -110
    try:
        rep_odds_i = int(rep_odds)
    except (TypeError, ValueError):
        rep_odds_i = -110

    phr = float(results.get("parlay_hit_rate") or 0)
    pev = float(results.get("parlay_ev") or 0)
    stmt = text(
        """
        INSERT INTO monte_carlo_results (
          event_id, sport, market, outcome, odds, true_prob, win_rate,
          avg_roi, roi_std_dev, roi_p5, roi_p95, confidence_score, num_simulations
        ) VALUES (
          :event_id, :sport, :market, :outcome, :odds, :true_prob, :win_rate,
          :avg_roi, :roi_std_dev, :roi_p5, :roi_p95, :confidence_score, :num_simulations
        )
        """
    )
    await session.execute(
        stmt,
        {
            "event_id": event_id,
            "sport": sport,
            "market": "parlay",
            "outcome": outcome_fp,
            "odds": rep_odds_i,
            "true_prob": phr,
            "win_rate": phr,
            "avg_roi": pev,
            "roi_std_dev": abs(pev) * 0.15,
            "roi_p5": pev * 0.5,
            "roi_p95": pev * 1.5,
            "confidence_score": phr * 100.0,
            "num_simulations": n_sims,
        },
    )
    await session.commit()


async def list_latest_by_sport(session: AsyncSession, sport: str, limit: int = 50) -> List[Dict[str, Any]]:
    if _is_sqlite():
        return []
    try:
        q = text(
            """
            SELECT id, event_id, sport, market, outcome, odds, true_prob, win_rate,
                   avg_roi, roi_std_dev, roi_p5, roi_p95, confidence_score, num_simulations, simulated_at
            FROM monte_carlo_results
            WHERE sport = :sport
            ORDER BY confidence_score DESC NULLS LAST, simulated_at DESC
            LIMIT :lim
            """
        )
        res = await session.execute(q, {"sport": sport, "lim": limit})
        return [dict(r._mapping) for r in res.fetchall()]
    except Exception as e:
        logger.debug("monte_carlo list: %s", e)
        return []
