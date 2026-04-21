# Railway production triage

Use this checklist when Postgres, Redis, or The Odds API misbehave in production. Backend reads env via [`apps/api/src/core/config.py`](../apps/api/src/core/config.py) and [`apps/api/src/db/session.py`](../apps/api/src/db/session.py).

## 1. Postgres: `Network is unreachable` / `[Errno 101]`

Means the Railway container has **no TCP route** to the host in `DATABASE_URL` (wrong host, paused project, region/DNS). It is not fixed by blindly appending `?sslmode=require` if the host is wrong.

**Checklist**

1. Supabase Dashboard: confirm the project is **not paused** and billing allows connections.
2. Supabase → **Settings → Database → Connection string** → copy the **URI** for **pooler** (Transaction mode is typical for serverless-style workers). Use the hostname and port Supabase shows.
3. Railway → API service → **Variables**: set `DATABASE_URL` to that URI (no stray quotes; trim spaces). Password must be correct for the `postgres` role (or the role shown in the URI).
4. Prefer **same region** for Railway and Supabase when possible.
5. **Redeploy** the API service after changing variables.

**How this repo treats URLs**

- [`apps/api/src/db/session.py`](../apps/api/src/db/session.py): strips `sslmode=` query params for asyncpg compatibility and may rewrite Supabase pooler URLs from port **5432 to 6543** when the host contains `pooler` and uses 5432.
- If Supabase already gives you **6543**, no further port rewrite is expected.

**If errors persist**

- Confirm the hostname resolves and is reachable from the public internet (Supabase pooler hosts should be).
- IPv6-only or corporate routing issues may require Supabase or Railway support.

**Shell test (same `DATABASE_URL` as the running service)**

From the API container or local shell with env loaded:

```bash
cd apps/api/src && python scripts/test_asyncpg_connect.py
```

This uses [`apps/api/src/scripts/test_asyncpg_connect.py`](../apps/api/src/scripts/test_asyncpg_connect.py) and [`core/asyncpg_dsn.py`](../apps/api/src/core/asyncpg_dsn.py), matching raw `asyncpg` behavior in production.

---

## 2. Redis: `Connection refused` / `Error 111` on `*.railway.internal:6379`

`REDIS_URL` must point at a **running** Redis (or Valkey) service. Connection refused means nothing is listening (service stopped, removed, or **stale hostname** after rename).

**Checklist**

1. Railway: open the **Redis** plugin and confirm it is **running**.
2. Railway → API service → **Variables**: set `REDIS_URL` using the **current** connection URL. Use **Variable Reference** from the Redis service if available (e.g. `${{Redis.REDIS_URL}}` — exact syntax depends on Railway’s UI).
3. **Redeploy** the API service.

Without `REDIS_URL`, [`core/config.py`](../apps/api/src/core/config.py) defaults to `redis://localhost:6379`, which will not work on Railway.

Failure to connect is **logged** in [`apps/api/src/main.py`](../apps/api/src/main.py) during background init (`initialize_backend_services`); the app can still boot, but the WebSocket Redis listener path in [`apps/api/src/core/connection_manager.py`](../apps/api/src/core/connection_manager.py) will not function.

---

## 3. The Odds API: quota / `OUT_OF_USAGE_CREDITS` / HTTP 401

Ingestion depends on valid keys in [`apps/api/src/services/odds_api_client.py`](../apps/api/src/services/odds_api_client.py).

**Checklist**

1. The Odds API dashboard: confirm **remaining quota** and billing.
2. Railway: ensure at least one of:
   - `ODDS_API_KEY` or `THE_ODDS_API_KEY` (primary)
   - `ODDS_API_KEY_BACKUP`
   - comma-separated `ODDS_API_KEYS`
3. To **reduce** request volume, tune the **ingest scheduler** (see below). Paying for quota or adding keys is still required for live odds.

**Tiered scheduler (default)** — [`apps/api/src/core/ingest_scheduler_config.py`](../apps/api/src/core/ingest_scheduler_config.py)

Unless **`INGEST_USE_LEGACY_SCHEDULER=true`**, the API schedules **active** sports more often than **inactive** ones:

| Variable | Role | Default |
|----------|------|---------|
| `INGEST_INTERVAL_ACTIVE_MINUTES` | Poll interval for active tier | `30` |
| `INGEST_INTERVAL_INACTIVE_HOURS` | Poll interval for inactive tier | `6` |
| `INGEST_ACTIVE_SPORTS` | Comma-separated keys (optional; defaults to NBA, NHL, MLS, EPL, UCL) | built-in list |
| `INGEST_INACTIVE_SPORTS` | Comma-separated keys (optional; defaults to remaining canonical sports minus active/disabled) | auto |
| `INGEST_DISABLED_SPORTS` | Comma-separated keys excluded from scheduling | empty |

**Legacy single interval:** set **`INGEST_USE_LEGACY_SCHEDULER=true`** — every canonical sport uses **`INGEST_INTERVAL_MINUTES`** (default `5`), matching old behavior.

**Cooldown: skip DB heartbeat**

When all Odds API keys are cooling down, ingestion skips work. By default (**`SKIP_HEARTBEAT_WHEN_ODDS_KEYS_COOLDOWN`** unset or `true`) it **does not** write ingest heartbeats to Postgres, avoiding extra DB load when quota is exhausted. Set to `false` to restore heartbeat rows for observability.

**Cooldown spam in logs**

When keys hit quota or HTTP 401, the client marks keys unavailable and backs off ([`odds_api_client`](../apps/api/src/services/odds_api_client.py)). Wider intervals (tiered or legacy) reduce noise; they do not restore quota.

No code change replaces paying for or rotating API credits.

---

## 4. Secondary variables (optional)

| Symptom / feature | Variable |
|-------------------|----------|
| Kalshi integration | `KALSHI_KEY_ID`, `KALSHI_PRIVATE_KEY`, `KALSHI_BASE_URL` |
| Transactional email | `RESEND_API_KEY` |
| Commence-time window logs | Expected filtering; change product/ingest windows only if requirements change |

---

## 5. Health checks and Railway probes

- **`GET /health`** ([`main.py`](../apps/api/src/main.py)): runs `SELECT 1` against Postgres. Returns **503** when the database is unreachable (e.g. Errno 101), so Railway’s default probe can surface real outages.
- **`GET /api/health`** / **`GET /api/health/deps`**: richer status (odds keys, heartbeats, etc.) via [`health.py`](../apps/api/src/routers/health.py).
- **`GET /api/health/ready`**: readiness gate (503 when DB is down or data plane is degraded—see router for rules).

**Recommended:** Point Railway’s **health check path** to **`/health`** or **`/api/health/ready`** so deploys fail fast when Postgres is misconfigured.

After updating env vars and redeploying:

- Confirm **`GET /health`** returns 200 with `"database": "connected"` (or 503 until `DATABASE_URL` is fixed).
- Watch Railway logs for `Startup DB error` (should be absent if Postgres is reachable).
- Watch for `WebSocket Redis Listener active` vs Redis connection errors.

Copy variable names from [`.env.example`](../.env.example) at the repo root.
