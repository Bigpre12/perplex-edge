from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from routers.auth_router import get_current_user
from services.webhook_service import webhook_service
from typing import Dict, Any

router = APIRouter(prefix="/execution", tags=["execution"])

@router.post("/signal")
async def dispatch_signal(
    payload: Dict[str, Any],
    user: dict = Depends(get_current_user)
):
    """
    Dispatch a betting signal to the user's configured webhooks.
    """
    # In a real implementation, we would fetch these from the user's profile/settings
    discord_webhook = user.get('discord_webhook_url') or "MOCK_DISCORD_URL" 
    telegram_bot_token = user.get('telegram_token')
    telegram_chat_id = user.get('telegram_chat_id')

    message = webhook_service.format_prop_signal(payload)
    
    results = {}
    
    # Attempt Discord
    if discord_webhook and discord_webhook != "MOCK_DISCORD_URL":
        results['discord'] = await webhook_service.send_discord_signal(discord_webhook, message)
    else:
        results['discord'] = "Skipped (Not Configured)"

    # Attempt Telegram
    if telegram_bot_token and telegram_chat_id:
        results['telegram'] = await webhook_service.send_telegram_signal(telegram_bot_token, telegram_chat_id, message)
    else:
        results['telegram'] = "Skipped (Not Configured)"

    return {
        "status": "Signal Dispatch Initiated",
        "results": results,
        "payload_received": payload.get('player_name', 'Unknown')
    }

@router.get("/bot-connect")
async def bot_connect_feed(
    limit: int = 10,
    min_ev: float = 3.0,
    db: AsyncSession = Depends(get_async_db),
    user: dict = Depends(get_current_user)
):
    """
    Simplified API for 3rd party bots to consume high-edge props.
    Returns only the data needed for execution.
    """
    from models.props import PropLine
    from sqlalchemy import select
    
    stmt = (
        select(PropLine)
        .where(PropLine.ev_percent >= min_ev)
        .order_by(PropLine.ev_percent.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    props = result.scalars().all()
    
    feed = []
    for p in props:
        feed.append({
            "asset_id": p.id,
            "player": p.player_name,
            "sport": p.sport_key,
            "market": p.stat_type,
            "line": p.line_value,
            "side": p.side,
            "best_odds": p.odds, # Should ideally be the best from line_shopping
            "ev_percent": round(float(p.ev_percent), 2) if p.ev_percent else 0,
            "status": "ready"
        })
        
    return {
        "bot_status": "Operational",
        "timestamp": "now",
        "signals": feed
    }
