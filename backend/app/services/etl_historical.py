"""
ETL service for historical odds data and game results.

Syncs data from OddsPapi for:
- Historical odds movements (for trend analysis)
- Game results/scores (for settlement)
- Pick settlement (calculating hit rates)
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Game,
    GameResult,
    Market,
    ModelPick,
    OddsSnapshot,
    PickResult,
    Player,
    Sport,
)
from app.services.oddspapi_provider import (
    OddsPapiProvider,
    SPORT_IDS,
    decimal_to_american,
    parse_oddspapi_datetime,
)

logger = logging.getLogger(__name__)

# Mapping from internal sport keys to OddsPapi sport IDs
SPORT_KEY_TO_ID = {
    "basketball_nba": 10,
    "americanfootball_nfl": 12,
    "baseball_mlb": 16,
    "icehockey_nhl": 17,
}

# NBA tournament IDs (common ones - can be fetched dynamically)
NBA_TOURNAMENT_IDS = [132, 133]  # Regular season, playoffs


async def sync_historical_odds(
    db: AsyncSession,
    sport_key: str = "basketball_nba",
    days_back: int = 7,
    bookmakers: list[str] = None,
) -> dict[str, Any]:
    """
    Sync historical odds for recent games from OddsPapi.
    
    Args:
        db: Database session
        sport_key: Sport identifier
        days_back: How many days back to fetch
        bookmakers: List of bookmakers to track
    
    Returns:
        Sync statistics
    """
    stats = {
        "fixtures_processed": 0,
        "snapshots_created": 0,
        "errors": [],
    }
    
    bookmakers = bookmakers or ["pinnacle", "draftkings", "fanduel"]
    
    try:
        # Get sport
        sport_result = await db.execute(
            select(Sport).where(Sport.league_code == sport_key.split("_")[-1].upper())
        )
        sport = sport_result.scalar_one_or_none()
        if not sport:
            stats["errors"].append(f"Sport not found: {sport_key}")
            return stats
        
        # Get recent games that need historical odds
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        games_result = await db.execute(
            select(Game).where(
                and_(
                    Game.sport_id == sport.id,
                    Game.start_time >= cutoff,
                )
            )
        )
        games = games_result.scalars().all()
        
        if not games:
            logger.info(f"No games found for {sport_key} in last {days_back} days")
            return stats
        
        async with OddsPapiProvider() as provider:
            for game in games:
                try:
                    # Use game's external_game_id as fixture_id
                    # Note: OddsPapi fixture IDs may differ - might need mapping
                    fixture_id = game.external_game_id
                    
                    # Fetch historical odds
                    historical = await provider.fetch_historical_odds(
                        fixture_id=fixture_id,
                        bookmakers=bookmakers[:3],
                    )
                    
                    if not historical or "bookmakers" not in historical:
                        continue
                    
                    stats["fixtures_processed"] += 1
                    
                    # Process odds data
                    snapshots = await _process_historical_odds(
                        db, game, historical, sport
                    )
                    stats["snapshots_created"] += snapshots
                    
                    # Rate limit: 5000ms between historical-odds calls
                    await asyncio.sleep(5.0)
                    
                except Exception as e:
                    stats["errors"].append(f"Game {game.id}: {str(e)[:100]}")
                    logger.warning(f"Error fetching historical odds for game {game.id}: {e}")
        
        await db.commit()
        
    except Exception as e:
        stats["errors"].append(str(e)[:200])
        logger.error(f"Historical odds sync failed: {e}")
    
    return stats


async def _process_historical_odds(
    db: AsyncSession,
    game: Game,
    historical: dict[str, Any],
    sport: Sport,
) -> int:
    """Process and store historical odds data."""
    snapshots_created = 0
    
    for bookmaker_slug, bookmaker_data in historical.get("bookmakers", {}).items():
        markets_data = bookmaker_data.get("markets", {})
        
        for market_id, market_data in markets_data.items():
            # Get or map market type
            market = await _get_market_for_oddspapi(db, sport.id, market_id)
            if not market:
                continue
            
            outcomes = market_data.get("outcomes", {})
            for outcome_id, outcome_data in outcomes.items():
                players_data = outcome_data.get("players", {})
                
                for player_key, odds_list in players_data.items():
                    if not isinstance(odds_list, list):
                        continue
                    
                    for odds_entry in odds_list:
                        try:
                            snapshot = OddsSnapshot(
                                game_id=game.id,
                                market_id=market.id,
                                external_fixture_id=historical.get("fixtureId", game.external_game_id),
                                external_market_id=str(market_id),
                                external_outcome_id=str(outcome_id),
                                bookmaker=bookmaker_slug,
                                price=odds_entry.get("price", 0),
                                american_odds=decimal_to_american(odds_entry.get("price", 2.0)),
                                is_active=odds_entry.get("active", True),
                                snapshot_at=parse_oddspapi_datetime(odds_entry.get("createdAt", "")),
                            )
                            db.add(snapshot)
                            snapshots_created += 1
                        except Exception as e:
                            logger.debug(f"Error creating snapshot: {e}")
    
    return snapshots_created


async def _get_market_for_oddspapi(
    db: AsyncSession,
    sport_id: int,
    oddspapi_market_id: str,
) -> Optional[Market]:
    """Map OddsPapi market ID to internal market."""
    # OddsPapi market ID mapping (common ones)
    # 101 = 1X2 (moneyline for soccer, but used for spreads too)
    # 104 = Over/Under
    # Player props have different IDs
    
    market_type_map = {
        "101": "moneyline",
        "104": "total",
        "10168": "spread",
    }
    
    market_type = market_type_map.get(str(oddspapi_market_id), "moneyline")
    
    result = await db.execute(
        select(Market).where(
            and_(
                Market.sport_id == sport_id,
                Market.market_type == market_type,
            )
        )
    )
    return result.scalar_one_or_none()


async def sync_game_results(
    db: AsyncSession,
    sport_key: str = "basketball_nba",
    days_back: int = 3,
) -> dict[str, Any]:
    """
    Sync game results/scores from OddsPapi for completed games.
    
    Args:
        db: Database session
        sport_key: Sport identifier
        days_back: How many days back to check
    
    Returns:
        Sync statistics
    """
    stats = {
        "games_checked": 0,
        "results_created": 0,
        "results_updated": 0,
        "errors": [],
    }
    
    try:
        # Get sport
        sport_result = await db.execute(
            select(Sport).where(Sport.league_code == sport_key.split("_")[-1].upper())
        )
        sport = sport_result.scalar_one_or_none()
        if not sport:
            stats["errors"].append(f"Sport not found: {sport_key}")
            return stats
        
        # Get games that might be completed (started more than 4 hours ago)
        cutoff_end = datetime.now(timezone.utc) - timedelta(hours=4)
        cutoff_start = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        games_result = await db.execute(
            select(Game).where(
                and_(
                    Game.sport_id == sport.id,
                    Game.start_time >= cutoff_start,
                    Game.start_time <= cutoff_end,
                )
            )
        )
        games = games_result.scalars().all()
        
        if not games:
            logger.info(f"No completed games found for {sport_key}")
            return stats
        
        async with OddsPapiProvider() as provider:
            for game in games:
                try:
                    stats["games_checked"] += 1
                    
                    # Check if we already have a result
                    existing_result = await db.execute(
                        select(GameResult).where(GameResult.game_id == game.id)
                    )
                    existing = existing_result.scalar_one_or_none()
                    
                    if existing and existing.is_settled:
                        continue  # Already settled
                    
                    # Fetch scores from OddsPapi
                    scores_data = await provider.fetch_scores(game.external_game_id)
                    
                    if not scores_data or "scores" not in scores_data:
                        continue
                    
                    # Extract final scores
                    scores = scores_data.get("scores", {})
                    home_score = 0
                    away_score = 0
                    period_scores_str = ""
                    
                    # Sum up period scores
                    period_parts = []
                    for period, period_data in scores.items():
                        p1 = period_data.get("participant1Score", 0)
                        p2 = period_data.get("participant2Score", 0)
                        home_score += p1
                        away_score += p2
                        period_parts.append(f"{period}:{p1}-{p2}")
                    
                    period_scores_str = ",".join(period_parts)
                    
                    if existing:
                        # Update existing result
                        existing.home_score = home_score
                        existing.away_score = away_score
                        existing.period_scores = period_scores_str
                        existing.is_settled = True
                        existing.settled_at = datetime.now(timezone.utc)
                        stats["results_updated"] += 1
                    else:
                        # Create new result
                        result = GameResult(
                            game_id=game.id,
                            external_fixture_id=game.external_game_id,
                            home_score=home_score,
                            away_score=away_score,
                            period_scores=period_scores_str,
                            is_settled=True,
                        )
                        db.add(result)
                        stats["results_created"] += 1
                    
                    # Update game status
                    game.status = "final"
                    
                    # Rate limit: 1000ms between scores calls
                    await asyncio.sleep(1.0)
                    
                except Exception as e:
                    stats["errors"].append(f"Game {game.id}: {str(e)[:100]}")
                    logger.warning(f"Error fetching scores for game {game.id}: {e}")
        
        await db.commit()
        
    except Exception as e:
        stats["errors"].append(str(e)[:200])
        logger.error(f"Game results sync failed: {e}")
    
    return stats


async def settle_picks(
    db: AsyncSession,
    sport_key: str = "basketball_nba",
) -> dict[str, Any]:
    """
    Settle picks using game results.
    
    Matches completed games with unsettled picks and determines
    if each pick was a hit or miss.
    
    Args:
        db: Database session
        sport_key: Sport identifier
    
    Returns:
        Settlement statistics
    """
    stats = {
        "picks_checked": 0,
        "picks_settled": 0,
        "hits": 0,
        "misses": 0,
        "pushes": 0,
        "errors": [],
    }
    
    try:
        # Get sport
        sport_result = await db.execute(
            select(Sport).where(Sport.league_code == sport_key.split("_")[-1].upper())
        )
        sport = sport_result.scalar_one_or_none()
        if not sport:
            stats["errors"].append(f"Sport not found: {sport_key}")
            return stats
        
        # Get unsettled picks for games with results
        picks_query = (
            select(ModelPick)
            .join(Game, ModelPick.game_id == Game.id)
            .join(GameResult, GameResult.game_id == Game.id)
            .outerjoin(PickResult, PickResult.pick_id == ModelPick.id)
            .where(
                and_(
                    ModelPick.sport_id == sport.id,
                    PickResult.id.is_(None),  # Not yet settled
                    GameResult.is_settled == True,
                )
            )
        )
        
        picks_result = await db.execute(picks_query)
        picks = picks_result.scalars().all()
        
        for pick in picks:
            try:
                stats["picks_checked"] += 1
                
                # Get game result
                result_query = await db.execute(
                    select(GameResult).where(GameResult.game_id == pick.game_id)
                )
                game_result = result_query.scalar_one_or_none()
                
                if not game_result:
                    continue
                
                # Determine if pick hit
                hit = await _evaluate_pick(db, pick, game_result)
                
                if hit is None:
                    stats["pushes"] += 1
                    actual_value = pick.line_value or 0
                elif hit:
                    stats["hits"] += 1
                    actual_value = _get_actual_value(pick, game_result, hit)
                else:
                    stats["misses"] += 1
                    actual_value = _get_actual_value(pick, game_result, hit)
                
                # Create pick result
                pick_result = PickResult(
                    pick_id=pick.id,
                    player_id=pick.player_id,
                    game_id=pick.game_id,
                    actual_value=actual_value,
                    line_value=pick.line_value or 0,
                    side=pick.side,
                    hit=hit if hit is not None else False,
                )
                db.add(pick_result)
                stats["picks_settled"] += 1
                
            except Exception as e:
                stats["errors"].append(f"Pick {pick.id}: {str(e)[:100]}")
                logger.warning(f"Error settling pick {pick.id}: {e}")
        
        await db.commit()
        
    except Exception as e:
        stats["errors"].append(str(e)[:200])
        logger.error(f"Pick settlement failed: {e}")
    
    return stats


async def _evaluate_pick(
    db: AsyncSession,
    pick: ModelPick,
    game_result: GameResult,
) -> Optional[bool]:
    """
    Evaluate if a pick hit based on game result.
    
    Returns:
        True if hit, False if miss, None if push
    """
    # Get market type
    market_result = await db.execute(
        select(Market).where(Market.id == pick.market_id)
    )
    market = market_result.scalar_one_or_none()
    
    if not market:
        return None
    
    market_type = market.market_type.lower()
    
    if market_type == "moneyline":
        # Home/away win
        if pick.side == "home":
            return game_result.home_win
        elif pick.side == "away":
            return game_result.away_win
    
    elif market_type == "spread":
        # Spread bet
        spread = game_result.spread  # home_score - away_score
        if pick.line_value is None:
            return None
        
        if pick.side == "home":
            # Home covers if spread > -line_value
            actual = spread + pick.line_value
        else:
            # Away covers if -spread > line_value
            actual = -spread + pick.line_value
        
        if actual > 0:
            return True
        elif actual < 0:
            return False
        else:
            return None  # Push
    
    elif market_type == "total":
        # Over/under total
        total = game_result.total_score
        if pick.line_value is None:
            return None
        
        if pick.side == "over":
            if total > pick.line_value:
                return True
            elif total < pick.line_value:
                return False
            else:
                return None  # Push
        else:  # under
            if total < pick.line_value:
                return True
            elif total > pick.line_value:
                return False
            else:
                return None  # Push
    
    # For player props, we'd need actual player stats
    # This would require additional data from a stats API
    
    return None


def _get_actual_value(
    pick: ModelPick,
    game_result: GameResult,
    hit: bool,
) -> float:
    """Get the actual value for a pick based on game result."""
    # Get market type from pick
    side = pick.side.lower()
    
    if side in ("home", "away"):
        # Moneyline - return spread as "value"
        return float(game_result.spread if side == "home" else -game_result.spread)
    elif side in ("over", "under"):
        # Total - return actual total
        return float(game_result.total_score)
    
    return 0.0


async def run_full_historical_sync(
    db: AsyncSession,
    sport_key: str = "basketball_nba",
) -> dict[str, Any]:
    """
    Run complete historical sync: odds, results, and settlement.
    
    Args:
        db: Database session
        sport_key: Sport identifier
    
    Returns:
        Combined statistics from all sync operations
    """
    results = {
        "historical_odds": {},
        "game_results": {},
        "settlements": {},
    }
    
    logger.info(f"Starting full historical sync for {sport_key}")
    
    # 1. Sync historical odds
    logger.info("Syncing historical odds...")
    results["historical_odds"] = await sync_historical_odds(db, sport_key)
    
    # 2. Sync game results
    logger.info("Syncing game results...")
    results["game_results"] = await sync_game_results(db, sport_key)
    
    # 3. Settle picks
    logger.info("Settling picks...")
    results["settlements"] = await settle_picks(db, sport_key)
    
    logger.info(f"Historical sync complete: {results}")
    return results
