import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from clients.odds_client import odds_api_client
from config import settings

async def check():
    print(f"Primary from settings: [{settings.ODDS_API_KEY_PRIMARY}]")
    print(f"Current key in client: [{odds_api_client.api_key}]")
    print(f"All keys in client: {odds_api_client.api_keys}")
    
    # Try a request with the primary key specifically
    import httpx
    async with httpx.AsyncClient() as client:
        url = f"https://api.the-odds-api.com/v4/sports?apiKey={settings.ODDS_API_KEY_PRIMARY}"
        resp = await client.get(url)
        print(f"\nDirect httpx request to {url}")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        if resp.status_code == 200:
            print(f"Remaining: {resp.headers.get('x-requests-remaining')}")

if __name__ == "__main__":
    asyncio.run(check())
