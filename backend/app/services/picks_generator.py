"""Picks generator service for creating model picks from lines and stats."""

import logging
import random
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import select, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Sport, Game, Line, Market, Player, PlayerGameStats, ModelPick

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
        
        # Get today's games
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
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
    
    # Group lines by market/player to avoid duplicate picks
    evaluated_keys = set()
    
    for line in lines:
        stats["lines_evaluated"] += 1
        
        # Create unique key to avoid duplicates
        pick_key = (game.id, line.market_id, line.player_id, line.side)
        if pick_key in evaluated_keys:
            continue
        evaluated_keys.add(pick_key)
        
        # Get player stats for props
        player_avg_stats = None
        hit_rate = None
        
        if line.player_id and line.market and line.market.stat_type:
            player_avg_stats = await _get_player_averages(
                db, line.player_id, line.market.stat_type
            )
            if player_avg_stats and line.line_value:
                hit_rate = await _calculate_hit_rate(
                    db, line.player_id, line.market.stat_type, line.line_value
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
        confidence = calculate_confidence_score(model_prob, implied_prob, ev, hit_rate)
        
        # Check thresholds
        if ev < min_ev or confidence < min_confidence:
            continue
        
        # Create pick
        pick = ModelPick(
            sport_id=sport.id,
            game_id=game.id,
            player_id=line.player_id,
            market_id=line.market_id,
            side=line.side,
            line_value=line.line_value,
            odds=line.odds,
            model_probability=model_prob,
            implied_probability=implied_prob,
            expected_value=round(ev, 4),
            hit_rate_30d=None,  # Would need historical data
            hit_rate_10g=hit_rate,
            confidence_score=confidence,
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
    games_back: int = 10,
) -> Optional[float]:
    """Calculate hit rate for a player over a line."""
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
    
    hits = sum(1 for v in values if v > line_value)
    return round(hits / len(values), 4)


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
