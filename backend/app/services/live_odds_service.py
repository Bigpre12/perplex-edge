"""
Live Odds Service - Real-time odds lookup for parlay builder.

Provides fresh odds for parlay legs with short TTL caching.
"""

from datetime import datetime, timedelta
from typing import Optional
import asyncio

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.cache import cache
from app.models import Line, Market, Player, Game
from app.services.parlay_service import american_to_decimal, decimal_to_american

logger = get_logger(__name__)

# =============================================================================
# Odds Normalizer - Convert provider data to standard format
# =============================================================================

class NormalizedOdds:
    """Standard odds format across all providers."""
    
    def __init__(
        self,
        sport_key: str,
        game_id: int,
        player_id: Optional[int],
        market_type: str,
        stat_type: Optional[str],
        line_value: Optional[float],
        side: str,
        sportsbook: str,
        american_odds: int,
        decimal_odds: float,
        implied_prob: float,
        last_update: datetime,
        is_stale: bool = False,
    ):
        self.sport_key = sport_key
        self.game_id = game_id
        self.player_id = player_id
        self.market_type = market_type
        self.stat_type = stat_type
        self.line_value = line_value
        self.side = side
        self.sportsbook = sportsbook
        self.american_odds = american_odds
        self.decimal_odds = decimal_odds
        self.implied_prob = implied_prob
        self.last_update = last_update
        self.is_stale = is_stale
    
    def to_dict(self) -> dict:
        return {
            "sport_key": self.sport_key,
            "game_id": self.game_id,
            "player_id": self.player_id,
            "market_type": self.market_type,
            "stat_type": self.stat_type,
            "line_value": self.line_value,
            "side": self.side,
            "sportsbook": self.sportsbook,
            "american_odds": self.american_odds,
            "decimal_odds": round(self.decimal_odds, 3),
            "implied_prob": round(self.implied_prob, 4),
            "last_update": self.last_update.isoformat(),
            "is_stale": self.is_stale,
        }


def normalize_odds(american_odds: int) -> tuple[float, float]:
    """
    Normalize American odds to decimal and implied probability.
    
    Returns:
        Tuple of (decimal_odds, implied_probability)
    """
    decimal_odds = american_to_decimal(american_odds)
    implied_prob = 1 / decimal_odds
    return decimal_odds, implied_prob


def calculate_odds_movement(old_odds: int, new_odds: int) -> dict:
    """
    Calculate odds movement between two American odds values.
    
    Returns:
        Dict with direction, magnitude, and display string
    """
    old_decimal = american_to_decimal(old_odds)
    new_decimal = american_to_decimal(new_odds)
    
    pct_change = ((new_decimal - old_decimal) / old_decimal) * 100
    
    if abs(pct_change) < 1:
        direction = "stable"
    elif new_decimal > old_decimal:
        direction = "up"  # Better payout
    else:
        direction = "down"  # Worse payout
    
    # Format display string
    old_str = f"+{old_odds}" if old_odds > 0 else str(old_odds)
    new_str = f"+{new_odds}" if new_odds > 0 else str(new_odds)
    
    return {
        "direction": direction,
        "magnitude": abs(pct_change),
        "old_odds": old_odds,
        "new_odds": new_odds,
        "display": f"{old_str} → {new_str}" if direction != "stable" else None,
        "favorable": direction == "up",
    }


# =============================================================================
# Live Odds Cache
# =============================================================================

# Cache key format: live_odds:{game_id}:{player_id}:{stat_type}:{line}:{side}
LIVE_ODDS_TTL = 30  # 30 seconds TTL for live odds
STALE_THRESHOLD = timedelta(minutes=5)  # Mark as stale if older than 5 minutes


def _build_leg_cache_key(
    game_id: int,
    player_id: Optional[int],
    stat_type: Optional[str],
    line_value: Optional[float],
    side: str,
) -> str:
    """Build a unique cache key for a parlay leg."""
    parts = [
        "live_odds",
        str(game_id),
        str(player_id or "game"),
        stat_type or "spread",
        str(line_value) if line_value is not None else "ml",
        side,
    ]
    return ":".join(parts)


async def get_cached_odds(key: str) -> Optional[dict]:
    """Get cached odds if available."""
    try:
        return await cache.get(key)
    except Exception as e:
        logger.warning(f"Cache get failed: {e}")
        return None


async def set_cached_odds(key: str, data: dict) -> None:
    """Cache odds with short TTL."""
    try:
        await cache.set(key, data, ttl=LIVE_ODDS_TTL)
    except Exception as e:
        logger.warning(f"Cache set failed: {e}")


# =============================================================================
# Database Odds Lookup
# =============================================================================

async def fetch_current_odds_for_leg(
    db: AsyncSession,
    game_id: int,
    player_id: Optional[int],
    stat_type: Optional[str],
    line_value: Optional[float],
    side: str,
    preferred_books: Optional[list[str]] = None,
) -> list[dict]:
    """
    Fetch current odds for a specific leg from the database.
    
    Args:
        db: Database session
        game_id: Game ID
        player_id: Player ID (for player props)
        stat_type: Stat type (for player props)
        line_value: Line value
        side: "over" or "under" for props, "home"/"away" for spread/ML
        preferred_books: List of preferred sportsbooks (ordered by preference)
    
    Returns:
        List of odds from different sportsbooks, sorted by preference
    """
    if preferred_books is None:
        preferred_books = ["fanduel", "draftkings", "betmgm", "caesars", "pointsbet"]
    
    # Build query
    query = (
        select(Line, Market, Player, Game)
        .join(Market, Line.market_id == Market.id)
        .join(Game, Line.game_id == Game.id)
        .outerjoin(Player, Line.player_id == Player.id)
        .where(
            and_(
                Line.game_id == game_id,
                Line.is_current == True,
                Line.side == side,
            )
        )
    )
    
    # Add player filter for player props
    if player_id:
        query = query.where(Line.player_id == player_id)
        if stat_type:
            query = query.where(Market.stat_type == stat_type)
        if line_value is not None:
            # Allow small variance in line (0.5 points)
            query = query.where(
                and_(
                    Line.line_value >= line_value - 0.5,
                    Line.line_value <= line_value + 0.5,
                )
            )
    else:
        query = query.where(Line.player_id.is_(None))
    
    result = await db.execute(query)
    rows = result.all()
    
    now = datetime.utcnow()
    odds_list = []
    
    for line, market, player, game in rows:
        decimal_odds, implied_prob = normalize_odds(int(line.odds))
        is_stale = (now - line.fetched_at) > STALE_THRESHOLD
        
        odds_list.append({
            "sportsbook": line.sportsbook,
            "american_odds": int(line.odds),
            "decimal_odds": round(decimal_odds, 3),
            "implied_prob": round(implied_prob, 4),
            "line_value": line.line_value,
            "last_update": line.fetched_at,
            "is_stale": is_stale,
            "game_id": game.id,
            "player_id": player.id if player else None,
            "player_name": player.name if player else None,
            "stat_type": market.stat_type,
            "market_type": market.market_type,
        })
    
    # Sort by preferred books
    def book_order(item):
        try:
            return preferred_books.index(item["sportsbook"].lower())
        except ValueError:
            return len(preferred_books)
    
    odds_list.sort(key=book_order)
    
    return odds_list


async def fetch_best_odds_for_leg(
    db: AsyncSession,
    game_id: int,
    player_id: Optional[int],
    stat_type: Optional[str],
    line_value: Optional[float],
    side: str,
) -> Optional[dict]:
    """
    Fetch the best (highest payout) current odds for a leg.
    
    Returns:
        Best odds dict or None if not found
    """
    odds_list = await fetch_current_odds_for_leg(
        db, game_id, player_id, stat_type, line_value, side
    )
    
    if not odds_list:
        return None
    
    # Find best odds (highest decimal = best payout)
    best = max(odds_list, key=lambda x: x["decimal_odds"])
    
    # Add comparison to other books
    best["all_books"] = odds_list
    best["is_best"] = True
    
    return best


# =============================================================================
# Parlay Quote Service
# =============================================================================

async def quote_parlay_legs(
    db: AsyncSession,
    legs: list[dict],
    use_cache: bool = True,
) -> dict:
    """
    Get real-time odds quote for a list of parlay legs.
    
    Args:
        db: Database session
        legs: List of leg specifications:
            - game_id: int
            - player_id: Optional[int]
            - stat_type: Optional[str]
            - line_value: Optional[float]
            - side: str
            - model_odds: Optional[int] - Original odds from model pick
            - model_prob: Optional[float] - Model probability
        use_cache: Whether to use cached odds
    
    Returns:
        Dict with:
        - legs: List of legs with current odds
        - parlay_odds: Combined parlay odds
        - parlay_decimal: Decimal odds
        - parlay_probability: Combined probability (independent)
        - has_movement: Whether any odds moved
        - stale_legs: Count of legs with stale odds
    """
    quoted_legs = []
    total_decimal = 1.0
    total_model_prob = 1.0
    has_movement = False
    stale_count = 0
    
    for i, leg in enumerate(legs):
        # Build cache key
        cache_key = _build_leg_cache_key(
            leg["game_id"],
            leg.get("player_id"),
            leg.get("stat_type"),
            leg.get("line_value"),
            leg["side"],
        )
        
        # Try cache first
        cached = None
        if use_cache:
            cached = await get_cached_odds(cache_key)
        
        if cached:
            current_odds = cached
        else:
            # Fetch from database
            current_odds = await fetch_best_odds_for_leg(
                db,
                leg["game_id"],
                leg.get("player_id"),
                leg.get("stat_type"),
                leg.get("line_value"),
                leg["side"],
            )
            
            # Cache result
            if current_odds and use_cache:
                await set_cached_odds(cache_key, current_odds)
        
        # Build quoted leg
        model_odds = leg.get("model_odds")
        model_prob = leg.get("model_prob", 0.5)
        
        if current_odds:
            # Check for movement
            movement = None
            if model_odds and current_odds["american_odds"] != model_odds:
                movement = calculate_odds_movement(model_odds, current_odds["american_odds"])
                has_movement = True
            
            # Calculate edge with current odds
            decimal_odds = current_odds["decimal_odds"]
            implied_prob = current_odds["implied_prob"]
            edge = model_prob - implied_prob
            
            quoted_leg = {
                "index": i,
                "game_id": leg["game_id"],
                "player_id": leg.get("player_id"),
                "player_name": current_odds.get("player_name"),
                "stat_type": current_odds.get("stat_type"),
                "line_value": current_odds.get("line_value"),
                "side": leg["side"],
                "sportsbook": current_odds["sportsbook"],
                "current_odds": current_odds["american_odds"],
                "decimal_odds": decimal_odds,
                "implied_prob": round(implied_prob, 4),
                "model_odds": model_odds,
                "model_prob": round(model_prob, 4),
                "edge": round(edge, 4),
                "movement": movement,
                "is_stale": current_odds.get("is_stale", False),
                "last_update": current_odds["last_update"].isoformat() if isinstance(current_odds["last_update"], datetime) else current_odds["last_update"],
                "found": True,
            }
            
            if current_odds.get("is_stale"):
                stale_count += 1
            
            total_decimal *= decimal_odds
            total_model_prob *= model_prob
        else:
            # Odds not found - use model odds as fallback
            fallback_odds = model_odds if model_odds else -110
            decimal_odds, implied_prob = normalize_odds(fallback_odds)
            
            quoted_leg = {
                "index": i,
                "game_id": leg["game_id"],
                "player_id": leg.get("player_id"),
                "stat_type": leg.get("stat_type"),
                "line_value": leg.get("line_value"),
                "side": leg["side"],
                "sportsbook": "unknown",
                "current_odds": fallback_odds,
                "decimal_odds": decimal_odds,
                "implied_prob": round(implied_prob, 4),
                "model_odds": model_odds,
                "model_prob": round(model_prob, 4),
                "edge": round(model_prob - implied_prob, 4),
                "movement": None,
                "is_stale": True,
                "last_update": None,
                "found": False,
            }
            
            stale_count += 1
            total_decimal *= decimal_odds
            total_model_prob *= model_prob
        
        quoted_legs.append(quoted_leg)
    
    # Calculate combined parlay odds
    parlay_american = decimal_to_american(total_decimal)
    implied_parlay_prob = 1 / total_decimal
    parlay_ev = total_model_prob - implied_parlay_prob
    
    return {
        "legs": quoted_legs,
        "leg_count": len(quoted_legs),
        "parlay_odds": parlay_american,
        "parlay_decimal": round(total_decimal, 3),
        "parlay_probability": round(total_model_prob, 4),
        "implied_probability": round(implied_parlay_prob, 4),
        "parlay_ev": round(parlay_ev, 4),
        "has_movement": has_movement,
        "stale_legs": stale_count,
        "all_fresh": stale_count == 0,
        "quoted_at": datetime.utcnow().isoformat(),
    }


# =============================================================================
# Odds Feed Health Check
# =============================================================================

async def check_odds_freshness(db: AsyncSession, sport_id: Optional[int] = None) -> dict:
    """
    Check overall freshness of odds data.
    
    Returns:
        Dict with health status and stats
    """
    from sqlalchemy import func
    
    now = datetime.utcnow()
    
    # Base query for current lines
    query = select(
        func.count(Line.id).label("total"),
        func.min(Line.fetched_at).label("oldest"),
        func.max(Line.fetched_at).label("newest"),
        func.count().filter(Line.fetched_at > now - STALE_THRESHOLD).label("fresh"),
    ).where(Line.is_current == True)
    
    if sport_id:
        query = query.join(Market, Line.market_id == Market.id).where(Market.sport_id == sport_id)
    
    result = await db.execute(query)
    row = result.one()
    
    total = row.total or 0
    fresh = row.fresh or 0
    stale = total - fresh
    oldest = row.oldest
    newest = row.newest
    
    # Calculate health status
    if total == 0:
        status = "no_data"
    elif fresh / total >= 0.9:
        status = "healthy"
    elif fresh / total >= 0.5:
        status = "degraded"
    else:
        status = "stale"
    
    return {
        "status": status,
        "total_lines": total,
        "fresh_lines": fresh,
        "stale_lines": stale,
        "freshness_pct": round((fresh / total * 100) if total > 0 else 0, 1),
        "oldest_update": oldest.isoformat() if oldest else None,
        "newest_update": newest.isoformat() if newest else None,
        "stale_threshold_minutes": int(STALE_THRESHOLD.total_seconds() / 60),
        "checked_at": now.isoformat(),
    }
