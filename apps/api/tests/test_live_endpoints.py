import asyncio
import httpx
import json

async def run_tests():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        print("Testing /immediate/games...")
        resp = await client.get("/immediate/games")
        print(f"Status: {resp.status_code}")
        games = resp.json().get("games", [])
        print(f"Found {len(games)} games.")
        print(f"Data: {json.dumps(resp.json(), indent=2)[:300]}...\n")

        print("Testing /immediate/working-player-props...")
        if games:
            game_id = games[0].get("id")
            if game_id:
                resp = await client.get(f"/immediate/working-player-props?game_id={game_id}&sport_key=basketball_nba")
                print(f"Status: {resp.status_code}")
                props = resp.json().get("props", [])
                print(f"Found {len(props)} props.")
                print(f"Data: {json.dumps(resp.json(), indent=2)[:300]}...\n")
            
        print("Testing /parlays/working-parlays...")
        resp = await client.get("/parlays/working-parlays")
        print(f"Status: {resp.status_code}")
        parlays = resp.json().get("parlays", [])
        print(f"Found {len(parlays)} parlays.")
        print(f"Data: {json.dumps(resp.json(), indent=2)[:500]}...\n")
        
        print("Testing /parlays/monte-carlo-simulation...")
        resp = await client.get("/parlays/monte-carlo-simulation?simulations=100")
        print(f"Status: {resp.status_code}")
        print(f"Data: {json.dumps(resp.json(), indent=2)[:500]}...\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
