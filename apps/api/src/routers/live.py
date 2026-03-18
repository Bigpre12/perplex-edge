import httpx, logging
from fastapi import APIRouter, Query
from typing import Optional

from core.sports_config import ALL_SPORTS, SPORT_DISPLAY
from real_data_connector import real_data_connector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/live", tags=["live"])

@router.get("/games")
async def live_games(sport: str = "basketball_nba"):
    """
    Unified Live Games endpoint.
    Cascades through real_data_connector (Waterfall) and falls back to seeded database games.
    """
    from services.props_service import get_all_props
    import random
    from datetime import datetime, timezone

    # 1. Fetch live games via waterfall (cascades through ESPN, TheSportsDB, etc.)
    all_games = []
    try:
        all_games = await real_data_connector.fetch_games_by_sport(sport)
    except Exception as e:
        logger.error(f"Waterfall error for {sport}: {e}")

    # 2. Database Fallback (if waterfall yields nothing)
    if not all_games:
        try:
            from db.session import get_db
            from sqlalchemy import select
            from models.prop import GameLine
            
            async for db in get_db():
                # Get unique games from seeded data
                stmt = select(GameLine).where(GameLine.sport_key == sport).limit(10)
                result = await db.execute(stmt)
                seeded_games = result.scalars().all()
                
                for g in seeded_games:
                    all_games.append({
                        "id": g.game_id,
                        "home_team": g.home_team,
                        "away_team": g.away_team,
                        "home_score": random.randint(80, 110),
                        "away_score": random.randint(80, 110),
                        "status": "live",
                        "period": random.randint(1, 4),
                        "clock": f"{random.randint(1, 12)}:{random.randint(0, 5)}{random.randint(0, 9)}",
                        "commence_time": g.commence_time.isoformat() if g.commence_time else None,
                        "source": "db_fallback"
                    })
        except Exception as db_e:
            logger.error(f"Seeded game fallback error: {db_e}")

    # 3. Final Mock Fallback (if DB is also empty)
    if not all_games:
        all_games = [{
            "id": "sim_1",
            "home_team": "Golden State Warriors",
            "away_team": "Los Angeles Lakers",
            "home_score": 102,
            "away_score": 98,
            "status": "live",
            "period": 4,
            "clock": "2:14",
            "commence_time": datetime.now(timezone.utc).isoformat(),
            "source": "hardcoded_fallback"
        }]

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
async def get_live_scores(sport: str = "basketball_nba"):
    """Fetch live scores via waterfall connector"""
    try:
        games = await real_data_connector.fetch_games_by_sport(sport)
        # Ensure status field is compatible with frontend requirements
        formatted_games = []
        for g in games:
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
                "sport": sport
            })
        return {"data": formatted_games, "count": len(formatted_games)}
    except Exception as e:
        logger.error(f"Error fetching scores for {sport}: {e}")
        return {"data": [], "error": str(e)}
