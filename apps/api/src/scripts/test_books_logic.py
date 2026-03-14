import asyncio
from routers.props import get_available_books

async def test_books():
    res = await get_available_books(sport="basketball_nba")
    print("RESULT:")
    import json
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    asyncio.run(test_books())
