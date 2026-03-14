import asyncio
from routers.slate import get_todays_slate
from database import SessionLocal

async def test_slate():
    db = SessionLocal()
    try:
        # Test without sport filter
        res = await get_todays_slate(session=db)
        print("RESULT (all):")
        import json
        print(json.dumps(res, indent=2))
        
        # Test with NBA filter
        res_nba = await get_todays_slate(sport="basketball_nba", session=db)
        print("\nRESULT (NBA):")
        print(json.dumps(res_nba, indent=2))
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_slate())
