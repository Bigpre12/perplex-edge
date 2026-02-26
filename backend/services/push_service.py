import os
import json
import logging
from typing import Dict, Any, Optional
from pywebpush import webpush, WebPushException

logger = logging.getLogger(__name__)

class PushService:
    def __init__(self):
        self.vapid_private_key = os.getenv("VAPID_PRIVATE_KEY")
        self.vapid_claims = {
            "sub": f"mailto:{os.getenv('ADMIN_EMAIL', 'admin@perplexedge.com')}"
        }

    async def send_notification(self, subscription: Dict[str, Any], message: str, title: str = "Perplex Edge Alert"):
        """
        Sends a web push notification to a specific subscriber.
        Subscription should contain {endpoint, p256dh, auth}.
        """
        if not self.vapid_private_key:
            logger.warning("Push Service Not Configured: Missing VAPID_PRIVATE_KEY")
            return False

        payload = {
            "title": title,
            "body": message,
            "icon": "/logo.png", # Path to your logo
            "badge": "/badge.png",
            "data": {
                "url": "/ledger" # Redirect URL on click
            }
        }

        try:
            webpush(
                subscription_info={
                    "endpoint": subscription["endpoint"],
                    "keys": {
                        "p256dh": subscription["p256dh"],
                        "auth": subscription["auth"]
                    }
                },
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims
            )
            return True
        except WebPushException as ex:
            logger.error(f"WebPush Error: {ex}")
            # If 410 Gone, the subscription has expired or been removed
            return False
        except Exception as e:
            logger.error(f"General Push Error: {e}")
            return False

push_service = PushService()
