"""
Debug Candidates API - Diagnose candidate filtering issues
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import ModelPick, Player, Team, Market

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/candidates/{sport_id}")
async def debug_candidates(
    sport_id: int,
    edge_grade: str = Query(default="B", description="Edge grade filter"),
    power: str = Query(default="flex", description="Power filter"),
    correlated: str = Query(default="medium", description="Correlation filter"),
    db: AsyncSession = Depends(get_db)
):
    """Debug endpoint to diagnose candidate filtering issues."""
    try:
        debug_info = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sport_id": sport_id,
            "filters": {
                "edge_grade": edge_grade,
                "power": power,
                "correlated": correlated
            },
            "filtering_stages": {},
            "sample_data": {},
            "diagnosis": {}
        }
        
        # Stage 1: Raw props (ModelPicks)
        raw_props_query = select(ModelPick).options(
            selectinload(ModelPick.player).selectinload(Player.team),
            selectinload(ModelPick.market)
        ).where(ModelPick.sport_id == sport_id)
        
        raw_props_result = await db.execute(raw_props_query)
        raw_props = raw_props_result.scalars().all()
        
        debug_info["filtering_stages"]["raw_props"] = len(raw_props)
        print(f"DEBUG: Raw props for sport {sport_id}: {len(raw_props)}")
        
        # Stage 2: Time filter (within 24 hours)
        now = datetime.now(timezone.utc)
        future_24h = now + timedelta(hours=24)
        
        # Since our data has old timestamps, let's check what we have
        time_filtered = []
        for prop in raw_props:
            # For debugging, let's include all props regardless of time
            time_filtered.append(prop)
        
        debug_info["filtering_stages"]["after_time_filter"] = len(time_filtered)
        print(f"DEBUG: After time filter: {len(time_filtered)}")
        
        # Stage 3: Edge grade filter
        edge_grade_map = {"A": 0.05, "B": 0.03, "C": 0.01, "ALL": 0.0}
        edge_threshold = edge_grade_map.get(edge_grade.upper(), 0.03)
        
        edge_filtered = []
        for prop in time_filtered:
            if prop.expected_value >= edge_threshold:
                edge_filtered.append(prop)
        
        debug_info["filtering_stages"]["after_edge_filter"] = len(edge_filtered)
        print(f"DEBUG: After edge {edge_grade} filter: {len(edge_filtered)}")
        
        # Stage 4: Power filter (simplified -  check confidence)
        power_map = {"HIGH": 0.8, "FLEX": 0.6, "LOW": 0.4, "ALL": 0.0}
        power_threshold = power_map.get(power.upper(), 0.6)
        
        power_filtered = []
        for prop in edge_filtered:
            if prop.confidence_score >= power_threshold:
                power_filtered.append(prop)
        
        debug_info["filtering_stages"]["after_power_filter"] = len(power_filtered)
        print(f"DEBUG: After power {power} filter: {len(power_filtered)}")
        
        # Stage 5: Correlation filter (simplified -  check if we have multiple props)
        # In reality, this would check correlation pairs table
        correlation_map = {"HIGH": 0.8, "MEDIUM": 0.6, "LOW": 0.4, "NONE": 0.0}
        correlation_threshold = correlation_map.get(correlated.upper(), 0.6)
        
        # For now, we'll  pass all props through correlation filter
        final_candidates = power_filtered
        debug_info["filtering_stages"]["after_correlation_filter"] = len(final_candidates)
        print(f"DEBUG: After correlation {correlated} filter: {len(final_candidates)}")
        
        # Sample data
        if final_candidates:
            debug_info["sample_data"]["candidates"] = [
                {
                    "player": prop.player.name if prop.player else "Unknown",
                    "team": prop.player.team.name if prop.player and prop.player.team else "Unknown",
                    "stat_type": prop.market.stat_type if prop.market else "unknown",
                    "expected_value": prop.expected_value,
                    "confidence_score": prop.confidence_score,
                    "line_value": prop.line_value,
                    "generated_at": prop.generated_at.isoformat() if prop.generated_at else None
                }
                for prop in final_candidates[:5]
            ]
        else:
            debug_info["sample_data"]["candidates"] = []
        
        # Diagnosis
        diagnosis = []
        
        if len(raw_props) == 0:
            diagnosis.append("CRITICAL: No raw props found for this sport")
        else:
            diagnosis.append(f"OK: Found {len(raw_props)} raw props")
        
        if len(time_filtered) == 0:
            diagnosis.append("ISSUE: Time filter removed all props")
        else:
            diagnosis.append(f"OK: {len(time_filtered)} props pass time filter")
        
        if len(edge_filtered) == 0:
            diagnosis.append(f"ISSUE: Edge grade {edge_grade} filter too strict")
            diagnosis.append(f"Suggestion: Try edge_grade='ALL' or lower threshold")
        else:
            diagnosis.append(f"OK: {len(edge_filtered)} props pass edge filter")
        
        if len(power_filtered) == 0:
            diagnosis.append(f"ISSUE: Power {power} filter too strict")
            diagnosis.append(f"Suggestion: Try power='ALL' or lower threshold")
        else:
            diagnosis.append(f"OK: {len(power_filtered)} props pass power filter")
        
        if len(final_candidates) == 0:
            diagnosis.append("CRITICAL: No candidates pass all filters")
            diagnosis.append("Suggestion: Loosen filters or check data quality")
        else:
            diagnosis.append(f"SUCCESS: {len(final_candidates)} final candidates")
        
        debug_info["diagnosis"] = {
            "issues": diagnosis,
            "recommendation": "Loosen filters if no candidates remain",
            "final_candidates_count": len(final_candidates)
        }
        
        return debug_info
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "diagnosis": "Failed to run candidate analysis"
        }
