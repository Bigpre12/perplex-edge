"""
Parlay service using raw SQL to avoid timezone issues.
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
from app.models import ModelPick, Player, Game, Team, Market, PlayerGameStats
from app.schemas.public import (
    ParlayLeg,
    ParlayRecommendation,
    ParlayBuilderResponse,
    HundredPercentProp,
)
from app.services.picks_generator import (
    _calculate_hit_rate_season,
    _calculate_hit_rate,
    check_100_percent_window,
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


# =============================================================================
# Correlation Detection
# =============================================================================

class CorrelationType:
    """Types of correlations between parlay legs."""
    SAME_GAME = "same_game"
    SAME_PLAYER = "same_player"
    STAT_LADDER = "stat_ladder"
    OPPOSING_SIDES = "opposing_sides"


# =============================================================================
# Platform-Specific Validation Rules
# =============================================================================

PLATFORM_RULES = {
    "prizepicks": {
        "max_props_per_player": 1,  # PrizePicks only allows 1 prop per player
        "max_props_per_game": None,  # No game limit
        "name": "PrizePicks",
    },
    "draftkings": {
        "max_props_per_player": 2,  # DraftKings allows up to 2 props per player
        "max_props_per_game": 4,     # Max 4 props from same game
        "name": "DraftKings",
    },
    "fanduel": {
        "max_props_per_player": 2,
        "max_props_per_game": 4,
        "name": "FanDuel",
    },
    "underdog": {
        "max_props_per_player": 1,
        "max_props_per_game": None,
        "name": "Underdog Fantasy",
    },
    "sportsbook": {
        "max_props_per_player": 3,  # Most sportsbooks are lenient
        "max_props_per_game": None,
        "name": "Sportsbook",
    },
}


def validate_parlay_for_platform(legs: list[dict], platform: str = "prizepicks") -> dict:
    """
    Validate a parlay combination against platform-specific rules.
    
    Args:
        legs: List of parlay leg dictionaries
        platform: Platform to validate against
    
    Returns:
        Dict with 'is_valid', 'violations', and 'platform_name'
    """
    rules = PLATFORM_RULES.get(platform.lower(), PLATFORM_RULES["prizepicks"])
    violations = []
    
    # Check props per player
    max_per_player = rules.get("max_props_per_player")
    if max_per_player:
        player_counts: dict[int, list[str]] = {}
        for leg in legs:
            pid = leg.get("player_id")
            if pid:
                if pid not in player_counts:
                    player_counts[pid] = []
                player_counts[pid].append(leg.get("player_name", "Unknown"))
        
        for pid, names in player_counts.items():
            if len(names) > max_per_player:
                violations.append({
                    "type": "player_limit_exceeded",
                    "severity": "CRITICAL",
                    "message": f"Too many props for {names[0]}: {len(names)} (max {max_per_player} on {rules['name']})",
                    "player_id": pid,
                    "count": len(names),
                    "max_allowed": max_per_per_player,
                })
    
    # Check props per game
    max_per_game = rules.get("max_props_per_game")
    if max_per_game:
        game_counts: dict[int, int] = {}
        for leg in legs:
            gid = leg.get("game_id")
            if gid:
                game_counts[gid] = game_counts.get(gid, 0) + 1
        
        for gid, count in game_counts.items():
            if count > max_per_game:
                violations.append({
                    "type": "game_limit_exceeded",
                    "severity": "HIGH",
                    "message": f"Too many props from same game: {count} (max {max_per_game} on {rules['name']})",
                    "game_id": gid,
                    "count": count,
                    "max_allowed": max_per_game,
                })
    
    return {
        "is_valid": len(violations) == 0,
        "violations": violations,
        "platform_name": rules["name"],
    }


def detect_correlations(legs: list[dict]) -> list[dict]:
    """
    Detect correlations between parlay legs.
    
    Correlations that books may disallow or that increase true risk:
    1. Same Game - Multiple legs from the same game
    2. Same Player - Multiple props for the same player
    3. Stat Ladder - Same player/stat at different lines (e.g., over 24.5 AND over 29.5)
    4. Opposing Sides - Conflicting bets (over AND under same prop)
    
    Args:
        legs: List of leg dictionaries with game_id, player_id, stat_type, line, side
    
    Returns:
        List of correlation warnings with:
        - type: CorrelationType
        - severity: "high", "medium", "low"
        - legs: indices of correlated legs
        - message: Human-readable warning
    """
    warnings = []
    
    # Group legs by game
    games = {}
    for i, leg in enumerate(legs):
        game_id = leg.get("game_id")
        if game_id:
            if game_id not in games:
                games[game_id] = []
            games[game_id].append(i)
    
    # Check for same-game correlations
    for game_id, indices in games.items():
        if len(indices) > 1:
            warnings.append({
                "type": CorrelationType.SAME_GAME,
                "severity": "medium",
                "legs": indices,
                "message": f"Legs {[i+1 for i in indices]} are from the same game - correlated outcomes",
            })
    
    # Group legs by player
    players = {}
    for i, leg in enumerate(legs):
        player_id = leg.get("player_id")
        if player_id:
            if player_id not in players:
                players[player_id] = []
            players[player_id].append((i, leg))
    
    # Check for same-player and stat-ladder correlations
    for player_id, player_legs in players.items():
        if len(player_legs) > 1:
            indices = [pl[0] for pl in player_legs]
            player_name = player_legs[0][1].get("player_name", "Unknown")
            
            # Check for stat ladders (same stat, different lines)
            stats = {}
            for idx, leg in player_legs:
                stat_type = leg.get("stat_type", "")
                if stat_type not in stats:
                    stats[stat_type] = []
                stats[stat_type].append((idx, leg))
            
            # Check for opposing sides (over AND under)
            sides = set(pl[1].get("side", "").lower() for pl in player_legs)
            if "over" in sides and "under" in sides:
                warnings.append({
                    "type": CorrelationType.OPPOSING_SIDES,
                    "severity": "high",
                    "legs": stat_indices,
                    "message": f"Legs {[i+1 for i in indices]} have opposing sides on {player_name} {stat_type} - likely disallowed",
                })
            else:
                warnings.append({
                    "type": CorrelationType.STAT_LADDER,
                    "severity": "high",
                    "legs": stat_indices,
                    "message": f"Legs {[i+1 for i in indices]} are stat ladders on {player_name} {stat_type} - books may disallowed",
                })
            
            # General same-player warning (if not already caught by stat ladder)
            if len(stats) > 1:  # Multiple different stats for same player
                warnings.append({
                    "type": CorrelationType.SAME_PLAYER,
                    "severity": "low",
                    "legs": indices,
                    "message": f"Legs {[i+1 for i in indices]} are for the same player ({player_name}) - correlated performance",
                })
    
    return warnings


def calculate_correlation_risk_score(warnings: list[dict]) -> tuple[float, str]:
    """
    Calculate overall correlation risk score for a parlay.
    
    Args:
        warnings: List of correlation warnings
    
    Returns:
        Tuple of (risk_score, risk_level)
    """
    risk_score = 0.0
    risk_level = "LOW"
    
    for warning in warnings:
        severity_weights = {"high": 1.0, "medium": 0.5, "low": 0.1}
        risk_score += severity_weights[warning["severity"]]
    
    if risk_score >= 2.0:
        risk_level = "CRITICAL"
    elif risk_score >= 1.0:
        risk_level = "HIGH"
    elif risk_score >= 0.5:
        risk_level = "MEDIUM"
    
    return risk_score, risk_level


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
    
    Args:
        legs: List of leg dictionaries
        leg_count: Number of legs per parlay (2-15)
        require_100_pct: Require at least one 100% hit rate leg
        block_correlated: If True, filter out high-correlation parlays
        max_correlation_risk: Maximum allowed correlation risk level
        max_results: Maximum number of parlays to return
    
    Returns:
        List of parlay dictionaries with calculated metrics
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
    
    # Filter by correlation risk if requested
    if block_correlated and max_correlation_risk != "CRITICAL":
        all_combinations = []
        for combo in all_combinations:
            warnings = detect_correlations(combo)
            risk_score, risk_level = calculate_correlation_risk(warnings)
            
            # Filter out high-risk parlays
            if risk_level == "CRITICAL":
                continue
            elif risk_level == "HIGH" and max_correlation_risk != "CRITICAL":
                continue
            elif risk_level == "MEDIUM" and max_correlation_risk in ["HIGH", "CRITICAL"]:
                continue
            
            all_combinations.append(combo)
        
        logger.info(f"[parlay] Filtered to {len(all_combinations)} combinations by correlation risk (max: {max_correlation_risk})")
    
    # Sort by expected value
    all_combinations.sort(key=lambda x: sum(leg.get("expected_value", 0) for leg in x), reverse=True)
    
    # Take top parlay combinations
    best_parlays = all_combinations[:max_results]
    
    logger.info(f"[parlay] Selected top {len(best_parlays)} parlays from {len(all_combinations)} combinations")
    
    return best_parlays


# =============================================================================
# Parlay Builder Core Logic
# =============================================================================

async def build_parlays(
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
    Build optimized parlays for a sport using raw SQL queries.
    
    Args:
        db: Database session
        sport_id: Sport ID
        leg_count: Number of legs per parlay (2-15)
        include_100_pct: Require at least one 100% hit rate leg
        min_grade: Minimum grade for each leg (A, B, C, D, F)
        max_results: Number of parlays to return
        block_correlated: If True, filter out high-correlation parlays
        max_correlation_risk: Maximum allowed correlation risk level
    
    Returns:
        ParlayBuilderResponse with recommended parlays
    """
    try:
        # Convert grade to numeric for filtering
        min_grade_numeric = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}[min_grade]
        now = datetime.now(timezone.utc)
        
        # Dynamic time window for active games
        if True:  # Always use force_refresh logic
            game_window_start = now - timedelta(hours=2)
            game_window_end = now + timedelta(hours=36)
        else:
            game_window_start = now - timedelta(hours=1)
            game_window_end = now + timedelta(hours=24)
        
        # Use raw SQL to avoid timezone issues
        sql = text(f"""
            SELECT 
                mp.id, mp.expected_value, mp.line_value, mp.generated_at,
                p.name as player_name, g.start_time as game_start,
                m.stat_type as stat_type
            FROM model_picks mp
            JOIN players p ON mp.player_id = p.id
            JOIN games g ON mp.game_id = g.id
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
        player_game_combinations = set()  # Track unique player-game combinations
        stat_variety_per_player = {}  # Track stat variety per player
        
        for row in rows:
            # Extract row data
            pick_id, expected_value, line_value, generated_at, player_name, game_start, stat_type = row
            
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
                "confidence_score": 0.0,  # Would be calculated
                "hit_rate_30d": 0.0, # Would be calculated
                "hit_rate_10g": 0.0,  # Would be calculated
                "hit_rate_5g": 0.0, # Would be calculated
                "hit_rate_3g": 0.0, # Would be calculated
            }
            
            # Track player-game combinations
            player_game_key = f"{player_id}_{game_start}"
            player_game_combinations.add(player_game_key)
            
            # Track stat variety per player
            if player_id not in stat_variety_per_player:
                stat_variety[player_id] = []
            stat_variety[player_id].append(stat_type)
            
            legs.append(leg)
        
        logger.info(f"[parlay] Processed {len(legs)} legs after filtering")
        
        # PERFORMANCE: Limit candidates to avoid combinatorial explosion
        MAX_CANDIDATES = 50
        if len(legs) > MAX_CANDIDATES:
            legs.sort(key=lambda x: x.get("edge", 0) or 0, reverse=True)
            legs = legs[:MAX_CANDIDATES]
            logger.info(f"[parlay] Limited to top {MAX_CANDIDATES} legs by EV for performance")
        
        # Find best parlays with anti-repetition
        best_parlays = find_best_parlays(
            legs, leg_count, include_100_pct, block_correlated, max_correlation_risk, max_results
        )
        
        # Create parlay recommendations
        parlays = []
        for parlay in best_parlays:
            # Calculate parlay metrics
            total_edge = sum(leg["edge"] for leg in parlay["legs"])
            parlay_probability = 1.0  # Would be calculated
            parlay_ev = total_edge / len(parlay["legs"])
            
            # Create parlay recommendation
            parlays.append({
                "legs": parlay["legs"],
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
