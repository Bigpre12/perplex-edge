"""
Snapshot service for versioned data storage and health checks.

Saves dated JSON snapshots before daily refresh for:
- Auditing past slates
- Rebuilding models
- Debugging pick decisions
- Data recovery without API calls

Also provides health check validation after syncs.
"""

import json
import logging
from dataclasses import dataclass
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Game, Line, ModelPick, Player, Sport

logger = logging.getLogger(__name__)

# Default snapshot directory
DEFAULT_SNAPSHOT_DIR = Path(__file__).parent.parent.parent / "snapshots"


# =============================================================================
# Sport Key to League Code Mapping
# =============================================================================

SPORT_KEY_TO_LEAGUE = {
    "basketball_nba": "NBA",
    "basketball_ncaab": "NCAAB",
    "americanfootball_nfl": "NFL",
}


# =============================================================================
# Health Check Thresholds
# =============================================================================

@dataclass
class HealthThresholds:
    """Minimum expected counts per sport for health checks."""
    min_games: int
    min_lines: int
    min_props: int
    min_picks: int


# Sport-specific thresholds (adjust based on typical daily volume)
HEALTH_THRESHOLDS = {
    "basketball_nba": HealthThresholds(min_games=3, min_lines=6, min_props=20, min_picks=5),
    "basketball_ncaab": HealthThresholds(min_games=5, min_lines=10, min_props=30, min_picks=5),
    "americanfootball_nfl": HealthThresholds(min_games=1, min_lines=2, min_props=10, min_picks=2),
}

# Default thresholds for sports without specific config
DEFAULT_THRESHOLDS = HealthThresholds(min_games=1, min_lines=2, min_props=5, min_picks=1)


# =============================================================================
# Snapshot Storage
# =============================================================================

def _get_snapshot_dir() -> Path:
    """Get the snapshot directory path."""
    settings = get_settings()
    snapshot_dir = getattr(settings, 'snapshot_dir', None)
    if snapshot_dir:
        return Path(snapshot_dir)
    return DEFAULT_SNAPSHOT_DIR


def _ensure_snapshot_dir() -> Path:
    """Ensure snapshot directory exists and return path."""
    snapshot_dir = _get_snapshot_dir()
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    return snapshot_dir


def get_snapshot_filename(sport_key: str, snapshot_date: date) -> str:
    """
    Generate snapshot filename.
    
    Format: {sport}_{YYYY-MM-DD}.json
    Example: nba_2026-01-30.json
    """
    # Normalize sport key to short name
    sport_short = sport_key.replace("basketball_", "").replace("americanfootball_", "")
    return f"{sport_short}_{snapshot_date.isoformat()}.json"


def get_snapshot_path(sport_key: str, snapshot_date: date) -> Path:
    """Get full path to snapshot file."""
    snapshot_dir = _get_snapshot_dir()
    return snapshot_dir / get_snapshot_filename(sport_key, snapshot_date)


async def save_daily_snapshot(
    db: AsyncSession,
    sport_key: str,
    snapshot_date: Optional[date] = None,
) -> dict[str, Any]:
    """
    Save a dated snapshot of current slate before refresh.
    
    Captures:
    - All games for the sport
    - All betting lines
    - All player props
    - All model picks
    - Sync metadata
    
    Args:
        db: Database session
        sport_key: Sport to snapshot (e.g., "basketball_nba")
        snapshot_date: Date for snapshot (defaults to today)
    
    Returns:
        Snapshot metadata including path and counts
    """
    snapshot_date = snapshot_date or date.today()
    snapshot_dir = _ensure_snapshot_dir()
    snapshot_path = snapshot_dir / get_snapshot_filename(sport_key, snapshot_date)
    
    # Get sport by league code
    league_code = SPORT_KEY_TO_LEAGUE.get(sport_key)
    if not league_code:
        logger.warning(f"Unknown sport key: {sport_key}")
        return {"error": f"Unknown sport key: {sport_key}"}
    
    sport_result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = sport_result.scalar_one_or_none()
    
    if not sport:
        logger.warning(f"Sport not found: {sport_key}")
        return {"error": f"Sport not found: {sport_key}"}
    
    # Fetch games for today/upcoming
    # Use timezone-naive datetimes to match database column type (TIMESTAMP WITHOUT TIME ZONE)
    today_start = datetime.combine(snapshot_date, datetime.min.time())
    tomorrow_end = datetime.combine(snapshot_date + timedelta(days=1), datetime.max.time())
    
    games_result = await db.execute(
        select(Game)
        .where(Game.sport_id == sport.id)
        .where(Game.start_time >= today_start - timedelta(hours=6))  # Include games from past 6h
        .where(Game.start_time <= tomorrow_end + timedelta(days=7))  # Include upcoming week
    )
    games = games_result.scalars().all()
    
    if not games:
        logger.info(f"No games found for {sport_key} snapshot")
        return {
            "sport": sport_key,
            "date": snapshot_date.isoformat(),
            "games": 0,
            "skipped": "no_games",
        }
    
    game_ids = [g.id for g in games]
    
    # Fetch lines for these games
    lines_result = await db.execute(
        select(Line).where(Line.game_id.in_(game_ids))
    )
    lines = lines_result.scalars().all()
    
    # Fetch picks for these games
    picks_result = await db.execute(
        select(ModelPick).where(ModelPick.game_id.in_(game_ids))
    )
    picks = picks_result.scalars().all()
    
    # Build snapshot content
    snapshot_content = {
        "snapshot_metadata": {
            "sport": sport_key,
            "sport_name": sport.name,
            "date": snapshot_date.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
        },
        "counts": {
            "games": len(games),
            "lines": len(lines),
            "props": sum(1 for l in lines if l.market_id and "player" in str(l.market_id).lower()),
            "picks": len(picks),
        },
        "games": [
            {
                "id": str(g.id),
                "external_id": g.external_id,
                "home_team": g.home_team,
                "away_team": g.away_team,
                "start_time": g.start_time.isoformat() if g.start_time else None,
                "status": g.status,
            }
            for g in games
        ],
        "lines": [
            {
                "id": str(l.id),
                "game_id": str(l.game_id),
                "market_id": str(l.market_id) if l.market_id else None,
                "player_id": str(l.player_id) if l.player_id else None,
                "stat_type": l.stat_type,
                "line_value": float(l.line_value) if l.line_value else None,
                "over_odds": l.over_odds,
                "under_odds": l.under_odds,
                "bookmaker": l.bookmaker,
            }
            for l in lines
        ],
        "picks": [
            {
                "id": str(p.id),
                "game_id": str(p.game_id),
                "player_id": str(p.player_id) if p.player_id else None,
                "pick_type": p.pick_type,
                "stat_type": p.stat_type,
                "line_value": float(p.line_value) if p.line_value else None,
                "direction": p.direction,
                "model_probability": float(p.model_probability) if p.model_probability else None,
                "ev": float(p.ev) if p.ev else None,
                "confidence": float(p.confidence) if p.confidence else None,
            }
            for p in picks
        ],
    }
    
    # Save to file
    try:
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot_content, f, indent=2, default=str)
        
        logger.info(
            f"Saved {sport_key} snapshot: {snapshot_path.name} "
            f"({len(games)} games, {len(lines)} lines, {len(picks)} picks)"
        )
        
        return {
            "sport": sport_key,
            "date": snapshot_date.isoformat(),
            "path": str(snapshot_path),
            "counts": snapshot_content["counts"],
        }
    
    except Exception as e:
        logger.error(f"Failed to save snapshot: {e}")
        return {"error": str(e)}


def load_snapshot(sport_key: str, snapshot_date: date) -> dict[str, Any]:
    """
    Load a snapshot from file.
    
    Args:
        sport_key: Sport key
        snapshot_date: Date of snapshot
    
    Returns:
        Snapshot content dictionary
    
    Raises:
        FileNotFoundError: If snapshot doesn't exist
    """
    snapshot_path = get_snapshot_path(sport_key, snapshot_date)
    
    if not snapshot_path.exists():
        raise FileNotFoundError(f"No snapshot found: {snapshot_path}")
    
    with open(snapshot_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_snapshots(sport_key: Optional[str] = None, limit: int = 30) -> list[dict[str, Any]]:
    """
    List available snapshots.
    
    Args:
        sport_key: Filter by sport (optional)
        limit: Maximum snapshots to return
    
    Returns:
        List of snapshot metadata
    """
    snapshot_dir = _get_snapshot_dir()
    
    if not snapshot_dir.exists():
        return []
    
    pattern = f"{sport_key.replace('basketball_', '').replace('americanfootball_', '')}_*.json" if sport_key else "*.json"
    
    snapshots = []
    for snapshot_file in sorted(snapshot_dir.glob(pattern), reverse=True)[:limit]:
        try:
            stat = snapshot_file.stat()
            # Parse filename: sport_YYYY-MM-DD.json
            parts = snapshot_file.stem.split("_")
            sport_short = parts[0]
            date_str = parts[1] if len(parts) > 1 else "unknown"
            
            snapshots.append({
                "filename": snapshot_file.name,
                "sport": sport_short,
                "date": date_str,
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        except Exception as e:
            logger.debug(f"Could not process {snapshot_file}: {e}")
    
    return snapshots


def delete_old_snapshots(days_to_keep: int = 90) -> int:
    """
    Delete snapshots older than specified days.
    
    Args:
        days_to_keep: Days of snapshots to retain
    
    Returns:
        Number of files deleted
    """
    snapshot_dir = _get_snapshot_dir()
    
    if not snapshot_dir.exists():
        return 0
    
    cutoff_date = date.today() - timedelta(days=days_to_keep)
    deleted = 0
    
    for snapshot_file in snapshot_dir.glob("*.json"):
        try:
            parts = snapshot_file.stem.split("_")
            if len(parts) >= 2:
                date_str = parts[1]
                file_date = date.fromisoformat(date_str)
                
                if file_date < cutoff_date:
                    snapshot_file.unlink()
                    deleted += 1
                    logger.info(f"Deleted old snapshot: {snapshot_file.name}")
        except (ValueError, OSError) as e:
            logger.debug(f"Could not process {snapshot_file}: {e}")
    
    if deleted > 0:
        logger.info(f"Deleted {deleted} old snapshot files")
    
    return deleted


# =============================================================================
# Health Checks
# =============================================================================

@dataclass
class HealthCheckResult:
    """Result of a sync health check."""
    healthy: bool
    sport: str
    games_count: int
    lines_count: int
    props_count: int
    picks_count: int
    issues: list[str]
    thresholds: HealthThresholds
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "healthy": self.healthy,
            "sport": self.sport,
            "counts": {
                "games": self.games_count,
                "lines": self.lines_count,
                "props": self.props_count,
                "picks": self.picks_count,
            },
            "thresholds": {
                "min_games": self.thresholds.min_games,
                "min_lines": self.thresholds.min_lines,
                "min_props": self.thresholds.min_props,
                "min_picks": self.thresholds.min_picks,
            },
            "issues": self.issues,
        }


async def check_sync_health(
    db: AsyncSession,
    sport_key: str,
    sync_result: Optional[dict[str, Any]] = None,
) -> HealthCheckResult:
    """
    Validate sync results against minimum thresholds.
    
    Checks:
    - Minimum games synced
    - Minimum lines synced
    - Minimum props synced
    - Minimum picks generated
    
    Args:
        db: Database session
        sport_key: Sport to check
        sync_result: Optional sync result dict (will query DB if not provided)
    
    Returns:
        HealthCheckResult with pass/fail status and details
    """
    thresholds = HEALTH_THRESHOLDS.get(sport_key, DEFAULT_THRESHOLDS)
    issues = []
    
    # Get counts from sync_result or query database
    if sync_result:
        games_count = sync_result.get("games_created", 0) + sync_result.get("games_updated", 0)
        lines_count = sync_result.get("lines_added", 0)
        props_count = sync_result.get("props_added", 0)
        picks_count = sync_result.get("picks_generated", 0)
    else:
        # Query database for today's data
        league_code = SPORT_KEY_TO_LEAGUE.get(sport_key)
        if not league_code:
            return HealthCheckResult(
                healthy=False,
                sport=sport_key,
                games_count=0,
                lines_count=0,
                props_count=0,
                picks_count=0,
                issues=[f"Unknown sport key: {sport_key}"],
                thresholds=thresholds,
            )
        
        sport_result = await db.execute(
            select(Sport).where(Sport.league_code == league_code)
        )
        sport = sport_result.scalar_one_or_none()
        
        if not sport:
            return HealthCheckResult(
                healthy=False,
                sport=sport_key,
                games_count=0,
                lines_count=0,
                props_count=0,
                picks_count=0,
                issues=["Sport not found in database"],
                thresholds=thresholds,
            )
        
        today_start = datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=timezone.utc)
        tomorrow = today_start + timedelta(days=1)
        
        # Count today's games
        games_result = await db.execute(
            select(func.count(Game.id))
            .where(Game.sport_id == sport.id)
            .where(Game.start_time >= today_start)
            .where(Game.start_time < tomorrow + timedelta(days=7))
        )
        games_count = games_result.scalar() or 0
        
        # Count lines and props for today's games
        game_ids_result = await db.execute(
            select(Game.id)
            .where(Game.sport_id == sport.id)
            .where(Game.start_time >= today_start)
            .where(Game.start_time < tomorrow + timedelta(days=7))
        )
        game_ids = [row[0] for row in game_ids_result.all()]
        
        if game_ids:
            lines_result = await db.execute(
                select(func.count(Line.id))
                .where(Line.game_id.in_(game_ids))
            )
            lines_count = lines_result.scalar() or 0
            
            props_result = await db.execute(
                select(func.count(Line.id))
                .where(Line.game_id.in_(game_ids))
                .where(Line.player_id.isnot(None))
            )
            props_count = props_result.scalar() or 0
            
            picks_result = await db.execute(
                select(func.count(ModelPick.id))
                .where(ModelPick.game_id.in_(game_ids))
            )
            picks_count = picks_result.scalar() or 0
        else:
            lines_count = props_count = picks_count = 0
    
    # Check thresholds
    if games_count < thresholds.min_games:
        issues.append(f"Games below threshold: {games_count} < {thresholds.min_games}")
    
    if lines_count < thresholds.min_lines:
        issues.append(f"Lines below threshold: {lines_count} < {thresholds.min_lines}")
    
    if props_count < thresholds.min_props:
        issues.append(f"Props below threshold: {props_count} < {thresholds.min_props}")
    
    if picks_count < thresholds.min_picks:
        issues.append(f"Picks below threshold: {picks_count} < {thresholds.min_picks}")
    
    healthy = len(issues) == 0
    
    result = HealthCheckResult(
        healthy=healthy,
        sport=sport_key,
        games_count=games_count,
        lines_count=lines_count,
        props_count=props_count,
        picks_count=picks_count,
        issues=issues,
        thresholds=thresholds,
    )
    
    # Log result
    if healthy:
        logger.info(
            f"Health check PASSED for {sport_key}: "
            f"{games_count} games, {lines_count} lines, {props_count} props, {picks_count} picks"
        )
    else:
        logger.warning(
            f"Health check FAILED for {sport_key}: {issues}"
        )
    
    return result


async def run_all_health_checks(db: AsyncSession) -> dict[str, Any]:
    """
    Run health checks for all configured sports.
    
    Returns:
        Dictionary with overall status and per-sport results
    """
    results = {}
    all_healthy = True
    
    for sport_key in HEALTH_THRESHOLDS.keys():
        result = await check_sync_health(db, sport_key)
        results[sport_key] = result.to_dict()
        if not result.healthy:
            all_healthy = False
    
    return {
        "overall_healthy": all_healthy,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "sports": results,
    }


# =============================================================================
# Combined Operations
# =============================================================================

async def pre_refresh_snapshot(
    db: AsyncSession,
    sport_keys: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Save snapshots for all sports before refresh.
    
    Call this at the start of your daily refresh job.
    
    Args:
        db: Database session
        sport_keys: Sports to snapshot (defaults to all configured)
    
    Returns:
        Snapshot results per sport
    """
    sport_keys = sport_keys or list(HEALTH_THRESHOLDS.keys())
    results = {}
    
    for sport_key in sport_keys:
        result = await save_daily_snapshot(db, sport_key)
        results[sport_key] = result
    
    # Clean up old snapshots
    deleted = delete_old_snapshots(days_to_keep=90)
    
    return {
        "snapshots": results,
        "old_snapshots_deleted": deleted,
    }


async def post_sync_validation(
    db: AsyncSession,
    sport_key: str,
    sync_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate sync and alert on issues.
    
    Call this after each sport sync to catch silent failures.
    
    Args:
        db: Database session
        sport_key: Sport that was synced
        sync_result: Result from sync operation
    
    Returns:
        Health check result with alert status
    """
    health = await check_sync_health(db, sport_key, sync_result)
    
    result = {
        "health_check": health.to_dict(),
        "alert_triggered": not health.healthy,
    }
    
    if not health.healthy:
        # Log alert-level message for monitoring
        logger.error(
            f"ALERT: Sync health check failed for {sport_key}! "
            f"Issues: {health.issues}"
        )
        
        # TODO: Add actual alerting (email, Slack, PagerDuty, etc.)
        # Example integration point:
        # await send_alert(
        #     title=f"Sync Health Check Failed: {sport_key}",
        #     message=f"Issues: {health.issues}",
        #     severity="warning",
        # )
    
    return result
