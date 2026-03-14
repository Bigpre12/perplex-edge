import asyncio
import os
import sys
import httpx
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

# Ensure env is loaded
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

from services.ai_service import ai_service

async def test_integration():
    print("Testing OpenRouter Integration...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("FAIL: OPENROUTER_API_KEY not found in environment.")
        return

    print(f"SUCCESS: API Key found: {api_key[:10]}...")

    # 1. Test Direct OpenRouter Connectivity
    print("\nTesting Direct OpenRouter Chat Completion...")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct",
        "messages": [
            {"role": "user", "content": "Hello, are you online? Respond with 'ONLINE'."}
        ]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload, timeout=20.0)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                print(f"SUCCESS: OpenRouter responded: {content.strip()}")
            else:
                print(f"FAIL: OpenRouter returned status {resp.status_code}")
                print(f"Details: {resp.text}")
    except Exception as e:
        print(f"ERROR during direct fetch: {e}")

    # 2. Test AIService Logic (will use Groq if present, then OpenRouter)
    print("\nTesting AIService configuration...")
    print(f"  - Groq Key: {'Set' if ai_service.groq_key else 'Missing'}")
    print(f"  - OpenRouter Key: {'Set' if ai_service.openrouter_key else 'Missing'}")
    print(f"  - Base URL being used: {ai_service.base_url}")

if __name__ == "__main__":
    asyncio.run(test_integration())
