"""
Simple Parlay Builder API - Works with available picks without game filtering
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import ModelPick, Player, Team, Market, Sport
from app.services.cache_service import cache_service

router = APIRouter(prefix="/api/simple-parlays", tags=["simple-parlays"])


@router.get("/")
async def get_simple_parlays(
    sport_id: int = Query(None, description="Filter by sport ID"),
    min_ev: float = Query(default=0.05, description="Minimum expected value"),
    min_confidence: float = Query(default=0.6, description="Minimum confidence score"),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get parlays from available picks without game filtering."""
    try:
        # Try cache first
        cache_key = f"simple_parlays:sport_{sport_id}:ev_{min_ev}:conf_{min_confidence}:limit_{limit}"
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        # Build simple query for available picks
        query = select(ModelPick).options(
            selectinload(ModelPick.player).selectinload(Player.team).selectinload(Team.sport),
            selectinload(ModelPick.market)
        )
        
        conditions = [
            ModelPick.line_value.isnot(None),
            ModelPick.line_value > 0,
            ModelPick.expected_value >= min_ev,
            ModelPick.confidence_score >= min_confidence
        ]
        
        if sport_id:
            conditions.append(ModelPick.sport_id == sport_id)
        
        # Only recent picks (24 hours)
        conditions.append(ModelPick.generated_at > datetime.now(timezone.utc) - timedelta(hours=24))
        
        query = query.where(and_(*conditions)).order_by(
            desc(ModelPick.expected_value)
        ).limit(limit * 2)  # Get extra for diversity
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        # Format picks for frontend
        formatted_picks = []
        for pick in picks:
            pick_data = {
                "id": pick.id,
                "player_id": pick.player_id,
                "player_name": pick.player.name if pick.player else "Unknown",
                "team_name": pick.player.team.name if pick.player and pick.player.team else "Unknown",
                "team_abbreviation": pick.player.team.abbreviation if pick.player and pick.player.team else None,
                "sport_id": pick.sport_id,
                "sport_key": f"sport_{pick.sport_id}" if pick.sport_id else "unknown",
                "game_id": pick.game_id,
                "market_id": pick.market_id,
                "stat_type": pick.market.stat_type if pick.market else "unknown",
                "line_value": pick.line_value,
                "side": pick.side,
                "odds": pick.odds,
                "model_probability": pick.model_probability,
                "implied_probability": pick.implied_probability,
                "expected_value": pick.expected_value,
                "confidence_score": pick.confidence_score,
                "generated_at": pick.generated_at.isoformat() if pick.generated_at else None
            }
            formatted_picks.append(pick_data)
        
        # Build parlays from picks
        parlays = []
        if len(formatted_picks) >= 2:
            # Simple 2-leg parlays
            for i in range(0, min(len(formatted_picks) - 1, limit)):
                # Avoid same player in same parlay
                if formatted_picks[i]["player_id"] != formatted_picks[i + 1]["player_id"]:
                    parlay = {
                        "id": f"simple_parlay_{i}",
                        "legs": [formatted_picks[i], formatted_picks[i + 1]],
                        "total_odds": formatted_picks[i]["odds"] * formatted_picks[i + 1]["odds"],
                        "total_probability": formatted_picks[i]["model_probability"] * formatted_picks[i + 1]["model_probability"],
                        "total_expected_value": formatted_picks[i]["expected_value"] + formatted_picks[i + 1]["expected_value"],
                        "confidence": (formatted_picks[i]["confidence_score"] + formatted_picks[i + 1]["confidence_score"]) / 2,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    parlays.append(parlay)
        
        response_data = {
            "parlays": parlays,
            "total_candidates": len(formatted_picks),
            "parlay_count": len(parlays),
            "filters": {
                "sport_id": sport_id,
                "min_ev": min_ev,
                "min_confidence": min_confidence,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dataExists": len(formatted_picks) > 0,
            "message": "Simple parlays from available picks"
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
        
        # Only recent picks (24 hours)
        conditions.append(ModelPick.generated_at > datetime.now(timezone.utc) - timedelta(hours=24))
        
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


@router.get("/build")
async def build_simple_parlays(
    sport_id: int = Query(None, description="Filter by sport ID"),
    leg_count: int = Query(default=2, ge=2, le=4, description="Number of legs in parlay"),
    min_ev: float = Query(default=0.05, description="Minimum expected value"),
    min_confidence: float = Query(default=0.6, description="Minimum confidence score"),
    limit: int = Query(default=10, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Build simple parlays from available picks."""
    try:
        # Get available picks
        query = select(ModelPick).options(
            selectinload(ModelPick.player).selectinload(Player.team),
            selectinload(ModelPick.market)
        )
        
        conditions = [
            ModelPick.line_value.isnot(None),
            ModelPick.line_value > 0,
            ModelPick.expected_value >= min_ev,
            ModelPick.confidence_score >= min_confidence
        ]
        
        if sport_id:
            conditions.append(ModelPick.sport_id == sport_id)
        
        # Only recent picks (24 hours)
        conditions.append(ModelPick.generated_at > datetime.now(timezone.utc) - timedelta(hours=24))
        
        query = query.where(and_(*conditions)).order_by(
            desc(ModelPick.expected_value)
        ).limit(limit * 3)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        if len(picks) < leg_count:
            return {
                "parlays": [],
                "total_candidates": len(picks),
                "parlay_count": 0,
                "message": f"Not enough quality picks for {leg_count}-leg parlays. Found {len(picks)} candidates.",
                "filters": {
                    "sport_id": sport_id,
                    "leg_count": leg_count,
                    "min_ev": min_ev,
                    "min_confidence": min_confidence,
                    "limit": limit
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "dataExists": False
            }
        
        # Build parlays
        parlays = []
        used_players = set()
        
        for i in range(len(picks) - leg_count + 1):
            current_legs = picks[i:i + leg_count]
            
            # Check for conflicts (same player)
            current_players = {leg.player_id for leg in current_legs}
            
            if len(current_players) == leg_count and not used_players.intersection(current_players):
                parlay = {
                    "id": f"simple_parlay_{len(parlays)}",
                    "legs": [
                        {
                            "id": leg.id,
                            "player_id": leg.player_id,
                            "player_name": leg.player.name if leg.player else "Unknown",
                            "team_name": leg.player.team.name if leg.player and leg.player.team else "Unknown",
                            "stat_type": leg.market.stat_type if leg.market else "unknown",
                            "line_value": leg.line_value,
                            "side": leg.side,
                            "odds": leg.odds,
                            "model_probability": leg.model_probability,
                            "expected_value": leg.expected_value,
                            "confidence_score": leg.confidence_score
                        }
                        for leg in current_legs
                    ],
                    "total_expected_value": sum(leg.expected_value for leg in current_legs),
                    "confidence": sum(leg.confidence_score for leg in current_legs) / leg_count,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                parlays.append(parlay)
                used_players.update(current_players)
                
                if len(parlays) >= limit:
                    break
        
        response_data = {
            "parlays": parlays,
            "total_candidates": len(picks),
            "parlay_count": len(parlays),
            "filters": {
                "sport_id": sport_id,
                "leg_count": leg_count,
                "min_ev": min_ev,
                "min_confidence": min_confidence,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dataExists": len(parlays) > 0
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
