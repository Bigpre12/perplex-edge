import asyncio
import httpx
import json

base = "http://localhost:8000/api"

endpoints = [
    "/injuries?sport=basketball_nba",
    "/whale?sport=basketball_nba",
    "/ev?sport=basketball_nba",
    "/ev/ev-top?sport=basketball_nba",
    "/signals/sharp-moves?sport=basketball_nba",
    "/steam?sport=basketball_nba",
    "/hit-rate?sport=basketball_nba",
    "/brain/decisions?sport=basketball_nba",
    "/brain/parlay-builder?sport=basketball_nba",
    "/parlay/suggestions?sport=basketball_nba",
    "/intel/whale?sport=basketball_nba",
]

async def test():
    async with httpx.AsyncClient() as client:
        with open("test_results.txt", "w", encoding="utf-8") as f:
            for p in endpoints:
                try:
                    res = await client.get(base + p, timeout=10)
                    f.write(f"Endpoint: {p}\nStatus: {res.status_code}\n")
                    if res.status_code != 200:
                        f.write(f"Error: {res.text[:200]}\n")
                    elif not res.json():
                        f.write("Result: Empty JSON\n")
                    else:
                        data = res.json()
                        if isinstance(data, list) and len(data) == 0:
                            f.write("Result: [] (Empty List)\n")
                        elif isinstance(data, dict):
                            keys = list(data.keys())
                            f.write(f"Result: Dict keys={keys}\n")
                    f.write("-" * 40 + "\n")
                except Exception as e:
                    f.write(f"Endpoint: {p}\nException: {e}\n" + "-" * 40 + "\n")

asyncio.run(test())
