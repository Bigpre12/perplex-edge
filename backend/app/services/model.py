"""Model service for computing probabilities and generating picks."""

import logging
import math
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from zoneinfo import ZoneInfo

# US Eastern timezone for consistent date handling
EASTERN_TZ = ZoneInfo("America/New_York")

from sqlalchemy import select, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Sport, Game, Line, Market, Player, Team,
    PlayerGameStats, Injury, ModelPick,
)
from app.models.injury import EXCLUDED_INJURY_STATUSES
from app.core.config import (
    get_games_window,
    get_ev_threshold,
    get_min_model_probability,
    get_sport_config,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Sport Key Mappings
# =============================================================================

SPORT_KEY_TO_LEAGUE = {
    "basketball_nba": "NBA",
    "americanfootball_nfl": "NFL",
    "baseball_mlb": "MLB",
    "icehockey_nhl": "NHL",
    "basketball_ncaab": "NCAAB",
    "americanfootball_ncaaf": "NCAAF",
    "tennis_atp": "ATP",
    "tennis_wta": "WTA",
}


# =============================================================================
# Probability Conversion Functions
# =============================================================================

def american_to_implied_prob(odds: int) -> float:
    """
    Convert American odds to implied probability.
    
    Args:
        odds: American odds (e.g., -110, +150)
    
    Returns:
        Implied probability between 0 and 1
    
    Examples:
        -110 -> 0.5238 (52.38%)
        +150 -> 0.4000 (40.00%)
        -200 -> 0.6667 (66.67%)
        +200 -> 0.3333 (33.33%)
    """
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)


def implied_prob_to_decimal(imp: float) -> float:
    """
    Convert implied probability to decimal odds.
    
    Args:
        imp: Implied probability between 0 and 1
    
    Returns:
        Decimal odds (e.g., 2.0 for even money)
    
    Examples:
        0.50 -> 2.00
        0.25 -> 4.00
        0.80 -> 1.25
    """
    if imp <= 0 or imp >= 1:
        raise ValueError(f"Implied probability must be between 0 and 1, got {imp}")
    return 1 / imp


def compute_ev(model_prob: float, odds: int) -> float:
    """
    Compute expected value for a bet.
    
    EV = (probability of winning * net profit) - (probability of losing * stake)
    
    For a $1 stake:
    - If odds are negative (e.g., -110): profit = 100/110 = 0.909
    - If odds are positive (e.g., +150): profit = 150/100 = 1.5
    
    Args:
        model_prob: Model's predicted probability of winning (0-1)
        odds: American odds
    
    Returns:
        Expected value as a decimal (0.05 = 5% EV)
    
    Examples:
        model_prob=0.55, odds=-110 -> EV = 0.55*0.909 - 0.45*1 = 0.05 (5% EV)
    """
    if odds < 0:
        profit = 100 / abs(odds)
    else:
        profit = odds / 100
    
    ev = (model_prob * profit) - ((1 - model_prob) * 1)
    return round(ev, 4)


# =============================================================================
# Statistical Helper Functions
# =============================================================================

def compute_hit_rate(values: list[float], line: float, side: str = "over") -> float:
    """
    Compute hit rate for a list of values against a line.
    
    Args:
        values: List of stat values
        line: The betting line
        side: "over" or "under"
    
    Returns:
        Hit rate between 0 and 1
    """
    if not values:
        return 0.5  # Default to 50% if no data
    
    if side.lower() == "over":
        hits = sum(1 for v in values if v > line)
    else:
        hits = sum(1 for v in values if v < line)
    
    return hits / len(values)


def compute_variance(values: list[float]) -> float:
    """Compute variance of a list of values."""
    if len(values) < 2:
        return 0.0
    
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return variance


def calculate_model_confidence(
    hit_rate_10g: float,
    hit_rate_30d: float,
    sample_size_10g: int,
    sample_size_30d: int,
    variance: float,
    edge: float,
) -> float:
    """
    Calculate overall confidence score for a model prediction.
    
    Factors:
    - Sample size: More games = higher confidence
    - Consistency: Lower variance = higher confidence
    - Agreement: Similar hit rates across timeframes = higher confidence
    
    Args:
        hit_rate_10g: Hit rate over last 10 games
        hit_rate_30d: Hit rate over last 30 days
        sample_size_10g: Number of games in 10-game sample
        sample_size_30d: Number of games in 30-day sample
        variance: Variance in the stat values
        edge: Model edge over implied probability
    
    Returns:
        Confidence score between 0 and 1
    """
    # Sample size score (0-1)
    # Full confidence at 20+ total games
    sample_score = min(1.0, (sample_size_10g + sample_size_30d) / 20)
    
    # Consistency score based on variance
    # Normalize variance - assume typical variance of ~50 for points
    normalized_variance = min(variance / 100, 0.5)
    consistency_score = 1.0 - normalized_variance
    
    # Agreement between timeframes
    agreement_score = 1.0 - abs(hit_rate_10g - hit_rate_30d)
    
    # Combine scores with weights
    confidence = (
        sample_score * 0.3 +
        consistency_score * 0.4 +
        agreement_score * 0.3
    )
    
    return round(min(1.0, max(0.0, confidence)), 4)


# =============================================================================
# Player Stats Query Functions
# =============================================================================

async def get_player_recent_stats(
    db: AsyncSession,
    player_id: int,
    stat_type: str,
    n_games: Optional[int] = None,
    sport_key: str = "basketball_nba",
) -> list[tuple[float, Optional[float]]]:
    """
    Get player's recent stats for a specific stat type.
    
    Args:
        db: Database session
        player_id: Player ID
        stat_type: Stat type (e.g., "PTS", "REB")
        n_games: Number of recent games (default from config)
        sport_key: Sport identifier for config lookup
    
    Returns:
        List of (value, minutes) tuples, most recent first
    """
    # Use config-based default if not specified
    if n_games is None:
        n_games = get_games_window(sport_key, "medium")
    
    result = await db.execute(
        select(PlayerGameStats.value, PlayerGameStats.minutes)
        .where(
            and_(
                PlayerGameStats.player_id == player_id,
                PlayerGameStats.stat_type == stat_type,
            )
        )
        .order_by(PlayerGameStats.created_at.desc())
        .limit(n_games)
    )
    return list(result.all())


async def get_player_stats_last_n_days(
    db: AsyncSession,
    player_id: int,
    stat_type: str,
    days: int = 30,
    sport_id: int = 30,  # Default to NBA, but should be passed for other sports
) -> list[tuple[float, Optional[float]]]:
    """
    Get player's stats from the last N days, respecting season boundaries.
    
    The cutoff will be the later of:
    - N days ago
    - Season start date for the sport
    
    This ensures we don't accidentally include stats from the previous season.
    
    Args:
        db: Database session
        player_id: Player ID
        stat_type: Stat type
        days: Number of days to look back
        sport_id: Sport ID (30=NBA, 31=NFL, 32=NCAAB) - determines season start
    
    Returns:
        List of (value, minutes) tuples
    """
    from app.services.season_helper import get_season_start_for_sport_id
    
    # Get season start for this sport
    season_start = get_season_start_for_sport_id(sport_id).replace(tzinfo=None)
    
    # Calculate N days ago cutoff
    days_cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).replace(tzinfo=None)
    
    # Use the later of the two (don't go before season start)
    cutoff = max(season_start, days_cutoff)
    
    result = await db.execute(
        select(PlayerGameStats.value, PlayerGameStats.minutes)
        .where(
            and_(
                PlayerGameStats.player_id == player_id,
                PlayerGameStats.stat_type == stat_type,
                PlayerGameStats.created_at >= cutoff,
            )
        )
        .order_by(PlayerGameStats.created_at.desc())
    )
    return list(result.all())


async def get_injured_teammates(
    db: AsyncSession,
    player_id: int,
    sport_id: int,
) -> list[dict[str, Any]]:
    """
    Get injured teammates for a player.
    
    Returns list of injured players on the same team with their status.
    """
    # Get player's team
    result = await db.execute(
        select(Player).where(Player.id == player_id)
    )
    player = result.scalar_one_or_none()
    
    if not player or not player.team_id:
        return []
    
    # Get injured teammates
    result = await db.execute(
        select(Injury, Player)
        .join(Player, Injury.player_id == Player.id)
        .where(
            and_(
                Player.team_id == player.team_id,
                Player.id != player_id,
                Injury.status.in_(EXCLUDED_INJURY_STATUSES),
            )
        )
    )
    
    injured = []
    for injury, teammate in result.all():
        injured.append({
            "player_id": teammate.id,
            "player_name": teammate.name,
            "position": teammate.position,
            "status": injury.status,
            "injury_detail": injury.status_detail,
        })
    
    return injured


# =============================================================================
# Main Model Probability Function
# =============================================================================

async def compute_player_prop_model_probabilities(
    db: AsyncSession,
    game_id: int,
    player_id: int,
    market_id: int,
    side: str,
    line_value: float,
) -> dict[str, Any]:
    """
    Compute model probabilities for a player prop bet.
    
    Algorithm:
    1. Get market's stat_type
    2. Query player's last 10 games and last 30 days stats
    3. Compute hit rates for both timeframes
    4. Calculate base model probability (weighted average)
    5. Apply adjustments for minutes and injuries
    6. Calculate confidence score
    
    Args:
        db: Database session
        game_id: Game ID
        player_id: Player ID
        market_id: Market ID (to get stat_type)
        side: "over" or "under"
        line_value: The betting line value
    
    Returns:
        Dictionary with:
        - model_prob: Final model probability
        - hit_rate_10g: Hit rate over last 10 games
        - hit_rate_30d: Hit rate over last 30 days
        - confidence: Confidence score (0-1)
        - factors: Dictionary of adjustment factors for transparency
    """
    factors = {}
    
    # Get market to find stat_type
    result = await db.execute(
        select(Market).where(Market.id == market_id)
    )
    market = result.scalar_one_or_none()
    
    if not market or not market.stat_type:
        return {
            "model_prob": 0.5,
            "hit_rate_10g": None,
            "hit_rate_30d": None,
            "confidence": 0.0,
            "factors": {"error": "Market or stat_type not found"},
        }
    
    stat_type = market.stat_type
    factors["stat_type"] = stat_type
    
    # Get player info
    result = await db.execute(
        select(Player).where(Player.id == player_id)
    )
    player = result.scalar_one_or_none()
    
    if not player:
        return {
            "model_prob": 0.5,
            "hit_rate_10g": None,
            "hit_rate_30d": None,
            "confidence": 0.0,
            "factors": {"error": "Player not found"},
        }
    
    # Get game to determine sport_id for season boundaries
    game_result = await db.execute(
        select(Game).where(Game.id == game_id)
    )
    game = game_result.scalar_one_or_none()
    sport_id = game.sport_id if game else 30  # Default to NBA if no game
    
    # Get last 10 games stats
    stats_10g = await get_player_recent_stats(db, player_id, stat_type, n_games=10)
    values_10g = [s[0] for s in stats_10g]
    minutes_10g = [s[1] for s in stats_10g if s[1] is not None]
    
    # Get last 30 days stats (with season boundary awareness)
    stats_30d = await get_player_stats_last_n_days(db, player_id, stat_type, days=30, sport_id=sport_id)
    values_30d = [s[0] for s in stats_30d]
    minutes_30d = [s[1] for s in stats_30d if s[1] is not None]
    
    # Compute hit rates
    hit_rate_10g = compute_hit_rate(values_10g, line_value, side) if values_10g else None
    hit_rate_30d = compute_hit_rate(values_30d, line_value, side) if values_30d else None
    
    factors["sample_size_10g"] = len(values_10g)
    factors["sample_size_30d"] = len(values_30d)
    factors["avg_value_10g"] = sum(values_10g) / len(values_10g) if values_10g else None
    factors["avg_value_30d"] = sum(values_30d) / len(values_30d) if values_30d else None
    
    # Handle cases with limited data
    if hit_rate_10g is None and hit_rate_30d is None:
        return {
            "model_prob": 0.5,
            "hit_rate_10g": None,
            "hit_rate_30d": None,
            "confidence": 0.0,
            "factors": {"error": "No historical data available"},
        }
    
    # Base model probability (weighted average)
    if hit_rate_10g is not None and hit_rate_30d is not None:
        base_prob = 0.6 * hit_rate_10g + 0.4 * hit_rate_30d
    elif hit_rate_10g is not None:
        base_prob = hit_rate_10g
    else:
        base_prob = hit_rate_30d
    
    factors["base_prob"] = round(base_prob, 4)
    
    # ==========================================================================
    # Adjustments
    # ==========================================================================
    
    adjustment = 0.0
    
    # 1. Minutes projection adjustment
    if minutes_10g and minutes_30d:
        avg_min_recent = sum(minutes_10g) / len(minutes_10g)
        avg_min_season = sum(minutes_30d) / len(minutes_30d)
        
        if avg_min_season > 0:
            minutes_ratio = avg_min_recent / avg_min_season
            
            # If playing more minutes recently, slight boost
            if minutes_ratio > 1.05:
                minutes_adj = min(0.03, (minutes_ratio - 1) * 0.1)
                if side.lower() == "over":
                    adjustment += minutes_adj
                else:
                    adjustment -= minutes_adj
                factors["minutes_adjustment"] = round(minutes_adj, 4)
            # If playing fewer minutes, slight decrease
            elif minutes_ratio < 0.95:
                minutes_adj = min(0.03, (1 - minutes_ratio) * 0.1)
                if side.lower() == "over":
                    adjustment -= minutes_adj
                else:
                    adjustment += minutes_adj
                factors["minutes_adjustment"] = round(-minutes_adj, 4)
    
    # 2. Injury context adjustment
    injured_teammates = await get_injured_teammates(db, player_id, player.sport_id)
    
    if injured_teammates:
        factors["injured_teammates"] = len(injured_teammates)
        
        # Simple heuristic: if teammates are out, more opportunity for stats
        # This is a simplified model - in production would use usage rates
        injury_boost = min(0.02 * len(injured_teammates), 0.05)
        
        # Scoring stats (PTS, 3PM) get boost when teammates out
        scoring_stats = ["PTS", "3PM", "FGM", "FGA", "FTM", "FTA"]
        # Assist stats may decrease if scorers are out
        assist_stats = ["AST"]
        # Rebounding may increase
        rebound_stats = ["REB", "OREB", "DREB"]
        
        if stat_type in scoring_stats:
            if side.lower() == "over":
                adjustment += injury_boost
            else:
                adjustment -= injury_boost
            factors["injury_adjustment"] = round(injury_boost, 4)
        elif stat_type in rebound_stats:
            if side.lower() == "over":
                adjustment += injury_boost * 0.5
            else:
                adjustment -= injury_boost * 0.5
            factors["injury_adjustment"] = round(injury_boost * 0.5, 4)
        elif stat_type in assist_stats:
            # Assists may decrease if good scorers are out
            if side.lower() == "over":
                adjustment -= injury_boost * 0.3
            else:
                adjustment += injury_boost * 0.3
            factors["injury_adjustment"] = round(-injury_boost * 0.3, 4)
    
    factors["total_adjustment"] = round(adjustment, 4)
    
    # Apply adjustment to base probability
    model_prob = base_prob + adjustment
    model_prob = max(0.05, min(0.95, model_prob))  # Clamp to reasonable range
    
    # ==========================================================================
    # Calculate confidence
    # ==========================================================================
    
    variance = compute_variance(values_10g) if values_10g else 0.0
    
    confidence = calculate_model_confidence(
        hit_rate_10g=hit_rate_10g or 0.5,
        hit_rate_30d=hit_rate_30d or 0.5,
        sample_size_10g=len(values_10g),
        sample_size_30d=len(values_30d),
        variance=variance,
        edge=0.0,  # Will be calculated separately
    )
    
    return {
        "model_prob": round(model_prob, 4),
        "hit_rate_10g": round(hit_rate_10g, 4) if hit_rate_10g is not None else None,
        "hit_rate_30d": round(hit_rate_30d, 4) if hit_rate_30d is not None else None,
        "confidence": confidence,
        "factors": factors,
    }


# =============================================================================
# Game Line Model (Simplified)
# =============================================================================

async def compute_game_line_model_probability(
    db: AsyncSession,
    game_id: int,
    market_id: int,
    side: str,
    line_value: Optional[float],
    odds: int,
) -> dict[str, Any]:
    """
    Compute model probability for game lines (spread, total, moneyline).
    
    This is a simplified model - for game lines, we primarily use the market
    efficiency assumption with small random variance as a placeholder.
    
    In production, this would incorporate:
    - Team strength ratings
    - Recent performance trends
    - Home/away splits
    - Rest days
    - Historical H2H records
    
    Args:
        db: Database session
        game_id: Game ID
        market_id: Market ID
        side: "home", "away", "over", "under"
        line_value: The line value (spread or total)
        odds: American odds
    
    Returns:
        Dictionary with model probability and confidence
    """
    # For game lines, use implied probability as baseline
    implied_prob = american_to_implied_prob(odds)
    
    # Add small variance (placeholder for actual model)
    # In production, this would be replaced with actual model predictions
    import random
    random.seed(hash(f"{game_id}_{market_id}_{side}"))
    variance = random.gauss(0, 0.03)
    
    model_prob = implied_prob + variance
    model_prob = max(0.05, min(0.95, model_prob))
    
    # Lower confidence for game lines (less edge available)
    confidence = 0.4
    
    return {
        "model_prob": round(model_prob, 4),
        "hit_rate_10g": None,
        "hit_rate_30d": None,
        "confidence": confidence,
        "factors": {
            "implied_prob": round(implied_prob, 4),
            "variance": round(variance, 4),
            "model_type": "game_line_placeholder",
        },
    }


# =============================================================================
# Main Picks Generation Function
# =============================================================================

async def generate_model_picks_for_today(
    db: AsyncSession,
    sport_key: str,
    ev_threshold: float = 0.05,
    confidence_threshold: float = 0.5,
    use_stubs: bool = False,
) -> dict[str, Any]:
    """
    Generate model picks for today's games.
    
    Algorithm:
    1. Get today's games for the sport
    2. Get all current lines for those games
    3. For each line:
       - Compute implied probability from odds
       - Compute model probability (player prop or game line model)
       - Compute expected value
       - If EV >= threshold and confidence >= threshold, create/update pick
    
    Args:
        db: Database session
        sport_key: Sport identifier (e.g., 'basketball_nba')
        ev_threshold: Minimum EV to create a pick (default 5%)
        confidence_threshold: Minimum confidence to create a pick (default 50%)
        use_stubs: Placeholder for stub mode (currently unused)
    
    Returns:
        Dictionary with generation statistics
    """
    stats = {
        "sport": None,
        "games_processed": 0,
        "lines_evaluated": 0,
        "picks_created": 0,
        "picks_updated": 0,
        "picks_skipped_ev": 0,
        "picks_skipped_confidence": 0,
        "picks_deactivated": 0,
        "errors": [],
    }
    
    try:
        # Get sport
        league_code = SPORT_KEY_TO_LEAGUE.get(sport_key, sport_key.upper())
        result = await db.execute(
            select(Sport).where(Sport.league_code == league_code)
        )
        sport = result.scalar_one_or_none()
        
        if not sport:
            logger.warning(f"Sport not found: {league_code}")
            return {"error": f"Sport not found: {league_code}"}
        
        stats["sport"] = sport.league_code
        
        # Get today's games using US Eastern time (handles DST)
        # This ensures we process today's US schedule even after midnight UTC
        now_et = datetime.now(EASTERN_TZ)
        today_start_et = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_start_et = today_start_et + timedelta(days=1)
        
        # Convert to UTC naive datetimes for PostgreSQL
        today = today_start_et.astimezone(timezone.utc).replace(tzinfo=None)
        tomorrow = tomorrow_start_et.astimezone(timezone.utc).replace(tzinfo=None)
        
        result = await db.execute(
            select(Game)
            .where(
                and_(
                    Game.sport_id == sport.id,
                    Game.start_time >= today,
                    Game.start_time < tomorrow,
                    Game.status == "scheduled",
                )
            )
        )
        games = list(result.scalars().all())
        
        if not games:
            logger.info(f"No games found for {sport_key} today")
            await db.commit()
            return stats
        
        logger.info(f"Processing {len(games)} games for {sport_key}")
        game_ids = [g.id for g in games]
        
        # Only deactivate picks for games being processed (not ALL picks)
        deactivated = await db.execute(
            update(ModelPick)
            .where(
                and_(
                    ModelPick.sport_id == sport.id,
                    ModelPick.game_id.in_(game_ids),
                    ModelPick.is_active == True,
                )
            )
            .values(is_active=False)
        )
        stats["picks_deactivated"] = deactivated.rowcount
        
        # Get all current lines for today's games
        result = await db.execute(
            select(Line)
            .options(
                selectinload(Line.market),
                selectinload(Line.player),
            )
            .where(
                and_(
                    Line.game_id.in_(game_ids),
                    Line.is_current == True,
                )
            )
        )
        lines = list(result.scalars().all())
        
        logger.info(f"Evaluating {len(lines)} lines")
        
        # Track processed combinations to avoid duplicates
        processed = set()
        
        for line in lines:
            try:
                # Create unique key
                key = (line.game_id, line.market_id, line.player_id, line.side)
                if key in processed:
                    continue
                processed.add(key)
                
                stats["lines_evaluated"] += 1
                
                # Compute implied probability
                implied_prob = american_to_implied_prob(line.odds)
                
                # Compute model probability
                if line.player_id:
                    # Player prop
                    model_result = await compute_player_prop_model_probabilities(
                        db,
                        game_id=line.game_id,
                        player_id=line.player_id,
                        market_id=line.market_id,
                        side=line.side,
                        line_value=line.line_value or 0,
                    )
                else:
                    # Game line
                    model_result = await compute_game_line_model_probability(
                        db,
                        game_id=line.game_id,
                        market_id=line.market_id,
                        side=line.side,
                        line_value=line.line_value,
                        odds=int(line.odds),
                    )
                
                model_prob = model_result["model_prob"]
                confidence = model_result["confidence"]
                hit_rate_10g = model_result.get("hit_rate_10g")
                hit_rate_30d = model_result.get("hit_rate_30d")
                
                # Compute EV
                ev = compute_ev(model_prob, int(line.odds))
                
                # Check thresholds
                if ev < ev_threshold:
                    stats["picks_skipped_ev"] += 1
                    continue
                
                if confidence < confidence_threshold:
                    stats["picks_skipped_confidence"] += 1
                    continue
                
                # Check for existing pick to update
                # Use scalars().first() instead of scalar_one_or_none() to handle
                # potential duplicate picks in the database gracefully
                result = await db.execute(
                    select(ModelPick).where(
                        and_(
                            ModelPick.game_id == line.game_id,
                            ModelPick.market_id == line.market_id,
                            ModelPick.player_id == line.player_id,
                            ModelPick.side == line.side,
                        )
                    )
                )
                existing_pick = result.scalars().first()
                
                if existing_pick:
                    # Update existing pick
                    existing_pick.line_value = line.line_value
                    existing_pick.odds = line.odds
                    existing_pick.model_probability = model_prob
                    existing_pick.implied_probability = implied_prob
                    existing_pick.expected_value = ev
                    existing_pick.hit_rate_10g = hit_rate_10g
                    existing_pick.hit_rate_30d = hit_rate_30d
                    existing_pick.confidence_score = confidence
                    existing_pick.is_active = True
                    existing_pick.generated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    stats["picks_updated"] += 1
                else:
                    # Create new pick
                    pick = ModelPick(
                        sport_id=sport.id,
                        game_id=line.game_id,
                        player_id=line.player_id,
                        market_id=line.market_id,
                        side=line.side,
                        line_value=line.line_value,
                        odds=line.odds,
                        model_probability=model_prob,
                        implied_probability=implied_prob,
                        expected_value=ev,
                        hit_rate_10g=hit_rate_10g,
                        hit_rate_30d=hit_rate_30d,
                        confidence_score=confidence,
                        is_active=True,
                    )
                    db.add(pick)
                    stats["picks_created"] += 1
            
            except Exception as e:
                logger.error(f"Error processing line {line.id}: {e}")
                stats["errors"].append(f"Line {line.id}: {str(e)}")
        
        stats["games_processed"] = len(games)
        
        await db.commit()
        logger.info(f"Picks generation completed for {sport_key}: {stats}")
        return stats
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Picks generation failed for {sport_key}: {e}")
        raise


# =============================================================================
# Convenience Functions
# =============================================================================

async def generate_all_model_picks(
    db: AsyncSession,
    ev_threshold: float = 0.05,
    confidence_threshold: float = 0.5,
) -> dict[str, Any]:
    """
    Generate model picks for all configured sports.
    
    Returns:
        Dictionary mapping sport_key to generation results
    """
    results = {}
    
    for sport_key in SPORT_KEY_TO_LEAGUE.keys():
        try:
            results[sport_key] = await generate_model_picks_for_today(
                db,
                sport_key,
                ev_threshold=ev_threshold,
                confidence_threshold=confidence_threshold,
            )
        except Exception as e:
            logger.error(f"Failed to generate picks for {sport_key}: {e}")
            results[sport_key] = {"error": str(e)}
    
    return results
