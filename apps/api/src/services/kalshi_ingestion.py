import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import async_session_maker
from services.kalshi_service import kalshi_service
from services.kalshi_ev import scan_all_ev_signals
from services.odds_api_client import odds_api_client
from models import UnifiedEVSignal
from core.sports_config import SPORT_MAP, PROP_MARKETS
from services.cache import cache
import json

logger = logging.getLogger(__name__)

KALSHI_CACHE_KEY = "kalshi:ev_signals:{sport}"

class KalshiIngestion:
    async def run(self, sport: str = "NBA"):
        """Fetches Kalshi markets and matches them against Sportsbook props to save EV signals."""
        logger.info(f"KalshiIngestion: Starting sync for {sport}")
        if odds_api_client.all_keys_dead():
            logger.debug("Skipping KalshiIngestion.run — all keys cooling down")
            return []
        
        kalshi_sport = sport.upper()
        odds_sport = SPORT_MAP.get(sport.lower(), "basketball_nba")
        
        try:
            # 1. Get Kalshi Markets
            markets = await kalshi_service.get_kalshi_sports_markets(kalshi_sport)
            if not markets:
                logger.info(f"KalshiIngestion: No markets found for {kalshi_sport}")
                return

            # 2. Get Sportsbook Odds (first few events)
            events = await odds_api_client.get_events(odds_sport)
            if not events:
                return
                
            real_props = []
            # Use a default market for Kalshi sync, as it usually focuses on main props
            markets_to_fetch = "player_points"
            
            # Fetch props for first 5 events to overlap with Kalshi
            for event in events[:5]:
                data = await odds_api_client.get_player_props(odds_sport, event['id'], markets_to_fetch)
                if not data: continue
                
                for book in data.get("bookmakers", []):
                    for mkt in book.get("markets", []):
                        for outcome in mkt.get("outcomes", []):
                            if outcome.get("name") == "Over":
                                real_props.append({
                                    "player": outcome.get("description", outcome.get("name")),
                                    "market": mkt.get("key"),
                                    "line": outcome.get("point"),
                                    "odds": outcome.get("price"),
                                    "bookmaker": book.get("title")
                                })
            
            # 3. Scan for EV Signals
            signals = scan_all_ev_signals(markets, real_props)
            logger.info(f"KalshiIngestion: Found {len(signals)} EV signals for {sport}")
            
            # 4. Cache for router
            cache_key = KALSHI_CACHE_KEY.format(sport=sport.lower())
            await cache.set(cache_key, json.dumps(signals), expire=600) # 10 min cache
            
            return signals

        except Exception as e:
            logger.error(f"KalshiIngestion Error for {sport}: {e}")
            return []

    async def get_cached_signals(self, sport: str = "NBA") -> list:
        cache_key = KALSHI_CACHE_KEY.format(sport=sport.lower())
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)
        # If not cached, trigger a background run and return empty for now to avoid blocking
        asyncio.create_task(self.run(sport))
        return []

kalshi_ingestion = KalshiIngestion()
