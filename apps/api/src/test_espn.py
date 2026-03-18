import asyncio
from clients.espn_client import espn_client

async def main():
    print("Fetching basketball_nba injuries...")
    injuries = await espn_client.fetch_injuries("basketball_nba")
    print(f"Injuries returned count: {len(injuries)}")
    if injuries:
        print(injuries[0])

if __name__ == "__main__":
    asyncio.run(main())
