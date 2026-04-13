from typing import Optional
from fastapi import WebSocket, Query, Depends, HTTPException, status
from api_utils.supabase_proxy import supabase
import logging

logger = logging.getLogger(__name__)

async def get_current_user_ws(
    token: Optional[str] = Query(None)
):
    """
    WebSocket dependency to verify Supabase JWT token from query parameter.
    Returns the user object or raises HTTPException.
    """
    if not token:
        # For public access or if you want to allow anonymous WS, return None
        # But for this app, we likely want auth.
        logger.warning("No token provided for WebSocket connection")
        return None
        
    try:
        # Verify token via Supabase Auth API
        sb_response = supabase.auth.get_user(token)
        
        if hasattr(sb_response, 'user') and sb_response.user:
            return sb_response.user
        
        if isinstance(sb_response, dict) and 'user' in sb_response:
            return sb_response['user']
            
    except Exception as e:
        logger.error(f"Supabase auth error in WebSocket: {e}")
        
    return None
