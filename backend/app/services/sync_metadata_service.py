"""
Sync Metadata Service for tracking data freshness.

Provides functions to:
- Record sync timestamps after successful updates
- Query last_updated times for display
- Check for stale data across sports
- Alert on sync failures
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SyncMetadata

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

SPORT_DISPLAY_NAMES = {
    "basketball_nba": "NBA",
    "basketball_ncaab": "NCAAB",
    "americanfootball_nfl": "NFL",
}

DATA_TYPES = ["games", "lines", "props", "injuries", "rosters", "picks"]


# =============================================================================
# Record Sync Metadata
# =============================================================================

async def record_sync(
    db: AsyncSession,
    sport_key: str,
    data_type: str = "games",
    games_count: Optional[int] = None,
    lines_count: Optional[int] = None,
    props_count: Optional[int] = None,
    picks_count: Optional[int] = None,
    source: Optional[str] = None,
    sync_duration_seconds: Optional[float] = None,
    error_message: Optional[str] = None,
    is_healthy: bool = True,
) -> SyncMetadata:
    """
    Record a sync event in the metadata table.
    
    Call this after each successful sync to update the "last updated" timestamp.
    
    Args:
        db: Database session
        sport_key: Sport identifier (e.g., "basketball_nba")
        data_type: Type of data synced (games, lines, props, etc.)
        games_count: Number of games synced
        lines_count: Number of lines synced
        props_count: Number of props synced
        picks_count: Number of picks generated
        source: Data source used (odds_api, espn, stubs)
        sync_duration_seconds: How long the sync took
        error_message: Error message if sync had issues
        is_healthy: Whether the sync met minimum thresholds
    
    Returns:
        The created or updated SyncMetadata record
    """
    # Check if record exists for this sport+type
    result = await db.execute(
        select(SyncMetadata).where(
            and_(
                SyncMetadata.sport_key == sport_key,
                SyncMetadata.data_type == data_type,
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing record
        existing.last_updated = datetime.now(timezone.utc)
        existing.games_count = games_count
        existing.lines_count = lines_count
        existing.props_count = props_count
        existing.picks_count = picks_count
        existing.source = source
        existing.sync_duration_seconds = sync_duration_seconds
        existing.error_message = error_message
        existing.is_healthy = is_healthy
        metadata = existing
    else:
        # Create new record
        metadata = SyncMetadata(
            sport_key=sport_key,
            data_type=data_type,
            last_updated=datetime.now(timezone.utc),
            games_count=games_count,
            lines_count=lines_count,
            props_count=props_count,
            picks_count=picks_count,
            source=source,
            sync_duration_seconds=sync_duration_seconds,
            error_message=error_message,
            is_healthy=is_healthy,
        )
        db.add(metadata)
    
    await db.commit()
    await db.refresh(metadata)
    
    logger.info(
        f"Recorded sync: {sport_key}/{data_type} - "
        f"games={games_count}, lines={lines_count}, props={props_count}, "
        f"source={source}, healthy={is_healthy}"
    )
    
    return metadata


# =============================================================================
# Query Sync Metadata
# =============================================================================

async def get_last_updated(
    db: AsyncSession,
    sport_key: str,
    data_type: str = "games",
) -> Optional[datetime]:
    """
    Get the last_updated timestamp for a sport and data type.
    
    Args:
        db: Database session
        sport_key: Sport identifier
        data_type: Type of data
    
    Returns:
        Last updated datetime or None if never synced
    """
    result = await db.execute(
        select(SyncMetadata.last_updated).where(
            and_(
                SyncMetadata.sport_key == sport_key,
                SyncMetadata.data_type == data_type,
            )
        )
    )
    return result.scalar_one_or_none()


async def get_sync_metadata(
    db: AsyncSession,
    sport_key: str,
    data_type: str = "games",
) -> Optional[SyncMetadata]:
    """
    Get the full sync metadata record for a sport and data type.
    
    Args:
        db: Database session
        sport_key: Sport identifier
        data_type: Type of data
    
    Returns:
        SyncMetadata record or None
    """
    result = await db.execute(
        select(SyncMetadata).where(
            and_(
                SyncMetadata.sport_key == sport_key,
                SyncMetadata.data_type == data_type,
            )
        )
    )
    return result.scalar_one_or_none()


async def get_all_sync_status(db: AsyncSession) -> dict[str, Any]:
    """
    Get sync status for all sports and data types.
    
    Returns:
        Dictionary with all sync metadata organized by sport
    """
    result = await db.execute(select(SyncMetadata))
    all_metadata = result.scalars().all()
    
    # Organize by sport
    status: dict[str, dict[str, Any]] = {}
    
    for sport_key in SPORT_DISPLAY_NAMES:
        status[sport_key] = {
            "display_name": SPORT_DISPLAY_NAMES[sport_key],
            "data_types": {},
        }
    
    for meta in all_metadata:
        if meta.sport_key in status:
            status[meta.sport_key]["data_types"][meta.data_type] = meta.to_dict()
    
    # Add overall freshness indicator
    now = datetime.now(timezone.utc)
    for sport_key, sport_data in status.items():
        games_meta = sport_data["data_types"].get("games")
        if games_meta and games_meta.get("last_updated"):
            last_updated = datetime.fromisoformat(games_meta["last_updated"].replace("Z", "+00:00"))
            hours_ago = (now - last_updated).total_seconds() / 3600
            
            if hours_ago < 1:
                sport_data["freshness"] = "fresh"
                sport_data["freshness_label"] = "Updated just now"
            elif hours_ago < 6:
                sport_data["freshness"] = "recent"
                sport_data["freshness_label"] = f"Updated {int(hours_ago)}h ago"
            elif hours_ago < 24:
                sport_data["freshness"] = "stale"
                sport_data["freshness_label"] = f"Updated {int(hours_ago)}h ago"
            else:
                sport_data["freshness"] = "outdated"
                sport_data["freshness_label"] = f"Updated {int(hours_ago/24)}d ago"
        else:
            sport_data["freshness"] = "unknown"
            sport_data["freshness_label"] = "Never synced"
    
    return status


async def get_frontend_meta(db: AsyncSession) -> dict[str, Any]:
    """
    Get a simplified metadata response for the frontend.
    
    Returns a clean structure for displaying "Last updated: X" in the UI.
    """
    result = await db.execute(
        select(SyncMetadata).where(SyncMetadata.data_type == "games")
    )
    games_metadata = result.scalars().all()
    
    now = datetime.now(timezone.utc)
    meta = {
        "updated_at": now.isoformat(),
        "sports": {},
    }
    
    for m in games_metadata:
        display_name = SPORT_DISPLAY_NAMES.get(m.sport_key, m.sport_key.upper())
        
        if m.last_updated:
            hours_ago = (now - m.last_updated).total_seconds() / 3600
            
            # Format relative time
            if hours_ago < 1:
                relative = "just now"
            elif hours_ago < 24:
                relative = f"{int(hours_ago)}h ago"
            else:
                relative = f"{int(hours_ago/24)}d ago"
            
            meta["sports"][m.sport_key] = {
                "name": display_name,
                "last_updated": m.last_updated.isoformat(),
                "relative": relative,
                "games_count": m.games_count,
                "lines_count": m.lines_count,
                "props_count": m.props_count,
                "source": m.source,
                "is_healthy": m.is_healthy,
            }
        else:
            meta["sports"][m.sport_key] = {
                "name": display_name,
                "last_updated": None,
                "relative": "never",
                "is_healthy": False,
            }
    
    # Add any sports that haven't been synced yet
    for sport_key, display_name in SPORT_DISPLAY_NAMES.items():
        if sport_key not in meta["sports"]:
            meta["sports"][sport_key] = {
                "name": display_name,
                "last_updated": None,
                "relative": "never",
                "is_healthy": False,
            }
    
    return meta


# =============================================================================
# Staleness Detection
# =============================================================================

async def check_stale_data(
    db: AsyncSession,
    max_age_hours: int = 24,
) -> dict[str, Any]:
    """
    Check for stale data across all sports.
    
    Args:
        db: Database session
        max_age_hours: Consider data stale if older than this
    
    Returns:
        Dictionary with stale data alerts
    """
    result = await db.execute(select(SyncMetadata))
    all_metadata = result.scalars().all()
    
    now = datetime.now(timezone.utc)
    stale_threshold = now - timedelta(hours=max_age_hours)
    
    stale_alerts = []
    healthy_count = 0
    unhealthy_count = 0
    
    for meta in all_metadata:
        if meta.last_updated and meta.last_updated < stale_threshold:
            hours_ago = (now - meta.last_updated).total_seconds() / 3600
            stale_alerts.append({
                "sport": meta.sport_key,
                "data_type": meta.data_type,
                "last_updated": meta.last_updated.isoformat(),
                "hours_ago": round(hours_ago, 1),
                "severity": "critical" if hours_ago > 48 else "warning",
            })
            unhealthy_count += 1
        elif meta.last_updated:
            healthy_count += 1
        
        if not meta.is_healthy:
            unhealthy_count += 1
    
    return {
        "checked_at": now.isoformat(),
        "max_age_hours": max_age_hours,
        "healthy_count": healthy_count,
        "unhealthy_count": unhealthy_count,
        "overall_healthy": len(stale_alerts) == 0,
        "stale_alerts": stale_alerts,
    }
