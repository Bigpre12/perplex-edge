import asyncio
import httpx
import json

async def check_games():
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get("http://localhost:8000/api/immediate/games?sport_id=30")
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"Total games: {data.get('total')}")
                for g in data.get('items', []):
                    print(f"ID: {g.get('id') or g.get('game_id')}")
                    print(f"  Teams: {g.get('home_team_name', g.get('home_team'))} vs {g.get('away_team_name', g.get('away_team'))}")
                    print(f"  Status: {g.get('status')} | Source: {g.get('source')}")
                    print(f"  Time: {g.get('start_time') or g.get('date')}")
                    print("-" * 20)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_games())
