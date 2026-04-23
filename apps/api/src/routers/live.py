import logging
from fastapi import APIRouter, Query, Depends
from typing import List, Dict, Any, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from real_data_connector import real_data_connector
from db.session import get_db
from services.live_scores_cache import read_cache_or_stale, upsert_live_scores_from_games

logger = logging.getLogger(__name__)

router = APIRouter(tags=["live"])


def _format_from_live_scores_row(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": r.get("event_id"),
        "home_team": r.get("home_team") or "Home",
        "away_team": r.get("away_team") or "Away",
        "home_score": r.get("home_score", 0),
        "away_score": r.get("away_score", 0),
        "status": r.get("status", "Scheduled"),
        "period": r.get("period", ""),
        "clock": r.get("clock", ""),
        "commence_time": None,
        "sport_key": r.get("sport"),
        "source": "live_scores_cache",
    }


async def _resolve_games_with_cache(
    db: AsyncSession, sport: str
) -> Tuple[List[Dict[str, Any]], str]:
    """Prefer ``live_scores`` when fresher than 60s; else waterfall + upsert."""
    rows, fresh = await read_cache_or_stale(db, sport, max_age_sec=60.0)
    if fresh and rows:
        return [_format_from_live_scores_row(dict(r)) for r in rows], "live_scores_cache"

    all_games: List[Dict[str, Any]] = []
    try:
        all_games = await real_data_connector.fetch_games_by_sport(sport)
    except Exception as e:
        logger.error(f"Waterfall error for {sport}: {e}")

    if all_games:
        await upsert_live_scores_from_games(db, sport, all_games)
    elif rows:
        return [_format_from_live_scores_row(dict(r)) for r in rows], "live_scores_stale"

    return all_games, "waterfall"


@router.get("/games")
async def live_games(sport: str = "basketball_nba", db: AsyncSession = Depends(get_db)):
    """
    Unified Live Games endpoint.
    Cascades through real_data_connector (Waterfall) and falls back to seeded database games.
    """
    from services.props_service import get_all_props
    import random
    from datetime import datetime, timezone

    # 1. Cache-first (live_scores), then waterfall
    all_games, _src = await _resolve_games_with_cache(db, sport)

    # 2. Database Fallback (if waterfall yields nothing)
    if not all_games:
        try:
            from db.session import AsyncSessionLocal
            from sqlalchemy import select
            from models.prop import GameV2
            
            async with AsyncSessionLocal() as db:
                # Get unique games from latest recorded data
                stmt = select(GameV2).where(GameV2.sport == sport).order_by(GameV2.commence_time.desc()).limit(10)
                result = await db.execute(stmt)
                db_games = result.scalars().all()
                
                for g in db_games:
                    all_games.append({
                        "id": str(g.id),
                        "home_team": g.home_team,
                        "away_team": g.away_team,
                        "home_score": g.home_score or 0,
                        "away_score": g.away_score or 0,
                        "status": g.status or "scheduled",
                        "period": "",
                        "clock": "",
                        "commence_time": g.commence_time.isoformat() if g.commence_time else None,
                        "source": "db_fallback"
                    })
        except Exception as db_e:
            logger.error(f"Seeded game fallback error: {db_e}")

    # 3. Final State Check
    if not all_games:
        return {
            "count": 0, 
            "games": [], 
            "status": "awaiting_ingest",
            "message": "No live data yet. Ingest job is running in the background."
        }

    # 4. Standardize for frontend
    formatted_games = []
    for g in all_games:
        formatted_games.append({
            "id": g.get("id"),
            "home_team": g.get("home_team") or g.get("home_team_name") or "Home",
            "away_team": g.get("away_team") or g.get("away_team_name") or "Away",
            "home_score": g.get("home_score", 0),
            "away_score": g.get("away_score", 0),
            "status": g.get("status", "Scheduled"),
            "period": g.get("period", 0),
            "clock": g.get("clock", ""),
            "commence_time": g.get("commence_time") or g.get("start_time"),
            "sport_key": sport,
            "source": g.get("source", "waterfall")
        })

    return {"count": len(formatted_games), "games": formatted_games}

@router.get("/scores")
async def get_live_scores(sport: str = "basketball_nba", db: AsyncSession = Depends(get_db)):
    """Fetch live scores via DB cache when fresh; else waterfall + upsert."""
    try:
        games, src = await _resolve_games_with_cache(db, sport)
        formatted_games = []
        for g in games:
            if src in ("live_scores_cache", "live_scores_stale"):
                formatted_games.append({
                    "game_id": g.get("id"),
                    "home_team": g.get("home_team"),
                    "away_team": g.get("away_team"),
                    "home_score": str(g.get("home_score", "0")),
                    "away_score": str(g.get("away_score", "0")),
                    "status": g.get("status", "Scheduled"),
                    "period": g.get("period", 0),
                    "clock": g.get("clock", ""),
                    "is_live": str(g.get("status", "")).lower() in ("in_progress", "live"),
                    "sport": sport,
                    "source": g.get("source", src),
                })
            else:
                formatted_games.append({
                    "game_id": g.get("id") or g.get("external_game_id"),
                    "home_team": g.get("home_team_name") or g.get("home_team"),
                    "away_team": g.get("away_team_name") or g.get("away_team"),
                    "home_score": g.get("home_score", "0"),
                    "away_score": g.get("away_score", "0"),
                    "status": g.get("status", "Scheduled"),
                    "period": g.get("period", 0),
                    "clock": g.get("clock", ""),
                    "is_live": g.get("status") == "in_progress",
                    "sport": sport,
                    "source": src,
                })
        return {"data": formatted_games, "count": len(formatted_games), "source": src}
    except Exception as e:
        logger.error(f"Error fetching scores for {sport}: {e}")
        return {
            "data": [], 
            "count": 0, 
            "status": "awaiting_ingest",
            "error_msg": str(e)
        }

@router.get("/stream")
async def get_live_stream(sport: str = "basketball_nba"):
    """
    Returns real-time streaming status for live games.
    """
    try:
        games = await real_data_connector.fetch_games_by_sport(sport)
        streams = []
        for g in games:
            if g.get("status") == "in_progress":
                streams.append({
                    "game_id": g.get("id"),
                    "home_team": g.get("home_team"),
                    "away_team": g.get("away_team"),
                    "has_stream": True,
                    "stream_url": f"https://perplex-edge-stream-proxy.up.railway.app/live/{g.get('id')}",
                    "bitrate": "4500kbps",
                    "latency": "2.1s"
                })
        return {
            "status": "ok",
            "count": len(streams),
            "data": streams
        }
    except Exception as e:
        logger.error(f"Stream discovery failed: {e}")
        return {"status": "error", "message": str(e), "data": []}
