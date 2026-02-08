#!/usr/bin/env python3
"""
Monitor Railway backend deployment status
"""
import time
import httpx
import asyncio

async def check_backend():
    """Check if backend is responding"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("https://railway-engine-production.up.railway.app/api/grading/health")
            print(f"✅ Backend responding! Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return True
    except httpx.TimeoutException:
        print("❌ Backend timeout - still starting or has issues")
        return False
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return False

async def main():
    """Monitor backend status"""
    attempts = 0
    max_attempts = 30
    
    while attempts < max_attempts:
        attempts += 1
        print(f"\n{'='*60}")
        print(f"Attempt {attempts}/{max_attempts}")
        print(f"{'='*60}")
        
        if await check_backend():
            print("\n🎉 Backend is ready!")
            break
        else:
            wait_time = min(30, attempts * 2)
            print(f"Waiting {wait_time} seconds before next check...")
            await asyncio.sleep(wait_time)
    
    if attempts >= max_attempts:
        print("\n❌ Backend failed to start after maximum attempts")
        print("Check Railway logs for specific errors")

if __name__ == "__main__":
    asyncio.run(main())
