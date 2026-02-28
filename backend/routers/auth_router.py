from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, async_session_maker
from models.users import User, APIKey
from services.auth_service import auth_service
from pydantic import BaseModel, EmailStr
from typing import Optional
import secrets

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

from database import get_async_db, async_session_maker

class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    subscription_tier: str

    class Config:
        from_attributes = True

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
    
    # 1. Try API Key first (Institutional/Bot execution)
    if x_api_key:
        stmt = select(User).join(APIKey, User.id == APIKey.user_id).where(APIKey.key_hash == x_api_key)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            # Update request count
            await db.execute(
                update(APIKey).where(APIKey.key_hash == x_api_key).values(requests_count=APIKey.requests_count + 1)
            )
            await db.commit()
            return user

    # 2. Fallback to JWT Token (Dashboard/UI)
    if not token:
        raise credentials_exception
        
    payload = auth_service.decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    return user


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

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):
    stmt = select(User).where((User.username == form_data.username) | (User.email == form_data.username))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(
        data={"sub": user.username, "email": user.email, "tier": user.subscription_tier or "free"}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/keys/generate")
async def generate_api_key(
    label: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Generate a new secure API Key for the user."""
    new_key = secrets.token_urlsafe(32)
    api_key_entry = APIKey(
        user_id=user.id,
        key_hash=new_key, # In production we would hash this, but for this dev sprint we use it directly
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
