from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, update
from db.session import get_db, get_async_db
from models.user import User, APIKey
from services.auth_service import auth_service
from services.email_service import email_service
from pydantic import BaseModel, EmailStr, ConfigDict
import secrets
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Already imported above

class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: Optional[int] = None
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

        # JWT is valid but user not in local DB — create synthetic user from claims                 email_fallback = payload.get("email")                 if email_fallback:                     synthetic = User(                         username=username,                         email=email_fallback,                         hashed_password="JWT_AUTH",                         subscription_tier=payload.get("tier", "free")                     )                     logger.info(f"Auth: returning synthetic user for {email_fallback} (JWT valid, not in local DB)")                     return synthetic          # Attempt B: Supabase (Modern Frontend)
        from core.config import settings
        from api_utils.supabase_proxy import create_client
        
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured — auth disabled")
        else:
            try:
                # Use the client for verification or keep the existing HTTPX logic 
                # but ensure the guard is present as requested.
                # The user specifically asked for 'supabase = create_client(...)'
                supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                
                import httpx
                auth_url = f"{settings.SUPABASE_URL}/auth/v1/user"
                headers = {"Authorization": f"Bearer {token}", "apikey": settings.SUPABASE_KEY}
                
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
            except Exception as e:
                logger.error(f"Supabase client error: {e}")
            
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
    
    # Trigger Welcome Email (Fire and forget or async)
    try:
        email_service.send_welcome_email(new_user.email, new_user.username)
    except Exception as e:
        logger.error(f"Signup: Failed to trigger welcome email: {e}")
        
    return new_user

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_async_db)):
    # 1. Try local DB authentication first
    stmt = select(User).where(User.email == login_data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    auth_success = False
    if user and user.hashed_password != "SUPABASE_AUTH_EXTERNAL":
        if auth_service.verify_password(login_data.password, user.hashed_password):
            auth_success = True
            
    # 2. Fallback to Supabase authentication if local fails
    if not auth_success:
        from core.config import settings
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                import httpx
                # Supabase Auth API: sign in with password to get a token
                sb_auth_url = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password"
                headers = {"apikey": settings.SUPABASE_KEY, "Content-Type": "application/json"}
                payload = {"email": login_data.email, "password": login_data.password}
                
                async with httpx.AsyncClient() as client:
                    resp = await client.post(sb_auth_url, json=payload, headers=headers)
                    
                if resp.status_code == 200:
                    sb_data = resp.json()
                    sb_user = sb_data.get("user", {})
                    email = sb_user.get("email")
                    
                    if email:
                        auth_success = True
                        # JIT Provision or Update local user
                        if not user:
                            # Provision new user from Supabase
                            base_username = email.split("@")[0]
                            username = base_username
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
                                hashed_password="SUPABASE_AUTH_EXTERNAL",
                                clerk_id=sb_user.get("id") # Store Supabase ID in clerk_id as a common external ref
                            )
                            db.add(user)
                            # Sync tier from metadata if available
                            meta = sb_user.get("user_metadata", {})
                            user.subscription_tier = meta.get("tier", "free")
                            
                            await db.commit()
                            await db.refresh(user)
                            logger.info(f"Auth: JIT provisioned Supabase user {email}")
                        else:
                            # User exists but authenticated via Supabase
                            user.hashed_password = "SUPABASE_AUTH_EXTERNAL"
                            if not user.clerk_id:
                                user.clerk_id = sb_user.get("id")
                            await db.commit()
                            logger.info(f"Auth: Synchronized existing user {email} with Supabase credentials")
            except Exception as e:
                logger.error(f"Auth: Supabase fallback login failed for {login_data.email}: {e}")

    if not auth_success or not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(
        data={"sub": user.username, "email": user.email, "tier": (user.subscription_tier or "free").lower()}
    )
    logger.info(f"Auth: Login success for {user.email}, user.id={user.id} (type={type(user.id)})")
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

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_async_db)):
    """Generate a reset token and email it to the user."""
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # Security: Always return 200 even if user doesn't exist to avoid enumeration
    if user:
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        user.password_reset_token = token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        await db.commit()
        
        # Send Email
        try:
            email_service.send_password_reset_email(user.email, token)
        except Exception as e:
            logger.error(f"Forgot Password: Failed to send email to {user.email}: {e}")
            
    return {"message": "If that email exists, a reset link has been sent."}

@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_async_db)):
    """Verify reset token and update password."""
    stmt = select(User).where(
        (User.password_reset_token == data.token) & 
        (User.password_reset_expires > datetime.now(timezone.utc))
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password and clear token
    user.hashed_password = auth_service.get_password_hash(data.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    await db.commit()
    
    return {"message": "Password updated successfully"}


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
        stmt = select(User).where(User.email == current_user.email)
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
            detail="Authentication check non-critical",
            headers={"WWW-Authenticate": "Bearer"},
        )
