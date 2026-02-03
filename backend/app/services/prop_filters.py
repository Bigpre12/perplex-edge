"""
Prop filtering and deduplication utilities.

These functions are used to ensure only fresh, unique props are returned
to the frontend, filtering out stale data and removing duplicates.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

# Maximum age for odds to be considered fresh
# Tightened from 30min to 5min to ensure users see fresh lines only
STALE_ODDS_MAX_AGE = timedelta(minutes=5)

# Maximum age for picks to be considered fresh
STALE_PICK_MAX_AGE = timedelta(hours=24)

# Injury statuses that should exclude a player from props
EXCLUDED_INJURY_STATUSES = ["OUT", "DOUBTFUL", "QUESTIONABLE", "GTD", "DAY_TO_DAY"]

# Game statuses that are valid for showing props
VALID_GAME_STATUSES = ["scheduled", "pregame"]


# =============================================================================
# Freshness Checks
# =============================================================================

def is_fresh_prop(
    pick: Any,
    game: Any,
    line_fetched_at: Optional[datetime] = None,
    now: Optional[datetime] = None,
) -> bool:
    """
    Check if a prop should be shown to users.
    
    A prop is considered fresh if:
    1. The game hasn't started yet
    2. The game status is scheduled/pregame (not in_progress/final)
    3. The odds were recently updated (if we have the timestamp)
    4. The pick was recently generated
    
    Args:
        pick: ModelPick object with generated_at field
        game: Game object with start_time and status fields
        line_fetched_at: Optional timestamp of when the line odds were fetched
        now: Optional current time (for testing), defaults to UTC now
    
    Returns:
        True if the prop is fresh and should be shown, False otherwise
    """
    if now is None:
        now = datetime.now(timezone.utc)
    
    # Ensure now is timezone-aware
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    
    # 1) Game hasn't started
    if game.start_time:
        game_start = game.start_time
        # Make timezone-aware if needed
        if game_start.tzinfo is None:
            game_start = game_start.replace(tzinfo=timezone.utc)
        
        if game_start <= now:
            logger.debug(f"Prop filtered: game started (start_time={game_start}, now={now})")
            return False
    
    # 2) Game status is valid (not in_progress, final, etc.)
    if game.status and game.status.lower() not in [s.lower() for s in VALID_GAME_STATUSES]:
        logger.debug(f"Prop filtered: invalid game status ({game.status})")
        return False
    
    # 3) Odds recently updated (if we have the timestamp)
    if line_fetched_at:
        if line_fetched_at.tzinfo is None:
            line_fetched_at = line_fetched_at.replace(tzinfo=timezone.utc)
        
        if line_fetched_at < now - STALE_ODDS_MAX_AGE:
            logger.debug(f"Prop filtered: stale odds (fetched_at={line_fetched_at})")
            return False
    
    # 4) Pick was recently generated
    if pick.generated_at:
        generated_at = pick.generated_at
        if generated_at.tzinfo is None:
            generated_at = generated_at.replace(tzinfo=timezone.utc)
        
        if generated_at < now - STALE_PICK_MAX_AGE:
            logger.debug(f"Prop filtered: stale pick (generated_at={generated_at})")
            return False
    
    return True


def is_game_fresh(game: Any, now: Optional[datetime] = None) -> bool:
    """
    Check if a game is fresh (hasn't started and is in valid status).
    
    Args:
        game: Game object with start_time and status fields
        now: Optional current time (for testing), defaults to UTC now
    
    Returns:
        True if the game is fresh, False otherwise
    """
    if now is None:
        now = datetime.now(timezone.utc)
    
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    
    # Check start time
    if game.start_time:
        game_start = game.start_time
        if game_start.tzinfo is None:
            game_start = game_start.replace(tzinfo=timezone.utc)
        
        if game_start <= now:
            return False
    
    # Check status
    if game.status and game.status.lower() not in [s.lower() for s in VALID_GAME_STATUSES]:
        return False
    
    return True


# =============================================================================
# Deduplication
# =============================================================================

def dedupe_props(props: list, key_fn=None) -> list:
    """
    Remove duplicate props, keeping the one with the best expected value.
    
    By default, deduplicates by (player_id, stat_type, line_value) key.
    When multiple props have the same key, keeps the one with highest EV.
    
    Args:
        props: List of prop objects (dicts or objects with player_id, stat_type, 
               line_value, and expected_value attributes)
        key_fn: Optional custom key function. If None, uses default key.
    
    Returns:
        Deduplicated list of props
    """
    if not props:
        return []
    
    seen: dict = {}
    
    for prop in props:
        # Get key
        if key_fn:
            key = key_fn(prop)
        else:
            key = _get_default_prop_key(prop)
        
        # Get EV for comparison
        ev = _get_prop_ev(prop)
        
        # Keep if new or better EV
        if key not in seen:
            seen[key] = prop
        else:
            existing_ev = _get_prop_ev(seen[key])
            if ev > existing_ev:
                seen[key] = prop
    
    result = list(seen.values())
    
    if len(result) < len(props):
        logger.info(f"Deduped props: {len(props)} -> {len(result)} ({len(props) - len(result)} duplicates removed)")
    
    return result


def _get_default_prop_key(prop) -> tuple:
    """
    Get the default deduplication key for a prop.
    
    Key is (sport_id, game_id, player_id, stat_type, line_value).
    Including sport_id and game_id ensures canonical uniqueness across sports.
    """
    # Handle both dict and object access
    if isinstance(prop, dict):
        sport_id = prop.get("sport_id")
        game_id = prop.get("game_id")
        player_id = prop.get("player_id")
        stat_type = prop.get("stat_type")
        line_value = prop.get("line_value") or prop.get("line")
    else:
        sport_id = getattr(prop, "sport_id", None)
        game_id = getattr(prop, "game_id", None)
        player_id = getattr(prop, "player_id", None)
        stat_type = getattr(prop, "stat_type", None)
        line_value = getattr(prop, "line_value", None) or getattr(prop, "line", None)
    
    return (sport_id, game_id, player_id, stat_type, line_value)


def _get_prop_ev(prop) -> float:
    """
    Get the expected value for a prop.
    """
    if isinstance(prop, dict):
        return prop.get("expected_value", 0.0) or 0.0
    else:
        return getattr(prop, "expected_value", 0.0) or 0.0


def dedupe_response_items(items: list) -> list:
    """
    Deduplicate response items (PlayerPropPick schema objects or dicts).
    
    This is for deduping at the response level after building the full
    response objects. Uses (player_id, stat_type, line) as the key.
    
    Args:
        items: List of PlayerPropPick-like dicts or objects
    
    Returns:
        Deduplicated list
    """
    if not items:
        return []
    
    seen: dict = {}
    
    for item in items:
        # Handle both dict and Pydantic model access
        if isinstance(item, dict):
            player_id = item.get("player_id")
            stat_type = item.get("stat_type")
            line = item.get("line")
            ev = item.get("expected_value", 0.0) or 0.0
        else:
            player_id = getattr(item, "player_id", None)
            stat_type = getattr(item, "stat_type", None)
            line = getattr(item, "line", None)
            ev = getattr(item, "expected_value", 0.0) or 0.0
        
        key = (player_id, stat_type, line)
        
        if key not in seen:
            seen[key] = item
        else:
            # Keep the one with higher EV
            existing_ev = 0.0
            if isinstance(seen[key], dict):
                existing_ev = seen[key].get("expected_value", 0.0) or 0.0
            else:
                existing_ev = getattr(seen[key], "expected_value", 0.0) or 0.0
            
            if ev > existing_ev:
                seen[key] = item
    
    result = list(seen.values())
    
    if len(result) < len(items):
        logger.info(f"Deduped response items: {len(items)} -> {len(result)}")
    
    return result


def dedupe_player_props(picks: list) -> list:
    """
    Deduplicate player prop picks, merging book_lines from duplicates.
    
    This is specifically for PlayerPropPick Pydantic models from the public API.
    Uses (game_id, player_id, stat_type, line) as the canonical identity.
    
    - Merges book_lines from all duplicates into one list
    - Keeps the best EV/Kelly values across all books
    - Updates best_book to reflect the merged best option
    
    Args:
        picks: List of PlayerPropPick Pydantic models
    
    Returns:
        Deduplicated list with merged book_lines
    """
    if not picks:
        return []
    
    grouped: dict = {}
    
    for pick in picks:
        key = (pick.game_id, pick.player_id, pick.stat_type, pick.line)
        
        if key not in grouped:
            grouped[key] = pick
        else:
            existing = grouped[key]
            
            # Merge book_lines from the duplicate into the existing pick
            if pick.book_lines:
                if existing.book_lines is None:
                    existing.book_lines = list(pick.book_lines)
                else:
                    # Avoid duplicate books by checking sportsbook name
                    existing_books = {bl.sportsbook for bl in existing.book_lines}
                    for bl in pick.book_lines:
                        if bl.sportsbook not in existing_books:
                            existing.book_lines.append(bl)
                            existing_books.add(bl.sportsbook)
            
            # Keep the higher EV version's stats
            if pick.expected_value > existing.expected_value:
                existing.expected_value = pick.expected_value
                existing.model_probability = pick.model_probability
                existing.implied_probability = pick.implied_probability
                existing.kelly_units = pick.kelly_units
                existing.kelly_edge_pct = pick.kelly_edge_pct
                existing.kelly_risk_level = pick.kelly_risk_level
                existing.best_book = pick.best_book
                existing.odds = pick.odds
    
    result = list(grouped.values())
    
    if len(result) < len(picks):
        logger.info(f"Deduped player props: {len(picks)} -> {len(result)} (merged book_lines)")
    
    return result


# =============================================================================
# Combined Filtering
# =============================================================================

def filter_and_dedupe_props(
    props: list,
    games_by_id: dict = None,
    fresh_only: bool = True,
    dedupe: bool = True,
) -> list:
    """
    Apply both freshness filtering and deduplication to a list of props.
    
    Args:
        props: List of prop objects
        games_by_id: Dict mapping game_id to Game object (for freshness check)
        fresh_only: If True, filter out stale props
        dedupe: If True, remove duplicates
    
    Returns:
        Filtered and deduplicated list of props
    """
    result = props
    
    # Apply freshness filter
    if fresh_only and games_by_id:
        result = [
            p for p in result
            if is_fresh_prop(
                p,
                games_by_id.get(getattr(p, "game_id", None) or p.get("game_id")),
            )
        ]
        logger.info(f"Fresh filter: {len(props)} -> {len(result)}")
    
    # Apply deduplication
    if dedupe:
        result = dedupe_props(result)
    
    return result
