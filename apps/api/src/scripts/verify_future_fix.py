import asyncio
import httpx
import json

async def verify():
    async with httpx.AsyncClient() as client:
        # 1. Verify Slate
        print("--- Verifying Slate (/api/props/slate/today) ---")
        r = await client.get("http://localhost:8000/api/props/slate/today")
        if r.status_code == 200:
            data = r.json()
            sports = data.get("sports", [])
            print(f"Found {len(sports)} sports in slate")
            for s in sports:
                print(f"Sport: {s['sport']} ({len(s['games'])} games)")
                for g in s['games'][:2]:
                     print(f"  {g['away_team']} @ {g['home_team']} | {g['commence_time']}")
        else:
            print(f"Slate failed: {r.status_code}")

if __name__ == "__main__":
    asyncio.run(verify())
