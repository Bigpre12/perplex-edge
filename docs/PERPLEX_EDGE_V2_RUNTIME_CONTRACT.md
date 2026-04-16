# Perplex Edge / LUCRIX — V2 Runtime Contract (Health, Degradation, Persistence)

**Status:** Build-ready addendum  
**Audience:** Product, Frontend, Backend, Data, DevOps, QA  
**Relationship:** This document **does not replace** [PERPLEX_EDGE_MASTER_BLUEPRINT_V2.md](./PERPLEX_EDGE_MASTER_BLUEPRINT_V2.md). It **binds** the blueprint to **observable runtime behavior**: what “live” means, when the UI must **not** pretend health, and how persistence must **never** crash on bad upstream labels.

**Companion docs (read in this order for implementation)**

1. [PERPLEX_EDGE_MASTER_BLUEPRINT_V2.md](./PERPLEX_EDGE_MASTER_BLUEPRINT_V2.md) — full product / IA / desks.
2. [UI_DATA_PROVENANCE.md](./UI_DATA_PROVENANCE.md) — badges, stale copy, confidence.
3. [WATERFALL_PROVIDER_MATRIX.md](./WATERFALL_PROVIDER_MATRIX.md) — routing, failover, audit.
4. [BRAINS_AUDIT_AND_REBUILD_SPEC.md](./BRAINS_AUDIT_AND_REBUILD_SPEC.md) — brains health, no silent failure.

---

## 1. Non-negotiables (runtime)

- **HTTP 200 ≠ healthy data.** Summaries and list endpoints MUST carry **`meta.degradation`** and **`meta.freshness`** (see §4).
- **Never rank or publish** EV/edge rows that fail canonical validation (e.g. missing resolved market label) — **dead-letter** instead of violating NOT NULL constraints.
- **Separate** model **confidence**, pipeline **trust**, and user **action score** in APIs and UI; never collapse into one “score.”
- **User-facing honesty:** use the **wording patterns** in §3 (copy is part of the contract).

---

## 2. Failure classes (mandatory handling matrix)

Each row is a **first-class** scenario for backend behavior, observability, UI, ranking policy, alerts, and admin escalation.

| # | Failure class | Example fingerprint (redacted / short) | Backend handling | Observability | UI banner / badge | Ranking / suppression | User alerts | Block user actions? | Admin escalation | Primary surfaces |
|---|---------------|------------------------------------------|------------------|---------------|-------------------|-------------------------|--------------|----------------------|------------------|------------------|
| 1 | Odds provider exhaustion / global cooldown | “All Odds API keys are dead/cooling down. Skipping request.” | Stop fanout; enter cooldown; serve **last good snapshot** with timestamp; no silent “live”. | `provider_cooldowns`, `provider_status`, metric `odds_provider_exhausted` | Global strip: **“Odds feeds cooling down — snapshot as of {ts}.”** | Demote “best line” claims; default sort uses **trust** not raw EV | Ops-only by default | **No** | Page on sustained duration | Scanner, Command Center, Game |
| 2 | Third-party rate limits (429, strict quotas) | “Betstack rate limit 429 … 1 req/60s per key” | Token bucket per key; backoff; skip call; schedule retry | `rate_limit_windows`, 429 rate | Badge: **“Rate-limited — {provider} paused ~{eta}s.”** | Freeze updates for affected slice | Optional if user pins that book | **No** | Tune limits / keys | Scanner, Connections |
| 3 | Waterfall exhaustion (league/stat) | Waterfall returns no priced source for class | Mark market class **unavailable**; partial board | `ingestion_failures.reason=waterfall_exhausted` | Yellow module: **“No priced source for this market class.”** | Hide or lane “unpriced” separately | No | **No** | Mapper / provider order | Scanner, Props |
| 4 | Missing / wrong canonical mapping | Unknown team/player/market keys | **Validate before persist**; `mapping_exceptions` | Counter + sampled payloads | Row: **“Mapping unverified — not ranked.”** | Exclude from default rank or quarantine lane | Optional | **No** | Queue human fix | Scanner, Player, Game |
| 5 | Missing credentials (optional feed) | Kalshi / SportMonks not configured | Disable feed; feature off; explicit status | `feed_credentials_status` | Module: **“Feed disconnected — configure credentials.”** | N/A for that feature | No | **No** | Credential workflow | Kalshi desk, optional modules |
| 6 | Zero-row ingest while job “succeeds” | “No unified rows generated for …”, “Final grouped_data count 0” | Treat as **data failure** when non-zero expected; heartbeat semantics | Heartbeat gap + `ingestion_failures` | Banner: **“Pipeline empty for {sport} — data gap, not a quiet board.”** | Suppress EV-first sorts | Ops | **No** | Runbook + rerun ingest | Command Center, Scanner |
| 7 | EV / history persistence constraint violations | `null value in column marketlabel … edgesevhistory violates not-null` | **Two-phase write**: staging → validate → publish; invalid → `dead_letter_ev_records` | DLQ depth, error class | **“EV updates paused — integrity check failed (missing market label).”** | Suppress EV sort; show last good cache | Ops + optional Pro “integrity” banner | **No** | Immediate DLQ triage | Scanner, CLV, Admin |
| 8 | Cross-sport / cross-league contamination | Soccer keys with wrong league labels | Graph invariants; block publish; `mapping_exceptions` **severity=critical** | Contamination detector metric | Row: **“Cross-league mismatch — row hidden.”** | Hard suppress | Ops alert | **Block only** that row’s bet/parlay export | Hotfix mapping | Scanner, Game |
| 9 | Healthy HTTP while data quality degraded | `/health` 200 but providers dead / zero rows / DLQ growing | **`/health`** liveness only; **`/health/deps`** truth; BFF includes `meta.degradation` | Synthetic checks vs heartbeats | Global chip: **“Service is up — market data is not.”** | Cap trust globally | Ops | **No** | Incident mode | **All** |
| 10 | Query timeout / write contention on EV | `QueryCanceledError` / statement timeout on `ev_signals` writes | Retry with decay; smaller batches; partition writes | Write latency p95/p99, timeout rate | **“Updates delayed — showing last successful write.”** | Read-only last good | Ops | **No** | Index / scale review | Scanner, Admin |

---

## 3. User-facing honesty (exact wording patterns)

Use these **patterns** (fill `{placeholders}` from `meta`):

- Snapshot: **“Snapshot only — not live. Last odds update {ts}.”**
- Rate limit: **“{Provider} rate-limited. Retrying automatically; updates paused ~{eta}s.”**
- Pipeline empty: **“Ingestion ran but produced no rows for {sport}. This is a data gap.”**
- Integrity / DLQ: **“EV grading paused for this segment after a data integrity check. Last good EV {ts}.”**
- Degraded global: **“Service is reachable; market data is incomplete or stale.”**
- Contamination: **“This row failed mapping checks and was hidden.”**

Avoid: tout language, “locks,” guaranteed profit, “AI certainty.”

---

## 4. API response envelope (contract)

All **user-facing list and summary** endpoints SHOULD return:

```json
{
  "data": {},
  "meta": {
    "request_id": "uuid",
    "server_time": "iso-8601",
    "freshness": {
      "odds": "iso-8601|null",
      "ev": "iso-8601|null",
      "injuries": "iso-8601|null"
    },
    "degradation": {
      "level": "none|partial|severe",
      "reasons": ["odds_cooldown", "ev_dlq", "zero_row_ingest"],
      "affected_providers": ["the_odds_api"],
      "user_message": "short safe string for UI strip"
    },
    "provenance": {
      "primary_odds_provider": "string|null",
      "fallback_used": false
    },
    "cache_ttl_s": 15,
    "cursor": "opaque|null"
  }
}
```

**Rules**

- `degradation.level=none` MUST NOT be used if any sub-check that the product cares about is failed (define checklist server-side).
- `user_message` MUST be safe to show without leaking secrets or internal table names.

---

## 5. Health endpoints (contract)

| Route | Purpose | When 200 |
|-------|---------|----------|
| `GET /health` | Process liveness (cheap) | API process up |
| `GET /health/deps` | **Dependency + data truth** | Returns JSON with **component statuses**: DB, Redis (if used), critical queues, **odds path**, **EV writer**, **last successful odds/ev timestamps**, **DLQ depth**, **mapping_exception_rate**. May return 200 with **`overall: degraded`** — that is **valid** and preferred over lying. |

**Frontend rule:** Command Center and Scanner MUST consume **`/health/deps` or BFF summary**, not raw `/health`, for any “system healthy” indicator.

---

## 6. Schema direction (defensive)

Minimum additive concepts (table or JSONB columns as appropriate):

- `dead_letter_ev_records` — payload, error class, retries, first_seen, last_seen  
- `mapping_exceptions` — entity, sport_key, evidence, severity, status  
- `ingestion_failures` — job, sport, reason enum, counts  
- `provider_status` / `provider_cooldowns` / `rate_limit_windows`  
- `degraded_snapshots` — materialized summary for fast dashboard (`level`, `reasons`, `ts`)  
- `feed_credentials_status` — provider, configured, last_ok_at  
- `signal_freshness` — per sport / channel (may overlap existing heartbeat tables; **normalize one source of truth** for UI)

**Market labels:** never insert into NOT NULL history without resolver pass; prefer **staging → validate → publish** over catching DB exceptions in hot paths.

---

## 7. WebSocket + reconnect (contract)

- Channels: `stream/odds`, `stream/alerts`, optional `stream/dashboard`, admin `stream/ops`.  
- Reconnect: client sends `since=cursor` or `Last-Event-ID`; server sends bounded replay.  
- If WS is connected but **no ticks** and freshness ages past threshold → UI shows **“connected but idle/stale”**, not “live”.

---

## 8. MVP engineering slice (first 2–4 weeks)

**Goal:** ship **truthful degradation** before more features.

**Shipped in repo (baseline):**

1. **`GET /api/health/deps`** — [`apps/api/src/routers/health.py`](../apps/api/src/routers/health.py): `overall`, `degradation{level,reasons,user_message}`, `freshness`, `components`, `sync`. Legacy **`GET /api/health`** unchanged for clients.  
2. **`meta.degradation`** on **`GET /api/signals/freshness`** — [`apps/api/src/routers/signals.py`](../apps/api/src/routers/signals.py) (top-level freshness fields preserved).  
3. **`edges_ev_history` write path** — [`apps/api/src/services/persistence_helpers.py`](../apps/api/src/services/persistence_helpers.py): sanitize rows, skip invalid / missing `market_label`, log skip count (DLQ-style logging; no silent crash).  
4. **UI** — [`DataDegradationBanner`](../apps/web/src/components/DataDegradationBanner.tsx) on Command Center ([`dashboard/page.tsx`](../apps/web/src/app/(app)/dashboard/page.tsx)) + [`API.healthDeps()`](../apps/web/src/lib/api.ts).

**Still recommended (next):** `meta` on dashboard BFF / edges search; row-level trust from `meta` on scanner; optional `dead_letter_ev_records` table for operator triage.

---

## 9. Mapping to the 25-section master prompt

The exhaustive **page-by-page** and **IA** content remains in [PERPLEX_EDGE_MASTER_BLUEPRINT_V2.md](./PERPLEX_EDGE_MASTER_BLUEPRINT_V2.md) and related specs. **This file owns:** §§2–8 above (failure matrix, copy, API `meta`, health split, schema defenses, WS reconnect, MVP slice). When the master blueprint is updated, add a one-line pointer back to this contract under “Failure handling / stale-data UX.”

---

## 10. Prompt hygiene (for LLM / human authors)

- Do not embed multi-megabyte logs in prompts; use **short fingerprints** like the examples in §2.  
- Do not paste presigned URLs into prompts or docs; treat as sensitive.
