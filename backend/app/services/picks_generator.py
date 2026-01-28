"""Picks generator service for creating model picks from lines and stats."""

import logging
import random
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import select, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Sport, Game, Line, Market, Player, PlayerGameStats, ModelPick, Injury

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
}


# =============================================================================
# Probability Helpers
# =============================================================================

def american_odds_to_probability(odds: float) -> float:
    """
    Convert American odds to implied probability.
    
    Args:
        odds: American odds (e.g., -110, +150)
    
    Returns:
        Implied probability between 0 and 1
    """
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)


def calculate_expected_value(
    model_prob: float,
    odds: float,
) -> float:
    """
    Calculate expected value for a bet.
    
    EV = (model_prob * net_profit) - ((1 - model_prob) * stake)
    
    For a $1 stake:
    - If odds are negative (e.g., -110): profit = 100/110 = 0.909
    - If odds are positive (e.g., +150): profit = 150/100 = 1.5
    
    Args:
        model_prob: Model's predicted probability of winning
        odds: American odds
    
    Returns:
        Expected value (positive = +EV bet)
    """
    if odds < 0:
        profit = 100 / abs(odds)
    else:
        profit = odds / 100
    
    ev = (model_prob * profit) - ((1 - model_prob) * 1)
    return ev


def calculate_confidence_score(
    model_prob: float,
    implied_prob: float,
    ev: float,
    hit_rate: Optional[float] = None,
) -> float:
    """
    Calculate overall confidence score for a pick.
    
    Factors:
    - Edge over implied probability
    - Expected value
    - Historical hit rate (if available)
    
    Returns:
        Confidence score between 0 and 1
    """
    # Base confidence from edge
    edge = model_prob - implied_prob
    edge_score = min(1.0, max(0.0, 0.5 + edge * 5))  # Scale edge to 0-1
    
    # EV component
    ev_score = min(1.0, max(0.0, 0.5 + ev * 2))  # Scale EV to 0-1
    
    # Combine scores
    if hit_rate is not None:
        confidence = (edge_score * 0.4 + ev_score * 0.3 + hit_rate * 0.3)
    else:
        confidence = (edge_score * 0.5 + ev_score * 0.5)
    
    return round(min(1.0, max(0.0, confidence)), 4)


# =============================================================================
# Stub Model Probability Generator
# =============================================================================

def generate_stub_probability(
    line: Line,
    player_stats: Optional[dict[str, float]] = None,
) -> float:
    """
    Generate a stub model probability.
    
    This is a placeholder that generates somewhat realistic probabilities.
    Replace with actual ML model predictions in production.
    
    Args:
        line: The betting line
        player_stats: Optional dict of player's average stats
    
    Returns:
        Simulated model probability
    """
    # Get implied probability as baseline
    implied = american_odds_to_probability(line.odds)
    
    # Add some "edge" - in production this would come from ML model
    # For stubs, add small random variance around implied
    random.seed(hash(f"{line.id}_{line.sportsbook}_{line.side}"))
    
    # Generate variance based on line type
    if line.player_id:  # Player prop
        # Props have more variance/edge potential
        variance = random.gauss(0, 0.08)
    else:  # Game line
        # Game lines are more efficient
        variance = random.gauss(0, 0.04)
    
    model_prob = implied + variance
    
    # Clamp to valid range
    return round(min(0.95, max(0.05, model_prob)), 4)


def _generate_stub_hit_rates(
    player_avg_stats: dict[str, float],
    line_value: float,
    side: str = "over",
) -> tuple[float, float, float, float]:
    """
    Generate synthetic hit rates for stub mode when no PlayerGameStats exist.
    
    Uses player averages to estimate realistic hit rates based on how far
    the line is from the player's average.
    
    Args:
        player_avg_stats: Dict with player's average for stat type
        line_value: The betting line value
        side: 'over' or 'under'
    
    Returns:
        Tuple of (hit_rate_10g, hit_rate_30d, hit_rate_5g, hit_rate_3g)
    """
    if not player_avg_stats:
        return (0.5, 0.5, 0.5, 0.5)
    
    # Get the first (and typically only) stat value
    avg_value = list(player_avg_stats.values())[0] if player_avg_stats else line_value
    
    # Calculate edge: how much the average exceeds/falls short of the line
    if side.lower() == "over":
        # For overs: higher avg = higher hit rate
        edge = (avg_value - line_value) / max(line_value, 1)
    else:
        # For unders: lower avg = higher hit rate  
        edge = (line_value - avg_value) / max(line_value, 1)
    
    # Convert edge to hit rate (sigmoid-like curve)
    # Edge of 0 = 50% hit rate, edge of 0.2 = ~70%, edge of -0.2 = ~30%
    base_hit_rate = 0.5 + (edge * 1.5)
    
    # Clamp and add slight variance for realism
    random.seed(hash(f"{avg_value}_{line_value}_{side}"))
    variance = random.gauss(0, 0.05)
    
    hit_rate_10g = round(min(0.9, max(0.1, base_hit_rate + variance)), 4)
    # 30d tends to be slightly more stable (closer to expected)
    hit_rate_30d = round(min(0.9, max(0.1, base_hit_rate + variance * 0.5)), 4)
    # Shorter windows have more variance
    hit_rate_5g = round(min(0.9, max(0.1, base_hit_rate + variance * 1.2)), 4)
    hit_rate_3g = round(min(0.9, max(0.1, base_hit_rate + variance * 1.5)), 4)
    
    return (hit_rate_10g, hit_rate_30d, hit_rate_5g, hit_rate_3g)


def _generate_stub_player_averages(
    stat_type: str,
    line_value: float,
) -> dict[str, float]:
    """
    Generate synthetic player averages for stub mode when PlayerGameStats is empty.
    
    Creates realistic averages that hover around the betting line value,
    which produces meaningful hit rate calculations.
    
    Args:
        stat_type: The stat type (e.g., 'PTS', 'REB', 'AST')
        line_value: The betting line value
    
    Returns:
        Dict with stat_type -> average value
    """
    # Base average slightly above/below line for realistic values
    random.seed(hash(f"{stat_type}_{line_value}"))
    variance = random.gauss(0, 0.15)
    avg = line_value * (1 + variance)
    return {stat_type: round(avg, 1)}


# =============================================================================
# Main Generator Function
# =============================================================================

async def generate_picks(
    db: AsyncSession,
    sport_key: str,
    min_ev: float = 0.0,
    min_confidence: float = 0.5,
    use_stubs: bool = True,
) -> dict[str, Any]:
    """
    Generate model picks for today's games.
    
    This function:
    1. Marks old picks as inactive
    2. Gets today's games with current lines
    3. Generates model probabilities (stub or real)
    4. Calculates EV and confidence
    5. Creates picks that meet thresholds
    
    Args:
        db: Database session
        sport_key: Sport identifier (e.g., 'basketball_nba')
        min_ev: Minimum expected value to create a pick
        min_confidence: Minimum confidence score to create a pick
        use_stubs: Use stub probability generator
    
    Returns:
        Dictionary with generation statistics
    """
    stats = {
        "sport": None,
        "picks_deactivated": 0,
        "picks_created": 0,
        "lines_evaluated": 0,
        "games_processed": 0,
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
        
        # Mark old picks as inactive
        deactivated = await _deactivate_old_picks(db, sport.id)
        stats["picks_deactivated"] = deactivated
        
        # Get today's games (use naive datetime for PostgreSQL compatibility)
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        result = await db.execute(
            select(Game)
            .options(
                selectinload(Game.home_team),
                selectinload(Game.away_team),
            )
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
            return stats
        
        logger.info(f"Processing {len(games)} games for {sport_key}")
        
        for game in games:
            try:
                picks_for_game = await _generate_picks_for_game(
                    db,
                    sport,
                    game,
                    min_ev=min_ev,
                    min_confidence=min_confidence,
                    use_stubs=use_stubs,
                )
                stats["picks_created"] += picks_for_game["picks_created"]
                stats["lines_evaluated"] += picks_for_game["lines_evaluated"]
                stats["games_processed"] += 1
            
            except Exception as e:
                logger.error(f"Error generating picks for game {game.id}: {e}")
                stats["errors"].append(f"Game {game.id}: {str(e)}")
        
        await db.commit()
        logger.info(f"Picks generation completed for {sport_key}: {stats}")
        return stats
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Picks generation failed for {sport_key}: {e}")
        raise


async def _deactivate_old_picks(
    db: AsyncSession,
    sport_id: int,
) -> int:
    """Mark all active picks for the sport as inactive."""
    result = await db.execute(
        update(ModelPick)
        .where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.is_active == True,
            )
        )
        .values(is_active=False)
    )
    return result.rowcount


async def _generate_picks_for_game(
    db: AsyncSession,
    sport: Sport,
    game: Game,
    min_ev: float,
    min_confidence: float,
    use_stubs: bool,
) -> dict[str, int]:
    """Generate picks for a single game."""
    stats = {"picks_created": 0, "lines_evaluated": 0}
    
    # Get current lines for this game
    result = await db.execute(
        select(Line)
        .options(
            selectinload(Line.market),
            selectinload(Line.player),
        )
        .where(
            and_(
                Line.game_id == game.id,
                Line.is_current == True,
            )
        )
    )
    lines = list(result.scalars().all())
    
    # Cache for injured players to avoid repeated queries
    injured_player_ids = set()
    
    # First pass: identify all injured players
    for line in lines:
        if line.player_id and line.player_id not in injured_player_ids:
            injury_result = await db.execute(
                select(Injury).where(
                    and_(
                        Injury.player_id == line.player_id,
                        Injury.status.in_(["OUT", "DOUBTFUL", "GTD", "DAY_TO_DAY"]),
                    )
                )
            )
            if injury_result.scalar_one_or_none():
                injured_player_ids.add(line.player_id)
    
    # Group lines by player/market (NOT including side) to find best pick per prop
    # Key: (market_id, player_id, sportsbook) -> list of candidate picks
    candidate_picks: dict[tuple, list[dict]] = {}
    
    for line in lines:
        stats["lines_evaluated"] += 1
        
        # Skip injured players
        if line.player_id and line.player_id in injured_player_ids:
            logger.debug(f"Skipping injured player {line.player_id}")
            continue
        
        # Get player stats for props
        player_avg_stats = None
        hit_rate_10g = None
        hit_rate_30d = None
        hit_rate_5g = None
        hit_rate_3g = None
        
        if line.player_id and line.market and line.market.stat_type:
            player_avg_stats = await _get_player_averages(
                db, line.player_id, line.market.stat_type
            )
            
            # Fallback: generate stub averages if none exist in stub mode
            if use_stubs and player_avg_stats is None and line.line_value:
                player_avg_stats = _generate_stub_player_averages(
                    line.market.stat_type, line.line_value
                )
            
            if player_avg_stats and line.line_value:
                # Calculate all hit rates with proper side handling
                hit_rate_10g = await _calculate_hit_rate(
                    db, line.player_id, line.market.stat_type, line.line_value,
                    side=line.side or "over"
                )
                hit_rate_30d = await _calculate_hit_rate_30d(
                    db, line.player_id, line.market.stat_type, line.line_value,
                    side=line.side or "over"
                )
                hit_rate_5g = await _calculate_hit_rate_5g(
                    db, line.player_id, line.market.stat_type, line.line_value,
                    side=line.side or "over"
                )
                hit_rate_3g = await _calculate_hit_rate_3g(
                    db, line.player_id, line.market.stat_type, line.line_value,
                    side=line.side or "over"
                )
                
                # Fallback: generate synthetic hit rates in stub mode if no data
                if use_stubs and hit_rate_10g is None:
                    hit_rate_10g, hit_rate_30d, hit_rate_5g, hit_rate_3g = _generate_stub_hit_rates(
                        player_avg_stats, line.line_value, line.side or "over"
                    )
        
        # Generate model probability
        if use_stubs:
            model_prob = generate_stub_probability(line, player_avg_stats)
        else:
            # In production, call actual ML model here
            model_prob = generate_stub_probability(line, player_avg_stats)
        
        # Calculate metrics
        implied_prob = american_odds_to_probability(line.odds)
        ev = calculate_expected_value(model_prob, line.odds)
        confidence = calculate_confidence_score(model_prob, implied_prob, ev, hit_rate_10g)
        
        # Check thresholds
        if ev < min_ev or confidence < min_confidence:
            continue
        
        # Group by market/player/sportsbook (exclude side) - we'll pick best side later
        group_key = (line.market_id, line.player_id, line.sportsbook)
        
        candidate = {
            "line": line,
            "model_prob": model_prob,
            "implied_prob": implied_prob,
            "ev": ev,
            "confidence": confidence,
            "hit_rate_10g": hit_rate_10g,
            "hit_rate_30d": hit_rate_30d,
            "hit_rate_5g": hit_rate_5g,
            "hit_rate_3g": hit_rate_3g,
        }
        
        if group_key not in candidate_picks:
            candidate_picks[group_key] = []
        candidate_picks[group_key].append(candidate)
    
    # Second pass: select BEST pick (highest EV) for each player/market/sportsbook
    # This prevents contradicting picks (both over AND under for same prop)
    for group_key, candidates in candidate_picks.items():
        # Sort by EV descending and pick the best one
        best_candidate = max(candidates, key=lambda c: c["ev"])
        line = best_candidate["line"]
        
        # Create pick (select best side - highest EV - per player/market)
        pick = ModelPick(
            sport_id=sport.id,
            game_id=game.id,
            player_id=line.player_id,
            market_id=line.market_id,
            side=line.side,
            line_value=line.line_value,
            odds=line.odds,
            model_probability=best_candidate["model_prob"],
            implied_probability=best_candidate["implied_prob"],
            expected_value=round(best_candidate["ev"], 4),
            hit_rate_30d=best_candidate["hit_rate_30d"],
            hit_rate_10g=best_candidate["hit_rate_10g"],
            hit_rate_5g=best_candidate["hit_rate_5g"],
            hit_rate_3g=best_candidate["hit_rate_3g"],
            confidence_score=best_candidate["confidence"],
            is_active=True,
        )
        db.add(pick)
        stats["picks_created"] += 1
    
    return stats


async def _get_player_averages(
    db: AsyncSession,
    player_id: int,
    stat_type: str,
    games_back: int = 10,
) -> Optional[dict[str, float]]:
    """Get player's average stats over last N games."""
    result = await db.execute(
        select(func.avg(PlayerGameStats.value))
        .where(
            and_(
                PlayerGameStats.player_id == player_id,
                PlayerGameStats.stat_type == stat_type,
            )
        )
        .limit(games_back)
    )
    avg = result.scalar()
    
    if avg:
        return {stat_type: float(avg)}
    return None


async def _calculate_hit_rate(
    db: AsyncSession,
    player_id: int,
    stat_type: str,
    line_value: float,
    side: str = "over",
    games_back: int = 10,
) -> Optional[float]:
    """
    Calculate hit rate for a player over/under a line (last N games).
    
    Args:
        db: Database session
        player_id: Player's internal ID
        stat_type: Stat type (e.g., 'PTS', 'REB', 'AST')
        line_value: The line to check against
        side: 'over' or 'under' - determines hit direction
        games_back: Number of games to look back
    
    Returns:
        Hit rate as decimal (0-1) or None if no data
    """
    result = await db.execute(
        select(PlayerGameStats.value)
        .where(
            and_(
                PlayerGameStats.player_id == player_id,
                PlayerGameStats.stat_type == stat_type,
            )
        )
        .order_by(PlayerGameStats.created_at.desc())
        .limit(games_back)
    )
    values = [row[0] for row in result.all()]
    
    if not values:
        return None
    
    # Count hits based on side
    if side.lower() == "under":
        hits = sum(1 for v in values if v < line_value)
    else:
        hits = sum(1 for v in values if v > line_value)
    
    return round(hits / len(values), 4)


async def _calculate_hit_rate_30d(
    db: AsyncSession,
    player_id: int,
    stat_type: str,
    line_value: float,
    side: str = "over",
) -> Optional[float]:
    """
    Calculate hit rate over last 30 days.
    
    Args:
        db: Database session
        player_id: Player's internal ID
        stat_type: Stat type (e.g., 'PTS', 'REB', 'AST')
        line_value: The line to check against
        side: 'over' or 'under' - determines hit direction
    
    Returns:
        Hit rate as decimal (0-1) or None if no data
    """
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    result = await db.execute(
        select(PlayerGameStats.value)
        .where(
            and_(
                PlayerGameStats.player_id == player_id,
                PlayerGameStats.stat_type == stat_type,
                PlayerGameStats.created_at >= thirty_days_ago,
            )
        )
        .order_by(PlayerGameStats.created_at.desc())
    )
    values = [row[0] for row in result.all()]
    
    if not values:
        return None
    
    # Count hits based on side
    if side.lower() == "under":
        hits = sum(1 for v in values if v < line_value)
    else:
        hits = sum(1 for v in values if v > line_value)
    
    return round(hits / len(values), 4)


async def _calculate_hit_rate_5g(
    db: AsyncSession,
    player_id: int,
    stat_type: str,
    line_value: float,
    side: str = "over",
) -> Optional[float]:
    """
    Calculate hit rate over last 5 games.
    
    Args:
        db: Database session
        player_id: Player's internal ID
        stat_type: Stat type (e.g., 'PTS', 'REB', 'AST')
        line_value: The line to check against
        side: 'over' or 'under' - determines hit direction
    
    Returns:
        Hit rate as decimal (0-1) or None if no data
    """
    return await _calculate_hit_rate(
        db, player_id, stat_type, line_value, side=side, games_back=5
    )


async def _calculate_hit_rate_3g(
    db: AsyncSession,
    player_id: int,
    stat_type: str,
    line_value: float,
    side: str = "over",
) -> Optional[float]:
    """
    Calculate hit rate over last 3 games.
    
    Args:
        db: Database session
        player_id: Player's internal ID
        stat_type: Stat type (e.g., 'PTS', 'REB', 'AST')
        line_value: The line to check against
        side: 'over' or 'under' - determines hit direction
    
    Returns:
        Hit rate as decimal (0-1) or None if no data
    """
    return await _calculate_hit_rate(
        db, player_id, stat_type, line_value, side=side, games_back=3
    )


# =============================================================================
# Convenience Functions
# =============================================================================

async def generate_all_picks(
    db: AsyncSession,
    min_ev: float = 0.0,
    min_confidence: float = 0.5,
    use_stubs: bool = True,
) -> dict[str, Any]:
    """
    Generate picks for all configured sports.
    
    Returns:
        Dictionary mapping sport_key to generation results
    """
    results = {}
    
    for sport_key in SPORT_KEY_TO_LEAGUE.keys():
        try:
            results[sport_key] = await generate_picks(
                db,
                sport_key,
                min_ev=min_ev,
                min_confidence=min_confidence,
                use_stubs=use_stubs,
            )
        except Exception as e:
            logger.error(f"Failed to generate picks for {sport_key}: {e}")
            results[sport_key] = {"error": str(e)}
    
    return results
