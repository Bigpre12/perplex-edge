
import asyncio
from sqlalchemy import text
from apps.api.src.db.session import AsyncSessionLocal
from apps.api.src.routers.health import health_check

async def test():
    async with AsyncSessionLocal() as db:
        print("Running health check...")
        result = await health_check(db)
        import json
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test())
