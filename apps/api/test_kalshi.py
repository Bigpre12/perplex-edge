import os
import asyncio
import sys
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))
load_dotenv()

from services.kalshi_service import kalshi_service

async def test_connection():
    print("Testing Kalshi v2 Authenticated Connection...", flush=True)
    
    # Derby public key to show user
    if kalshi_service._private_key:
        public_key = kalshi_service._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        print("\n--- DERIVED PUBLIC KEY ---")
        print(public_key)
        print("--------------------------\n", flush=True)

    try:
        print("Sending request to /portfolio/balance...", flush=True)
        # Attempt to fetch portfolio (requires authentication)
        portfolio = await asyncio.wait_for(kalshi_service.get_kalshi_portfolio(), timeout=15)
        if isinstance(portfolio, dict) and "error" in portfolio:
            print(f"❌ Connection Failed: {portfolio['error']}", flush=True)
            if "401" in str(portfolio['error']):
                print("Suggestion: Make sure the PUBLIC KEY shown above is uploaded to Kalshi with the correct Key ID.", flush=True)
        else:
            print("✅ Connection Successful!", flush=True)
            print(f"Balance: ${portfolio.get('balance', 0) / 100:.2f}", flush=True)
    except asyncio.TimeoutError:
        print("❌ Error: Connection timed out after 15 seconds. Check your internet or Kalshi API status.", flush=True)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(test_connection())
