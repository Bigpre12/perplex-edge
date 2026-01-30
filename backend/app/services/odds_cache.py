"""
Odds cache for storing last known good data.

Provides fallback data when all APIs fail, ensuring the app always has
some data to display.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Cache file location (in app directory)
CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_FILE = CACHE_DIR / "last_good_odds.json"
CACHE_EXPIRY_HOURS = 24  # Cache expires after 24 hours


def _ensure_cache_dir() -> None:
    """Ensure the cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def save_to_cache(sport_key: str, data: dict[str, Any]) -> bool:
    """
    Save successful sync data to cache.
    
    Args:
        sport_key: Sport identifier (e.g., 'basketball_nba')
        data: Sync result data to cache
    
    Returns:
        True if save successful, False otherwise
    """
    try:
        _ensure_cache_dir()
        
        # Load existing cache
        cache = {}
        if CACHE_FILE.exists():
            try:
                cache = json.loads(CACHE_FILE.read_text())
            except (json.JSONDecodeError, IOError):
                cache = {}
        
        # Update cache for this sport
        cache[sport_key] = {
            "data": data,
            "cached_at": datetime.utcnow().isoformat(),
        }
        
        # Save cache
        CACHE_FILE.write_text(json.dumps(cache, indent=2, default=str))
        logger.info(f"Cached sync data for {sport_key}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save cache for {sport_key}: {e}")
        return False


def load_from_cache(sport_key: str) -> Optional[dict[str, Any]]:
    """
    Load cached sync data for a sport.
    
    Args:
        sport_key: Sport identifier
    
    Returns:
        Cached data dict or None if not found/expired
    """
    try:
        if not CACHE_FILE.exists():
            logger.info("No cache file exists")
            return None
        
        cache = json.loads(CACHE_FILE.read_text())
        
        if sport_key not in cache:
            logger.info(f"No cached data for {sport_key}")
            return None
        
        entry = cache[sport_key]
        cached_at = datetime.fromisoformat(entry["cached_at"])
        age_hours = (datetime.utcnow() - cached_at).total_seconds() / 3600
        
        if age_hours > CACHE_EXPIRY_HOURS:
            logger.warning(f"Cache for {sport_key} expired ({age_hours:.1f}h old)")
            return None
        
        logger.info(f"Loaded cache for {sport_key} ({age_hours:.1f}h old)")
        return entry["data"]
        
    except Exception as e:
        logger.error(f"Failed to load cache for {sport_key}: {e}")
        return None


def get_cache_status() -> dict[str, Any]:
    """
    Get status of all cached data.
    
    Returns:
        Dict with cache status for each sport
    """
    status = {"exists": False, "sports": {}}
    
    try:
        if not CACHE_FILE.exists():
            return status
        
        cache = json.loads(CACHE_FILE.read_text())
        status["exists"] = True
        
        for sport_key, entry in cache.items():
            cached_at = datetime.fromisoformat(entry["cached_at"])
            age_hours = (datetime.utcnow() - cached_at).total_seconds() / 3600
            
            status["sports"][sport_key] = {
                "cached_at": entry["cached_at"],
                "age_hours": round(age_hours, 1),
                "expired": age_hours > CACHE_EXPIRY_HOURS,
            }
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get cache status: {e}")
        return status


def clear_cache(sport_key: Optional[str] = None) -> bool:
    """
    Clear cached data.
    
    Args:
        sport_key: If provided, only clear cache for this sport.
                   If None, clear all cache.
    
    Returns:
        True if successful
    """
    try:
        if sport_key is None:
            # Clear all cache
            if CACHE_FILE.exists():
                CACHE_FILE.unlink()
                logger.info("Cleared all cache")
            return True
        
        # Clear specific sport
        if not CACHE_FILE.exists():
            return True
        
        cache = json.loads(CACHE_FILE.read_text())
        if sport_key in cache:
            del cache[sport_key]
            CACHE_FILE.write_text(json.dumps(cache, indent=2, default=str))
            logger.info(f"Cleared cache for {sport_key}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return False
