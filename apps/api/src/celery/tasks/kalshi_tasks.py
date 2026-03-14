import logging
import asyncio
import random
from services.kalshi_service import kalshi_service
from services.kalshi_ev import scan_all_ev_signals
from services.kalshi_arb import detect_arb_opportunities
from database import SessionLocal

logger = logging.getLogger(__name__)

async def call_with_backoff(func, *args, max_retries=5, **kwargs):
    """Execution wrapper with exponential backoff for 429s"""
    retry_delay = 1
    for i in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if "429" in str(e) or (hasattr(e, 'response') and e.response.status_code == 429):
                wait = retry_delay + random.uniform(0, 1)
                logger.warning(f"Kalshi: Rate limited. Retrying in {wait:.2f}s (Attempt {i+1})...")
                await asyncio.sleep(wait)
                retry_delay *= 2
            else:
                raise e
    raise Exception("Kalshi: Max retries exceeded")

async def sync_kalshi_markets():
    """Sync open markets every 60s with 429 backoff and DB upsert"""
    try:
        logger.info("Syncing Kalshi markets...")
        markets = await call_with_backoff(kalshi_service.get_kalshi_sports_markets, "NBA")
        
        async with SessionLocal() as session:
            from models.kalshi import KalshiMarket
            from sqlalchemy import select
            
            for m in markets:
                ticker = m.get("ticker")
                if not ticker: continue
                
                stmt = select(KalshiMarket).where(KalshiMarket.ticker == ticker)
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if existing:
                    existing.yes_price = float(m.get("yes_bid", 0)) / 100.0 if m.get("yes_bid") else existing.yes_price
                    existing.no_price = float(m.get("no_bid", 0)) / 100.0 if m.get("no_bid") else existing.no_price
                    existing.volume = m.get("volume", 0)
                else:
                    new_m = KalshiMarket(
                        ticker=ticker,
                        title=m.get("title"),
                        category=m.get("category"),
                        yes_price=float(m.get("yes_bid", 0)) / 100.0 if m.get("yes_bid") else 0,
                        no_price=float(m.get("no_bid", 0)) / 100.0 if m.get("no_bid") else 0,
                        volume=m.get("volume", 0),
                        is_active=True
                    )
                    session.add(new_m)
            
            await session.commit()
            logger.info(f"Successfully synced {len(markets)} Kalshi markets to DB")
    except Exception as e:
        logger.error(f"Failed to sync Kalshi markets: {e}")

async def sync_kalshi_ev_signals():
    """Sync EV signals every 30s with 429 backoff"""
    try:
        logger.info("Syncing Kalshi EV signals...")
        markets = await call_with_backoff(kalshi_service.get_kalshi_sports_markets, "NBA")
        signals = scan_all_ev_signals(markets, []) # In production, pass real sportsbook odds
        # Upsert logic...
    except Exception as e:
        logger.error(f"Failed to sync Kalshi EV signals: {e}")

async def sync_kalshi_arb_alerts():
    """Sync arb alerts every 30s with 429 backoff"""
    try:
        logger.info("Syncing Kalshi arb alerts...")
        markets = await call_with_backoff(kalshi_service.get_kalshi_sports_markets, "NBA")
        alerts = detect_arb_opportunities(markets, []) # In production, pass real sportsbook odds
        # Upsert logic...
    except Exception as e:
        logger.error(f"Failed to sync Kalshi arb alerts: {e}")
