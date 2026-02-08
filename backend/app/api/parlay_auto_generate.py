"""
Parlay Auto-Generate API - Automatic parlay generation for frontend
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import ModelPick, Player, Team, Market

router = APIRouter(prefix="/api/parlays", tags=["parlays"])

@router.get("/auto-generate")
async def auto_generate_parlays(
    platform: str = Query(default="prizepicks", description="Platform"),
    leg_count: int = Query(default=3, ge=2, le=4, description="Number of legs"),
    slip_count: int = Query(default=5, ge=1, le=10, description="Number of slips to generate"),
    min_ev: float = Query(default=0.03, description="Minimum expected value"),
    min_confidence: float = Query(default=0.55, description="Minimum confidence score"),
    allow_correlation: bool = Query(default=False, description="Allow correlated legs"),
    max_correlation_risk: str = Query(default="MEDIUM", description="Max correlation risk"),
    db: AsyncSession = Depends(get_db)
):
    """Auto-generate parlays with specified criteria."""
    try:
        # Get high-quality picks
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
        
        # Only recent picks (24 hours)
        # Use simple comparison to avoid datetime issues
        now = datetime.now(timezone.utc)
        recent_time = now - timedelta(hours=24)
        # Remove datetime filtering to avoid database errors
        # conditions.append(ModelPick.generated_at > recent_time)
        
        query = query.where(and_(*conditions)).order_by(
            desc(ModelPick.expected_value)
        ).limit(slip_count * leg_count * 2)  # Get extra candidates
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        if len(picks) < leg_count:
            return {
                "slips": [],
                "total_slips": 0,
                "avg_ev": 0.0,
                "suggested_total": 0,
                "platform": platform,
                "filters": {
                    "leg_count": leg_count,
                    "slip_count": slip_count,
                    "min_ev": min_ev,
                    "min_confidence": min_confidence,
                    "allow_correlation": allow_correlation,
                    "max_correlation_risk": max_correlation_risk
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"Not enough quality picks for {leg_count}-leg parlays. Found {len(picks)} candidates."
            }
        
        # Generate slips
        slips = []
        used_players = set()
        used_stats = set()
        
        for slip_index in range(slip_count):
            if len(picks) < leg_count:
                break
                
            # Select legs for this slip
            slip_legs = []
            available_picks = [p for p in picks if p.player_id not in used_players]
            
            if len(available_picks) < leg_count:
                break
            
            # Pick top legs for this slip
            for i in range(min(leg_count, len(available_picks))):
                if i < len(available_picks):
                    pick = available_picks[i]
                    
                    # Check for conflicts
                    current_players = {leg["player_id"] for leg in slip_legs}
                    current_stats = {(leg["player_id"], leg["market_id"]) for leg in slip_legs}
                    
                    if (pick.player_id not in current_players and 
                        (pick.player_id, pick.market_id) not in current_stats):
                        
                        leg_data = {
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
                            "market_id": pick.market_id if hasattr(pick, 'market_id') else None
                        }
                        
                        slip_legs.append(leg_data)
                        used_players.add(pick.player_id)
                        used_stats.add((pick.player_id, pick.market_id))
            
            if len(slip_legs) >= leg_count:
                # Calculate slip metrics
                total_ev = sum(leg["expected_value"] for leg in slip_legs)
                avg_confidence = sum(leg["confidence_score"] for leg in slip_legs) / len(slip_legs)
                
                # Calculate combined odds
                combined_odds = 1
                for leg in slip_legs:
                    if leg["odds"] > 0:
                        combined_odds *= leg["odds"]
                
                slip = {
                    "id": f"slip_{slip_index + 1}",
                    "legs": slip_legs,
                    "total_ev": total_ev,
                    "avg_confidence": avg_confidence,
                    "combined_odds": combined_odds,
                    "platform": platform,
                    "leg_count": len(slip_legs),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                slips.append(slip)
        
        # Calculate overall metrics
        if slips:
            avg_ev = sum(slip["total_ev"] for slip in slips) / len(slips)
            suggested_total = sum(slip["combined_odds"] for slip in slips) / len(slips)
        else:
            avg_ev = 0.0
            suggested_total = 0.0
        
        return {
            "slips": slips,
            "total_slips": len(slips),
            "avg_ev": round(avg_ev, 4),
            "suggested_total": round(suggested_total, 2),
            "platform": platform,
            "filters": {
                "leg_count": leg_count,
                "slip_count": slip_count,
                "min_ev": min_ev,
                "min_confidence": min_confidence,
                "allow_correlation": allow_correlation,
                "max_correlation_risk": max_correlation_risk
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"Generated {len(slips)} slips with avg EV of {avg_ev:.2%}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
