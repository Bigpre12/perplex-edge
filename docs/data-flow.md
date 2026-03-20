# Perplex Edge: Data Flow & Architecture

This document outlines the standardized data flow in the Perplex Edge backend, from ingestion to API delivery.

## 1. 📥 Ingestion Layer (`UnifiedIngestionService`)

- **Source**: TheOddsAPI (and other providers).
- **Process**:
  1. Fetches raw odds/lines.
  2. Normalizes into `PropRecord` Pydantic models via `OddsMapper`.
  3. **Grouped Persistence**: Outcomes (Over/Under) are consolidated into a single market row.
  4. **Live Upsert**: Updates `props_live` table (primary key: `game_id`, `player_name`, `market_key`).
  5. **Historical Append**: Appends snapshot to `props_history`.

## 2. 🧠 Intelligence Layer (The "Brains")

Post-ingestion, specialized brains process the data:
- **Sharp/Whale Brain**: Detects heavy betting volume and steam moves.
- **CLV Tracker**: Monitors line movement vs. closing prices.
- **Injury Brain**: Quantifies the impact of player status changes.
- **EV Engine**: Calculates expected value vs. "true" probabilities.

## 3. 💾 Standardized Persistence (`persistence_helpers.py`)

All brains utilize common helpers to ensure schema integrity and async reliability:
- `upsert_props_live` / `append_props_history`
- `insert_edges_ev_history`
- `insert_whale_moves`
- `insert_clv_records`
- `insert_injury_events`

## 4. 🚀 API Delivery (Hardened Routers)

- **Schema Enforcement**: All routers (`props.py`, `intel.py`, `whale.py`, etc.) enforce Pydantic schemas (e.g., `PropLiveSchema`, `EvEdgeSchema`).
- **Zero-Mock Policy**: No local JSON mock files are permitted in production. All data is served from Supabase/Postgres.
- **Elite Tiering**: Premium routes (Whale, EV+) use `require_elite` decorators for access control.

## 🛡️ Reliablity & Verification

- **Test Suite**: `tests/test_api_reliability.py` automates schema compliance and mock-data checks.
- **Health Checks**: `/api/health` and `/api/meta/inspect` provide real-time infrastructure status.
