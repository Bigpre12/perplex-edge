import asyncio
import httpx
import json

endpoints = [
    ("/api/parlay/suggestions?sport=basketball_nba", "GET"),
    ("/api/ev?sport=basketball_nba", "GET"),
    ("/api/intel/whale?sport=basketball_nba", "GET"),
    ("/api/injuries?sport=basketball_nba", "GET"),
    ("/api/brain/parlay-builder?sport=basketball_nba", "GET"),
    ("/api/health", "GET")
]

base_url = "http://localhost:8000"

async def test_endpoints():
    async with httpx.AsyncClient() as client:
        # Give server time to start if it just restarted
        await asyncio.sleep(6)
        
        for ep, method in endpoints:
            try:
                if method == "GET":
                    res = await client.get(base_url + ep)
                else:
                    res = await client.post(base_url + ep)
                
                print(f"--- {method} {ep} ---")
                print(f"STATUS: {res.status_code}")
                try:
                    data = res.json()
                    print(json.dumps(data, indent=2)[:500] + ("..." if len(json.dumps(data)) > 500 else ""))
                except:
                    print("Raw text:", res.text)
            except Exception as e:
                print(f"FAILED {ep}: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
