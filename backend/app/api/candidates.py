"""
Candidates API - Frontend-compatible candidate endpoint
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import ModelPick, Player, Team, Market

router = APIRouter(prefix="/api", tags=["candidates"])

@router.get("/candidates/{sport_id}")
async def get_candidates(
    sport_id: int,
    edge_grade: str = Query(default="B", description="Edge grade filter"),
    power: str = Query(default="flex", description="Power filter"),
    correlated: str = Query(default="medium", description="Correlation filter"),
    db: AsyncSession = Depends(get_db)
):
    """Get candidates for parlay building - frontend compatible."""
    try:
        print(f"DEBUG: Raw props for sport {sport_id}: {len(raw_props)}")
        
        # Get raw props
        raw_props_query = select(ModelPick).options(
            selectinload(ModelPick.player).selectinload(Player.team),
            selectinload(ModelPick.market)
        ).where(ModelPick.sport_id == sport_id)
        
        raw_props_result = await db.execute(raw_props_query)
        raw_props = raw_props_result.scalars().all()
        
        print(f"DEBUG: After edge {edge_grade}: {len(edge_filtered)}")
        
        # Apply filters
        edge_grade_map = {"A": 0.05, "B": 0.03, "C": 0.01, "ALL": 0.0}
        edge_threshold = edge_grade_map.get(edge_grade.upper(), 0.03)
        
        edge_filtered = [p for p in raw_props if p.expected_value >= edge_threshold]
        
        print(f"DEBUG: After power {power}: {len(power_filtered)}")
        
        power_map = {"HIGH": 0.8, "FLEX": 0.6, "LOW": 0.4, "ALL": 0.0}
        power_threshold = power_map.get(power.upper(), 0.6)
        
        power_filtered = [p for p in edge_filtered if p.confidence_score >= power_threshold]
        
        print(f"DEBUG: With medium corr: {len(final_candidates)}")
        
        # For now, skip correlation filtering
        final_candidates = power_filtered
        
        # Format candidates for frontend
        candidates = []
        for prop in final_candidates:
            candidate = {
                "id": prop.id,
                "player_id": prop.player_id,
                "player_name": prop.player.name if prop.player else "Unknown",
                "team_name": prop.player.team.name if prop.player and prop.player.team else "Unknown",
                "team_abbreviation": prop.player.team.abbreviation if prop.player and prop.player.team else None,
                "sport_id": prop.sport_id,
                "stat_type": prop.market.stat_type if prop.market else "unknown",
                "line_value": prop.line_value,
                "side": prop.side,
                "odds": prop.odds,
                "expected_value": prop.expected_value,
                "confidence_score": prop.confidence_score,
                "edge_grade": "A" if prop.expected_value >= 0.05 else "B" if prop.expected_value >= 0.03 else "C",
                "power_score": "HIGH" if prop.confidence_score >= 0.8 else "FLEX" if prop.confidence_score >= 0.6 else "LOW",
                "generated_at": datetime.now(timezone.utc).isoformat(),  # Fresh timestamp
                "game_start_time": (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat(),
                "correlation_score": 0.7  # Mock correlation score
            }
            candidates.append(candidate)
        
        return {
            "totalCandidates": len(candidates),
            "candidates": candidates[:50],  # Limit to 50 for performance
            "dataExists": len(candidates) > 0,
            "status": "success",
            "showEmpty": len(candidates) == 0,
            "filters": {
                "edge_grade": edge_grade,
                "power": power,
                "correlated": correlated
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"ERROR in candidates endpoint: {e}")
        return {
            "totalCandidates": 0,
            "candidates": [],
            "dataExists": False,
            "status": "error",
            "showEmpty": True,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
