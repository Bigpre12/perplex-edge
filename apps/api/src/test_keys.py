import httpx
import asyncio

async def test_key(key):
    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
    params = {
        "apiKey": key,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "american"
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        print(f"Key: {key}")
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Remaining: {r.headers.get('x-requests-remaining')}")
        else:
            print(f"Error: {r.text}")

if __name__ == "__main__":
    asyncio.run(test_key("534f28df45cd7fc2d3af6be2d23b6315"))
    asyncio.run(test_key("b94144c89048238eff1856d83c383d9a"))
