from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional, List
import asyncio
import json
import logging
import redis.asyncio as redis # Keep this import
import os
from core.config import settings
from starlette.websockets import WebSocketState

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/kalshi")
async def kalshi_ws_proxy(
    websocket: WebSocket, 
    token: str = Query(...), 
    tickers: Optional[str] = Query(None)
):
    """
    FastAPI WebSocket proxy for Kalshi prices.
    Subscribes to Redis "kalshi:prices" and broadcasts to clients.
    """
    # 1. Authenticate via token (Clerk JWT)
    # from api_utils.auth_supabase import verify_token
    # if not await verify_token(token):
    #     await websocket.close(code=4003)
    #     return

    await websocket.accept()
    
    redis_url = settings.REDIS_URL
    if not redis_url:
        logger.error("KalshiWSProxy: REDIS_URL not configured")
        await websocket.close(code=4000)
        return
        
    redis_conn = redis.from_url(redis_url, decode_responses=True)
    pubsub = redis_conn.pubsub()
    await pubsub.subscribe("kalshi:prices")
    
    ticker_list = tickers.split(",") if tickers else []
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                
                # Filter by ticker if requested
                if not ticker_list or data.get("ticker") in ticker_list:
                    await websocket.send_json(data)
                    
    except WebSocketDisconnect:
        logger.info("KalshiWSProxy: Client disconnected")
    except Exception as e:
        logger.error(f"KalshiWSProxy: Error: {e}")
    finally:
        try:
            await pubsub.unsubscribe("kalshi:prices")
            await redis_conn.close()
            if websocket.application_state == WebSocketState.CONNECTED:
                await websocket.close()
        except Exception:
            pass
