# Phase 0 Contract Inventory

This inventory freezes current backend and frontend integration points before phased rewrite work.

## Backend Route Surface (from `apps/api/src/main.py`)

Mounted router prefixes currently include:

- `/api/health`
- `/api/meta`
- `/api/auth`
- `/api/props`
- `/api/ev`
- `/api/clv`
- `/api/brain`
- `/api/bets`
- `/api/injuries`
- `/api/news`
- `/api/signals`
- `/api/metrics`
- `/api/hit-rate`
- `/api/whale`
- `/api/steam`
- `/api/stripe`
- `/api/billing`
- `/api/search`
- `/api/oracle`
- `/api/live`
- `/api/slate`
- `/api/line-movement`
- `/api/arbitrage`
- `/api/middle-boost`
- `/api/kalshi`
- `/api/kalshi_ws`
- `/api/sharp`
- `/api/parlays`
- `/api/simulation`
- `/api/waterfall`
- `/api/hero`
- `/api` (pick-intel and unified routers)

Standalone endpoints in `main.py`:

- `GET /health` (process liveness + DB check)
- `GET /` (root)
- multiple admin endpoints under `/api/admin/*`

## Frontend Consumer Surface (MVP pages)

The MVP pages currently consume:

- `dashboard` via `useDashboard`:
  - `/api/health`
  - `/api/brain/status`
  - `/api/props`
  - `/api/whale`
  - `/api/ev/top`
- `scanner` direct fetch:
  - `/api/props?sport=*`
- `player-props` via `useProps`:
  - `/api/props?sport=*&limit=*`
- `ev` via `useEV`:
  - `/api/ev/top?sport=*&limit=*`
- `live` via `useLiveGames`:
  - `/api/live/scores?sport=basketball_nba`
  - websocket `/api/live/ws`

## Contract Guardrails (active)

1. Do not break existing route signatures unless introducing explicit versioning.
2. Frontend must consume backend contract; no frontend-first payload inventions.
3. New fields are additive whenever possible.
4. Keep liveness endpoints (`/health`, `/api/health`, `/api/health/deps`) HTTP 200 with degradation signaled in payload.

