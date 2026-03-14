import os
import httpx
import asyncio
from dotenv import load_dotenv

async def test_key():
    load_dotenv("apps/api/.env")
    key = os.getenv("THE_ODDS_API_KEY")
    url = f"https://api.the-odds-api.com/v4/sports/?apiKey={key}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        print(f"Status: {resp.status_code}")
        print(f"Headers: {dict(resp.headers)}")
        if resp.status_code == 200:
            print("Key is VALID")
            print(f"Remaining: {resp.headers.get('x-requests-remaining')}")
            print(f"Used: {resp.headers.get('x-requests-used')}")
        else:
            print(f"Key is INVALID or EXHAUSTED: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_key())
