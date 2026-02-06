"""Parlay builder service for creating optimized parlays from picks."""

from itertools import combinations
from typing import Any, Optional

from sqlalchemy import select, and_
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


# =============================================================================
# Grade Thresholds
# =============================================================================

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
                    "max_allowed": max_per_player,
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
            
            for stat_type, stat_legs in stats.items():
                if len(stat_legs) > 1:
                    stat_indices = [sl[0] for sl in stat_legs]
                    
                    # Check for opposing sides (over AND under)
                    sides = set(sl[1].get("side", "").lower() for sl in stat_legs)
                    if "over" in sides and "under" in sides:
                        warnings.append({
                            "type": CorrelationType.OPPOSING_SIDES,
                            "severity": "high",
                            "legs": stat_indices,
                            "message": f"Legs {[i+1 for i in stat_indices]} have opposing sides on {player_name} {stat_type} - likely disallowed",
                        })
                    else:
                        warnings.append({
                            "type": CorrelationType.STAT_LADDER,
                            "severity": "high",
                            "legs": stat_indices,
                            "message": f"Legs {[i+1 for i in stat_indices]} are stat ladders on {player_name} {stat_type} - books may disallow",
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
    
    Returns:
        Tuple of (risk_score 0-1, risk_label)
        - risk_score: 0 = no correlation, 1 = highly correlated
        - risk_label: "LOW", "MEDIUM", "HIGH", "CRITICAL"
    """
    if not warnings:
        return 0.0, "LOW"
    
    # Weight severities
    severity_weights = {"high": 0.4, "medium": 0.2, "low": 0.1}
    
    total_risk = sum(severity_weights.get(w["severity"], 0.1) for w in warnings)
    
    # Cap at 1.0
    risk_score = min(1.0, total_risk)
    
    # Determine label
    if risk_score >= 0.8:
        risk_label = "CRITICAL"
    elif risk_score >= 0.5:
        risk_label = "HIGH"
    elif risk_score >= 0.2:
        risk_label = "MEDIUM"
    else:
        risk_label = "LOW"
    
    return round(risk_score, 2), risk_label


# =============================================================================
# Kelly Criterion Bet Sizing
# =============================================================================

def calculate_kelly_fraction(
    win_prob: float,
    american_odds: int,
    kelly_multiplier: float = 0.25,  # Quarter Kelly is safer
) -> dict:
    """
    Calculate Kelly criterion bet sizing.
    
    Full Kelly: f* = (bp - q) / b
    where:
        b = decimal odds - 1 (profit per unit wagered)
        p = probability of winning
        q = probability of losing (1 - p)
    
    Args:
        win_prob: Model's win probability (0-1)
        american_odds: American odds
        kelly_multiplier: Fraction of Kelly to use (0.25 = quarter Kelly)
    
    Returns:
        Dict with kelly_fraction, suggested_units, edge, and risk_level
    """
    # Convert to decimal odds
    if american_odds >= 100:
        decimal_odds = 1 + (american_odds / 100)
    else:
        decimal_odds = 1 + (100 / abs(american_odds))
    
    b = decimal_odds - 1  # Profit per unit
    p = win_prob
    q = 1 - p
    
    # Full Kelly fraction
    full_kelly = (b * p - q) / b if b > 0 else 0
    
    # Apply multiplier (quarter Kelly is standard for variance reduction)
    kelly_fraction = max(0, full_kelly * kelly_multiplier)
    
    # Calculate edge
    edge = (p * decimal_odds) - 1
    
    # Determine risk level and suggested units
    if kelly_fraction <= 0:
        risk_level = "NO_BET"
        suggested_units = 0
    elif kelly_fraction < 0.01:
        risk_level = "SMALL"
        suggested_units = 0.5
    elif kelly_fraction < 0.02:
        risk_level = "STANDARD"
        suggested_units = 1.0
    elif kelly_fraction < 0.04:
        risk_level = "CONFIDENT"
        suggested_units = 2.0
    elif kelly_fraction < 0.06:
        risk_level = "STRONG"
        suggested_units = 3.0
    else:
        risk_level = "MAX"
        suggested_units = 5.0  # Cap at 5 units
    
    return {
        "full_kelly_pct": round(full_kelly * 100, 2),
        "kelly_fraction": round(kelly_fraction, 4),
        "suggested_units": suggested_units,
        "edge_pct": round(edge * 100, 2),
        "risk_level": risk_level,
        "decimal_odds": round(decimal_odds, 3),
        "kelly_multiplier": kelly_multiplier,
    }


def calculate_parlay_kelly(
    parlay_prob: float,
    decimal_odds: float,
    kelly_multiplier: float = 0.1,  # 10% Kelly for parlays (higher variance)
) -> dict:
    """
    Calculate Kelly sizing for a parlay.
    
    Parlays have higher variance, so we use a smaller Kelly fraction.
    """
    b = decimal_odds - 1
    p = parlay_prob
    q = 1 - p
    
    full_kelly = (b * p - q) / b if b > 0 else 0
    kelly_fraction = max(0, full_kelly * kelly_multiplier)
    edge = (p * decimal_odds) - 1
    
    # More conservative for parlays
    if kelly_fraction <= 0:
        risk_level = "NO_BET"
        suggested_units = 0
    elif kelly_fraction < 0.005:
        risk_level = "SMALL"
        suggested_units = 0.25
    elif kelly_fraction < 0.01:
        risk_level = "STANDARD"
        suggested_units = 0.5
    elif kelly_fraction < 0.02:
        risk_level = "CONFIDENT"
        suggested_units = 1.0
    else:
        risk_level = "STRONG"
        suggested_units = 2.0  # Cap parlays at 2 units
    
    return {
        "full_kelly_pct": round(full_kelly * 100, 2),
        "kelly_fraction": round(kelly_fraction, 4),
        "suggested_units": suggested_units,
        "edge_pct": round(edge * 100, 2),
        "risk_level": risk_level,
        "kelly_multiplier": kelly_multiplier,
    }


# =============================================================================
# Odds Conversion Utilities
# =============================================================================

def american_to_decimal(american_odds: int) -> float:
    """Convert American odds to decimal odds."""
    if american_odds >= 100:
        return 1 + (american_odds / 100)
    else:  # Negative odds
        return 1 + (100 / abs(american_odds))


def decimal_to_american(decimal_odds: float) -> int:
    """Convert decimal odds to American odds."""
    if decimal_odds >= 2.0:
        return int(round((decimal_odds - 1) * 100))
    else:
        return int(round(-100 / (decimal_odds - 1)))


def calculate_parlay_odds(legs_odds: list[int]) -> tuple[int, float]:
    """
    Calculate combined parlay odds from individual leg odds.
    
    Args:
        legs_odds: List of American odds for each leg
    
    Returns:
        Tuple of (american_odds, decimal_odds)
    """
    # Convert all to decimal, multiply, convert back
    decimal_product = 1.0
    for odds in legs_odds:
        decimal_product *= american_to_decimal(odds)
    
    american = decimal_to_american(decimal_product)
    return american, decimal_product


def calculate_implied_probability(american_odds: int) -> float:
    """Calculate implied probability from American odds."""
    if american_odds >= 100:
        return 100 / (american_odds + 100)
    else:
        return abs(american_odds) / (abs(american_odds) + 100)


# =============================================================================
# Parlay EV Calculation
# =============================================================================

def calculate_parlay_ev(
    legs: list[dict],
) -> tuple[float, float]:
    """
    Calculate parlay probability and EV.
    
    Args:
        legs: List of leg dicts with 'win_prob' and 'odds'
    
    Returns:
        Tuple of (parlay_probability, parlay_ev)
    """
    # Parlay probability = product of individual win probabilities
    parlay_prob = 1.0
    for leg in legs:
        parlay_prob *= leg["win_prob"]
    
    # Calculate combined odds
    legs_odds = [leg["odds"] for leg in legs]
    american_odds, decimal_odds = calculate_parlay_odds(legs_odds)
    
    # EV = P(win) * profit - P(lose) * stake
    # For $1 stake: EV = P(win) * (decimal_odds - 1) - P(lose) * 1
    profit_if_win = decimal_odds - 1
    parlay_ev = (parlay_prob * profit_if_win) - ((1 - parlay_prob) * 1)
    
    return parlay_prob, parlay_ev


def determine_parlay_label(
    legs: list[dict],
    parlay_prob: float,
    parlay_ev: float,
) -> str:
    """
    Determine LOCK/PLAY/SKIP label for a parlay.
    
    LOCK criteria:
    - All legs have edge >= 0.02
    - No leg has win_prob < 0.40
    - Parlay EV >= 0.03 and parlay_prob >= 0.15
    
    PLAY criteria:
    - Parlay EV >= 0.01 but doesn't meet LOCK criteria
    
    SKIP:
    - Any leg has negative edge or win_prob < 0.35
    """
    min_prob = min(leg["win_prob"] for leg in legs)
    min_edge = min(leg["edge"] for leg in legs)
    all_edges_above_02 = all(leg["edge"] >= 0.02 for leg in legs)
    
    # SKIP conditions
    if min_edge < 0 or min_prob < 0.35:
        return "SKIP"
    
    # LOCK conditions
    if (all_edges_above_02 and 
        min_prob >= 0.40 and 
        parlay_ev >= 0.03 and 
        parlay_prob >= 0.15):
        return "LOCK"
    
    # PLAY conditions
    if parlay_ev >= 0.01:
        return "PLAY"
    
    return "SKIP"


# =============================================================================
# Hit Rate Calculation for Props
# =============================================================================

async def get_hit_rate_data(
    db: AsyncSession,
    player_id: int,
    stat_type: str,
    line_value: float,
    side: str = "over",
    sport_id: int = 30,  # Default to NBA, but should be passed for other sports
) -> dict[str, Any]:
    """
    Get comprehensive hit rate data for a player prop.
    
    Args:
        db: Database session
        player_id: Player's internal ID
        stat_type: Stat type (e.g., 'PTS', 'REB', 'AST')
        line_value: The line to check against
        side: 'over' or 'under' - determines hit direction
        sport_id: Sport ID (30=NBA, 31=NFL, 32=NCAAB) - determines season start date
    
    Returns dict with:
    - hit_rate_season, games_season, is_100_season
    - hit_rate_last_10, games_last_10, is_100_last_10
    - hit_rate_last_5, games_last_5, is_100_last_5
    """
    # Season data - use sport-specific season start
    hr_season, games_season, is_100_season = await _calculate_hit_rate_season(
        db, player_id, stat_type, line_value, side, sport_id=sport_id
    )
    
    # Last 10 games
    hr_10 = await _calculate_hit_rate(db, player_id, stat_type, line_value, side, games_back=10)
    games_10 = 10 if hr_10 is not None else 0
    
    # Last 5 games
    hr_5 = await _calculate_hit_rate(db, player_id, stat_type, line_value, side, games_back=5)
    games_5 = 5 if hr_5 is not None else 0
    
    # Check 100% flags for last 10 and last 5
    # We need actual values for this
    from datetime import datetime
    from app.services.season_helper import get_season_start_for_sport_id
    season_start = get_season_start_for_sport_id(sport_id)
    
    result = await db.execute(
        select(PlayerGameStats.value)
        .where(
            and_(
                PlayerGameStats.player_id == player_id,
                PlayerGameStats.stat_type == stat_type,
            )
        )
        .order_by(PlayerGameStats.created_at.desc())
        .limit(10)
    )
    values_10 = [row[0] for row in result.all()]
    values_5 = values_10[:5] if len(values_10) >= 5 else values_10
    
    is_100_10 = check_100_percent_window(values_10, line_value, side, min_games=3)
    is_100_5 = check_100_percent_window(values_5, line_value, side, min_games=3)
    
    return {
        "hit_rate_season": hr_season,
        "games_season": games_season,
        "is_100_season": is_100_season,
        "hit_rate_last_10": hr_10,
        "games_last_10": len(values_10),
        "is_100_last_10": is_100_10,
        "hit_rate_last_5": hr_5,
        "games_last_5": len(values_5),
        "is_100_last_5": is_100_5,
    }


# =============================================================================
# Parlay Builder Core Logic
# =============================================================================

async def build_parlay_legs(
    db: AsyncSession,
    sport_id: int,
    min_grade: str = "C",
    active_games_only: bool = True,
    max_props_per_player: int = 1,
    force_refresh: bool = False,
) -> list[dict]:
    """
    Build list of eligible parlay legs from active player prop picks.
    
    Enhanced with dynamic prop swapping and stale line detection.
    
    Args:
        db: Database session
        sport_id: Sport ID to filter picks
        min_grade: Minimum grade to include (default C)
        active_games_only: If True, only include props for games starting in next 24 hours
        max_props_per_player: Maximum props per player (1 for PrizePicks rules)
        force_refresh: Force refresh of stale data
    
    Returns:
        List of leg dictionaries with all required data
    """
    from datetime import datetime, timezone, timedelta
    import random
    
    min_grade_numeric = grade_to_numeric(min_grade)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Dynamic time window for active games
    if force_refresh:
        # Wider window when forcing refresh to get more variety
        game_window_start = now - timedelta(hours=2)
        game_window_end = now + timedelta(hours=36)
    else:
        game_window_start = now - timedelta(hours=1)
        game_window_end = now + timedelta(hours=24)
    
    # Build query conditions with freshness check
    conditions = [
        Game.sport_id == sport_id,
        ModelPick.player_id.isnot(None),  # Player props only
        ModelPick.created_at > now - timedelta(hours=6),  # Only recent picks (avoid stale data)
    ]
    
    # Only include active games if enabled
    if active_games_only:
        conditions.extend([
            Game.start_time > game_window_start,
            Game.start_time < game_window_end,
        ])
        logger.info(f"[parlay] Dynamic filtering for active games: {game_window_start} to {game_window_end}")
    
    # Query player prop picks with freshness
    result = await db.execute(
        select(ModelPick, Player, Game, Team, Market)
        .join(Player, ModelPick.player_id == Player.id)
        .join(Game, ModelPick.game_id == Game.id)
        .outerjoin(Team, Player.team_id == Team.id)
        .join(Market, ModelPick.market_id == Market.id)
        .where(and_(*conditions))
        .order_by(ModelPick.created_at.desc())  # Prioritize newest picks
    )
    rows = result.all()
    
    logger.info(f"[parlay] Query returned {len(rows)} fresh props for sport {sport_id}")
    
    legs = []
    player_game_combinations = set()  # Track unique player-game combinations
    stat_variety_per_player = {}  # Track stat variety per player
    
    for pick, player, game, team, market in rows:
        # Skip picks with invalid line values
        if pick.line_value is None or pick.line_value == 0:
            continue
        
        # Dynamic freshness check - skip very old picks
        pick_age = now - pick.created_at.replace(tzinfo=None)
        if pick_age.total_seconds() > 21600:  # 6 hours old
            continue
        
        # Calculate edge
        edge = pick.expected_value
        grade = calculate_grade(edge)
        
        # Skip if below minimum grade
        if grade_to_numeric(grade) < min_grade_numeric:
            continue
        
        stat_type = market.stat_type or market.market_type
        
        # Enhanced stat type filtering - be more permissive for variety
        HIDDEN_STAT_TYPES = {
            # Basketball - very low volume
            "STL", "BLK",
            # Hockey - low volume
            "BLK_SHOTS",
            # Football - very random
            "INT",
            # Baseball - low volume
            "OUTS",
            # Tennis - very low volume
            "DF",
        }
        
        # Allow 3PM for NBA (more volume than other low-volume stats)
        if stat_type in HIDDEN_STAT_TYPES and not (sport_id == 30 and stat_type == "3PM"):
            continue
        
        # Dynamic player-game combination tracking
        player_game_key = f"{player.id}-{game.id}"
        if player_game_key in player_game_combinations:
            # Skip if we already have this player in this game, but allow if it's a different stat
            existing_legs = [leg for leg in legs if leg["player_id"] == player.id and leg["game_id"] == game.id]
            existing_stats = [leg["stat_type"] for leg in existing_legs]
            if stat_type in existing_stats:
                continue  # Skip duplicate stat for same player-game
        
        player_game_combinations.add(player_game_key)
        
        # Track stat variety per player
        if player.id not in stat_variety_per_player:
            stat_variety_per_player[player.id] = set()
        stat_variety_per_player[player.id].add(stat_type)
        
        # Use pre-calculated hit rates with fallback
        hr_5g = pick.hit_rate_5g or 0.0
        hr_10g = pick.hit_rate_10g or 0.0
        hr_30d = pick.hit_rate_30d or 0.0
        hr_3g = pick.hit_rate_3g or 0.0
        
        # Dynamic 100% flags with more lenient criteria
        is_100_5 = hr_5g >= 0.95  # Lower threshold for more variety
        is_100_10 = hr_10g >= 0.95
        is_100_season = hr_30d >= 0.95
        
        legs.append({
            "pick_id": pick.id,
            "player_name": player.name,
            "player_id": player.id,
            "team_abbr": team.abbreviation if team else "UNK",
            "stat_type": stat_type,
            "line": pick.line_value,
            "side": pick.side,
            "odds": pick.odds,
            "grade": grade,
            "win_prob": pick.model_probability,
            "edge": edge,
            "ev": pick.expected_value,
            "confidence": pick.confidence_score,
            "game_id": game.id,
            "game_start_time": game.start_time,
            "pick_created_at": pick.created_at,
            "pick_age_hours": pick_age.total_seconds() / 3600,
            # Hit rate data
            "hit_rate_season": hr_30d,
            "games_season": 30 if hr_30d > 0 else 0,
            "is_100_season": is_100_season,
            "hit_rate_last_10": hr_10g,
            "games_last_10": 10 if hr_10g > 0 else 0,
            "is_100_last_10": is_100_10,
            "hit_rate_last_5": hr_5g,
            "games_last_5": 5 if hr_5g > 0 else 0,
            "is_100_last_5": is_100_5,
        })
    
    # Enhanced player prop limiting with dynamic allocation
    if max_props_per_player > 0:
        # Sort by multiple factors for better variety
        legs.sort(key=lambda x: (
            x.get("ev", 0),  # Primary: EV
            x.get("confidence", 0),  # Secondary: Confidence
            -x.get("pick_age_hours", 0),  # Tertiary: Freshness (newer is better)
        ), reverse=True)
        
        player_prop_count: dict[int, int] = {}
        player_stat_types: dict[int, set] = {}
        filtered_legs = []
        
        for leg in legs:
            pid = leg["player_id"]
            stat_type = leg["stat_type"]
            
            if pid not in player_prop_count:
                player_prop_count[pid] = 0
            if pid not in player_stat_types:
                player_stat_types[pid] = set()
            
            # Dynamic allocation: allow more props if player has diverse stats
            max_for_player = max_props_per_player
            if len(stat_variety_per_player.get(pid, set())) >= 3:
                max_for_player = min(max_props_per_player + 1, 3)  # Allow one extra for diverse players
            
            if (player_prop_count[pid] < max_for_player and 
                stat_type not in player_stat_types[pid]):  # No duplicate stats per player
                filtered_legs.append(leg)
                player_prop_count[pid] += 1
                player_stat_types[pid].add(stat_type)
        
        logger.info(
            f"[parlay] Dynamic filtering: {len(legs)} -> {len(filtered_legs)} legs "
            f"(max {max_props_per_player} props per player, with stat variety)"
        )
        legs = filtered_legs
    
    # Final variety boost: shuffle to avoid same players appearing in every parlay
    if len(legs) > 10:
        # Keep top 10 by EV, then shuffle the rest for variety
        top_legs = legs[:10]
        remaining_legs = legs[10:]
        random.shuffle(remaining_legs)
        legs = top_legs + remaining_legs
    
    logger.info(f"[parlay] Final leg pool: {len(legs)} diverse legs for sport {sport_id}")
    return legs


CORRELATION_RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


def find_best_parlays(
    legs: list[dict],
    leg_count: int,
    require_100_pct: bool = False,
    max_results: int = 5,
    block_correlated: bool = True,
    max_correlation_risk: str = "MEDIUM",
    avoid_repetition: bool = True,
) -> list[dict]:
    """
    Find the best parlay combinations from available legs.
    
    Enhanced with anti-repetition and variety boosting.
    
    Args:
        legs: List of eligible leg dictionaries
        leg_count: Number of legs per parlay
        require_100_pct: Require at least one 100% hit rate leg
        max_results: Maximum number of parlays to return
        block_correlated: If True, filter out parlays exceeding max_correlation_risk
        max_correlation_risk: Maximum allowed correlation risk level
        avoid_repetition: If True, avoid repetitive player/stat combinations
    
    Returns:
        List of parlay dictionaries sorted by EV
    """
    import random
    
    if len(legs) < leg_count:
        logger.warning(f"Not enough legs ({len(legs)}) for {leg_count}-leg parlay")
        return []
    
    # Track used combinations to avoid repetition
    used_player_sets = set()
    used_stat_combinations = set()
    used_game_combinations = set()
    
    # Use generator to avoid memory overhead - evaluate lazily
    # Limit total combinations evaluated for performance
    MAX_COMBOS_TO_EVALUATE = 25000
    combo_count = 0
    
    parlays = []
    for combo in combinations(legs, leg_count):
        combo_count += 1
        if combo_count > MAX_COMBOS_TO_EVALUATE:
            logger.info(f"Stopped at {MAX_COMBOS_TO_EVALUATE} combinations evaluated")
            break
        
        combo_list = list(combo)
        
        # Anti-repetition checks
        if avoid_repetition:
            # Check player set repetition
            player_set = frozenset(leg["player_id"] for leg in combo_list)
            player_set_key = tuple(sorted(player_set))
            if player_set_key in used_player_sets:
                continue  # Skip duplicate player set
            
            # Check stat combination repetition
            stat_combo = tuple(sorted(f"{leg['player_id']}_{leg['stat_type']}" for leg in combo_list))
            if stat_combo in used_stat_combinations:
                continue  # Skip duplicate stat combination
            
            # Check game distribution (avoid too many from same game)
            game_set = frozenset(leg["game_id"] for leg in combo_list)
            if len(game_set) < leg_count - 1:  # Allow max 2 legs from same game
                game_combo_key = tuple(sorted(game_set))
                if game_combo_key in used_game_combinations:
                    continue  # Skip duplicate game distribution
        
        # Check 100% requirement if enabled
        if require_100_pct:
            has_100 = any(
                leg.get("is_100_last_5") or leg.get("is_100_last_10") or leg.get("is_100_season")
                for leg in combo_list
            )
            if not has_100:
                continue
        
        # Calculate parlay metrics
        parlay_prob, parlay_ev = calculate_parlay_ev(combo_list)
        legs_odds = [leg["odds"] for leg in combo_list]
        american_odds, decimal_odds = calculate_parlay_odds(legs_odds)
        
        # Determine label
        label = determine_parlay_label(combo_list, parlay_prob, parlay_ev)
        
        # Skip SKIP-labeled parlays (negative edge or too risky)
        if label == "SKIP":
            continue
        
        # Calculate overall grade (average of leg grades)
        avg_grade_numeric = sum(grade_to_numeric(leg["grade"]) for leg in combo_list) / leg_count
        if avg_grade_numeric >= 3.5:
            overall_grade = "A"
        elif avg_grade_numeric >= 2.5:
            overall_grade = "B"
        elif avg_grade_numeric >= 1.5:
            overall_grade = "C"
        elif avg_grade_numeric >= 0.5:
            overall_grade = "D"
        else:
            overall_grade = "F"
        
        # Detect correlations
        correlations = detect_correlations(combo_list)
        correlation_risk, correlation_risk_label = calculate_correlation_risk_score(correlations)
        
        # Filter by correlation risk if blocking is enabled
        if block_correlated:
            max_risk_level = CORRELATION_RISK_ORDER.get(max_correlation_risk.upper(), 1)
            current_risk_level = CORRELATION_RISK_ORDER.get(correlation_risk_label, 0)
            if current_risk_level > max_risk_level:
                continue  # Skip this parlay - too correlated
        
        # Validate against all major platforms
        platform_validity = {
            "prizepicks": validate_parlay_for_platform(combo_list, "prizepicks"),
            "draftkings": validate_parlay_for_platform(combo_list, "draftkings"),
            "fanduel": validate_parlay_for_platform(combo_list, "fanduel"),
            "underdog": validate_parlay_for_platform(combo_list, "underdog"),
        }
        
        # Collect all violations
        all_violations = []
        valid_platforms = []
        for platform, validation in platform_validity.items():
            if validation["is_valid"]:
                valid_platforms.append(validation["platform_name"])
            else:
                all_violations.extend(validation["violations"])
        
        # Calculate variety score (higher for more diverse parlays)
        variety_score = 0
        if avoid_repetition:
            # Player diversity bonus
            variety_score += len(player_set) * 0.3
            # Stat diversity bonus
            stat_diversity = len(set(leg["stat_type"] for leg in combo_list))
            variety_score += stat_diversity * 0.2
            # Game distribution bonus
            variety_score += len(game_set) * 0.1
        
        parlay_data = {
            "legs": combo_list,
            "leg_count": leg_count,
            "total_odds": american_odds,
            "decimal_odds": round(decimal_odds, 2),
            "parlay_probability": round(parlay_prob, 4),
            "parlay_ev": round(parlay_ev, 4),
            "overall_grade": overall_grade,
            "label": label,
            "min_leg_prob": round(min(leg["win_prob"] for leg in combo_list), 4),
            "avg_edge": round(sum(leg["edge"] for leg in combo_list) / leg_count, 4),
            "correlations": correlations,
            "correlation_risk": correlation_risk,
            "correlation_risk_label": correlation_risk_label,
            "variety_score": round(variety_score, 2),
            # Platform validation info
            "platform_validity": platform_validity,
            "valid_platforms": valid_platforms,
            "platform_violations": all_violations,
            "is_universally_valid": len(all_violations) == 0,
        }
        
        parlays.append(parlay_data)
        
        # Mark combinations as used to avoid repetition
        if avoid_repetition:
            used_player_sets.add(player_set_key)
            used_stat_combinations.add(stat_combo)
            used_game_combinations.add(tuple(sorted(game_set)))
    
    logger.info(f"Evaluated {combo_count} combinations, found {len(parlays)} valid parlays")
    
    # Enhanced sorting: EV first, then variety score, then probability
    parlays.sort(key=lambda p: (
        p["parlay_ev"], 
        p["variety_score"], 
        p["parlay_probability"]
    ), reverse=True)
    
    # Apply final variety filter to top results
    if avoid_repetition and len(parlays) > max_results:
        # Take top results but ensure variety
        final_parlays = []
        used_players_final = set()
        used_stats_final = set()
        
        for parlay in parlays:
            if len(final_parlays) >= max_results:
                break
            
            # Check if this parlay adds variety
            parlay_players = set(leg["player_id"] for leg in parlay["legs"])
            parlay_stats = set(f"{leg['player_id']}_{leg['stat_type']}" for leg in parlay["legs"])
            
            # Allow some overlap but not too much
            player_overlap = len(used_players_final & parlay_players)
            stat_overlap = len(used_stats_final & parlay_stats)
            
            if player_overlap <= 1 and stat_overlap <= 1:  # Allow max 1 overlap each
                final_parlays.append(parlay)
                used_players_final.update(parlay_players)
                used_stats_final.update(parlay_stats)
        
        parlays = final_parlays
    
    return parlays[:max_results]


async def build_parlays(
    db: AsyncSession,
    sport_id: int,
    leg_count: int = 3,
    include_100_pct: bool = False,
    min_leg_grade: str = "C",
    max_results: int = 5,
    block_correlated: bool = True,
    max_correlation_risk: str = "MEDIUM",
) -> ParlayBuilderResponse:
    """
    Build optimized parlays for a sport.
    
    Args:
        db: Database session
        sport_id: Sport ID
        leg_count: Number of legs (2-15)
        include_100_pct: Require at least one 100% hit rate leg
        min_leg_grade: Minimum grade for each leg
        max_results: Number of parlays to return
        block_correlated: If True, filter out high-correlation parlays
        max_correlation_risk: Maximum correlation risk level allowed
    
    Returns:
        ParlayBuilderResponse with recommended parlays
    """
    try:
        # Clamp leg count
        leg_count = max(2, min(15, leg_count))
        
        # Get eligible legs with dynamic variety
        legs = await build_parlay_legs(db, sport_id, min_leg_grade, force_refresh=True)
        logger.info(f"Found {len(legs)} diverse legs for sport {sport_id}")
        
        # PERFORMANCE: Limit candidates to avoid combinatorial explosion
        # With N legs and k=3, combinations are C(N,k). 
        # N=50, k=3 -> 19,600 combos (fast)
        # N=150, k=3 -> 551,300 combos (slow!)
        # Take top 50 legs by EV for fast response (~20k combinations for k=3)
        MAX_CANDIDATES = 50
        if len(legs) > MAX_CANDIDATES:
            legs.sort(key=lambda x: x.get("ev", 0) or 0, reverse=True)
            legs = legs[:MAX_CANDIDATES]
            logger.info(f"Limited to top {MAX_CANDIDATES} legs by EV for performance")
        
        # Find best parlays with anti-repetition
        best_parlays = find_best_parlays(
            legs, 
            leg_count, 
            require_100_pct=include_100_pct, 
            max_results=max_results,
            block_correlated=block_correlated,
            max_correlation_risk=max_correlation_risk,
            avoid_repetition=True,  # Enable anti-repetition
        )
        
        # Convert to response format
        from app.schemas.public import CorrelationWarning
        
        parlay_recommendations = []
        for p in best_parlays:
            parlay_legs = [
                ParlayLeg(
                    pick_id=leg["pick_id"],
                    player_name=leg["player_name"],
                    player_id=leg.get("player_id"),
                    team_abbr=leg["team_abbr"],
                    game_id=leg.get("game_id"),
                    stat_type=leg["stat_type"],
                    line=leg["line"],
                    side=leg["side"],
                    odds=leg["odds"],
                    grade=leg["grade"],
                    win_prob=leg["win_prob"],
                    edge=leg["edge"],
                    hit_rate_5g=leg.get("hit_rate_last_5"),
                    is_100_last_5=leg.get("is_100_last_5", False),
                )
                for leg in p["legs"]
            ]
            
            # Convert correlation warnings to schema
            correlation_warnings = [
                CorrelationWarning(
                    type=c["type"],
                    severity=c["severity"],
                    legs=c["legs"],
                    message=c["message"],
                )
                for c in p.get("correlations", [])
            ]
            
            # Calculate Kelly sizing for this parlay
            kelly_data = calculate_parlay_kelly(
                parlay_prob=p["parlay_probability"],
                decimal_odds=p["decimal_odds"],
            )
            
            from app.schemas.public import KellySizing
            kelly_sizing = KellySizing(
                full_kelly_pct=kelly_data["full_kelly_pct"],
                kelly_fraction=kelly_data["kelly_fraction"],
                suggested_units=kelly_data["suggested_units"],
                edge_pct=kelly_data["edge_pct"],
                risk_level=kelly_data["risk_level"],
            )
            
            # Convert platform violations to schema
            from app.schemas.public import PlatformViolation
            platform_violations = [
                PlatformViolation(
                    type=v["type"],
                    severity=v["severity"],
                    message=v["message"],
                    player_id=v.get("player_id"),
                    game_id=v.get("game_id"),
                    count=v.get("count", 0),
                    max_allowed=v.get("max_allowed", 0),
                )
                for v in p.get("platform_violations", [])
            ]
            
            parlay_recommendations.append(
                ParlayRecommendation(
                    legs=parlay_legs,
                    leg_count=p["leg_count"],
                    total_odds=p["total_odds"],
                    decimal_odds=p["decimal_odds"],
                    parlay_probability=p["parlay_probability"],
                    parlay_ev=p["parlay_ev"],
                    overall_grade=p["overall_grade"],
                    label=p["label"],
                    min_leg_prob=p["min_leg_prob"],
                    avg_edge=p["avg_edge"],
                    correlations=correlation_warnings,
                    correlation_risk=p.get("correlation_risk", 0.0),
                    correlation_risk_label=p.get("correlation_risk_label", "LOW"),
                    kelly=kelly_sizing,
                    # Platform validation
                    valid_platforms=p.get("valid_platforms", []),
                    platform_violations=platform_violations,
                    is_universally_valid=p.get("is_universally_valid", True),
                )
            )
    
        return ParlayBuilderResponse(
            parlays=parlay_recommendations,
            total_candidates=len(legs),
            leg_count=leg_count,
            filters_applied={
                "min_leg_grade": min_leg_grade,
                "include_100_pct": include_100_pct,
                "sport_id": sport_id,
            },
        )
    except Exception as e:
        logger.error(f"Error building parlays for sport {sport_id}: {e}", exc_info=True)
        # Return empty response instead of crashing
        return ParlayBuilderResponse(
            parlays=[],
            total_candidates=0,
            leg_count=leg_count,
            filters_applied={
                "min_leg_grade": min_leg_grade,
                "include_100_pct": include_100_pct,
                "sport_id": sport_id,
            },
        )


# =============================================================================
# Auto-Generate Non-Overlapping Slips
# =============================================================================

async def auto_generate_slips(
    db: AsyncSession,
    sport_id: int,
    platform: str = "prizepicks",
    leg_count: int = 4,
    slip_count: int = 3,
    min_leg_ev: float = 0.03,
    min_confidence: float = 0.55,
    allow_correlation: bool = False,
) -> dict:
    """
    Auto-generate N optimal non-overlapping parlays.
    
    Each slip uses completely different legs (no shared picks between slips).
    This allows users to fire multiple slips without redundancy.
    
    Args:
        db: Database session
        sport_id: Sport ID
        platform: DFS platform (prizepicks, fliff, underdog, sportsbook)
        leg_count: Number of legs per slip
        slip_count: Number of slips to generate
        min_leg_ev: Minimum EV per leg (0.03 = 3%)
        min_confidence: Minimum model confidence per leg (0.55 = 55%)
        allow_correlation: If True, allow correlated legs within slips
    
    Returns:
        Dict with slips, stats, and quality assessment
    """
    from app.schemas.public import (
        ParlayLeg, ParlayRecommendation, CorrelationWarning, KellySizing
    )
    
    try:
        # Get eligible legs with stricter filters for auto-generate
        legs = await build_parlay_legs(db, sport_id, min_grade="D")  # Get all, filter below
        logger.info(f"[auto-gen] Found {len(legs)} total legs for sport {sport_id}")
        
        # Apply EV and confidence filters
        legs = [
            leg for leg in legs
            if (leg.get("ev") or 0) >= min_leg_ev
            and (leg.get("win_prob") or 0) >= min_confidence
        ]
        logger.info(f"[auto-gen] After EV/confidence filter: {len(legs)} legs")
        
        # Sort by EV descending - prioritize best edges
        legs.sort(key=lambda x: (x.get("ev") or 0, x.get("win_prob") or 0), reverse=True)
        
        # Track used pick IDs to ensure no overlap between slips
        used_pick_ids = set()
        generated_slips = []
        
        # Correlation settings based on platform and allow_correlation flag
        max_correlation_risk = "MEDIUM" if not allow_correlation else "CRITICAL"
        
        for slip_idx in range(slip_count):
            # Filter out already-used legs
            available_legs = [
                leg for leg in legs
                if leg["pick_id"] not in used_pick_ids
            ]
            
            if len(available_legs) < leg_count:
                logger.info(f"[auto-gen] Not enough unused legs for slip {slip_idx + 1}")
                break
            
            # Find best parlay from available legs
            best_parlays = find_best_parlays(
                available_legs,
                leg_count=leg_count,
                require_100_pct=False,
                max_results=1,  # Just get the best one
                block_correlated=not allow_correlation,
                max_correlation_risk=max_correlation_risk,
            )
            
            if not best_parlays:
                logger.info(f"[auto-gen] No valid parlay found for slip {slip_idx + 1}")
                break
            
            best = best_parlays[0]
            
            # Mark these legs as used
            for leg in best["legs"]:
                used_pick_ids.add(leg["pick_id"])
            
            # Convert to response format
            parlay_legs = [
                ParlayLeg(
                    pick_id=leg["pick_id"],
                    player_name=leg["player_name"],
                    player_id=leg.get("player_id"),
                    team_abbr=leg["team_abbr"],
                    game_id=leg.get("game_id"),
                    stat_type=leg["stat_type"],
                    line=leg["line"],
                    side=leg["side"],
                    odds=leg["odds"],
                    grade=leg["grade"],
                    win_prob=leg["win_prob"],
                    edge=leg["edge"],
                    hit_rate_5g=leg.get("hit_rate_last_5"),
                    is_100_last_5=leg.get("is_100_last_5", False),
                )
                for leg in best["legs"]
            ]
            
            # Correlation warnings
            correlation_warnings = [
                CorrelationWarning(
                    type=c["type"],
                    severity=c["severity"],
                    legs=c["legs"],
                    message=c["message"],
                )
                for c in best.get("correlations", [])
            ]
            
            # Kelly sizing
            kelly_data = calculate_parlay_kelly(
                parlay_prob=best["parlay_probability"],
                decimal_odds=best["decimal_odds"],
            )
            kelly_sizing = KellySizing(
                full_kelly_pct=kelly_data["full_kelly_pct"],
                kelly_fraction=kelly_data["kelly_fraction"],
                suggested_units=kelly_data["suggested_units"],
                edge_pct=kelly_data["edge_pct"],
                risk_level=kelly_data["risk_level"],
            )
            
            generated_slips.append(
                ParlayRecommendation(
                    legs=parlay_legs,
                    leg_count=best["leg_count"],
                    total_odds=best["total_odds"],
                    decimal_odds=best["decimal_odds"],
                    parlay_probability=best["parlay_probability"],
                    parlay_ev=best["parlay_ev"],
                    overall_grade=best["overall_grade"],
                    label=best["label"],
                    min_leg_prob=best["min_leg_prob"],
                    avg_edge=best["avg_edge"],
                    correlations=correlation_warnings,
                    correlation_risk=best.get("correlation_risk", 0.0),
                    correlation_risk_label=best.get("correlation_risk_label", "LOW"),
                    kelly=kelly_sizing,
                )
            )
        
        # Calculate summary stats
        if generated_slips:
            avg_ev = sum(s.parlay_ev for s in generated_slips) / len(generated_slips)
            avg_prob = sum(s.parlay_probability for s in generated_slips) / len(generated_slips)
            total_units = sum(s.kelly.suggested_units for s in generated_slips if s.kelly)
        else:
            avg_ev = 0.0
            avg_prob = 0.0
            total_units = 0.0
        
        # Determine slate quality
        total_candidates = len(legs)
        if len(generated_slips) >= slip_count and avg_ev >= 0.05:
            slate_quality = "STRONG"
        elif len(generated_slips) >= slip_count and avg_ev >= 0.02:
            slate_quality = "GOOD"
        elif len(generated_slips) > 0:
            slate_quality = "THIN"
        else:
            slate_quality = "PASS"
        
        return {
            "slips": generated_slips,
            "slip_count": len(generated_slips),
            "leg_count": leg_count,
            "platform": platform,
            "total_candidates": total_candidates,
            "filters": {
                "min_leg_ev": min_leg_ev,
                "min_confidence": min_confidence,
                "allow_correlation": allow_correlation,
                "sport_id": sport_id,
            },
            "avg_slip_ev": round(avg_ev, 4),
            "avg_slip_probability": round(avg_prob, 4),
            "total_suggested_units": round(total_units, 2),
            "slate_quality": slate_quality,
        }
    
    except Exception as e:
        logger.error(f"[auto-gen] Error generating slips: {e}", exc_info=True)
        return {
            "slips": [],
            "slip_count": 0,
            "leg_count": leg_count,
            "platform": platform,
            "total_candidates": 0,
            "filters": {
                "min_leg_ev": min_leg_ev,
                "min_confidence": min_confidence,
                "allow_correlation": allow_correlation,
                "sport_id": sport_id,
            },
            "avg_slip_ev": 0.0,
            "avg_slip_probability": 0.0,
            "total_suggested_units": 0.0,
            "slate_quality": "PASS",
        }


# =============================================================================
# 100% Hit Rate Props
# =============================================================================

async def get_100_percent_props(
    db: AsyncSession,
    sport_id: int,
    window: str = "season",  # "season", "last_10", "last_5"
    limit: int = 50,
    min_hit_rate: float = 0.70,  # Fallback threshold if no 100% props exist
) -> list[HundredPercentProp]:
    """
    Get props with high hit rates over specified window.
    
    First tries to find 100% hit rate props. If none found, falls back to
    showing props with hit_rate >= min_hit_rate, sorted by hit rate descending.
    
    Args:
        db: Database session
        sport_id: Sport ID
        window: Time window - "season", "last_10", "last_5"
        limit: Maximum results
        min_hit_rate: Minimum hit rate threshold for fallback (0.0-1.0, default 0.70 = 70%)
    
    Returns:
        List of HundredPercentProp sorted by hit rate (100% first, then by rate desc)
    """
    from datetime import datetime, timezone
    
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    logger.info(f"[100pct] Querying props for sport_id={sport_id}, window={window}, limit={limit}")
    
    # Query player prop picks (removed is_active and start_time filters)
    result = await db.execute(
        select(ModelPick, Player, Game, Team, Market)
        .join(Player, ModelPick.player_id == Player.id)
        .join(Game, ModelPick.game_id == Game.id)
        .outerjoin(Team, Player.team_id == Team.id)  # Outerjoin to include players without team
        .join(Market, ModelPick.market_id == Market.id)
        .where(
            and_(
                Game.sport_id == sport_id,
                # ModelPick.is_active == True,  # Disabled - show all picks
                ModelPick.player_id.isnot(None),
                # Game.start_time > now,  # Disabled - games stored at midnight UTC
            )
        )
    )
    rows = result.all()
    
    logger.info(f"[100pct] Query returned {len(rows)} total rows")
    
    perfect_props = []  # 100% hit rate props
    high_hit_props = []  # Props meeting min_hit_rate threshold
    all_props = []  # All props (fallback when no hit rate data)
    skipped_no_line = 0  # Counter for debugging
    
    # Pre-load all teams for opponent lookup (single query instead of 2 per pick)
    all_team_ids = set()
    for pick, player, game, team, market in rows:
        all_team_ids.add(game.home_team_id)
        all_team_ids.add(game.away_team_id)
    
    teams_result = await db.execute(
        select(Team).where(Team.id.in_(all_team_ids))
    )
    teams_by_id = {t.id: t for t in teams_result.scalars().all()}
    
    for pick, player, game, team, market in rows:
        # Skip picks with invalid line values
        if pick.line_value is None or pick.line_value == 0:
            skipped_no_line += 1
            continue
        
        stat_type = market.stat_type or market.market_type
        
        # Skip stat types hidden from the UI (low-volume, noisy markets)
        HIDDEN_STAT_TYPES = {
            # Basketball - low volume, noisy
            "STL", "BLK", "3PM",
            # Hockey - blocked shots (low volume)
            "BLK_SHOTS",
            # Football - interceptions (low volume, random)
            "INT",
            # Baseball - outs (low volume)
            "OUTS",
            # Tennis - double faults (low volume)
            "DF",
        }
        if stat_type in HIDDEN_STAT_TYPES:
            continue
        
        # Use pre-calculated hit rates from ModelPick instead of slow DB queries
        hr_5g = pick.hit_rate_5g or 0.0
        hr_10g = pick.hit_rate_10g or 0.0
        hr_30d = pick.hit_rate_30d or 0.0
        
        # Determine 100% flags (hit rate >= 0.999)
        is_100_5 = hr_5g >= 0.999
        is_100_10 = hr_10g >= 0.999
        is_100_season = hr_30d >= 0.999
        
        # Determine hit rate and 100% flag for selected window
        if window == "season":
            hit_rate = hr_30d
            is_100 = is_100_season
            games_count = 30 if hr_30d > 0 else 0
        elif window == "last_10":
            hit_rate = hr_10g
            is_100 = is_100_10
            games_count = 10 if hr_10g > 0 else 0
        else:  # last_5
            hit_rate = hr_5g
            is_100 = is_100_5
            games_count = 5 if hr_5g > 0 else 0
        
        # Get opponent team from pre-loaded cache
        home_team = teams_by_id.get(game.home_team_id)
        away_team = teams_by_id.get(game.away_team_id)
        
        # Determine opponent
        if player.team_id == game.home_team_id:
            opponent = away_team
        else:
            opponent = home_team
        
        # Serialize game_start_time to ISO string (or None if missing)
        game_start_iso = None
        if game.start_time:
            try:
                game_start_iso = game.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                game_start_iso = str(game.start_time)
        
        prop = HundredPercentProp(
            pick_id=pick.id,
            player_name=player.name,
            player_id=player.id,
            team=team.name if team else "Unknown",
            team_abbr=team.abbreviation if team else "UNK",
            opponent_team=opponent.name if opponent else "Unknown",
            opponent_abbr=opponent.abbreviation if opponent else None,
            stat_type=stat_type,
            line=pick.line_value,
            side=pick.side or "over",
            odds=pick.odds or -110,
            sportsbook=None,
            hit_rate_season=hr_30d if hr_30d > 0 else None,
            games_season=30 if hr_30d > 0 else 0,
            hit_rate_last_10=hr_10g if hr_10g > 0 else None,
            games_last_10=10 if hr_10g > 0 else 0,
            hit_rate_last_5=hr_5g if hr_5g > 0 else None,
            games_last_5=5 if hr_5g > 0 else 0,
            is_100_season=is_100_season,
            is_100_last_10=is_100_10,
            is_100_last_5=is_100_5,
            model_probability=pick.model_probability or 0.5,
            expected_value=pick.expected_value or 0.0,
            confidence_score=pick.confidence_score or 0.0,
            game_id=game.id,
            game_start_time=game_start_iso,
        )
        
        # Categorize: 100% props vs high hit rate vs all props
        if is_100:
            perfect_props.append((prop, hit_rate))
        elif hit_rate >= min_hit_rate:
            high_hit_props.append((prop, hit_rate))
        
        # Always add to all_props (used as fallback when no hit rate data)
        # Sort by EV instead of hit rate for fallback
        all_props.append((prop, pick.expected_value or 0, pick.confidence_score or 0))
    
    logger.info(f"[100pct] Categorized: {len(perfect_props)} perfect, {len(high_hit_props)} high-hit, {len(all_props)} total, {skipped_no_line} skipped (no line)")
    
    # Priority 1: Return 100% props if available
    if perfect_props:
        perfect_props.sort(key=lambda x: (x[1], x[0].expected_value or 0), reverse=True)
        result = [p[0] for p in perfect_props[:limit]]
        logger.info(f"[100pct] Returning {len(result)} perfect props")
        return result
    
    # Priority 2: Return high hit rate props if available
    if high_hit_props:
        high_hit_props.sort(key=lambda x: (x[1], x[0].expected_value or 0), reverse=True)
        result = [p[0] for p in high_hit_props[:limit]]
        logger.info(f"[100pct] Returning {len(result)} high-hit props (no perfect found)")
        return result
    
    # Priority 3 (FALLBACK): Return best picks by EV/confidence when no hit rate data
    # This ensures the UI always shows something instead of spinning forever
    all_props.sort(key=lambda x: (x[1], x[2]), reverse=True)  # Sort by EV, then confidence
    result = [p[0] for p in all_props[:limit]]
    logger.info(f"[100pct] Returning {len(result)} all props as fallback (no hit rate data)")
    return result


# =============================================================================
# Alt-Line Explorer
# =============================================================================

def prob_to_fair_american_odds(prob: float) -> int:
    """Convert probability to fair American odds (no vig)."""
    if prob >= 1.0:
        return -10000
    if prob <= 0.0:
        return 10000
    if prob >= 0.5:
        return int(round(-100 * prob / (1 - prob)))
    else:
        return int(round(100 * (1 - prob) / prob))


def calculate_alt_line_probs(
    projection: float,
    std_dev: float,
    line: float,
) -> tuple[float, float]:
    """
    Calculate over/under probabilities for a line given projection and std dev.
    
    Uses normal distribution approximation.
    
    Args:
        projection: Model's expected value
        std_dev: Standard deviation of the stat
        line: The line to evaluate
    
    Returns:
        Tuple of (over_prob, under_prob)
    """
    import math
    
    if std_dev <= 0:
        # No variance - binary outcome
        if projection > line:
            return 0.95, 0.05
        elif projection < line:
            return 0.05, 0.95
        else:
            return 0.5, 0.5
    
    # Z-score
    z = (line - projection) / std_dev
    
    # CDF approximation (standard normal)
    # P(X < line) = CDF(z)
    def normal_cdf(z: float) -> float:
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))
    
    under_prob = normal_cdf(z)
    over_prob = 1 - under_prob
    
    # Clamp to reasonable bounds
    over_prob = max(0.01, min(0.99, over_prob))
    under_prob = max(0.01, min(0.99, under_prob))
    
    return round(over_prob, 4), round(under_prob, 4)


def calculate_ev_for_odds(prob: float, american_odds: int) -> float:
    """Calculate EV for given probability and odds."""
    if american_odds >= 100:
        profit = american_odds / 100
    else:
        profit = 100 / abs(american_odds)
    
    ev = (prob * profit) - ((1 - prob) * 1)
    return round(ev, 4)


async def get_alt_lines_for_prop(
    db: AsyncSession,
    player_id: int,
    stat_type: str,
    game_id: int,
    main_line: float,
    main_odds: int,
    model_prob: float,
) -> list[dict]:
    """
    Generate alternate lines for a player prop.
    
    Creates a ladder of lines around the main line with calculated probabilities.
    
    Args:
        db: Database session
        player_id: Player ID
        stat_type: Stat type (PTS, REB, etc.)
        game_id: Game ID
        main_line: The primary market line
        main_odds: The odds for the main line
        model_prob: Model's probability for the main line
    
    Returns:
        List of alt line dictionaries
    """
    from app.models import Line, Market
    
    # Estimate standard deviation from model probability
    # If model says 60% over at line 24.5, we can back out an implied projection
    # For simplicity, use a fixed std dev based on stat type
    stat_std_devs = {
        "PTS": 6.0,
        "player_points": 6.0,
        "REB": 3.0,
        "player_rebounds": 3.0,
        "AST": 2.5,
        "player_assists": 2.5,
        "3PM": 1.5,
        "player_threes": 1.5,
        "PRA": 8.0,
        "player_points_rebounds_assists": 8.0,
    }
    
    std_dev = stat_std_devs.get(stat_type, 5.0)
    
    # Estimate projection from main line and model prob
    # If over_prob > 0.5, projection > line
    import math
    
    def inv_normal_cdf(p: float) -> float:
        """Inverse CDF approximation."""
        if p <= 0.01:
            return -2.33
        if p >= 0.99:
            return 2.33
        # Approximation
        a = 8 * (math.pi - 3) / (3 * math.pi * (4 - math.pi))
        x = 2 * p - 1
        ln_term = math.log(1 - x * x)
        return math.copysign(
            math.sqrt(
                math.sqrt((2 / (math.pi * a) + ln_term / 2) ** 2 - ln_term / a)
                - (2 / (math.pi * a) + ln_term / 2)
            ),
            x,
        ) * math.sqrt(2)
    
    # If model_prob is for "over", then P(X > line) = model_prob
    # P(X < line) = 1 - model_prob
    # z = (line - projection) / std_dev
    # CDF(z) = 1 - model_prob
    z = inv_normal_cdf(1 - model_prob)
    projection = main_line - z * std_dev
    projection = round(projection, 1)
    
    # Generate ladder of lines
    # Points: 0.5 increments from -3 to +3 around main line
    # Rebounds/Assists: 0.5 increments from -2 to +2
    if "point" in stat_type.lower() or stat_type == "PTS":
        offsets = [-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]
    else:
        offsets = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]
    
    alt_lines = []
    
    for offset in offsets:
        line = main_line + offset
        if line <= 0:
            continue
        
        over_prob, under_prob = calculate_alt_line_probs(projection, std_dev, line)
        
        # Calculate fair odds
        over_fair = prob_to_fair_american_odds(over_prob)
        under_fair = prob_to_fair_american_odds(under_prob)
        
        # Estimate market odds (add ~5% vig to fair odds)
        # For simplicity, use -110/-110 as typical market odds for main line
        # and adjust based on probability
        if over_prob >= 0.5:
            over_odds = max(-500, min(-105, int(-100 * over_prob / (1 - over_prob) * 1.05)))
            under_odds = max(100, min(500, int(100 * (1 - under_prob) / under_prob / 1.05)))
        else:
            over_odds = max(100, min(500, int(100 * (1 - over_prob) / over_prob / 1.05)))
            under_odds = max(-500, min(-105, int(-100 * under_prob / (1 - under_prob) * 1.05)))
        
        # Calculate EV
        over_ev = calculate_ev_for_odds(over_prob, over_odds)
        under_ev = calculate_ev_for_odds(under_prob, under_odds)
        
        alt_lines.append({
            "line": line,
            "over_odds": over_odds,
            "under_odds": under_odds,
            "over_prob": over_prob,
            "under_prob": under_prob,
            "over_ev": over_ev,
            "under_ev": under_ev,
            "over_fair_odds": over_fair,
            "under_fair_odds": under_fair,
            "is_main_line": abs(offset) < 0.1,
        })
    
    return alt_lines, projection, std_dev


async def explore_alt_lines(
    db: AsyncSession,
    pick_id: int,
) -> dict:
    """
    Get full alt-line exploration for a specific pick.
    
    Args:
        db: Database session
        pick_id: ModelPick ID to explore
    
    Returns:
        AltLineExplorerResponse data
    """
    from app.models import ModelPick, Player, Game, Team, Market
    from app.schemas.public import AltLine, AltLineExplorerResponse
    
    # Get the pick
    pick = await db.get(ModelPick, pick_id)
    if not pick:
        raise ValueError(f"Pick {pick_id} not found")
    
    if not pick.player_id:
        raise ValueError(f"Pick {pick_id} is not a player prop")
    
    # Get related data
    player = await db.get(Player, pick.player_id)
    game = await db.get(Game, pick.game_id)
    team = await db.get(Team, player.team_id) if player and player.team_id else None
    
    market_result = await db.execute(
        select(Market).where(Market.id == pick.market_id)
    )
    market = market_result.scalar_one_or_none()
    
    stat_type = market.stat_type or market.market_type if market else "unknown"
    
    # Get opponent
    if game:
        if player and player.team_id == game.home_team_id:
            opponent_result = await db.execute(
                select(Team).where(Team.id == game.away_team_id)
            )
        else:
            opponent_result = await db.execute(
                select(Team).where(Team.id == game.home_team_id)
            )
        opponent = opponent_result.scalar_one_or_none()
    else:
        opponent = None
    
    # Generate alt lines
    alt_lines_data, projection, std_dev = await get_alt_lines_for_prop(
        db,
        player_id=pick.player_id,
        stat_type=stat_type,
        game_id=pick.game_id,
        main_line=pick.line_value if pick.line_value is not None else 0,
        main_odds=int(pick.odds),
        model_prob=pick.model_probability,
    )
    
    # Convert to schema
    alt_lines = [
        AltLine(
            line=al["line"],
            over_odds=al["over_odds"],
            under_odds=al["under_odds"],
            over_prob=al["over_prob"],
            under_prob=al["under_prob"],
            over_ev=al["over_ev"],
            under_ev=al["under_ev"],
            over_fair_odds=al["over_fair_odds"],
            under_fair_odds=al["under_fair_odds"],
            is_main_line=al["is_main_line"],
        )
        for al in alt_lines_data
    ]
    
    # Find best over/under lines
    best_over = max(alt_lines, key=lambda x: x.over_ev or -999) if alt_lines else None
    best_under = max(alt_lines, key=lambda x: x.under_ev or -999) if alt_lines else None
    
    # Get sport_id from the game for correct season boundaries
    sport_id = game.sport_id if game else 30  # Default to NBA if no game
    
    # Get hit rate - use sport-specific season start
    hr_data = await get_hit_rate_data(
        db, pick.player_id, stat_type, pick.line_value if pick.line_value is not None else 0, pick.side, sport_id=sport_id
    )
    
    # Get season average using sport-specific season start
    from datetime import datetime
    from app.services.season_helper import get_season_start_for_sport_id
    season_start = get_season_start_for_sport_id(sport_id)
    
    result = await db.execute(
        select(func.avg(PlayerGameStats.value))
        .where(
            and_(
                PlayerGameStats.player_id == pick.player_id,
                PlayerGameStats.stat_type == stat_type,
                PlayerGameStats.created_at >= season_start,
            )
        )
    )
    season_avg = result.scalar()
    
    return AltLineExplorerResponse(
        player_name=player.name if player else "Unknown",
        player_id=pick.player_id,
        team_abbr=team.abbreviation if team else None,
        stat_type=stat_type,
        game_id=pick.game_id,
        opponent_abbr=opponent.abbreviation if opponent else None,
        game_start_time=game.start_time if game else datetime.now(),
        model_projection=projection,
        projection_std=std_dev,
        alt_lines=alt_lines,
        best_over_line=best_over if best_over and (best_over.over_ev or 0) > 0 else None,
        best_under_line=best_under if best_under and (best_under.under_ev or 0) > 0 else None,
        hit_rate_5g=hr_data.get("hit_rate_last_5"),
        season_avg=round(season_avg, 1) if season_avg else None,
    )


# Need func for SQL
from sqlalchemy import func
