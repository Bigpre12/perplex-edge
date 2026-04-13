# Perplex Edge Backend Audit

## 1. Ingestion Entrypoints & Schedulers
The backend uses `APScheduler` (specifically `AsyncIOScheduler`) in `main.py` to orchestrate recurring tasks.

- **Main Ingestion**: `unified_ingestion.run_with_retries` runs every 5 minutes for NBA, NFL, and NCAAF.
- **Grading**: `grading_service.run_grading_cycle` runs every 10 minutes.
- **Startup Tasks**: 
  - `initial_ingest()`: Runs `unified_ingestion` immediately after a 5-second delay.
  - `start_clv_tracker()`: Initiates the CLV tracking loop.

## 2. Brains & Analytics Engines
The "Brains" are specialized services that process market data and news to generate insights.

- **EV Engine**: `workers/ev_engine.py` (via `EVEngine.run_ev_cycle`)
- **Sharp Money**: `services/brain_sharp_money.py`
- **CLV Tracker**: `services/brain_clv_tracker.py`
- **Injury Impact**: `services/brain_injury_impact.py`
- **Advanced Service**: `services/brain_advanced_service.py` (Neural Engine/Neural Intelligence)
- **Anomaly detector**: `services/brain_anomaly_detector.py`

## 3. Database Access Layer
- **Core**: SQLAlchemy 2.0 with `asyncio`.
- **Infrastructure**: `db/session.py` provides `engine`, `AsyncSessionLocal`, and `SessionLocal` (sync).
- **Supabase**: Direct connection via `DATABASE_URL` (Postgres). Configuration in `core/config.py`.

## 4. API Routers
Routers are located in `apps/api/src/routers/` and imported dynamically in `main.py`.
- `/api/props`: `routers/props.py`
- `/api/intel`: `routers/intel.py`
- `/api/ev`: `routers/ev.py`
- `/api/clv`: `routers/clv.py`
- `/api/whale`: `routers/whale.py`
- `/api/injuries`: `routers/injuries.py`
- `/api/brain`: `routers/brain_router.py`
- `/api/signals`: `routers/signals.py`

## 5. Technical Debt & Issues Identified
- **Unawaited Coroutines**: `EVEngine.run_ev_cycle` has been noted in logs as "never awaited."
- **Mock Data**: Several `data/*.json` files and "emergency" fallbacks exist in `services/`.
- **Inconsistent Models**: Some services use older table structures or raw dictionaries.
