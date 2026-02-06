"""Hot/Cold players service - market-aware player streak tracking."""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Player, PlayerHitRate, PlayerMarketHitRate, Sport, Team

logger = logging.getLogger(__name__)


# Market display names for UI
MARKET_DISPLAY_NAMES = {
    # Basketball
    "player_points": "PTS",
    "player_rebounds": "REB",
    "player_assists": "AST",
    "player_threes": "3PM",
    "player_pra": "PRA",
    "player_pts_rebs": "P+R",
    "player_pts_asts": "P+A",
    "player_rebs_asts": "R+A",
    "player_steals": "STL",
    "player_blocks": "BLK",
    "player_turnovers": "TO",
    "player_double_double": "DD",
    "player_triple_double": "TD",
    
    # Hockey
    "goals": "GOALS",
    "assists_hockey": "AST_H",
    "points_hockey": "PTS_H",
    "shots_on_goal": "SOG",
    "blocked_shots": "BLK_SHOTS",
    "saves": "SAVES",
    "power_play_points": "PPP",
    "penalty_minutes": "PIM",
    
    # Football
    "pass_yards": "PASS_YDS",
    "pass_tds": "PASS_TDS",
    "pass_attempts": "PASS_ATT",
    "pass_completions": "PASS_COMP",
    "interceptions": "INT",
    "rush_yards": "RUSH_YDS",
    "rush_attempts": "RUSH_ATT",
    "rush_tds": "RUSH_TDS",
    "receiving_yards": "REC_YDS",
    "receptions": "REC",
    "receiving_tds": "REC_TDS",
    "rush_rec_yards": "RUSH_REC_YDS",
    "anytime_td": "ANYTIME_TD",
    
    # Baseball
    "hits": "H",
    "runs": "R",
    "runs_batted_in": "RBI",
    "total_bases": "TB",
    "home_runs": "HR",
    "strikeouts": "K",
    "outs": "OUTS",
    
    # Tennis
    "aces": "ACES",
    "double_faults": "DF",
    "games": "GAMES",
    "sets": "SETS",
    "total_games": "TOTAL_GAMES",
    
    # Short forms map to themselves
    "PTS": "PTS",
    "REB": "REB",
    "AST": "AST",
    "3PM": "3PM",
    "PRA": "PRA",
    "STL": "STL",
    "BLK": "BLK",
    "TO": "TO",
    "DD": "DD",
    "TD": "TD",
    "BLK_SHOTS": "BLK_SHOTS",
    "INT": "INT",
    "OUTS": "OUTS",
    "DF": "DF",
}


def format_market_name(market: str) -> str:
    """Convert internal market name to display name."""
    return MARKET_DISPLAY_NAMES.get(market, market.upper())


async def get_hot_cold_players(
    db: AsyncSession,
    sport_id: Optional[int] = None,
    min_picks: int = 3,
    hot_streak_threshold: int = 3,
    cold_streak_threshold: int = -3,
    hot_rate_threshold: float = 0.70,
    cold_rate_threshold: float = 0.40,
    limit: int = 25,
) -> dict:
    """
    Get hot and cold players based on recent performance (player-level, all markets combined).
    
    Args:
        db: Database session
        sport_id: Filter to specific sport (optional)
        min_picks: Minimum picks in 7 days to qualify
        hot_streak_threshold: Minimum streak to be "hot"
        cold_streak_threshold: Maximum streak to be "cold" (negative)
        hot_rate_threshold: Minimum 7-day hit rate to be "hot"
        cold_rate_threshold: Maximum 7-day hit rate to be "cold"
        limit: Max results per category
    
    Returns:
        {"hot": [...], "cold": [...]}
    """
    base_query = (
        select(
            Player.name.label("player_name"),
            Team.name.label("team"),
            Sport.league_code.label("sport"),
            PlayerHitRate.hit_rate_7d,
            PlayerHitRate.hits_7d,
            PlayerHitRate.total_7d,
            PlayerHitRate.current_streak,
            PlayerHitRate.last_5_results,
            PlayerHitRate.hit_rate_all,
        )
        .join(Player, PlayerHitRate.player_id == Player.id)
        .join(Sport, PlayerHitRate.sport_id == Sport.id)
        .outerjoin(Team, Player.team_id == Team.id)
        .where(PlayerHitRate.total_7d >= min_picks)
    )
    
    if sport_id:
        base_query = base_query.where(PlayerHitRate.sport_id == sport_id)
    
    # Hot players
    hot_query = (
        base_query
        .where(
            or_(
                PlayerHitRate.current_streak >= hot_streak_threshold,
                PlayerHitRate.hit_rate_7d >= hot_rate_threshold,
            )
        )
        .order_by(PlayerHitRate.current_streak.desc(), PlayerHitRate.hit_rate_7d.desc())
        .limit(limit)
    )
    
    # Cold players
    cold_query = (
        base_query
        .where(
            or_(
                PlayerHitRate.current_streak <= cold_streak_threshold,
                PlayerHitRate.hit_rate_7d <= cold_rate_threshold,
            )
        )
        .order_by(PlayerHitRate.current_streak.asc(), PlayerHitRate.hit_rate_7d.asc())
        .limit(limit)
    )
    
    hot_result = await db.execute(hot_query)
    cold_result = await db.execute(cold_query)
    
    def format_player(row) -> dict:
        return {
            "player_name": row.player_name,
            "team": row.team,
            "sport": row.sport,
            "hit_rate_7d": round(row.hit_rate_7d * 100, 1) if row.hit_rate_7d else None,
            "picks_7d": f"{row.hits_7d}/{row.total_7d}",
            "streak": row.current_streak,
            "last_5": row.last_5_results,
            "hit_rate_all": round(row.hit_rate_all * 100, 1) if row.hit_rate_all else None,
        }
    
    return {
        "hot": [format_player(r) for r in hot_result.all()],
        "cold": [format_player(r) for r in cold_result.all()],
    }


async def get_hot_cold_players_by_market(
    db: AsyncSession,
    sport_id: Optional[int] = None,
    market: Optional[str] = None,
    side: Optional[str] = None,
    min_picks: int = 3,
    hot_streak_threshold: int = 3,
    cold_streak_threshold: int = -3,
    hot_rate_threshold: float = 0.70,
    cold_rate_threshold: float = 0.40,
    limit: int = 25,
) -> dict:
    """
    Get hot and cold players by specific market (stat type).
    
    Example output:
        "CJ McCollum – 6/6 on 3PM OVER (100% hit rate)"
    
    Args:
        db: Database session
        sport_id: Filter to specific sport (optional)
        market: Filter to specific market like "PTS", "REB", "3PM" (optional)
        side: Filter to "over" or "under" (optional)
        min_picks: Minimum picks in 7 days to qualify
        hot_streak_threshold: Minimum streak to be "hot"
        cold_streak_threshold: Maximum streak to be "cold" (negative)
        hot_rate_threshold: Minimum 7-day hit rate to be "hot"
        cold_rate_threshold: Maximum 7-day hit rate to be "cold"
        limit: Max results per category
    
    Returns:
        {"hot": [...], "cold": [...]}
    """
    base_query = (
        select(
            PlayerMarketHitRate.player_id,
            Player.name.label("player_name"),
            Team.name.label("team"),
            Sport.league_code.label("sport"),
            PlayerMarketHitRate.market,
            PlayerMarketHitRate.side,
            PlayerMarketHitRate.hit_rate_7d,
            PlayerMarketHitRate.hits_7d,
            PlayerMarketHitRate.total_7d,
            PlayerMarketHitRate.current_streak,
            PlayerMarketHitRate.last_5_results,
            PlayerMarketHitRate.hit_rate_all,
        )
        .join(Player, PlayerMarketHitRate.player_id == Player.id)
        .join(Sport, PlayerMarketHitRate.sport_id == Sport.id)
        .outerjoin(Team, Player.team_id == Team.id)
        .where(PlayerMarketHitRate.total_7d >= min_picks)
    )
    
    if sport_id:
        base_query = base_query.where(PlayerMarketHitRate.sport_id == sport_id)
    if market:
        base_query = base_query.where(PlayerMarketHitRate.market == market.lower())
    if side:
        base_query = base_query.where(PlayerMarketHitRate.side == side.lower())
    
    # Hot players
    hot_query = (
        base_query
        .where(
            or_(
                PlayerMarketHitRate.current_streak >= hot_streak_threshold,
                PlayerMarketHitRate.hit_rate_7d >= hot_rate_threshold,
            )
        )
        .order_by(
            PlayerMarketHitRate.current_streak.desc(),
            PlayerMarketHitRate.hit_rate_7d.desc(),
        )
        .limit(limit)
    )
    
    # Cold players
    cold_query = (
        base_query
        .where(
            or_(
                PlayerMarketHitRate.current_streak <= cold_streak_threshold,
                PlayerMarketHitRate.hit_rate_7d <= cold_rate_threshold,
            )
        )
        .order_by(
            PlayerMarketHitRate.current_streak.asc(),
            PlayerMarketHitRate.hit_rate_7d.asc(),
        )
        .limit(limit)
    )
    
    hot_result = await db.execute(hot_query)
    cold_result = await db.execute(cold_query)
    
    def format_player(row) -> dict:
        return {
            "player_id": row.player_id,
            "player_name": row.player_name,
            "team": row.team,
            "sport": row.sport,
            "market": format_market_name(row.market),
            "side": row.side.upper() if row.side else None,
            "display": f"{row.player_name} – {format_market_name(row.market)} {row.side.upper() if row.side else ''}",
            "hit_rate_7d": row.hit_rate_7d,  # Raw value (0-1) for API compatibility
            "hit_rate_7d_pct": round(row.hit_rate_7d * 100, 1) if row.hit_rate_7d else None,
            "hits_7d": row.hits_7d,
            "total_7d": row.total_7d,
            "picks_7d": f"{row.hits_7d}/{row.total_7d}",
            "current_streak": row.current_streak,
            "last_5_results": row.last_5_results,
            "hit_rate_all": round(row.hit_rate_all * 100, 1) if row.hit_rate_all else None,
        }
    
    return {
        "hot": [format_player(r) for r in hot_result.all()],
        "cold": [format_player(r) for r in cold_result.all()],
    }


async def get_hot_players_with_best_market(
    db: AsyncSession,
    sport_id: int,
    min_picks: int = 3,
    hot_rate_threshold: float = 0.70,
    hot_streak_threshold: int = 3,
    limit: int = 10,
) -> list[dict]:
    """
    Get hot players with their best-performing market (stat_type + side).
    
    For each player, finds the market where they have the highest hit rate.
    
    Args:
        db: Database session
        sport_id: Sport ID to filter by
        min_picks: Minimum picks in 7 days to qualify
        hot_rate_threshold: Minimum 7-day hit rate to be "hot"
        hot_streak_threshold: Minimum streak to be "hot"
        limit: Maximum players to return
    
    Returns:
        List of hot players with their best market info
    """
    # Query all market hit rates for players meeting hot criteria
    query = (
        select(
            Player.id.label("player_id"),
            Player.name.label("player_name"),
            PlayerMarketHitRate.market,
            PlayerMarketHitRate.side,
            PlayerMarketHitRate.hit_rate_7d,
            PlayerMarketHitRate.hits_7d,
            PlayerMarketHitRate.total_7d,
            PlayerMarketHitRate.current_streak,
            PlayerMarketHitRate.last_5_results,
        )
        .join(Player, PlayerMarketHitRate.player_id == Player.id)
        .where(
            PlayerMarketHitRate.sport_id == sport_id,
            PlayerMarketHitRate.total_7d >= min_picks,
            or_(
                PlayerMarketHitRate.hit_rate_7d >= hot_rate_threshold,
                PlayerMarketHitRate.current_streak >= hot_streak_threshold,
            ),
        )
        .order_by(
            PlayerMarketHitRate.hit_rate_7d.desc(),
            PlayerMarketHitRate.current_streak.desc(),
        )
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    # Group by player and keep best market per player
    seen_players: dict[int, dict] = {}
    
    for row in rows:
        player_id = row.player_id
        
        # Only keep the first (best) market for each player
        if player_id in seen_players:
            continue
        
        seen_players[player_id] = {
            "player_id": player_id,
            "player_name": row.player_name,
            "stat_type": format_market_name(row.market),
            "side": row.side,  # Keep as lowercase for frontend
            "hit_rate_7d": row.hit_rate_7d,  # Keep as decimal (0-1)
            "hits_7d": row.hits_7d,
            "total_7d": row.total_7d,
            "current_streak": row.current_streak,
            "last_5": row.last_5_results,
        }
        
        if len(seen_players) >= limit:
            break
    
    return list(seen_players.values())


async def update_player_market_hit_rate(
    db: AsyncSession,
    player_id: int,
    sport_id: int,
    market: str,
    side: str,
    hit: bool,
) -> PlayerMarketHitRate:
    """
    Update player market hit rate after a pick settles.
    
    Called by the grading/settlement job.
    
    Args:
        db: Database session
        player_id: Player ID
        sport_id: Sport ID
        market: Market type (e.g., "PTS", "REB", "3PM")
        side: "over" or "under"
        hit: Whether the pick hit
    
    Returns:
        Updated PlayerMarketHitRate record
    """
    # Normalize inputs
    market = market.lower()
    side = side.lower()
    
    # Get or create the record
    result = await db.execute(
        select(PlayerMarketHitRate)
        .where(
            PlayerMarketHitRate.player_id == player_id,
            PlayerMarketHitRate.sport_id == sport_id,
            PlayerMarketHitRate.market == market,
            PlayerMarketHitRate.side == side,
        )
    )
    record = result.scalar_one_or_none()
    
    if not record:
        record = PlayerMarketHitRate(
            player_id=player_id,
            sport_id=sport_id,
            market=market,
            side=side,
        )
        db.add(record)
    
    # Update counts
    record.total_7d += 1
    record.total_all += 1
    if hit:
        record.hits_7d += 1
        record.hits_all += 1
    
    # Recalculate hit rates
    record.recalculate_hit_rates()
    
    # Update streak
    record.update_streak(hit)
    
    # Update last 5
    record.update_last_5(hit)
    
    # Update timestamp
    record.last_pick_at = datetime.now(timezone.utc)
    
    await db.flush()
    
    logger.info(
        f"Updated market hit rate: player_id={player_id}, {market} {side}, "
        f"hit={hit}, streak={record.current_streak}, rate_7d={record.hit_rate_7d}"
    )
    
    return record
