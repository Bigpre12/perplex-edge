from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, desc
from db.session import get_db
from datetime import datetime, timezone
from services.heartbeat_service import HeartbeatService
import logging
from typing import Optional

from models.brain import SharpSignal, WhaleMove

logger = logging.getLogger(__name__)

router = APIRouter()


def _max_dt(*values: Optional[datetime]) -> Optional[datetime]:
    """Return the latest non-null datetime, or None if all are null."""
    valid = [v for v in values if v is not None]
    return max(valid) if valid else None


@router.get("")
@router.get("/")
async def list_signals(
    sport: str = Query("basketball_nba"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Canonical /api/signals list endpoint for frontend Signals tab.
    Reads whale_moves and returns an empty list when no rows exist.
    """
    try:
        res = await db.execute(
            select(WhaleMove)
            .where(WhaleMove.sport == sport)
            .order_by(desc(WhaleMove.created_at))
            .limit(limit)
        )
        rows = res.scalars().all()
        items = [
            {
                "id": r.id,
                "player_name": r.player_name or r.selection or "Unknown",
                "stat_type": r.stat_type or r.market_key or "unknown",
                "line": r.line,
                "trust_level": r.whale_rating,
                "signal_type": r.move_type or r.move_size or r.severity or "SHARP_MONEY",
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
        return items
    except Exception as e:
        logger.warning("signals list query failed: %s", e)
        return []

@router.get("/sharp-moves")
async def sharp_moves(
    sport: str = Query("basketball_nba"),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
):
    try:
        res = await db.execute(
            select(SharpSignal)
            .where(SharpSignal.sport == sport)
            .order_by(desc(SharpSignal.created_at))
            .limit(limit)
        )
        rows = res.scalars().all()
    except Exception as e:
        logger.warning("sharp-moves query failed: %s", e)
        return {"sport": sport, "items": [], "count": 0, "error": str(e)}

    items = []
    for r in rows:
        items.append(
            {
                "id": r.id,
                "event_id": r.event_id,
                "sport": r.sport,
                "market_key": r.market_key,
                "selection": r.selection,
                "signal_type": r.signal_type,
                "severity": r.severity,
                "bookmakers_involved": r.bookmakers_involved,
                "detected_at": r.created_at.isoformat() if r.created_at else None,
            }
        )
    return {"sport": sport, "items": items, "count": len(items)}

@router.get("/freshness")
async def freshness(
    db: AsyncSession = Depends(get_db),
    sport: str = Query("basketball_nba"),
):
    """
    Board freshness for the UI.

    Semantics:
    - last_odds_update: max(ingest_{sport} heartbeat last_success_at, system_sync_state.last_odds_sync,
      MAX(props_live.last_updated_at) for this sport) so the bar reflects real row activity, not only ingest ok.
    - last_ev_update: max(ev_grader heartbeat last_success_at, last_run_at, MAX(ev_signals.created_at));
      intelligence_{sport} is a fallback feed name.

    Ops (very old ingest heartbeat / odds line): confirm Celery or deploy scheduler runs unified_ingestion for
    this sport_key; inspect Heartbeat row ingest_{sport} (status, meta); run a manual ingest and verify
    last_success_at advances; if props are updating but heartbeat is stuck, this endpoint still surfaces
    props_live / system_sync_state timestamps.
    """
    try:
        ingest_hb = await HeartbeatService.get_heartbeat(db, f"ingest_{sport}")
        hb_odds = ingest_hb.last_success_at if ingest_hb else None

        sync_odds: Optional[datetime] = None
        try:
            ss_res = await db.execute(
                text("SELECT last_odds_sync FROM system_sync_state WHERE id = 1")
            )
            ss_row = ss_res.mappings().first()
            if ss_row and ss_row.get("last_odds_sync"):
                sync_odds = ss_row["last_odds_sync"]
        except Exception:
            pass

        props_max: Optional[datetime] = None
        try:
            pr = await db.execute(
                text(
                    "SELECT MAX(last_updated_at) AS m FROM props_live WHERE sport = :sport"
                ),
                {"sport": sport},
            )
            row = pr.mappings().first()
            if row and row.get("m"):
                props_max = row["m"]
        except Exception:
            pass

        last_odds = _max_dt(hb_odds, sync_odds, props_max)

        ev_hb = await HeartbeatService.get_heartbeat(db, f"ev_grader_{sport}")
        if not ev_hb:
            ev_hb = await HeartbeatService.get_heartbeat(db, f"intelligence_{sport}")

        hb_ev_success = ev_hb.last_success_at if ev_hb else None
        hb_ev_run = ev_hb.last_run_at if ev_hb else None

        ev_signals_max: Optional[datetime] = None
        try:
            er = await db.execute(
                text(
                    "SELECT MAX(created_at) AS m FROM ev_signals WHERE sport = :sport OR sport_key = :sport"
                ),
                {"sport": sport},
            )
            erow = er.mappings().first()
            if erow and erow.get("m"):
                ev_signals_max = erow["m"]
        except Exception:
            pass

        last_ev = _max_dt(hb_ev_success, hb_ev_run, ev_signals_max)

        now = datetime.now(timezone.utc)
        deg_reasons = []
        deg_level = "none"
        if not last_odds:
            deg_reasons.append("no_odds_timestamp")
            deg_level = "partial"
        else:
            lo = last_odds if last_odds.tzinfo else last_odds.replace(tzinfo=timezone.utc)
            age_s = (now - lo).total_seconds()
            if age_s > 3 * 3600:
                deg_reasons.append("odds_stale_over_3h")
                deg_level = "severe"
            elif age_s > 3600:
                deg_reasons.append("odds_delayed_over_1h")
                deg_level = "partial" if deg_level != "severe" else deg_level

        if last_ev:
            ev_dt = last_ev if last_ev.tzinfo else last_ev.replace(tzinfo=timezone.utc)
            if (now - ev_dt).total_seconds() > 4 * 3600 and last_odds:
                deg_reasons.append("ev_stale_over_4h")
                if deg_level == "none":
                    deg_level = "partial"

        if deg_level == "severe":
            user_msg = "Odds snapshot is stale — verify lines before acting."
        elif deg_level == "partial":
            user_msg = "Board freshness is delayed or incomplete."
        else:
            user_msg = ""

        return {
            "sport": sport,
            "status": "fresh" if last_odds else "stale",
            "last_odds_update": last_odds.isoformat() if last_odds else None,
            "last_ev_update": last_ev.isoformat() if last_ev else None,
            "server_time": now.isoformat(),
            "meta": {
                "degradation": {
                    "level": deg_level,
                    "reasons": deg_reasons,
                    "user_message": user_msg,
                },
                "freshness": {
                    "odds": last_odds.isoformat() if last_odds else None,
                    "ev": last_ev.isoformat() if last_ev else None,
                },
            },
        }
    except Exception as e:
        logger.error(f"Freshness check failed: {e}")
        now = datetime.now(timezone.utc)
        return {
            "sport": sport,
            "status": "error",
            "message": str(e),
            "last_odds_update": None,
            "last_ev_update": None,
            "server_time": now.isoformat(),
            "meta": {
                "degradation": {
                    "level": "severe",
                    "reasons": ["freshness_query_failed"],
                    "user_message": "Freshness check failed — treat board as unknown.",
                },
                "freshness": {"odds": None, "ev": None},
            },
        }

# Alias for intel.py import
get_signals = sharp_moves
