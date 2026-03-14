import os
import httpx
import datetime
import base64
import asyncio
import traceback
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv

load_dotenv()

class KalshiServiceStandalone:
    def __init__(self):
        self.api_key_id = os.getenv("KALSHI_API_KEY_ID")
        self.private_key_path = os.getenv("KALSHI_PRIVATE_KEY_PATH")
        self.base_url = os.getenv("KALSHI_BASE_URL", "https://demo-api.kalshi.co/trade-api/v2")
        self.client = httpx.AsyncClient(base_url=self.base_url)
        self._private_key = None
        
        if self.private_key_path and os.path.exists(self.private_key_path):
            with open(self.private_key_path, "rb") as key_file:
                self._private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )

    def _create_signature(self, timestamp: str, method: str, path: str) -> str:
        if not self._private_key: return ""
        path_without_query = path.split('?')[0]
        message = f"{timestamp}{method}{path_without_query}".encode('utf-8')
        signature = self._private_key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')

    async def _get_auth_headers(self, method: str, path: str) -> Dict[str, str]:
        timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
        parsed_base = urlparse(self.base_url)
        # Fix path construction
        full_path = (parsed_base.path + path).replace('//', '/')
        signature = self._create_signature(timestamp, method, full_path)
        return {
            "Content-Type": "application/json",
            "KALSHI-ACCESS-KEY": self.api_key_id,
            "KALSHI-ACCESS-SIGNATURE": signature,
            "KALSHI-ACCESS-TIMESTAMP": timestamp
        }

    async def get_portfolio(self):
        path = "/portfolio/balance"
        headers = await self._get_auth_headers("GET", path)
        print(f"Headers: {headers}", flush=True)
        resp = await self.client.get(path, headers=headers)
        return resp.json()

async def main():
    service = KalshiServiceStandalone()
    print(f"Testing Kalshi v2 Connection (Base: {service.base_url})...", flush=True)
    try:
        portfolio = await asyncio.wait_for(service.get_portfolio(), timeout=15)
        print(f"✅ Result: {portfolio}", flush=True)
    except Exception:
        print("❌ Failed with traceback:", flush=True)
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
