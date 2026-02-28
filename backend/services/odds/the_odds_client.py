import os
import httpx
import logging
from datetime import datetime
from services.cache import cache

logger = logging.getLogger(__name__)

API_KEY  = os.getenv("THE_ODDS_API_KEY")
BASE_URL = os.getenv("THE_ODDS_API_BASE", "https://api.the-odds-api.com/v4")
MAX_CALLS_PER_DAY = int(os.getenv("THE_ODDS_API_MAX_CALLS_PER_DAY", 600))

async def increment_call_count() -> int:
    """Store the API hit count in Redis so it survives server restarts."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    key = f"odds_api:calls:{today}"
    
    # Check if cache is connected to real Redis
    if cache.is_redis and cache._redis:
        try:
            count = await cache._redis.incr(key)
            if count == 1:
                await cache._redis.expire(key, 86400)  # expires at end of day
            return count
        except Exception as e:
            logger.error(f"Failed to increment Redis call count: {e}")
            
    # Fallback to local memory dictionary if no Redis
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
            
    # Fallback to local memory
    val = cache._memory.get(key)
    return int(val["val"]) if val else 0

async def fetch_odds(path: str, params: dict | None = None):
    """
    Single, safe entrypoint for ALL TheOddsAPI requests.
    Enforces daily call cap so you don't blow the 20k tier.
    """
    calls_today = await get_call_count()
    if calls_today >= MAX_CALLS_PER_DAY:
        logger.warning(f"TheOddsAPI daily call cap ({MAX_CALLS_PER_DAY}) reached, using cache only.")
        return None

    if params is None:
        params = {}
    params["apiKey"] = API_KEY

    url = f"{BASE_URL}{path}"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10.0)
            if resp.status_code != 200:
                logger.error(f"TheOddsAPI error {resp.status_code}: {resp.text[:200]}")
                return None

            await increment_call_count()
            data = resp.json()
            return data
    except Exception as e:
        logger.exception(f"TheOddsAPI request failed: {e}")
        return None

async def get_odds_usage():
    """Return the current daily and monthly usage projections for The Odds API."""
    calls_today = await get_call_count()
    max_daily   = MAX_CALLS_PER_DAY
    remaining   = max_daily - calls_today
    pct_used    = round((calls_today / max_daily) * 100, 1) if max_daily > 0 else 0

    # Projected monthly usage
    projected_monthly = calls_today * 30
    monthly_limit     = 20000
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
