import os
import httpx
import logging
from datetime import datetime
from services.cache import cache
from dotenv import load_dotenv, find_dotenv

# Search for .env starting from this file's location
# apps/api/src/services/odds/the_odds_client.py -> search upwards
env_path = find_dotenv()
if env_path:
    load_dotenv(env_path)
else:
    # Fallback to absolute path search if find_dotenv fails
    load_dotenv()

from config import settings

logger = logging.getLogger(__name__)

# --- Key Rotation Logic ---
_KEYS = []
_CURRENT_KEY_IDX = 0

def init_keys():
    global _KEYS
    # Support Primary (100k) and Backup (20k) from settings
    p = settings.ODDS_API_KEY_PRIMARY
    b = settings.ODDS_API_KEY_BACKUP
    keys = [k for k in [p, b] if k]
    if not keys:
        # Fallback to any generic key
        k = os.getenv("THE_ODDS_API_KEY") or os.getenv("ODDS_API_KEY")
        if k: keys = [k]
    
    _KEYS.clear()
    _KEYS.extend(keys)
    
    if not _KEYS:
        logger.error("❌ No Odds API keys found!")

def get_api_key():
    if not _KEYS: init_keys()
    if not _KEYS: return None
    return _KEYS[_CURRENT_KEY_IDX]

def rotate_api_key():
    global _CURRENT_KEY_IDX
    if not _KEYS: init_keys()
    if len(_KEYS) <= 1: return False
    _CURRENT_KEY_IDX = (_CURRENT_KEY_IDX + 1) % len(_KEYS)
    logger.info(f"🔄 Rotating to Odds API key index {_CURRENT_KEY_IDX}")
    return True

def get_base_url():
    return os.getenv("THE_ODDS_API_BASE", "https://api.the-odds-api.com/v4")

def get_max_calls():
    # 120k monthly = ~4k daily (baseline), but we allow aggressive burst up to 10k
    # User math for new 100k tier aggressive strategy is ~9,360/day
    return int(os.getenv("THE_ODDS_API_MAX_CALLS_PER_DAY", 10000))

async def increment_call_count() -> int:
    """Store the API hit count in Redis so it survives server restarts."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    key = f"odds_api:calls:{today}"
    
    if cache.is_redis and cache._redis:
        try:
            count = await cache._redis.incr(key)
            if count == 1:
                await cache._redis.expire(key, 86400)
            return count
        except Exception as e:
            logger.error(f"Failed to increment Redis call count: {e}")
            
    val = cache._memory.get(key, {"val": 0})
    new_count = int(val["val"]) + 1
    cache._memory[key] = {"val": new_count, "exp": datetime.utcnow().timestamp() + 86400}
    return new_count

async def get_call_count() -> int:
    """Get the current API hit count from Redis."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    key = f"odds_api:calls:{today}"
    
    if cache.is_redis and cache._redis:
        try:
            count = await cache._redis.get(key)
            return int(count) if count else 0
        except Exception as e:
            logger.error(f"Failed to get Redis call count: {e}")
            
    val = cache._memory.get(key)
    return int(val["val"]) if val else 0

call_log = []

async def fetch_odds(path: str, params: dict | None = None, retry_on_fail=True):
    """
    Single, safe entrypoint for ALL TheOddsAPI requests.
    Enforces daily call cap and handles 401/429 with automatic Key Rotation.
    """
    api_key = get_api_key()
    base_url = get_base_url()
    max_calls = get_max_calls()

    calls_today = await get_call_count()
    if calls_today >= max_calls and not settings.DEVELOPMENT_MODE:
        logger.warning(f"🚨 TheOddsAPI daily call cap ({max_calls}) reached. serving CACHED data.")
        return None

    if params is None:
        params = {}
    
    # We use a copy to avoid mutating the original params in case of retry
    p = params.copy()
    p["apiKey"] = api_key

    url = f"{base_url}{path}"
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=p, timeout=10.0)
            
            used = resp.headers.get("x-requests-used")
            rem = resp.headers.get("x-requests-remaining")
            
            # Log usage headers on every call forpaid tier tracking
            logger.info(f"✅ OddsAPI quota → used: {used} | remaining: {rem} | Path: {path}")
            
            # Alert when getting low (threshold: 10,000 credits remaining)
            try:
                if rem and int(rem) < 10000:
                    logger.warning(f"⚠️ OddsAPI quota low: {rem} remaining")
            except (ValueError, TypeError):
                pass

            if resp.status_code == 200:
                await increment_call_count()
                return resp.json()
            
            elif resp.status_code in (401, 429):
                logger.error(f"❌ OddsAPI Key index {_CURRENT_KEY_IDX} Exhausted ({resp.status_code})")
                if retry_on_fail and rotate_api_key():
                    return await fetch_odds(path, params, retry_on_fail=False)
                return None
            else:
                logger.error(f"❌ OddsAPI Error {resp.status_code} | Path: {path} | Detail: {resp.text[:100]}")
                return None
    except Exception as e:
        logger.exception(f"TheOddsAPI request failed: {e}")
        return None

async def get_odds_usage():
    """Return the current daily and monthly usage projections for The Odds API."""
    calls_today = await get_call_count()
    max_daily   = get_max_calls()
    remaining   = max_daily - calls_today
    pct_used    = round((calls_today / max_daily) * 100, 1) if max_daily > 0 else 0

    # Projected monthly usage
    projected_monthly = calls_today * 30
    monthly_limit     = 120000 # Combined 100k + 20k
    monthly_pct       = round((projected_monthly / monthly_limit) * 100, 1)

    return {
        "today": {
            "calls_made":    calls_today,
            "calls_remaining": remaining,
            "daily_limit":   max_daily,
            "pct_used":      pct_used,
            "status":        "OK" if pct_used < 80 else "WARNING" if pct_used < 95 else "CRITICAL"
        },
        "monthly_projection": {
            "projected_calls": projected_monthly,
            "monthly_limit":   monthly_limit,
            "pct_projected":   monthly_pct,
            "status":          "OK" if monthly_pct < 80 else "WARNING" if monthly_pct < 95 else "CRITICAL"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
