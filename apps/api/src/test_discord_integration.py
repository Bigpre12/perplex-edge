import asyncio
import os
import sys
import httpx
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

# Ensure env is loaded
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

async def test_discord_webhook():
    print("Testing Discord Webhook Integration...")
    
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("FAIL: DISCORD_WEBHOOK_URL not found in environment.")
        return

    print(f"SUCCESS: Webhook URL found: {webhook_url[:40]}...")

    # Test Payload
    payload = {
        "username": "LUCRIX ALPHA",
        "embeds": [{
            "title": "🚀 Discord Integration Successful",
            "description": "LUCRIX is now connected to your Discord server! Live signals and daily digests will be posted here.",
            "color": 3447003,
            "fields": [
                {"name": "Status", "value": "Operational ✅", "inline": True},
                {"name": "Environment", "value": "Production-Edge", "inline": True}
            ],
            "footer": {"text": "Lucrix Sports Betting Analytics"},
            "timestamp": datetime.utcnow().isoformat()
        }]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(webhook_url, json=payload, timeout=10.0)
            if resp.status_code in [200, 204]:
                print("SUCCESS: Discord message sent successfully!")
            else:
                print(f"FAIL: Discord returned status {resp.status_code}")
                print(f"Details: {resp.text}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_discord_webhook())
