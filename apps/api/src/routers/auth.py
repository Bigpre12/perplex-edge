from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, update
from db.session import get_async_db, async_session_maker
from models.user import User, APIKey
from services.auth_service import auth_service
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
import secrets
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Already imported above

class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    tier: str

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class WebhookUpdate(BaseModel):
    discord_webhook_url: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None


# ── Auth dependency (must be defined before any route that uses it) ──

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme), 
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_async_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Try API Key first (Institutional/Bot execution)
        if x_api_key:
            import hashlib
            key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()
            stmt = select(User).join(APIKey, User.id == APIKey.user_id).where(APIKey.key_hash == key_hash)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                # Update request count
                await db.execute(
                    update(APIKey).where(APIKey.key_hash == key_hash).values(requests_count=APIKey.requests_count + 1)
                )
                await db.commit()
                return user

        # 2. Fallback to JWT Token (Dashboard/UI)
        if not token:
            raise credentials_exception
            
        # Attempt A: Local JWT (Legacy/Internal)
        payload = auth_service.decode_access_token(token)
        if payload:
            username: str = payload.get("sub")
            if username:
                stmt = select(User).where(User.username == username)
                result = await db.execute(stmt)
                user = result.scalar_one_or_none()
                if user:
                    return user

        # Attempt B: Supabase (Modern Frontend) via raw HTTPX
        import httpx
        import os
        from core.config import settings
        
        supabase_url = settings.SUPABASE_URL or os.environ.get("SUPABASE_URL")
        supabase_key = settings.SUPABASE_ANON_KEY or os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if supabase_url and supabase_key:
            auth_url = f"{supabase_url}/auth/v1/user"
            headers = {"Authorization": f"Bearer {token}", "apikey": supabase_key}
            
            async with httpx.AsyncClient() as client:
                resp = await client.get(auth_url, headers=headers)
                
            if resp.status_code == 200:
                sb_user = resp.json()
                email = sb_user.get("email")
                
                if email:
                    # Try to find user by email in local DB
                    stmt = select(User).where(User.email == email)
                    result = await db.execute(stmt)
                    user = result.scalar_one_or_none()
                    
                    if not user:
                        # Provision JIT user if they exist in Supabase but not local DB
                        base_username = email.split("@")[0]
                        username = base_username
                        
                        # Collision protection: Ensure username is unique
                        count = 0
                        while True:
                            check_stmt = select(User).where(User.username == username)
                            check_res = await db.execute(check_stmt)
                            if not check_res.scalar_one_or_none():
                                break
                            count += 1
                            username = f"{base_username}{count}"
                        
                        user = User(
                            username=username,
                            email=email,
                            hashed_password="SUPABASE_AUTH_EXTERNAL"
                        )
                        db.add(user)
                        await db.commit()
                        await db.refresh(user)
                    
                    return user
            else:
                logger.error(f"Supabase auth rejected {resp.status_code}: {resp.text}")
        else:
            logger.error("Missing SUPABASE_URL or SUPABASE_ANON_KEY in settings")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Auth process crash (DB or Network): {e}")
        raise credentials_exception

    raise credentials_exception


# ── Routes ──

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserSignup, db: AsyncSession = Depends(get_async_db)):
    # Check if user already exists
    stmt = select(User).where((User.username == user_data.username) | (User.email == user_data.email))
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    hashed_pw = auth_service.get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_async_db)):
    stmt = select(User).where(User.email == login_data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not auth_service.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(
        data={"sub": user.username, "email": user.email, "tier": (user.subscription_tier or "free").lower()}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "tier": (user.subscription_tier or "free").lower()
        }
    }


@router.post("/keys/generate")
async def generate_api_key(
    label: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Generate a new secure API Key for the user."""
    new_key = secrets.token_urlsafe(32)
    import hashlib
    key_hash = hashlib.sha256(new_key.encode()).hexdigest()
    
    api_key_entry = APIKey(
        user_id=user.id,
        key_hash=key_hash,
        label=label
    )
    db.add(api_key_entry)
    await db.commit()
    return {"api_key": new_key, "label": label}

@router.get("/keys")
async def list_api_keys(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """List all API keys for the current user."""
    stmt = select(APIKey).where(APIKey.user_id == user.id)
    result = await db.execute(stmt)
    keys = result.scalars().all()
    return keys

@router.post("/profile/update-webhooks")
async def update_webhooks(
    data: WebhookUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update the user's webhook configurations for signal dispatch."""
    if data.discord_webhook_url is not None:
        user.discord_webhook_url = data.discord_webhook_url
    if data.telegram_bot_token is not None:
        user.telegram_bot_token = data.telegram_bot_token
    if data.telegram_chat_id is not None:
        user.telegram_chat_id = data.telegram_chat_id
        
    await db.commit()
    return {"status": "Webhooks updated successfully"}

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Generic logout endpoint (client clears tokens)."""
    return {"message": "Successfully logged out"}

@router.post("/refresh-token", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Issue a new JWT with the current DB tier."""
    access_token = auth_service.create_access_token(
        data={"sub": current_user.username, "email": current_user.email, "tier": (current_user.subscription_tier or "free").lower()}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "tier": (current_user.subscription_tier or "free").lower()
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    """Fetch the latest user data directly from the DB, ensuring tier status is fresh."""
    try:
        stmt = select(User).where(User.id == current_user.id)
        result = await db.execute(stmt)
        fresh_user = result.scalar_one_or_none()
        
        if not fresh_user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return fresh_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Critical /auth/me failure: {e}")
        # Return 401 instead of 500 to stop frontend retry storms
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed during DB refresh",
            headers={"WWW-Authenticate": "Bearer"},
        )
