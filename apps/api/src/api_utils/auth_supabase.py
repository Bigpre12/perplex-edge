import os
from typing import Optional
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api_utils.supabase_proxy import supabase

security = HTTPBearer(auto_error=False)

async def get_current_user_supabase(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    FastAPI dependency to verify Supabase JWT token and return user info.
    Now supports optional authentication for public endpoints.
    """
    if not credentials:
        return None
        
    token = credentials.credentials
    try:
        # Verify token via Supabase Auth API
        sb_response = supabase.auth.get_user(token)
        
        # In supabase-py, get_user returns a response with .user and .error
        # or it might throw depending on the version.
        if hasattr(sb_response, 'user') and sb_response.user:
            return sb_response.user
        
        # Fallback for dict-based responses if applicable
        if isinstance(sb_response, dict) and 'user' in sb_response:
            return sb_response['user']
            
    except Exception as e:
        print(f"Supabase auth error: {e}")
        
    return None # Return None instead of raising 401 to handle public access
