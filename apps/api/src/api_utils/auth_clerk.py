import os
import httpx
from jose import jwt
from fastapi import HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer()

# Usually: https://clerk.your-domain.com/.well-known/jwks.json 
# or https://<your-pk>.clerk.accounts.dev/.well-known/jwks.json
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")
CLERK_AUDIENCE = os.getenv("CLERK_AUDIENCE") # optional

class ClerkAuth:
    def __init__(self):
        self.jwks = None

    async def get_jwks(self):
        if not self.jwks:
            async with httpx.AsyncClient() as client:
                resp = await client.get(CLERK_JWKS_URL)
                if resp.status_code == 200:
                    self.jwks = resp.json()
                else:
                    raise Exception(f"Failed to fetch JWKS from {CLERK_JWKS_URL}")
        return self.jwks

    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Security(security)):
        token = credentials.credentials
        try:
            jwks = await self.get_jwks()
            # In a production environment, you should use jose.jwt.decode with the JWKS
            # Clerk tokens are standard JWTs
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
                    break
            
            if rsa_key:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=CLERK_AUDIENCE,
                    options={"verify_at_hash": False}
                )
                return payload
            
            raise HTTPException(status_code=401, detail="Invalid token header")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Unauthorized: {str(e)}")

clerk_auth = ClerkAuth()

async def get_current_user_clerk(token_payload: dict = Security(clerk_auth.verify_token)):
    """
    Returns the Clerk user ID (sub) and other payload info.
    You can use this to fetch/provision a local user.
    """
    return {
        "id": token_payload.get("sub"),
        "email": token_payload.get("email"),
        "metadata": token_payload.get("public_metadata", {})
    }
