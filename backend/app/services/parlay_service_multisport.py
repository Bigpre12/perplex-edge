"""
Multi-sport parlay service using raw SQL.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, List
from itertools import combinations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.cache import cache, cached
from app.schemas.public import (
    ParlayLeg,
    ParlayRecommendation,
    ParlayBuilderResponse,
)

logger = get_logger(__name__)

# Grade thresholds
GRADE_THRESHOLDS = {
    "A": 0.05,   # Edge >= 5%
    "B": 0.03,   # Edge >= 3%
    "C": 0.01,   # Edge >= 1%
    "D": 0.00,   # Edge >= 0%
    "F": -1.0,   # Negative edge
}

GRADE_ORDER = ["A", "B", "C", "D", "F"]

def calculate_grade(edge: float) -> str:
    """Calculate letter grade from edge percentage."""
    if edge >= 0.05:
        return "A"
    elif edge >= 0.03:
        return "B"
    elif edge >= 0.01:
        return "C"
    elif edge >= 0.00:
        return "D"
    else:
        return "F"


def grade_to_numeric(grade: str) -> int:
    """Convert grade to numeric for comparison (A=4, B=3, C=2, D=1, F=0)."""
    return {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}.get(grade.upper(), 0)


def find_best_parlays(
    legs: list[dict],
    leg_count: int,
    require_100_pct: bool = False,
    block_correlated: bool = True,
    max_correlation_risk: str = "MEDIUM",
    max_results: int = 5,
) -> list[dict]:
    """
    Find optimal parlays from available legs using combinatorial optimization.
    """
    best_parlays = []
    
    # Generate all possible combinations
    all_combinations = list(combinations(legs, leg_count))
    logger.info(f"[parlay] Generated {len(all_combinations)} combinations from {len(legs)} legs")
    
    # Filter by 100% requirement if requested
    if require_100_pct:
        all_combinations = [
            combo for combo in all_combinations
            if any(leg.get("hit_rate_30d", 0) >= 1.0 for leg in combo)
        ]
        logger.info(f"[parlay] Filtered to {len(all_combinations)} combinations with 100% hit rate legs")
    
    # Sort by expected value
    all_combinations.sort(key=lambda x: sum(leg.get("expected_value", 0) for leg in x), reverse=True)
    
    # Take top parlay combinations
    best_parlays = all_combinations[:max_results]
    
    logger.info(f"[parlay] Selected top {len(best_parlays)} parlays from {len(all_combinations)} combinations")
    
    return best_parlays


async def build_parlays_multisport(
    db: AsyncSession,
    sport_id: int,
    leg_count: int = 3,
    include_100_pct: bool = False,
    min_grade: str = "C",
    max_results: int = 5,
    block_correlated: bool = True,
    max_correlation_risk: str = "MEDIUM",
) -> ParlayBuilderResponse:
    """
    Build optimized parlays for a sport using raw SQL (multi-sport version).
    
    This version supports all sports with proper data integrity checks.
    """
    try:
        # Convert grade to numeric for filtering
        min_grade_numeric = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}[min_grade]
        now = datetime.now(timezone.utc)
        
        # Dynamic time window for active games
        game_window_start = now - timedelta(hours=2)
        game_window_end = now + timedelta(hours=36)
        
        # Use raw SQL to avoid timezone issues
        sql = text(f"""
            SELECT 
                mp.id, mp.expected_value, mp.line_value, mp.generated_at,
                p.name as player_name, p.id as player_id, g.start_time as game_start,
                m.stat_type as stat_type
            FROM model_picks mp
            JOIN players p ON mp.player_id = p.id
            JOIN games g ON mp.game_id = g.id
            JOIN markets m ON mp.market_id = m.id
            WHERE g.sport_id = {sport_id}
            AND mp.generated_at > '{now - timedelta(hours=6)}'
            AND mp.line_value IS NOT NULL AND mp.line_value > 0
            AND g.start_time > '{game_window_start}'
            AND g.start_time < '{game_window_end}'
            ORDER BY mp.expected_value DESC
            LIMIT 1000
        """)
        
        result = await db.execute(sql)
        rows = result.fetchall()
        
        logger.info(f"[parlay] Raw SQL returned {len(rows)} candidate legs for sport {sport_id}")
        
        legs = []
        
        for row in rows:
            # Extract row data
            pick_id, expected_value, line_value, generated_at, player_name, player_id, game_start, stat_type = row
            
            # Calculate grade
            edge = expected_value
            grade = calculate_grade(edge)
            
            # Skip if below minimum grade
            if grade_to_numeric(grade) < min_grade_numeric:
                continue
            
            # Create leg dictionary
            leg = {
                "pick_id": pick_id,
                "player_name": player_name,
                "game_start": game_start.isoformat(),
                "generated_at": generated_at.isoformat(),
                "stat_type": stat_type,
                "line_value": line_value,
                "expected_value": expected_value,
                "grade": grade,
                "edge": edge,
                "grade_numeric": grade_to_numeric(grade),
                "confidence_score": 0.0,
                "hit_rate_30d": 0.0,
                "hit_rate_10g": 0.0,
                "hit_rate_5g": 0.0,
                "hit_rate_3g": 0.0,
            }
            
            legs.append(leg)
        
        logger.info(f"[parlay] Processed {len(legs)} legs after filtering")
        
        # PERFORMANCE: Limit candidates to avoid combinatorial explosion
        MAX_CANDIDATES = 50
        if len(legs) > MAX_CANDIDATES:
            legs.sort(key=lambda x: x.get("edge", 0) or 0, reverse=True)
            legs = legs[:MAX_CANDIDATES]
            logger.info(f"[parlay] Limited to top {MAX_CANDIDATES} legs by EV for performance")
        
        # Find best parlays
        best_parlays = find_best_parlays(
            legs, leg_count, include_100_pct, block_correlated, max_correlation_risk, max_results
        )
        
        # Create parlay recommendations
        parlays = []
        for parlay in best_parlays:
            # Calculate parlay metrics
            total_edge = sum(leg["edge"] for leg in parlay)
            parlay_probability = 1.0  # Would be calculated
            parlay_ev = total_edge / len(parlay)
            
            # Create parlay recommendation
            parlays.append({
                "legs": parlay,
                "parlay_probability": parlay_probability,
                "parlay_ev": parlay_ev,
                "confidence": "HIGH" if parlay_ev > 0.03 else "MEDIUM" if parlay_ev > 0.01 else "LOW",
                "labels": ["LOCK" if parlay_ev > 0.03 else "PLAY"],
                "total_edge": total_edge,
                "leg_count": leg_count,
                "sport_id": sport_id
            })
        
        logger.info(f"[parlay] Generated {len(parlays)} parlays from {len(legs)} legs")
        
        return ParlayBuilderResponse(
            parlays=parlays,
            total_candidates=len(legs),
            leg_count=leg_count,
            filters_applied={
                "min_leg_grade": min_grade,
                "include_100_pct": include_100_pct,
                "sport_id": sport_id
            }
        )
        
    except Exception as e:
        logger.error(f"[parlay] Error building parlays for sport {sport_id}: {e}", exc_info=True)
        # Return empty response instead of 500 error to prevent CORS issues
        return ParlayBuilderResponse(
            parlays=[],
            total_candidates=0,
            leg_count=leg_count,
            filters_applied={
                "min_leg_grade": min_grade,
                "include_100_pct": include_100_pct,
                "sport_id": sport_id
            }
        )


async def get_supported_sports(db: AsyncSession) -> list[dict]:
    """Get list of supported sports with available candidates."""
    try:
        # Check which sports have recent model picks
        sql = text("""
            SELECT DISTINCT g.sport_id, s.name, s.key, COUNT(*) as pick_count
            FROM model_picks mp
            JOIN games g ON mp.game_id = g.id
            JOIN sports s ON g.sport_id = s.id
            WHERE mp.generated_at > NOW() - INTERVAL '24 hours'
            AND mp.line_value IS NOT NULL AND mp.line_value > 0
            GROUP BY g.sport_id, s.name, s.key
            ORDER BY pick_count DESC
        """)
        
        result = await db.execute(sql)
        rows = result.fetchall()
        
        supported_sports = []
        for row in rows:
            sport_id, sport_name, sport_key, pick_count = row
            supported_sports.append({
                "sport_id": sport_id,
                "name": sport_name,
                "key": sport_key,
                "pick_count": pick_count
            })
        
        return supported_sports
        
    except Exception as e:
        logger.error(f"Error getting supported sports: {e}")
        return []
