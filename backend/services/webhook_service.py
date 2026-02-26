import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class WebhookService:
    async def send_discord_signal(self, webhook_url: str, content: str, embed: Optional[Dict[str, Any]] = None):
        """
        Send a signal to a Discord webhook.
        """
        payload = {"content": content}
        if embed:
            payload["embeds"] = [embed]
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
                return True
            except Exception as e:
                logger.error(f"Failed to send Discord signal: {e}")
                return False

    async def send_telegram_signal(self, bot_token: str, chat_id: str, message: str):
        """
        Send a signal via Telegram Bot API.
        """
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return True
            except Exception as e:
                logger.error(f"Failed to send Telegram signal: {e}")
                return False

    def format_prop_signal(self, prop_data: Dict[str, Any]) -> str:
        """
        Format property data into a readable signal message.
        """
        player = prop_data.get('player_name', 'Unknown Player')
        sport = prop_data.get('sport_key', 'Unknown Sport').upper()
        market = prop_data.get('stat_type', 'Market')
        line = prop_data.get('line_value', prop_data.get('line', 'N/A'))
        side = prop_data.get('side', 'OVER/UNDER').upper()
        odds = prop_data.get('odds_taken', prop_data.get('odds', 'N/A'))
        ev = prop_data.get('ev_percent', prop_data.get('edge', 0) * 100)
        book = prop_data.get('sportsbook', 'Unknown Book')

        return (
            f"🚨 <b>PERPLEX EDGE SIGNAL</b> 🚨\n\n"
            f"<b>Player:</b> {player}\n"
            f"<b>Sport:</b> {sport}\n"
            f"<b>Market:</b> {market}\n"
            f"<b>Selection:</b> {side} {line} (@{odds})\n"
            f"<b>Edge:</b> +{round(ev, 2)}% EV\n"
            f"<b>Bookmaker:</b> {book}\n\n"
            f"<i>Execute via Perplex Hub.</i>"
        )

webhook_service = WebhookService()
