"""
Watchlist alert service - Checks watchlists periodically and sends alerts for new matches.

This service runs in the background and:
1. Queries all watchlists with alerts enabled
2. For each watchlist, counts current matching picks
3. If matches increased since last check, sends Discord alert
4. Updates last_match_count and last_notified_at
"""

import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Watchlist, Sport, ModelPick, Player, Game, Market
from app.services.alerts_service import send_watchlist_alert

logger = logging.getLogger(__name__)


# =============================================================================
# Main Alert Check Function
# =============================================================================

async def check_watchlists_and_alert(db: AsyncSession) -> dict:
    """
    Check all watchlists with alerts enabled and send notifications for new matches.
    
    This function:
    1. Queries watchlists where alert_enabled=True and alert_discord_webhook is set
    2. For each watchlist, counts current picks matching the filters
    3. If current_count > last_match_count, finds the new picks
    4. Sends Discord alert with new picks
    5. Updates last_match_count and last_notified_at
    
    Returns:
        Summary dict with watchlists_checked, alerts_sent, total_new_matches
    """
    logger.info("[watchlist_alert] Starting watchlist alert check...")
    
    # Get all watchlists with alerts enabled and webhook configured
    result = await db.execute(
        select(Watchlist).where(
            and_(
                Watchlist.alert_enabled == True,
                Watchlist.alert_discord_webhook.isnot(None),
                Watchlist.alert_discord_webhook != "",
            )
        )
    )
    watchlists = result.scalars().all()
    
    if not watchlists:
        logger.debug("[watchlist_alert] No watchlists with alerts enabled")
        return {"watchlists_checked": 0, "alerts_sent": 0, "total_new_matches": 0}
    
    watchlists_checked = 0
    alerts_sent = 0
    total_new_matches = 0
    
    for watchlist in watchlists:
        try:
            # Count current matches for this watchlist
            current_count, matching_picks = await get_matching_picks(db, watchlist)
            watchlists_checked += 1
            
            # Check if there are new matches
            previous_count = watchlist.last_match_count or 0
            new_count = max(0, current_count - previous_count)
            
            if new_count > 0 and current_count > previous_count:
                logger.info(
                    f"[watchlist_alert] '{watchlist.name}': {new_count} new matches "
                    f"({previous_count} -> {current_count})"
                )
                
                # Get sport name if available
                sport_name = None
                if watchlist.sport_id:
                    sport = await db.get(Sport, watchlist.sport_id)
                    if sport:
                        sport_name = sport.name
                
                # Prepare new picks data for alert (take the top new_count picks by EV)
                new_picks_data = [
                    {
                        "player_name": p.get("player_name", "Unknown"),
                        "stat_type": p.get("stat_type", ""),
                        "line": p.get("line", 0),
                        "side": p.get("side", "over"),
                        "ev": p.get("expected_value", 0),
                    }
                    for p in matching_picks[:new_count]
                ]
                
                # Send alert
                success = await send_watchlist_alert(
                    webhook_url=watchlist.alert_discord_webhook,
                    watchlist_name=watchlist.name,
                    new_picks=new_picks_data,
                    total_matches=current_count,
                    sport_name=sport_name,
                )
                
                if success:
                    alerts_sent += 1
                    total_new_matches += new_count
                    
                    # Update last_notified_at
                    watchlist.last_notified_at = datetime.now(timezone.utc).replace(tzinfo=None)
            
            # Always update last_match_count and last_check_at
            watchlist.last_match_count = current_count
            watchlist.last_check_at = datetime.now(timezone.utc).replace(tzinfo=None)
            
        except Exception as e:
            logger.error(f"[watchlist_alert] Error checking watchlist '{watchlist.name}': {e}")
            continue
    
    # Commit all updates
    await db.commit()
    
    logger.info(
        f"[watchlist_alert] Completed: {watchlists_checked} watchlists checked, "
        f"{alerts_sent} alerts sent, {total_new_matches} new matches"
    )
    
    return {
        "watchlists_checked": watchlists_checked,
        "alerts_sent": alerts_sent,
        "total_new_matches": total_new_matches,
    }


# =============================================================================
# Helper Functions
# =============================================================================

async def get_matching_picks(
    db: AsyncSession,
    watchlist: Watchlist,
) -> tuple[int, list[dict]]:
    """
    Get picks matching a watchlist's filters.
    
    Returns:
        Tuple of (count, list of pick dicts sorted by EV desc)
    """
    from pytz import timezone as tz
    
    filters = watchlist.filters or {}
    
    # Eastern timezone for today's date calculation
    EASTERN_TZ = tz("US/Eastern")
    now_et = datetime.now(EASTERN_TZ)
    today_start_et = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start_et = today_start_et + timedelta(days=1)
    
    # Convert to UTC
    today_utc = today_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    tomorrow_utc = tomorrow_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    
    # Build base conditions
    conditions = [
        ModelPick.player_id.isnot(None),  # Player props only
        Game.start_time >= today_utc,
        Game.start_time < tomorrow_utc + timedelta(days=7),  # Include upcoming week
    ]
    
    # Apply sport filter
    sport_id = filters.get("sport_id") or watchlist.sport_id
    if sport_id:
        conditions.append(ModelPick.sport_id == sport_id)
    
    # Apply stat_type filter
    if filters.get("stat_type"):
        conditions.append(Market.stat_type == filters["stat_type"])
    
    # Apply side filter
    if filters.get("side"):
        conditions.append(ModelPick.side == filters["side"])
    
    # Apply min_confidence filter
    min_confidence = filters.get("min_confidence", 0) or 0
    if min_confidence > 0:
        conditions.append(ModelPick.confidence_score >= min_confidence)
    
    # Apply min_ev filter
    min_ev = filters.get("min_ev", 0) or 0
    if min_ev > 0:
        conditions.append(ModelPick.expected_value >= min_ev)
    
    # Query matching picks
    query = (
        select(ModelPick, Player, Market)
        .join(Player, ModelPick.player_id == Player.id)
        .join(Game, ModelPick.game_id == Game.id)
        .join(Market, ModelPick.market_id == Market.id)
        .where(and_(*conditions))
        .order_by(ModelPick.expected_value.desc())
        .limit(100)  # Cap for performance
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    # Build list of pick dicts
    picks = []
    for pick, player, market in rows:
        picks.append({
            "player_name": player.name,
            "stat_type": market.stat_type,
            "line": pick.line_value,
            "side": pick.side,
            "expected_value": pick.expected_value,
            "confidence_score": pick.confidence_score,
        })
    
    return len(rows), picks
