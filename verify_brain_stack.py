import asyncio
import logging
import sys
import os
import json
import traceback
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from decimal import Decimal

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'apps', 'api', 'src')))

# Mock things that might fail in local env
sys.modules['celery'] = MagicMock()
sys.modules['celery_app'] = MagicMock(celery_app=MagicMock())

from services.unified_ingestion import UnifiedIngestionService
from services.cache import cache
from database import async_session_maker, engine, Base
from models.brain import SharpSignal, InjuryImpact, CLVRecord
import models # Ensure all models are loaded for create_all

# Set logging to DEBUG to see everything
logging.basicConfig(level=logging.DEBUG)
# Suppress some noisy logs
logging.getLogger("aioredis").setLevel(logging.WARNING)

async def verify_brain_stack():
    print("\n--- Verifying Brain Stack (Week 1) ---")
    
    # 0. Ensure Tables Exist
    print("Ensuring database tables exist...")
    Base.metadata.create_all(engine)
    
    await cache.connect()
    
    sport = "basketball_nba"
    event_id = "test_brain_event_1"
    
    # Clear all test keys
    print("Clearing test cache keys...")
    await cache.delete(f"odds:raw:{sport}")
    await cache.delete(f"odds:last_run:{sport}")
    await cache.delete(f"clv:open:{sport}:{event_id}:h2h:lakers:draftkings")
    track_key = f"sharp:track:{sport}:{event_id}:h2h:lakers:draftkings"
    await cache.delete(track_key)

    service = UnifiedIngestionService()
    
    # Mock data with a fake event
    mock_raw = [{
        "id": event_id,
        "sport_title": "NBA",
        "commence_time": datetime.now(timezone.utc).isoformat(),
        "bookmakers": [{
            "key": "draftkings",
            "markets": [{
                "key": "h2h",
                "outcomes": [
                    {"name": "Lakers", "price": -110},
                    {"name": "Celtics", "price": 110}
                ]
            }]
        }]
    }]

    # 1. Test Ingestion + Sharp/CLV Trigger
    print("\nSimulating ingestion cycle (Run 1 - Opening)...")
    with patch('services.unified_ingestion.fetch_odds') as mock_fetch:
        mock_fetch.return_value = mock_raw
        with patch.object(UnifiedIngestionService, 'has_active_events', return_value=True):
            await service.run(sport)

    # 2. Check CLV Record (Opening line should be in Redis)
    open_key = f"clv:open:{sport}:{event_id}:h2h:lakers:draftkings"
    opener = await cache.get(open_key)
    print(f"\nCLV Opening Record in Redis: {'FOUND' if opener else 'MISSING'}")
    if opener:
        print(f"  - Data: {opener}")

    # 3. Trigger a "Steam" move (second run with data change)
    print("\nSimulating line movement (Run 2 - Steam)...")
    mock_raw_v2 = json.loads(json.dumps(mock_raw))
    # Change price significantly to trigger steam (Decimal price move > 0.15)
    # -110 is ~1.91 decimal. -250 is ~1.4 decimal. Delta is ~0.5.
    mock_raw_v2[0]["bookmakers"][0]["markets"][0]["outcomes"][0]["price"] = -250 
    
    with patch('services.unified_ingestion.fetch_odds') as mock_fetch:
        mock_fetch.return_value = mock_raw_v2
        with patch.object(UnifiedIngestionService, 'has_active_events', return_value=True):
            # Bypass cache to force second run processing
            await cache.delete(f"odds:raw:{sport}")
            await cache.delete(f"odds:last_run:{sport}")
            await service.run(sport)

    # 4. Verify DB Records
    print("\nVerifying Database Records...")
    async with async_session_maker() as session:
        try:
            from sqlalchemy import select
            # Check Sharp Signals
            stmt = select(SharpSignal).where(SharpSignal.event_id == event_id)
            res = await session.execute(stmt)
            signals = res.scalars().all()
            print(f"Sharp Signals generated: {len(signals)}")
            for s in signals:
                print(f"  - Signal: {s.signal_type} on {s.selection} (Severity: {s.severity})")

            # Check Injury Impacts
            stmt_inj = select(InjuryImpact).where(InjuryImpact.sport == sport)
            res_inj = await session.execute(stmt_inj)
            impacts = res_inj.scalars().all()
            print(f"Injury Impacts quantified: {len(impacts)}")
            if impacts:
                print(f"  - Sample: {impacts[0].player_name} ({impacts[0].status})")
                
        except Exception as e:
            print(f"DB Verification Error: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_brain_stack())
