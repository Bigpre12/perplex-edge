import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_key():
    api_key = os.getenv("THE_ODDS_API_KEY")
    print(f"Testing key: {api_key}")
    url = f"https://api.the-odds-api.com/v4/sports/?apiKey={api_key}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print("✅ Key is VALID")
            # print(resp.json()[:2])
        else:
            print(f"❌ Key is INVALID: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_key())
