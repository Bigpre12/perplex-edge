"""
Ultra-Simple Parlay Builder API - Works with basic picks only
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import ModelPick, Player, Team, Market
from app.services.cache_service import cache_service

router = APIRouter(prefix="/api/ultra-simple-parlays", tags=["ultra-simple-parlays"])


@router.get("/")
async def get_ultra_simple_parlays(
    sport_id: int = Query(None, description="Filter by sport ID"),
    min_ev: float = Query(default=0.01, description="Minimum expected value"),
    min_confidence: float = Query(default=0.5, description="Minimum confidence score"),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get ultra-simple parlays from available picks."""
    try:
        # Try cache first
        cache_key = f"ultra_parlays:sport_{sport_id}:ev_{min_ev}:conf_{min_confidence}:limit_{limit}"
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        # Build simple query without datetime filtering
        query = select(ModelPick).options(
            selectinload(ModelPick.player).selectinload(Player.team),
            selectinload(ModelPick.market)
        )
        
        # Basic conditions only
        conditions = [
            ModelPick.line_value.isnot(None),
            ModelPick.line_value > 0,
            ModelPick.expected_value >= min_ev,
            ModelPick.confidence_score >= min_confidence
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
                    # Calculate combined odds
                    combined_odds = formatted_picks[i]["odds"] * formatted_picks[i + 1]["odds"]
                    if combined_odds <= 0:
                        combined_odds = 1  # Default to 1 if calculation fails
                    
                    parlay = {
                        "id": f"ultra_parlay_{i}",
                        "legs": [formatted_picks[i], formatted_picks[i + 1]],
                        "total_odds": combined_odds,
                        "total_expected_value": formatted_picks[i]["expected_value"] + formatted_picks[i + 1]["expected_value"],
                        "confidence": (formatted_picks[i]["confidence_score"] + formatted_picks[i + 1]["confidence_score"]) / 2,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "platform": "prizepicks",
                        "leg_count": 2
                    }
                    parlays.append(parlay)
        
        # Calculate metrics
        if parlays:
            avg_ev = sum(parlay["total_expected_value"] for parlay in parlays) / len(parlays)
            suggested_total = sum(parlay["total_odds"] for parlay in parlays) / len(parlays)
        else:
            avg_ev = 0.0
            suggested_total = 0.0
        
        response_data = {
            "slips": parlays,
            "total_slips": len(parlays),
            "avg_ev": round(avg_ev, 4),
            "suggested_total": round(suggested_total, 2),
            "platform": "prizepicks",
            "filters": {
                "sport_id": sport_id,
                "min_ev": min_ev,
                "min_confidence": min_confidence,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dataExists": len(formatted_picks) > 0,
            "message": f"Generated {len(parlays)} parlays with avg EV of {avg_ev:.2%}",
            "parlay_count": len(parlays),
            "total_candidates": len(formatted_picks)
        }
        
        # Cache the result
        await cache_service.set(cache_key, response_data, ttl=60)
        
        return response_data
        
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
