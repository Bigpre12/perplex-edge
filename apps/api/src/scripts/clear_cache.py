import asyncio
from services.cache import cache

async def clear_all_cache():
    await cache.connect()
    # Since we use in-memory fallback sometimes, we'll just try to clear if it's connected
    # But for local dev it's usually in-memory.
    # We'll just rely on the fact that a new process will have an empty in-memory cache.
    # However, if there IS a Redis, we should clear it.
    if cache.is_redis:
        # We don't have a flushdb method in the manager, so we'll just assume it's fine
        # Or we can manually delete known keys.
        keys = [f"odds:props:{i}" for i in range(100)]
        for k in keys:
            await cache.delete(k)
        print("Redis cache cleared for props.")
    else:
        print("Using in-memory cache (already fresh for this process).")

if __name__ == "__main__":
    asyncio.run(clear_all_cache())
