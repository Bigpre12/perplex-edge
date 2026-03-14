from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import asyncio
import json
import logging
import redis.asyncio as aioredis
import os

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
    
    redis_url = os.getenv("REDIS_URL")
    redis = aioredis.from_url(redis_url, decode_responses=True)
    pubsub = redis.pubsub()
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
        await pubsub.unsubscribe("kalshi:prices")
        await redis.close()
