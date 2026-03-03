import httpx
import os
import logging
from typing import Dict, Any
from services.insight_engine import get_top_edges
from database import SessionLocal

logger = logging.getLogger(__name__)
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

def format_edge_embed(prop: Dict[str, Any]) -> Dict[str, Any]:
    """Formats a prop edge into a Discord embed object."""
    # Color based on hit rate: Green for 75%+, Orange for 70%+
    color = 0x22c55e if prop["hit_rate"] >= 0.75 else 0xf59e0b
    trend_emoji = "🔥" if prop["trend"] == "heating_up" else "📊"
    
    return {
        "title": f"{trend_emoji} {prop['player_name']} — {prop['prop_type'].replace('player_', '').upper()} {prop['line']}",
        "color": color,
        "fields": [
            {"name": "Hit Rate (L15)", "value": f"{(prop['hit_rate'] * 100):.0f}%", "inline": True},
            {"name": "Trend", "value": prop["trend"].replace("_", " ").title(), "inline": True},
            {"name": "Sample", "value": str(prop["sample_size"]), "inline": True},
        ],
        "footer": {"text": "Lucrix Edge Alert | AI Powered"},
    }

async def send_daily_top_edges():
    """Fetches top edges and posts them to Discord."""
    if not DISCORD_WEBHOOK:
        logger.warning("DISCORD_WEBHOOK_URL not set, skipping alerts.")
        return

    db = SessionLocal()
    try:
        # Get top 5 edges with at least 70% hit rate
        edges = get_top_edges(db, min_hit_rate=0.70, limit=5)
        if not edges:
            logger.info("No high-probability edges found for Discord alert.")
            return

        embeds = [format_edge_embed(e) for e in edges]
        payload = {
            "username": "Lucrix Edge Bot",
            "avatar_url": "https://lucrix.ai/logo.png",
            "content": "🏆 **Today's Top Analytics Edges** — Lucrix",
            "embeds": embeds,
        }

        async with httpx.AsyncClient() as client:
            r = await client.post(DISCORD_WEBHOOK, json=payload, timeout=10)
            logger.info(f"Discord Edge Alert sent: {r.status_code}")
    except Exception as e:
        logger.error(f"Error sending Discord edge alert: {e}")
    finally:
        db.close()
