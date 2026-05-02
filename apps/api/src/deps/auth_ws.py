from typing import Optional
from fastapi import WebSocket, Query, Depends, HTTPException, status
from api_utils.supabase_proxy import supabase
from services.auth_service import auth_service
import logging
import asyncio

logger = logging.getLogger(__name__)

async def get_current_user_ws(
    token: Optional[str] = Query(None)
):
    """
    WebSocket dependency to verify JWT token from query parameter.
    Supports both local JWT (from auth_service) and Supabase JWT.
    Returns the user object or None.
    """
    if not token:
        logger.warning("No token provided for WebSocket connection")
        return None
        
    try:
        # 1. Try Local JWT (Legacy/Internal)
        payload = auth_service.decode_access_token(token)
        if payload:
            # Create a synthetic user object to match expected interface
            return {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "app_metadata": {"tier": payload.get("tier", "free")},
                "user_metadata": {"tier": payload.get("tier", "free")}
            }

        # 2. Try Supabase Auth API (Synchronous call wrapped in executor to avoid blocking loop)
        loop = asyncio.get_running_loop()
        sb_response = await loop.run_in_executor(None, lambda: supabase.auth.get_user(token))
        
        if hasattr(sb_response, 'user') and sb_response.user:
            return sb_response.user
        
        if isinstance(sb_response, dict) and 'user' in sb_response:
            return sb_response['user']
            
    except Exception as e:
        logger.error(f"Auth error in WebSocket: {e}")
        
    return None
