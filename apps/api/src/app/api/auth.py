import os
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import jwt

router = APIRouter()

SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
ALGORITHM = "HS256"

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    accessToken: str
    tier: str
    email: str

def create_token(email: str, tier: str) -> str:
    payload = {
        "sub":   email,
        "tier":  tier,
        "exp":   datetime.now(timezone.utc) + timedelta(days=7),
        "iat":   datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ── POST /api/auth/login ───────────────────────────────────────────────────
@router.post("/login")
async def login(body: LoginRequest):
    # TODO: replace with real DB lookup
    # For now — any login works, tier is "free"
    token = create_token(email=body.email, tier="free")
    return {
        "accessToken": token,
        "tier":        "free",
        "email":       body.email,
        "timestamp":   datetime.now(timezone.utc).isoformat(),
    }

# ── GET /api/auth/me ───────────────────────────────────────────────────────
@router.get("/me")
async def get_me(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")

    token   = authorization.split(" ")[1]
    payload = decode_token(token)

    return {
        "email":     payload.get("sub"),
        "tier":      payload.get("tier", "free"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

# ── POST /api/auth/logout ──────────────────────────────────────────────────
@router.post("/logout")
async def logout():
    # JWT is stateless — client just deletes the token
    return {"message": "Logged out", "timestamp": datetime.now(timezone.utc).isoformat()}

# ── GET /api/auth/tier ─────────────────────────────────────────────────────
@router.get("/tier")
async def get_tier(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return {"tier": "free", "authenticated": False}

    try:
        token   = authorization.split(" ")[1]
        payload = decode_token(token)
        return {
            "tier":          payload.get("tier", "free"),
            "authenticated": True,
            "email":         payload.get("sub"),
            "timestamp":     datetime.now(timezone.utc).isoformat(),
        }
    except HTTPException:
        return {"tier": "free", "authenticated": False}
