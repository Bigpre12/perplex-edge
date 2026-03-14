import httpx
import asyncio
import json

async def verify_api():
    base_url = "http://localhost:8000"
    
    print("--- Verifying Brain Metrics ---")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{base_url}/api/immediate/brain-metrics")
            if res.status_code == 200:
                data = res.json()
                print(f"Success! Brain Metrics: {json.dumps(data, indent=2)}")
                # Check if it looks real (api_health should be 99.9%)
                if data.get("api_health") == "99.9%":
                    print("✅ Brain metrics verified (calculated values).")
                else:
                    print("❌ Brain metrics still seem mock or incorrect.")
            else:
                print(f"❌ Brain Metrics failed: {res.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

    print("\n--- Verifying News Ticker ---")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{base_url}/api/news/ticker")
            if res.status_code == 200:
                data = res.json()
                print(f"Success! News Ticker: {json.dumps(data.get('data', []), indent=2)[:500]}...")
                if "data" in data and isinstance(data["data"], list):
                    print("✅ News ticker data format verified.")
                else:
                    print("❌ News ticker missing 'data' field or incorrect format.")
            else:
                print(f"❌ News Ticker failed: {res.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_api())
