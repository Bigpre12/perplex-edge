import json
import os
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SHARES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "shares.json")

class ShareService:
    def __init__(self):
        self.shares_file = SHARES_FILE
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.shares_file):
            with open(self.shares_file, "w") as f:
                json.dump({}, f)

    def _load_shares(self) -> Dict[str, Any]:
        try:
            with open(self.shares_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading shares: {e}")
            return {}

    def _save_shares(self, shares: Dict[str, Any]):
        try:
            with open(self.shares_file, "w") as f:
                json.dump(shares, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving shares: {e}")

    async def create_share(self, prop_data: Dict[str, Any]) -> str:
        """Create a shareable link ID for a prop"""
        shares = self._load_shares()
        share_id = str(uuid.uuid4())[:8] # Short ID
        
        shares[share_id] = {
            "data": prop_data,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        self._save_shares(shares)
        return share_id

    async def get_share(self, share_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve prop data for a share ID"""
        shares = self._load_shares()
        return shares.get(share_id)

share_service = ShareService()
