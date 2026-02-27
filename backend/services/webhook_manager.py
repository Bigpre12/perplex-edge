import httpx
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class WebhookManager:
    def __init__(self):
        self.http_client = httpx.AsyncClient()

    async def send_discord_alert(self, webhook_url: str, pick_data: dict):
        """
        Sends a rich-embed Discord notification for a specific +EV pick.
        """
        try:
            player_name = pick_data.get("player_name", "Unknown Player")
            edge = pick_data.get("ev_percentage", 0)
            line = pick_data.get("line", 0)
            stat = pick_data.get("stat_type", "Stat")
            book = pick_data.get("sportsbook", "DraftKings")
            
            payload = {
                "username": "Perplex Edge Bot",
                "avatar_url": "https://perplexedge.com/og-image.png",
                "embeds": [{
                    "title": f"🚀 Institutional +EV Alert: {player_name}",
                    "description": f"Target found at **{book}** with a verified edge.",
                    "color": 0x10b981, # Emerald Green
                    "fields": [
                        {"name": "stat", "value": stat, "inline": True},
                        {"name": "line", "value": f"{line}", "inline": True},
                        {"name": "edge", "value": f"+{edge}%", "inline": True},
                    ],
                    "footer": {"text": "Powered by Perplex Edge Intelligence"}
                }]
            }
            
            # Use self.http_client to send the post
            response = await self.http_client.post(webhook_url, json=payload, timeout=5.0)
            return response.status_code == 204
        except Exception as e:
            logger.error(f"Failed to send Discord webhook: {e}")
            return False

    async def dispatch_alerts(self, picking_data: list, registered_hooks: list):
        """
        Iterates through active picks and dispatches them to all registered customer webhooks.
        """
        tasks = []
        # For efficiency, we only alert on high-value items (e.g. Edge > 4%)
        high_ev_picks = [p for p in picking_data if p.get("ev_percentage", 0) > 4.0]
        
        for pick in high_ev_picks:
            for hook_url in registered_hooks:
                tasks.append(self.send_discord_alert(hook_url, pick))
        
        if tasks:
            results = await asyncio.gather(*tasks)
            logger.info(f"📢 Dispatched {sum(results)} alerts to external Discord Webhooks.")

webhook_manager = WebhookManager()
