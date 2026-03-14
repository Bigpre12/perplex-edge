import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def test_load():
    path = r"C:\Users\preio\OneDrive\Documents\Untitled\perplex_engine\perplex-edge\apps\api\kalshi.key"
    print(f"Checking path: {path}")
    if os.path.exists(path):
        print("✅ File exists!")
        try:
            with open(path, "rb") as key_file:
                content = key_file.read()
                print(f"✅ Read {len(content)} bytes")
                key = serialization.load_pem_private_key(
                    content,
                    password=None,
                    backend=default_backend()
                )
                print("✅ Key loaded successfully with cryptography!")
        except Exception as e:
            print(f"❌ Error loading: {e}")
    else:
        print("❌ File does NOT exist at that path.")

if __name__ == "__main__":
    test_load()
