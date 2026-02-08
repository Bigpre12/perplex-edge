"""
Debug Slates API - Diagnose "No Active Slates" issue
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import ModelPick, Player, Team, Market, Game

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/slates")
async def debug_slates(
    sport_id: int = Query(30, description="Sport ID"),
    db: AsyncSession = Depends(get_db)
):
    """Debug endpoint to diagnose slates issue."""
    try:
        debug_info = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sport_id": sport_id,
            "database_checks": {},
            "time_filters": {},
            "sample_data": {},
            "diagnosis": {}
        }
        
        # Check total picks in database
        total_picks_query = select(func.count(ModelPick.id))
        total_picks_result = await db.execute(total_picks_query)
        total_picks = total_picks_result.scalar()
        debug_info["database_checks"]["total_picks"] = total_picks
        
        # Check picks by sport
        sport_picks_query = select(func.count(ModelPick.id)).where(ModelPick.sport_id == sport_id)
        sport_picks_result = await db.execute(sport_picks_query)
        sport_picks = sport_picks_result.scalar()
        debug_info["database_checks"]["sport_picks"] = sport_picks
        
        # Check games table (if it exists)
        try:
            games_query = select(func.count(Game.id))
            games_result = await db.execute(games_query)
            total_games = games_result.scalar()
            debug_info["database_checks"]["total_games"] = total_games
            
            # Games by sport
            sport_games_query = select(func.count(Game.id)).where(Game.sport_id == sport_id)
            sport_games_result = await db.execute(sport_games_query)
            sport_games = sport_games_result.scalar()
            debug_info["database_checks"]["sport_games"] = sport_games
            
            # Games in next 24 hours
            now = datetime.now(timezone.utc)
            future_24h = now + timedelta(hours=24)
            
            upcoming_games_query = select(func.count(Game.id)).where(
                and_(
                    Game.sport_id == sport_id,
                    Game.start_time >= now,
                    Game.start_time <= future_24h
                )
            )
            upcoming_games_result = await db.execute(upcoming_games_query)
            upcoming_games = upcoming_games_result.scalar()
            debug_info["database_checks"]["upcoming_games_24h"] = upcoming_games
            
        except Exception as e:
            debug_info["database_checks"]["games_error"] = str(e)
        
        # Check picks with timestamps
        try:
            # Picks with generated_at
            picks_with_time_query = select(func.count(ModelPick.id)).where(
                ModelPick.generated_at.isnot(None)
            )
            picks_with_time_result = await db.execute(picks_with_time_query)
            picks_with_time = picks_with_time_result.scalar()
            debug_info["database_checks"]["picks_with_timestamp"] = picks_with_time
            
            # Picks in last 24 hours
            recent_picks_query = select(func.count(ModelPick.id)).where(
                ModelPick.generated_at >= (datetime.now(timezone.utc) - timedelta(hours=24))
            )
            recent_picks_result = await db.execute(recent_picks_query)
            recent_picks = recent_picks_result.scalar()
            debug_info["database_checks"]["recent_picks_24h"] = recent_picks
            
        except Exception as e:
            debug_info["database_checks"]["timestamp_error"] = str(e)
        
        # Time filter analysis
        now = datetime.now(timezone.utc)
        future_24h = now + timedelta(hours=24)
        debug_info["time_filters"]["now_utc"] = now.isoformat()
        debug_info["time_filters"]["future_24h_utc"] = future_24h.isoformat()
        debug_info["time_filters"]["time_window_hours"] = 24
        
        # Get sample data
        try:
            sample_picks_query = select(ModelPick).options(
                selectinload(ModelPick.player).selectinload(Player.team),
                selectinload(ModelPick.market)
            ).where(ModelPick.sport_id == sport_id).limit(3)
            
            sample_picks_result = await db.execute(sample_picks_query)
            sample_picks = sample_picks_result.scalars().all()
            
            debug_info["sample_data"]["sample_picks"] = [
                {
                    "id": pick.id,
                    "player": pick.player.name if pick.player else "Unknown",
                    "team": pick.player.team.name if pick.player and pick.player.team else "Unknown",
                    "market": pick.market.stat_type if pick.market else "Unknown",
                    "generated_at": pick.generated_at.isoformat() if pick.generated_at else None,
                    "expected_value": pick.expected_value,
                    "confidence_score": pick.confidence_score
                }
                for pick in sample_picks
            ]
        except Exception as e:
            debug_info["sample_data"]["error"] = str(e)
        
        # Diagnosis
        diagnosis = []
        
        if total_picks == 0:
            diagnosis.append("CRITICAL: No picks in database at all")
        elif sport_picks == 0:
            diagnosis.append("WARNING: No picks for this sport")
        else:
            diagnosis.append(f"OK: Found {sport_picks} picks for this sport")
        
        if "upcoming_games_24h" in debug_info["database_checks"]:
            if debug_info["database_checks"]["upcoming_games_24h"] == 0:
                diagnosis.append("ISSUE: No games in next 24 hours (games table)")
            else:
                diagnosis.append(f"OK: Found {debug_info['database_checks']['upcoming_games_24h']} games in next 24 hours")
        
        if debug_info["database_checks"].get("recent_picks_24h", 0) == 0:
            diagnosis.append("ISSUE: No picks generated in last 24 hours")
        else:
            diagnosis.append(f"OK: Found {debug_info['database_checks']['recent_picks_24h']} recent picks")
        
        debug_info["diagnosis"] = {
            "issues": diagnosis,
            "recommendation": "Check games table and data ingestion process"
        }
        
        return debug_info
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "diagnosis": "Failed to run debug analysis"
        }
