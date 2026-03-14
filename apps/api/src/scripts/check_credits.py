import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def check_credits():
    api_key = os.getenv("THE_ODDS_API_KEY")
    url = f"https://api.the-odds-api.com/v4/sports/?apiKey={api_key}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        print(f"Status: {response.status_code}")
        print(f"Remaining: {response.headers.get('x-requests-remaining')}")
        print(f"Used: {response.headers.get('x-requests-used')}")
        if response.status_code != 200:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_credits())
