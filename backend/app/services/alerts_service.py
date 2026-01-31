"""
Discord webhook alerts for high-EV picks and important notifications.

Configure by setting DISCORD_WEBHOOK_URL environment variable.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Alert thresholds
HIGH_EV_THRESHOLD = 0.08  # 8%+ EV
LOCK_PARLAY_EV_THRESHOLD = 0.10  # 10%+ parlay EV
HIT_RATE_ALERT_GAMES = 5  # Alert on 100% hit rate over 5+ games


# =============================================================================
# Discord Message Formatting
# =============================================================================

def format_odds(odds: int) -> str:
    """Format American odds."""
    return f"+{odds}" if odds > 0 else str(odds)


def format_percent(value: float) -> str:
    """Format percentage."""
    return f"{value * 100:.1f}%"


def create_embed(
    title: str,
    description: str,
    color: int,
    fields: list[dict[str, Any]] = None,
    footer: str = None,
) -> dict:
    """Create a Discord embed object."""
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if fields:
        embed["fields"] = fields
    
    if footer:
        embed["footer"] = {"text": footer}
    
    return embed


# =============================================================================
# Alert Senders
# =============================================================================

async def send_discord_message(
    content: str = None,
    embeds: list[dict] = None,
    username: str = "Perplex Engine",
) -> bool:
    """
    Send a message to Discord via webhook.
    
    Args:
        content: Plain text content
        embeds: List of embed objects
        username: Bot display name
    
    Returns:
        True if sent successfully
    """
    if not DISCORD_WEBHOOK_URL:
        logger.debug("Discord webhook not configured, skipping alert")
        return False
    
    payload = {"username": username}
    
    if content:
        payload["content"] = content
    
    if embeds:
        payload["embeds"] = embeds
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                DISCORD_WEBHOOK_URL,
                json=payload,
                timeout=10.0,
            )
            
            if response.status_code in (200, 204):
                logger.info("Discord alert sent successfully")
                return True
            else:
                logger.warning(f"Discord webhook returned {response.status_code}: {response.text}")
                return False
    except Exception as e:
        logger.error(f"Failed to send Discord alert: {e}")
        return False


# =============================================================================
# Alert Types
# =============================================================================

async def alert_high_ev_pick(
    player_name: str,
    stat_type: str,
    line: float,
    side: str,
    odds: int,
    ev: float,
    model_prob: float,
    hit_rate_5g: float = None,
    sport: str = "NBA",
    game_time: str = None,
) -> bool:
    """
    Send alert for a high-EV player prop.
    
    Args:
        player_name: Player's name
        stat_type: Stat type (PTS, REB, etc.)
        line: The line value
        side: "over" or "under"
        odds: American odds
        ev: Expected value (0.08 = 8%)
        model_prob: Model's win probability
        hit_rate_5g: Optional hit rate over last 5 games
        sport: Sport name
        game_time: Game start time string
    """
    # Color based on EV (green gradient)
    if ev >= 0.15:
        color = 0x00FF00  # Bright green
    elif ev >= 0.10:
        color = 0x32CD32  # Lime green
    else:
        color = 0x228B22  # Forest green
    
    fields = [
        {"name": "Prop", "value": f"{side.upper()} {line}", "inline": True},
        {"name": "Odds", "value": format_odds(odds), "inline": True},
        {"name": "EV", "value": f"**+{format_percent(ev)}**", "inline": True},
        {"name": "Model Prob", "value": format_percent(model_prob), "inline": True},
    ]
    
    if hit_rate_5g is not None:
        fields.append({
            "name": "L5 Hit Rate",
            "value": format_percent(hit_rate_5g),
            "inline": True,
        })
    
    if game_time:
        fields.append({
            "name": "Game Time",
            "value": game_time,
            "inline": True,
        })
    
    embed = create_embed(
        title=f"🔥 High EV Pick: {player_name} {stat_type}",
        description=f"**{sport}** - Strong value detected",
        color=color,
        fields=fields,
        footer="Perplex Engine | High EV Alert",
    )
    
    return await send_discord_message(embeds=[embed])


async def alert_lock_parlay(
    legs: list[dict],
    total_odds: int,
    parlay_prob: float,
    parlay_ev: float,
    sport: str = "NBA",
) -> bool:
    """
    Send alert for a LOCK parlay recommendation.
    
    Args:
        legs: List of leg dicts with player_name, stat_type, line, side
        total_odds: Total parlay odds
        parlay_prob: Parlay win probability
        parlay_ev: Parlay expected value
        sport: Sport name
    """
    # Format legs as a bulleted list
    legs_text = "\n".join([
        f"• {leg['player_name']} {leg['side'].upper()} {leg['line']} {leg['stat_type']}"
        for leg in legs
    ])
    
    embed = create_embed(
        title=f"🔒 LOCK Parlay ({len(legs)} legs)",
        description=f"**{sport}**\n\n{legs_text}",
        color=0xFFD700,  # Gold
        fields=[
            {"name": "Odds", "value": format_odds(total_odds), "inline": True},
            {"name": "Win Prob", "value": format_percent(parlay_prob), "inline": True},
            {"name": "EV", "value": f"**+{format_percent(parlay_ev)}**", "inline": True},
        ],
        footer="Perplex Engine | LOCK Parlay Alert",
    )
    
    return await send_discord_message(embeds=[embed])


async def alert_100_percent_streak(
    player_name: str,
    stat_type: str,
    line: float,
    games_count: int,
    current_odds: int,
    sport: str = "NBA",
) -> bool:
    """
    Send alert for a 100% hit rate streak.
    
    Args:
        player_name: Player's name
        stat_type: Stat type
        line: The line value
        games_count: Number of games in streak
        current_odds: Current odds for this line
        sport: Sport name
    """
    embed = create_embed(
        title=f"🎯 100% Hit Rate: {player_name}",
        description=f"**{sport}** - {player_name} has hit OVER {line} {stat_type} in **{games_count} straight games**",
        color=0x9400D3,  # Purple
        fields=[
            {"name": "Stat", "value": stat_type, "inline": True},
            {"name": "Line", "value": str(line), "inline": True},
            {"name": "Streak", "value": f"{games_count} games", "inline": True},
            {"name": "Current Odds", "value": format_odds(current_odds), "inline": True},
        ],
        footer="Perplex Engine | 100% Streak Alert",
    )
    
    return await send_discord_message(embeds=[embed])


async def alert_sync_complete(
    sport: str,
    games_synced: int,
    props_synced: int,
    picks_generated: int,
    high_ev_count: int,
    duration_ms: int,
) -> bool:
    """
    Send alert when a data sync completes.
    
    Args:
        sport: Sport name
        games_synced: Number of games synced
        props_synced: Number of props synced
        picks_generated: Number of picks generated
        high_ev_count: Number of high-EV picks
        duration_ms: Sync duration in milliseconds
    """
    embed = create_embed(
        title=f"✅ Sync Complete: {sport}",
        description=f"Data refresh completed in {duration_ms / 1000:.1f}s",
        color=0x00CED1,  # Dark cyan
        fields=[
            {"name": "Games", "value": str(games_synced), "inline": True},
            {"name": "Props", "value": str(props_synced), "inline": True},
            {"name": "Picks", "value": str(picks_generated), "inline": True},
            {"name": "High EV", "value": str(high_ev_count), "inline": True},
        ],
        footer="Perplex Engine | Sync Alert",
    )
    
    return await send_discord_message(embeds=[embed])


async def alert_error(
    error_type: str,
    message: str,
    details: str = None,
) -> bool:
    """
    Send alert for an error condition.
    
    Args:
        error_type: Type of error (e.g., "API Error", "Sync Failed")
        message: Error message
        details: Optional additional details
    """
    description = message
    if details:
        description += f"\n\n```\n{details[:500]}\n```"
    
    embed = create_embed(
        title=f"⚠️ {error_type}",
        description=description,
        color=0xFF4500,  # Red-orange
        footer="Perplex Engine | Error Alert",
    )
    
    return await send_discord_message(embeds=[embed])


# =============================================================================
# Batch Alert Processing
# =============================================================================

async def alert_line_movement(
    player_name: str,
    stat_type: str,
    old_line: float,
    new_line: float,
    old_odds: int,
    new_odds: int,
    direction: str,  # "steamed" (sharp money) or "faded" (public money)
    sport: str = "NBA",
) -> bool:
    """
    Send alert for significant line movement.
    
    Args:
        player_name: Player's name
        stat_type: Stat type
        old_line: Previous line
        new_line: Current line
        old_odds: Previous odds
        new_odds: Current odds
        direction: "steamed" or "faded"
        sport: Sport name
    """
    line_diff = new_line - old_line
    odds_diff = new_odds - old_odds
    
    # Determine color based on direction
    if direction == "steamed":
        color = 0xFF6B6B  # Red - line moved against public
        emoji = "🔥"
        desc = f"Sharp money detected - line moved {abs(line_diff):.1f} points"
    else:
        color = 0x4ECDC4  # Teal - line moved with public
        emoji = "❄️"
        desc = f"Public money detected - line moved {abs(line_diff):.1f} points"
    
    embed = create_embed(
        title=f"{emoji} Line Move: {player_name} {stat_type}",
        description=f"**{sport}** - {desc}",
        color=color,
        fields=[
            {"name": "Old Line", "value": str(old_line), "inline": True},
            {"name": "New Line", "value": f"**{new_line}**", "inline": True},
            {"name": "Change", "value": f"{'+' if line_diff > 0 else ''}{line_diff:.1f}", "inline": True},
            {"name": "Old Odds", "value": format_odds(old_odds), "inline": True},
            {"name": "New Odds", "value": format_odds(new_odds), "inline": True},
            {"name": "Odds Move", "value": f"{'+' if odds_diff > 0 else ''}{odds_diff}", "inline": True},
        ],
        footer="Perplex Engine | Line Movement Alert",
    )
    
    return await send_discord_message(embeds=[embed])


async def detect_line_movements(
    db,
    sport_key: str,
    threshold_line: float = 1.0,  # Alert if line moves 1+ point
    threshold_odds: int = 20,  # Alert if odds move 20+ cents
) -> list[dict]:
    """
    Detect significant line movements since last sync.
    
    Compares current lines to previous snapshot and identifies moves.
    
    Args:
        db: Database session
        sport_key: Sport key
        threshold_line: Minimum line movement to alert
        threshold_odds: Minimum odds movement to alert
    
    Returns:
        List of line movement dictionaries
    """
    from sqlalchemy import select, and_
    from app.models import Line, Market, Player, Game, Sport
    from datetime import datetime, timezone, timedelta
    
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent_cutoff = now - timedelta(hours=6)  # Compare to lines from 6+ hours ago
    
    # Get sport ID
    sport_result = await db.execute(
        select(Sport).where(Sport.key == sport_key)
    )
    sport = sport_result.scalar_one_or_none()
    if not sport:
        return []
    
    # This would require storing historical line snapshots
    # For now, return empty - would need a LineHistory model
    # TODO: Implement proper line history tracking
    
    return []


async def process_picks_for_alerts(
    picks: list[dict],
    sport: str = "NBA",
) -> dict:
    """
    Process a list of picks and send alerts for high-EV ones.
    
    Args:
        picks: List of pick dictionaries
        sport: Sport name
    
    Returns:
        Summary dict with counts
    """
    alerts_sent = 0
    high_ev_count = 0
    
    for pick in picks:
        ev = pick.get("expected_value", 0)
        
        if ev >= HIGH_EV_THRESHOLD:
            high_ev_count += 1
            
            # Send alert (rate limit: max 5 alerts per batch)
            if alerts_sent < 5:
                success = await alert_high_ev_pick(
                    player_name=pick.get("player_name", "Unknown"),
                    stat_type=pick.get("stat_type", ""),
                    line=pick.get("line", 0),
                    side=pick.get("side", "over"),
                    odds=pick.get("odds", -110),
                    ev=ev,
                    model_prob=pick.get("model_probability", 0.5),
                    hit_rate_5g=pick.get("hit_rate_5g"),
                    sport=sport,
                )
                if success:
                    alerts_sent += 1
    
    return {
        "high_ev_count": high_ev_count,
        "alerts_sent": alerts_sent,
    }
