import asyncio
from services.odds.the_odds_client import get_odds_usage

async def check():
    usage = await get_odds_usage()
    import json
    print(json.dumps(usage, indent=2))

if __name__ == "__main__":
    asyncio.run(check())
