"""
Ultra-Simple Parlay Builder API - Works with basic picks only
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import ModelPick, Player, Team, Market

router = APIRouter(prefix="/api/ultra-simple-parlays", tags=["ultra-simple-parlays"])


@router.get("/")
async def get_ultra_simple_parlays(
    sport_id: int = Query(None, description="Filter by sport ID"),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get ultra-simple parlays from basic picks."""
    try:
        # Simple query without datetime filtering
        query = select(ModelPick).options(
            selectinload(ModelPick.player).selectinload(Player.team),
            selectinload(ModelPick.market)
        )
        
        # Basic conditions only
        conditions = [
            ModelPick.line_value.isnot(None),
            ModelPick.line_value > 0,
            ModelPick.expected_value > 0
        ]
        
        if sport_id:
            conditions.append(ModelPick.sport_id == sport_id)
        
        query = query.where(and_(*conditions)).order_by(
            desc(ModelPick.expected_value)
        ).limit(limit * 2)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        # Format picks
        formatted_picks = []
        for pick in picks:
            pick_data = {
                "id": pick.id,
                "player_id": pick.player_id,
                "player_name": pick.player.name if pick.player else "Unknown",
                "team_name": pick.player.team.name if pick.player and pick.player.team else "Unknown",
                "team_abbreviation": pick.player.team.abbreviation if pick.player and pick.player.team else None,
                "sport_id": pick.sport_id,
                "stat_type": pick.market.stat_type if pick.market else "unknown",
                "line_value": pick.line_value,
                "side": pick.side,
                "odds": pick.odds,
                "expected_value": pick.expected_value,
                "confidence_score": pick.confidence_score,
                "generated_at": pick.generated_at.isoformat() if pick.generated_at else None
            }
            formatted_picks.append(pick_data)
        
        # Build simple 2-leg parlays
        parlays = []
        if len(formatted_picks) >= 2:
            for i in range(0, min(len(formatted_picks) - 1, limit)):
                # Avoid same player in same parlay
                if formatted_picks[i]["player_id"] != formatted_picks[i + 1]["player_id"]:
                    parlay = {
                        "id": f"ultra_parlay_{i}",
                        "legs": [formatted_picks[i], formatted_picks[i + 1]],
                        "total_odds": formatted_picks[i]["odds"] * formatted_picks[i + 1]["odds"],
                        "total_expected_value": formatted_picks[i]["expected_value"] + formatted_picks[i + 1]["expected_value"],
                        "confidence": (formatted_picks[i]["confidence_score"] + formatted_picks[i + 1]["confidence_score"]) / 2,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    parlays.append(parlay)
        
        return {
            "parlays": parlays,
            "total_candidates": len(formatted_picks),
            "parlay_count": len(parlays),
            "filters": {
                "sport_id": sport_id,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dataExists": len(formatted_picks) > 0,
            "message": "Ultra-simple parlays from available picks"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-picks")
async def get_available_picks(
    sport_id: int = Query(None, description="Filter by sport ID"),
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get available picks for parlay construction."""
    try:
        query = select(ModelPick).options(
            selectinload(ModelPick.player).selectinload(Player.team),
            selectinload(ModelPick.market)
        )
        
        conditions = [
            ModelPick.line_value.isnot(None),
            ModelPick.line_value > 0,
            ModelPick.expected_value > 0
        ]
        
        if sport_id:
            conditions.append(ModelPick.sport_id == sport_id)
        
        query = query.where(and_(*conditions)).order_by(
            desc(ModelPick.expected_value)
        ).limit(limit)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        # Format picks
        formatted_picks = []
        for pick in picks:
            pick_data = {
                "id": pick.id,
                "player_id": pick.player_id,
                "player_name": pick.player.name if pick.player else "Unknown",
                "team_name": pick.player.team.name if pick.player and pick.player.team else "Unknown",
                "team_abbreviation": pick.player.team.abbreviation if pick.player and pick.player.team else None,
                "sport_id": pick.sport_id,
                "stat_type": pick.market.stat_type if pick.market else "unknown",
                "line_value": pick.line_value,
                "side": pick.side,
                "odds": pick.odds,
                "expected_value": pick.expected_value,
                "confidence_score": pick.confidence_score,
                "generated_at": pick.generated_at.isoformat() if pick.generated_at else None
            }
            formatted_picks.append(pick_data)
        
        return {
            "picks": formatted_picks,
            "total_picks": len(formatted_picks),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dataExists": len(formatted_picks) > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
