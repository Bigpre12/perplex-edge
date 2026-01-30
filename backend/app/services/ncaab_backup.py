"""
NCAAB odds backup utility for JSON file storage.

Saves daily backups of NCAAB odds data for fallback when APIs fail.
"""

import json
import logging
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Default backup directory
DEFAULT_BACKUP_DIR = Path(__file__).parent.parent.parent / "backups"


def _get_backup_dir() -> Path:
    """Get the backup directory path."""
    settings = get_settings()
    backup_dir = getattr(settings, 'ncaab_backup_dir', None)
    if backup_dir:
        path = Path(backup_dir)
    else:
        path = DEFAULT_BACKUP_DIR
    return path


def _ensure_backup_dir() -> Path:
    """Ensure backup directory exists and return path."""
    backup_dir = _get_backup_dir()
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def get_backup_filename(backup_date: date) -> str:
    """
    Generate backup filename for a given date.
    
    Format: YYYY-MM-DD-NCAAB-odds.json
    """
    return f"{backup_date.isoformat()}-NCAAB-odds.json"


def get_backup_path(backup_date: date) -> Path:
    """Get full path to backup file for a given date."""
    backup_dir = _get_backup_dir()
    return backup_dir / get_backup_filename(backup_date)


def save_backup(odds_data: list[dict[str, Any]], backup_date: Optional[date] = None) -> str:
    """
    Save NCAAB odds data to JSON backup file.
    
    Args:
        odds_data: List of odds dictionaries to save
        backup_date: Date for the backup (defaults to today)
    
    Returns:
        Path to the saved backup file
    """
    backup_date = backup_date or date.today()
    backup_dir = _ensure_backup_dir()
    backup_path = backup_dir / get_backup_filename(backup_date)
    
    backup_content = {
        "backup_date": backup_date.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sport": "NCAAB",
        "count": len(odds_data),
        "odds": odds_data,
    }
    
    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_content, f, indent=2, default=str)
        
        logger.info(f"Saved NCAAB odds backup: {backup_path} ({len(odds_data)} records)")
        return str(backup_path)
    
    except Exception as e:
        logger.error(f"Failed to save backup to {backup_path}: {e}")
        raise


def load_backup(backup_date: date) -> list[dict[str, Any]]:
    """
    Load NCAAB odds data from backup file for a specific date.
    
    Args:
        backup_date: Date of the backup to load
    
    Returns:
        List of odds dictionaries from backup
    
    Raises:
        FileNotFoundError: If backup file doesn't exist
    """
    backup_path = get_backup_path(backup_date)
    
    if not backup_path.exists():
        raise FileNotFoundError(f"No backup found for {backup_date}: {backup_path}")
    
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = json.load(f)
        
        odds_data = backup_content.get("odds", [])
        logger.info(f"Loaded NCAAB odds backup: {backup_path} ({len(odds_data)} records)")
        return odds_data
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in backup {backup_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to load backup from {backup_path}: {e}")
        raise


def get_latest_backup() -> tuple[Optional[list[dict[str, Any]]], Optional[date]]:
    """
    Find and load the most recent backup file.
    
    Searches backwards from today for up to 30 days.
    
    Returns:
        Tuple of (odds_data, backup_date) or (None, None) if no backup found
    """
    backup_dir = _get_backup_dir()
    
    if not backup_dir.exists():
        logger.warning(f"Backup directory does not exist: {backup_dir}")
        return None, None
    
    # Search backwards from today
    today = date.today()
    for days_back in range(30):
        check_date = today - timedelta(days=days_back)
        backup_path = backup_dir / get_backup_filename(check_date)
        
        if backup_path.exists():
            try:
                odds_data = load_backup(check_date)
                logger.info(f"Found latest backup from {check_date}")
                return odds_data, check_date
            except Exception as e:
                logger.warning(f"Could not load backup from {check_date}: {e}")
                continue
    
    logger.warning("No valid backup found in the last 30 days")
    return None, None


def list_backups(limit: int = 30) -> list[dict[str, Any]]:
    """
    List available backup files.
    
    Args:
        limit: Maximum number of backups to list
    
    Returns:
        List of backup info dictionaries
    """
    backup_dir = _get_backup_dir()
    
    if not backup_dir.exists():
        return []
    
    backups = []
    for backup_file in sorted(backup_dir.glob("*-NCAAB-odds.json"), reverse=True)[:limit]:
        try:
            stat = backup_file.stat()
            # Extract date from filename
            date_str = backup_file.stem.replace("-NCAAB-odds", "")
            backups.append({
                "filename": backup_file.name,
                "date": date_str,
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        except Exception as e:
            logger.debug(f"Could not stat {backup_file}: {e}")
    
    return backups


def delete_old_backups(days_to_keep: int = 90) -> int:
    """
    Delete backup files older than specified days.
    
    Args:
        days_to_keep: Number of days of backups to retain
    
    Returns:
        Number of files deleted
    """
    backup_dir = _get_backup_dir()
    
    if not backup_dir.exists():
        return 0
    
    cutoff_date = date.today() - timedelta(days=days_to_keep)
    deleted = 0
    
    for backup_file in backup_dir.glob("*-NCAAB-odds.json"):
        try:
            # Extract date from filename
            date_str = backup_file.stem.replace("-NCAAB-odds", "")
            file_date = date.fromisoformat(date_str)
            
            if file_date < cutoff_date:
                backup_file.unlink()
                deleted += 1
                logger.info(f"Deleted old backup: {backup_file.name}")
        except (ValueError, OSError) as e:
            logger.debug(f"Could not process {backup_file}: {e}")
    
    if deleted > 0:
        logger.info(f"Deleted {deleted} old backup files")
    
    return deleted


def backup_exists(backup_date: date) -> bool:
    """Check if a backup exists for the given date."""
    return get_backup_path(backup_date).exists()
