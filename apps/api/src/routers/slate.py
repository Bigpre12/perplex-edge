# apps/api/src/routers/slate.py
from fastapi import APIRouter, Query, Depends
from typing import Optional, List, Dict
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from db.session import get_db
from models.prop import PropLine
import logging
from real_data_connector import real_data_connector

logger = logging.getLogger(__name__)
router = APIRouter(tags=["slate"])

@router.get("/today")
async def get_todays_slate(
    sport: Optional[str] = Query(None),
    session: Session = Depends(get_db)
):
    """
    Returns today's games grouped by sport, including game identifiers.
    Now using real_data_connector for live, up-to-date schedule.
    """
    try:
        # Map sport key if numeric sport_id passed (backward compat)
        sport_id_map = {"30": "basketball_nba", "31": "americanfootball_nfl", "32": "baseball_mlb", "33": "icehockey_nhl"}
        if sport and sport.isdigit():
            sport = sport_id_map.get(sport, "basketball_nba")

        # Define sports to fetch if 'all' or None
        sports_to_fetch = [sport] if sport and sport != "all" else ["basketball_nba", "americanfootball_nfl", "baseball_mlb", "icehockey_nhl"]
        
        all_games = []
        for s_key in sports_to_fetch:
            try:
                # Use special NBA fetch for better coverage, others use generic fetch
                if s_key == "basketball_nba":
                    games = await real_data_connector.get_nba_games()
                else:
                    games = await real_data_connector.fetch_games_by_sport(s_key)
                
                for g in games:
                    all_games.append({
                        "game_id": g.get("id") or g.get("game_id"),
                        "event_id": g.get("id") or g.get("game_id"),
                        "sport": s_key,
                        "home_team": g.get("home_team") or g.get("home_team_name") or "Home",
                        "away_team": g.get("away_team") or g.get("away_team_name") or "Away",
                        "commence_time": g.get("start_time").isoformat() if hasattr(g.get("start_time"), "isoformat") else g.get("start_time"),
                        "status": g.get("status", "Scheduled")
                    })
            except Exception as e:
                logger.error(f"Error fetching games for {s_key}: {e}")

        if sport and sport != "all":
            # Return flat list for specific sport
            return [g for g in all_games if g["sport"] == sport]

        # Group games by sport
        sports_map: Dict[str, List[dict]] = {}
        for game in all_games:
            s_key = game["sport"]
            if s_key not in sports_map:
                sports_map[s_key] = []
            sports_map[s_key].append(game)

        output = []
        for s_key, s_games in sports_map.items():
            output.append({
                "sport": s_key,
                "game_count": len(s_games),
                "games": sorted(s_games, key=lambda x: str(x["commence_time"] or ""))
            })

        return {"sports": sorted(output, key=lambda x: x["sport"])}

    except Exception as e:
        logger.error(f"Error in slate generation: {e}", exc_info=True)
        return {"sports": [], "error": str(e)}
