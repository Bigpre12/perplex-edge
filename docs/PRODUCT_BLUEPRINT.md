# LUCRIX / Perplex Edge — Product Blueprint

Version: 1.0 (living document)  
Stack: Next.js 14 (Vercel) + FastAPI (Railway) + Postgres (Supabase) + Redis optional

**Institutional narrative, full IA, and page-by-page build spec:** [PERPLEX_EDGE_MASTER_BLUEPRINT.md](./PERPLEX_EDGE_MASTER_BLUEPRINT.md).

**V2 (event markets, simulation desk, five-column waterfall Part II):** [PERPLEX_EDGE_MASTER_BLUEPRINT_V2.md](./PERPLEX_EDGE_MASTER_BLUEPRINT_V2.md) · [WATERFALL_PROVIDER_MATRIX.md — Part II](./WATERFALL_PROVIDER_MATRIX.md#part-ii-v2-routing-spec).

**Brains audit (registry, health architecture, recovery, wiring notes):** [BRAINS_AUDIT_AND_REBUILD_SPEC.md](./BRAINS_AUDIT_AND_REBUILD_SPEC.md).

## 1. Product philosophy

LUCRIX is a **market intelligence operating system**: ingest multi-book odds, props, alt lines, injuries, news, Kalshi contracts, and internal model outputs; normalize; then surface **EV, edge quality, CLV potential, hit rates, disagreement, steam, and confidence-adjusted rankings**—never a single naked number without context (sample size, data freshness, model disagreement, liquidity).

**Principles**

- EV without confidence is a liability; always pair with confidence / data-quality.
- Hit rate without sample size and bucket definition is misleading.
- CLV is a **process** metric, not a payout promise.
- Alerts require **dedupe** and throttling or they become noise.
- Parlay UI must state **correlation assumptions** explicitly.
- Kalshi is **binary contract** risk; teach yes/no implied prob vs sportsbook semantics separately.

## 2. Information architecture

| Area | Route(s) | Purpose |
|------|-----------|---------|
| Marketing | `/` | Acquisition, proof, pricing |
| Auth | `/login`, `/signup`, `/forgot-password`, `/reset-password` | Session |
| Command | `/dashboard` | Terminal-style overview |
| Scanner | `/institutional/scanner` | Cross-market scan (v1 institutional surface) |
| Props | `/player-props` | Player prop board |
| EV+ | `/ev` | Edge table + compute triggers |
| CLV | `/clv` | Closing line value / results |
| Hit rate | `/hit-rate` | Graded performance |
| Signals | `/signals` | Alert-style feed (`/api/signals`) |
| Live | `/live` | Scores / live systems |
| Line move | `/line-movement` | Tick history |
| Tracker | `/bet-tracker` | Portfolio / slips |
| Brain | `/brain` | Model / intel status |
| Parlay | `/parlays`, `/parlay-builder` | Correlation builder |
| Sharp / Steam / Whale | `/sharp`, `/steam`, `/whale` | Flow analytics |
| Arb | `/arbitrage` | Cross-book arb |
| Kalshi | `/kalshi` | Event contracts (tier-gated) |
| Oracle | `/oracle` | LLM deep dive |
| Settings / Billing | `/settings`, `/pricing`, `/subscription`, `/checkout` | Prefs + Stripe |

## 3. Global design system (direction)

- **Dark-first**, high contrast, monospace for numbers, clear hierarchy (H1 display / section labels / table density).
- **Density modes** (future): compact / standard / relaxed; default compact on desktop.
- **Status**: live pulse, stale banner (ingestion lag), book freshness timestamp per row cluster.
- **Motion**: skeletons for heavy tables; micro-transition on row focus only.
- **Components**: DataTable pattern, `ErrorRetry`, `LoadingSkeleton`, sport filter bar, tab bar (mobile-first subset).

## 4. Backend architecture (per area)

| Area | Primary routers | Core services |
|------|-----------------|---------------|
| Health / meta | `/api/health`, `/api/meta/*` | DB, odds key health, `system_sync_state` |
| Props | `/api/props/*` | `props_service`, `persistence_helpers`, `unified_ingestion` |
| EV | `/api/ev/*`, compute | `ev_service`, `grader` |
| CLV | `/api/clv` | `brain_clv_tracker_loop`, CLV records |
| Hit rate | `/api/hit-rate/*` | `hit_rate` router, `player_hit_rates` |
| Brain | `/api/brain/*` | `brain_service`, advanced brain writers |
| Kalshi | `/api/kalshi/*`, `/api/kalshi_ws` | `kalshi_service`, `kalshi_ingestion`, `kalshi_ws` |
| Alerts / signals | `/api/alerts`, `/api/signals` | `alert_writer`, signals router |
| Ingestion | waterfall jobs | `unified_ingestion`, `odds_api_client`, BetStack client |

**Multi-provider waterfall:** see [WATERFALL_PROVIDER_MATRIX.md](./WATERFALL_PROVIDER_MATRIX.md) (chains per `sport_key` + `data_type`, trust tiers, ingestion stages). UI provenance rules: [UI_DATA_PROVENANCE.md](./UI_DATA_PROVENANCE.md).

**API versioning:** `GET /api/meta/build` returns `api_version`, `git_sha`, `environment` for clients to log and gate features.

**Standard error JSON** (non-2xx): `{ "error": { "code", "message", "request_id" } }` via global handlers (see implementation).

## 5. Core engines (conceptual contracts)

### 5.1 Odds ingestion + normalization

- Single canonical **event_id** per game; map book-specific ids.
- **Market keys** aligned to Odds API + internal enum (`h2h`, `spreads`, `totals`, `player_*`).
- **Line history** in `line_ticks` / props history for CLV and steam.
- **Stale handling**: do not delete props without minimum replacement count; surface `last_odds_sync` in health.

### 5.2 EV engine

- Implied prob from American odds; optional de-vig for consensus.
- Model prob vs implied → **edge_pct**, **confidence-adjusted** rank when model variance / data quality available.
- Outputs persist to **`ev_signals`** / edges history as implemented.

### 5.3 Hit-rate engine

- Bucket by line, opponent, home/away, role; show **n** and recency.
- Warn when **n < threshold**; cap display when corrupt (>100%).

### 5.4 CLV engine

- Store **entry line + price**; compare to **closing** line + price; support props where line and price move independently.

### 5.5 Brains engine

- Rank opportunities; attach **tags** (book disagreement, steam-confirmed, injury mismatch, thin liquidity).
- Separate **model confidence** vs **action score** (execution + liquidity).

### 5.6 Kalshi engine

- REST + optional WS; map contracts to sportsbook events when possible; surface **liquidity and resolution time**.

### 5.7 Parlay / correlation (V2+)

- Leg compatibility; SGP correlation adjustment; duplicate exposure warnings.

## 6. Suggested database schema (incremental toward)

Existing tables (repo): `props_live`, `props_history`, `unified_odds`, `ev_signals`, `line_ticks`, `sharp_alerts`, `player_hit_rates`, `model_picks`, `system_sync_state`, Kalshi-related, injuries, etc.

**Add over time:** `saved_views`, `user_bets` (normalized legs), `clv_records` (per bet snapshot), `alert_rules`, `alert_deliveries`, `feature_flags`, `ingestion_jobs` audit.

## 7. REST / WebSocket catalog (practical)

| Method | Path | Role |
|--------|------|------|
| GET | `/api/meta/build` | Version + deploy metadata |
| GET | `/api/health` | Liveness + pipeline timestamps |
| GET | `/api/props/live` | Props board |
| GET | `/api/props/graded` | Dashboard graded |
| GET | `/api/ev` | EV+ table |
| POST | `/api/ev/compute` | Recompute EV |
| GET | `/api/clv` | CLV views |
| GET | `/api/hit-rate` | Aggregate |
| GET | `/api/hit-rate/players` | Player table |
| GET | `/api/signals` | Signals feed |
| GET | `/api/slate/today` | Slate |
| GET | `/api/line-movement` | Moves per event |
| GET | `/api/kalshi` | Kalshi summary |
| WS | `/api/ws_ev` | Streaming EV (where enabled) |

## 8. Copy pack (premium, trader tone)

- **Hero:** “Market intelligence, not noise.” / “Quantify edges across books, props, and event contracts.”
- **Stale banner:** “Odds sync delayed. Showing last known board. Est. fresh: {eta}.”
- **Empty EV:** “No +EV edges at current thresholds. Widen filters or wait for board refresh.”
- **Upgrade (Pro):** “Unlock live steam, scanner exports, and alert webhooks.”
- **Disclaimer:** “Edges are model-assisted estimates. Past CLV does not guarantee future closing value.”

## 9. Subscription gating (recommended)

| Feature | Free | Pro | Elite |
|---------|------|-----|-------|
| Props / EV table (delayed) | Yes | Yes | Yes |
| Live / steam / whale (low latency) | Limited | Yes | Yes |
| Kalshi terminal + WS | No | Read-only | Full |
| Webhooks / exports | No | Yes | Yes |
| Scanner saved views | No | Yes | Yes |
| Admin / meta inspect | No | No | Staff |

## 10. User journeys (short)

1. **Scan → drill:** Scanner row → game page → player page → add to tracker / alert.
2. **EV session:** Dashboard health OK → EV+ → compute → sort by confidence-adjusted EV → book link out.
3. **CLV review:** Bet tracker → CLV page → segment by book/sport.

## 11. Admin / observability

- `/api/meta/inspect`, `/api/health/odds-api-status` (if present), logs, `system_sync_state`, Railway metrics.
- Feature flags table (future) for risky model rollouts.

## 12. Edge cases

- All Odds API keys cooling → show banner; preserve last board.
- BetStack 429 → single-flight cache per league.
- Pool exhaustion → scale pool (ops) + stagger jobs (implemented in API).

## 13. Launch priorities

### MVP (ship first)

Command center, props explorer, EV+, hit rate, CLV read paths, signals, line movement, health/stale UX, auth/billing shell, meta version endpoint.

### V2

Parlay correlation v1, Kalshi arb panel, webhook delivery UI, portfolio exposure rollup, WS odds subset.

### V3 (moat)

Multi-book “connections”, full model lab calibration UI, advanced correlation, institutional automation.

## 14. Default dashboard layout (recommended)

Row 1: **Board health** (sync timestamps, odds API status).  
Row 2: **Top edges** (sortable) + **Watchlist** (pinned from scanner).  
Row 3: **CLV drift** + **Open exposure**.  
Row 4: **Injuries / news impact** + **Brain queue** (top convictions).  
Footer: **Recently graded** + **Recommended actions**.

## 15. Recommended nav structure

See Sidebar + TabBar in `apps/web` after IA pass: **Desk → Scanner → Props → EV+ → CLV → Hit rate → Signals** as primary; secondary: Live, Move, Tracker, Brain, Parlay, Sharp, Arb, Whale, Kalshi, History, Settings.

## 16. Analytics events (product)

`page_view`, `sport_change`, `compute_trigger`, `ev_row_expand`, `alert_create`, `upgrade_click`, `kalshi_contract_view`, `clv_segment_change`.

---

*Implementation note: This blueprint aligns with the current monorepo (`apps/web`, `apps/api`). Incremental refactors should map UI routes to the contracts above without big-bang rewrites.*
