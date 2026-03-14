import os
import datetime
import sys
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))
load_dotenv()

from services.kalshi_service import kalshi_service

def test_crypto():
    print("Testing RSA Key Loading...")
    if kalshi_service._private_key:
        print("✅ Private key loaded in KalshiService!")
        
        timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
        try:
            sig = kalshi_service._create_signature(timestamp, "GET", "/trade-api/v2/portfolio/balance")
            if sig:
                print(f"✅ Signature generated: {sig[:20]}...")
            else:
                print("❌ Signature generation returned empty string!")
        except Exception as e:
            print(f"❌ Signature generation failed: {e}")
    else:
        print("❌ Private key NOT loaded in KalshiService!")
        print(f"Path: {kalshi_service.private_key_path}")
        print(f"Exists: {os.path.exists(kalshi_service.private_key_path) if kalshi_service.private_key_path else 'N/A'}")

if __name__ == "__main__":
    test_crypto()
