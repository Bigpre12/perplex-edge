# Perplex Edge / LUCRIX — Master Product Blueprint

**Version:** 2.0 (institutional narrative + build-ready IA) — **snapshot**  
**Full V2 scope** (Kalshi sports vs life-event, Monte Carlo desk, five-column domain matrix, routing contracts, audit schema): use **[PERPLEX_EDGE_MASTER_BLUEPRINT_V2.md](./PERPLEX_EDGE_MASTER_BLUEPRINT_V2.md)** and **[WATERFALL_PROVIDER_MATRIX.md — Part II](./WATERFALL_PROVIDER_MATRIX.md#part-ii-v2-routing-spec)**.

**Stack:** Next.js 14 (`apps/web`) · FastAPI (`apps/api`) · Postgres (Supabase) · Redis (optional)  
**Companion specs:** [WATERFALL_PROVIDER_MATRIX.md](./WATERFALL_PROVIDER_MATRIX.md) · [UI_DATA_PROVENANCE.md](./UI_DATA_PROVENANCE.md) · [BRAINS_AUDIT_AND_REBUILD_SPEC.md](./BRAINS_AUDIT_AND_REBUILD_SPEC.md) · [PRODUCT_BLUEPRINT.md](./PRODUCT_BLUEPRINT.md) (implementation-oriented summary)

---

## 0. Executive framing

### 0.1 What this product is

**LUCRIX (Perplex Edge)** is a **private market intelligence operating system** for serious bettors and small trading desks. It is not a sportsbook, not a touts marketplace, and not a single-vendor odds viewer. It is a **fusion layer**: multi-book prices, props, alt lines, injuries, schedules, scores, optional **Kalshi** event contracts, and **internal model outputs**—normalized into one canonical event and market graph—then scored for **EV**, **edge quality**, **CLV process**, **hit-rate integrity**, **cross-book disagreement**, **steam / flow proxies**, **liquidity quality**, and **confidence-adjusted actionability**.

The experience target: **Bloomberg-grade density** + **quant research workstation** clarity + **execution desk** workflows (scan → drill → size → track → review CLV).

### 0.2 What this product is not

- Not “The Odds API with a skin.” The Odds API is one **tier-A** ingress for multi-book US/international boards—not the architecture.
- Not a promise of profit. Numbers are **estimates** conditioned on data lineage, sample size, and model variance.
- Not Kalshi-as-sportsbook. Contracts are **binary exchange instruments**; implied probabilities are comparable only with explicit mapping and separate confidence streams.

### 0.3 Non-negotiable: multi-provider waterfall

All product copy, UI badges, engineering contracts, and **sales narrative** must reflect **multi-source fusion** and **ordered failover**, per `core/waterfall_config.py`, `WaterfallRouter`, `unified_ingestion`, and the matrix doc.

**Live / roadmap provider set (narrative + code):**

| Layer | Providers |
|-------|-----------|
| **Odds & props (primary board)** | The Odds API; BetStack (consensus lines); merge + persist in `unified_ingestion` |
| **Odds waterfall (API / router)** | Ordered chain typically includes The Odds API → BetStack → TheRundown → SportsGameOdds → iSports → API-Sports (sport-dependent); see matrix |
| **Schedules & US games** | BallDontLie → API-Sports → TheSportsDB → ESPN |
| **Soccer depth** | API-Sports → SportMonks → TheSportsDB → ESPN |
| **Scores / live state** | ESPN → API-Sports → … |
| **Injuries** | ESPN → API-Sports → TheSportsDB |
| **MMA / alt-line bias** | SportsGameOdds (quota-aware) + The Odds API where applicable |
| **Analytics (soccer specialty)** | StatsBomb (event analytics path—not live odds) |
| **Exchange** | Kalshi REST / WS (tiered) |
| **Roadmap** | OddsPapi (config key; client TBD); SportsDataIO; Sportradar |

External reference (vendor landscape context): [The Odds API — sports APIs overview](https://the-odds-api.com/sports-odds-data/sports-apis.html).

---

## 1. Design principles (product + UX)

1. **Every number has lineage** — source provider, freshness, and confidence (or explicit “unknown”).
2. **EV is a distribution, not a headline** — show edge, uncertainty, and data tier together.
3. **CLV is process** — language never implies payout guarantee.
4. **Alerts are budgeted** — dedupe, throttle, severity; user controls caps.
5. **Parlays state correlation** — same-game exposure and leg dependence are visible, not buried.
6. **Kalshi is labeled exchange risk** — separate badges, tooltips, and optional tab isolation.
7. **Degraded mode is first-class** — stale banners, last-known board, reduced confidence (see UI provenance doc).

---

## 2. Voice & UX writing system

### 2.1 Tone

- **Institutional:** precise, no hype adjectives, no emoji in product chrome.
- **Technical:** define buckets, books, markets, and lookback windows in UI.
- **Honest:** “No edge at current filters” beats fake activity.

### 2.2 Microcopy patterns

| Context | Copy direction |
|---------|----------------|
| Global stale | “Board sync delayed. Showing last known lines. Freshness: {relative}.” |
| Fallback provider | “Consensus / backup feed” + tooltip with provider name from `source_provider`. |
| Empty EV | “No signals above threshold. Widen book set, lower min edge, or wait for ingest.” |
| Kalshi | “Exchange contract — not a sportsbook line.” |
| Small sample hit rate | “n = {n} in this bucket. Shrink toward prior below {N}.” |
| Legal footer | “Intelligence only. You place bets at licensed operators. Past CLV does not predict future closes.” |

### 2.3 Typography & layout (global)

- **Dark-first**, monospace for prices and deltas, proportional for prose.
- **Three density modes:** Compact (default desktop), Standard, Relaxed (onboarding / tablet).
- **Tables:** frozen header, column-driven resize, optional row detail drawer (no navigation dead-ends).
- **Motion:** skeletons for >200ms fetch; 150ms row focus; no gratuitous chart animation.

---

## 3. Information architecture (nav clusters)

Primary rail (Desk): **Command · Scanner · Props · EV+ · CLV · Hit rate · Signals**  
Secondary: **Live · Line move · Tracker · Brain · Parlay lab · Flow (Sharp / Steam / Whale) · Arb · Kalshi · Oracle**  
Utility: **Slate · Schedule · Injuries · News · Books · Markets · History · Performance · Ledger · Bankroll · Streaks**  
Institutional (tier): **Scanner · Execution · Strategy lab · Affiliate · Settings**  
System: **Settings · Pricing · Subscription · Checkout · Upgrade · Support · Admin · Audit**

---

## 4. Page-by-page specification

Each row is **build-ready**: primary user job, **data lineage** (which layers feed the page—not only Odds API), primary API contracts (as implemented or targeted), layout blocks, and critical states.

**Legend — Data lineage tags:**  
`ING` = unified ingestion (`props_live` / `unified_odds`); `WF-O` = waterfall odds (`/api/waterfall/odds` or router); `WF-S` = schedule waterfall; `H` = health/meta; `INT` = internal engines (EV, brain, grader).

| Route | User job | Primary data lineage | Primary APIs / services | Layout blocks | Empty / error / edge |
|-------|----------|----------------------|-------------------------|---------------|----------------------|
| `/` | Understand product; convert | Narrative + social proof | Marketing CMS / static | Hero, proof strip, pricing teaser, CTA | Skeleton hero; geo-gated CTA |
| `/login` | Authenticate | Supabase auth | Auth API | Email/password, SSO future | Lockout copy; magic link future |
| `/signup` | Register | Supabase | Auth API | Form, plan hint | Duplicate email precise message |
| `/forgot-password` | Recover | Supabase | Auth API | Email field | Rate-limit message |
| `/reset-password` | Set password | Supabase | Auth API | Password + confirm | Token expired |
| `/dashboard` | Day-open health + top opportunities | `ING` + `INT` + `H` | `/api/health`, `/api/meta/build`, `/api/meta/waterfall`, props/EV slices | Board health row, top edges, watchlist, CLV snapshot, brain queue | All sections stale-aware |
| `/top-edges` | Ranked edges only | `INT` + `ING` | `/api/ev`, compute | Sortable table, confidence column | Empty per microcopy |
| `/institutional/scanner` | Cross-market scan | `ING` + multi-book | Props/unified odds, scanner API | Filters, density toggle, export (gated) | “No rows” + filter reset |
| `/institutional/execution` | Desk-style execution | `ING` + tracker | Tracker + odds | Watchlist + line table | Requires auth persistence |
| `/institutional/strategy-lab` | Experiment with thresholds | `INT` | EV compute, flags | Sliders, backtest stub | “Insufficient history” |
| `/institutional/affiliate` | Partner flows | Static + referrals | Partner API | Cards, disclosures | Region block |
| `/institutional/settings` | Org prefs | User/org | Settings API | Feature flags read-only | Permission denied |
| `/player-props` | Prop board | **`ING` (Odds API + BetStack merge)** | `/api/props/live`, ingest meta | Sport bar, market tabs, book columns, provenance chip | Stale banner; single-book warning |
| `/props` | Alternate props view | `ING` | `/api/props/*` | Table + detail | Same |
| `/props-history` | Time series props | `ING` + DB history | History endpoints | Chart + table | Sparse tick warning |
| `/prop-combos` | Correlated combos | `ING` + model | Combo service | Leg builder | Correlation disclaimer |
| `/player/[id]` | Player drill-down | `ING` + hit-rate | Player APIs | Profile, prop chart, hit buckets | Low-n banner |
| `/ev` | EV+ table | `INT` | `/api/ev`, `POST /api/ev/compute` | Filters, edge, confidence, book | Post-compute refresh |
| `/brain` | Model / brain status | `INT` | `/api/brain/*` | Queue, conviction, errors | “Brain idle” with last run |
| `/oracle` | LLM-assisted research | LLM + context | Oracle router | Chat + citations | Rate limit; no picks without sources |
| `/clv` | Closing value analysis | `INT` + ticks | `/api/clv` | Entry vs close, segments | “No close” per bucket |
| `/hit-rate` | Graded performance | `INT` | `/api/hit-rate`, players | Buckets, n, recency | Shrink thresholds visible |
| `/signals` | Alert stream | Alerts + `INT` | `/api/signals`, `/api/alerts` | Feed, severity, dedupe id | Empty feed not failure |
| `/live` | Scores / live | **`WF-S` + ESPN bias** | Scoreboard APIs | Scoreboard, period | Delay banner |
| `/line-movement` | Tick history | DB ticks + `ING` | `/api/line-movement` | Event picker, sparkline | Low tick density |
| `/steam` | Steam detection | Ticks + flow | Steam router | Windows, book | Noise disclaimer |
| `/sharp` | Sharp / consensus shift | Models + ticks | Sharp APIs | Table + chart | |
| `/whale` | Large move / whale heuristics | Flow proxies | Whale APIs | Timeline | Sparse data |
| `/arbitrage` | Cross-book arb | Multi-book `ING` | Arb endpoints | Arb table, fee field | After-vig negative common |
| `/parlays`, `/parlay`, `/parlay-builder` | Parlay construction | `ING` + correlation | Parlay APIs | Leg picker, SGP warn | Leg stripped if no price |
| `/kalshi` | Event contracts | **Kalshi only** | `/api/kalshi`, WS | Order book style, separate badge | Tier gate; not odds |
| `/bet-tracker` | Portfolio | User bets + lines | Tracker APIs | Open / graded, CLV link | Empty portfolio CTA |
| `/slate`, `/schedule` | Slate / schedule | **`WF-S`** (BDL, API-Sports, …) | `/api/slate/today`, waterfall games | Cards by time | DNP handling |
| `/injuries` | Injury panel | ESPN → API-Sports → TSB | Injuries API | Team filter | Delay tooltip |
| `/news` | News context | ESPN / feeds | News API | Headlines | |
| `/books`, `/markets` | Book + market reference | Metadata | Meta | Reference tables | |
| `/performance` | P&L / ROI views | Tracker + grades | Analytics | Charts | |
| `/ledger`, `/ledger/analytics` | Accounting-style log | User + settlements | Ledger APIs | Tables | |
| `/bankroll` | Bankroll rules | User | User prefs | Kelly / flat (info only) | Not financial advice |
| `/streaks` | Streak stats | Derived | Stats | Fun / serious toggle | |
| `/middle-boost`, `/trend-hunter`, `/shared-intel`, `/share/[id]`, `/intel`, `/leaderboard`, `/results`, `/upgrade`, `/pricing`, `/subscription`, `/checkout`, `/settings`, `/support`, `/admin`, `/audit` | Growth, social, billing, compliance | Mixed | Appropriate routers | Each: one primary job, provenance where numeric | See UI provenance |

---

## 5. State management (frontend architecture)

### 5.1 Global client state

- **`useSession`** — auth + tier + feature flags from `/api/meta/build` + user endpoint.
- **`useBoardHealth`** — `last_odds_sync`, heartbeat-derived freshness, `/api/meta/waterfall` optional aggregation.
- **`useSportContext`** — selected sport keys; persist per device.
- **`useProvenance`** — map row → `source_provider`, `fallback_used`, `data_freshness_seconds` (forward fields).

### 5.2 Server state

- TanStack Query (or equivalent): **staleTime** per resource class — odds 30–60s, CLV 5–15m, hit-rate 1h.
- **Single-flight** compute: `POST /api/ev/compute` debounced globally per session.

### 5.3 URL as state

- Scanner, EV, props: filters in querystring for shareable desk links (`sport`, `books`, `minEdge`, `market`, `sort`).

---

## 6. Intelligence engines (operational contract)

| Engine | Inputs | Outputs | Confidence downgrades |
|--------|--------|---------|------------------------|
| **Ingestion normalizer** | Odds API events; BetStack events; optional Kalshi; waterfall fallback shapes | `unified_odds`, `props_live`, ticks | Fallback chain used; single-book; stale sync |
| **Fair / de-vig** | Multi-book lines | Fair p | Few books; wide spread |
| **EV** | Fair vs offered; injury flags | `ev_signals` | Stale board; fallback_used |
| **Brain ranker** | EV + liquidity + disagreement + steam | Picks / tags | Model disagreement |
| **CLV** | Entry snapshot + closing tick | CLV records | Close from secondary provider |
| **Hit rate** | Graded bets | Buckets | Low n |
| **Steam / sharp / whale** | `line_ticks`, volume proxies | Alerts | Low tick density |
| **Parlay correlation** | Leg covariance estimates | Adjusted price / warning | Missing correlation model |
| **Kalshi bridge** | Contract mid, volume, time to resolution | Cross-signal features | Illiquid contract |

---

## 7. Backend integration map (authoritative handoff)

| Domain | Routers / jobs | Upstream providers (never single-source story) |
|--------|----------------|-----------------------------------------------|
| Props / odds board | `/api/props/*`, `unified_ingestion` | Odds API + BetStack + (opt) Kalshi; DB persistence |
| Waterfall read APIs | `/api/waterfall/*` | Full odds chain from `waterfall_config` |
| EV / brain | `/api/ev/*`, `/api/brain/*` | Postgres signals; ingest freshness |
| CLV / hit-rate | `/api/clv`, `/api/hit-rate/*` | Ticks + grades |
| Kalshi | `/api/kalshi*`, WS | Kalshi only |
| Health / meta | `/api/health`, `/api/meta/*` | Heartbeats; `/api/meta/waterfall` provider last success |
| Flow | Steam / sharp / whale routers | Ticks + internal |

---

## 8. Subscription & gates (recommended framing)

| Capability | Free | Pro | Elite |
|------------|------|-----|-------|
| Delayed board + EV | ✓ | ✓ | ✓ |
| Live / low-latency flow | Limited | ✓ | ✓ |
| Kalshi terminal + WS | — | Read | Full |
| Webhooks / exports | — | ✓ | ✓ |
| Scanner saved views | — | ✓ | ✓ |
| Admin / audit | — | — | Staff |

Copy always states **what data classes** unlock, not vague “more picks.”

---

## 9. Observability & trust

- **`GET /api/meta/build`** — version, SHA, environment (client logging).
- **`GET /api/meta/waterfall`** — per-provider last success (heartbeat-mapped + stubs).
- **`GET /api/meta/inspect`** — row counts, stale signal flags.
- **Audit** (`/audit`, admin): model version, ingest job id, config hash (future).

---

## 10. Analytics events (product telemetry)

`page_view`, `sport_change`, `compute_ev`, `ev_row_expand`, `props_filter_apply`, `stale_banner_shown`, `fallback_badge_view`, `alert_create`, `kalshi_contract_open`, `clv_segment_change`, `upgrade_click`, `export_scanner_csv`.

---

## 11. Implementation waves

| Wave | Scope |
|------|--------|
| **W1** | Global nav per §3; board health + provenance on props/EV/dashboard; stale/fallback copy from UI doc |
| **W2** | URL state for scanner/EV; meta waterfall panel in settings for Elite |
| **W3** | Parlay correlation UI; Kalshi cross-signal column on desk |
| **W4** | OddsPapi / enterprise feeds behind same fusion contracts when wired |

---

## 12. Positioning paragraph (external-ready)

**Perplex Edge** is a **multi-source sports betting intelligence platform** that fuses live sportsbook odds, player props, alt lines, injuries, schedules, scores, optional **Kalshi** event contracts, and proprietary models into a single normalized market graph. It ranks opportunities by **expected value, edge quality, CLV discipline, hit-rate integrity, cross-book disagreement, steam-sensitive flow, and confidence**—designed for bettors who treat the market as a data problem, not a narrative. Pricing and failover span **The Odds API, BetStack, TheRundown, SportsGameOdds, iSports, API-Sports, SportMonks, BallDontLie, ESPN, TheSportsDB**, and **StatsBomb**-class analytics where licensed, with **OddsPapi, SportsDataIO, and Sportradar** on the integration roadmap—not as afterthoughts, as **explicit tiers** in the architecture.

---

*This document is the narrative and IA source of truth for “full redesign” discussions; schema and endpoint details remain aligned with `PRODUCT_BLUEPRINT.md` and the repo until intentionally superseded.*
