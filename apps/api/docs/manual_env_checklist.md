# Manual Environment Update Checklist

## 1) Supabase service role key correctness (highest blast radius)
- Ensure `SUPABASE_URL` matches the target project URL.
- Ensure `SUPABASE_KEY` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` is the anon key.
- Ensure `SUPABASE_SERVICE_ROLE_KEY` (or `SUPABASE_SERVICE_KEY`) is present and different from anon key.
- Verify API health reports `supabase_role_split_ready=true` and `supabase_service_key_looks_anon=false`.

## 2) Auth bypass disabled in production
- Set `BYPASS_AUTH=false`.
- Confirm no preview/production environment has `NEXT_PUBLIC_BYPASS_AUTH=true`.
- Verify app boots successfully (startup now hard-fails when production + bypass enabled).

## 3) Kalshi endpoint/key normalization
- Set `KALSHI_BASE_URL` to the proper environment host (no trailing backticks).
- Set `KALSHI_API_KEY_ID` / `KALSHI_KEY_ID`.
- Set one of: `KALSHI_PRIVATE_KEY` (PEM), `KALSHI_PRIVATE_KEY_PATH`, or `KALSHI_PRIVATE_KEY_B64`.
- Confirm Kalshi status in health/admin is configured or intentionally disabled (no crash-loop).

## 4) Stripe price IDs corrected
- Set `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET`.
- Set `STRIPE_PRO_MONTHLY_PRICE_ID`, `STRIPE_PRO_ANNUAL_PRICE_ID`, `STRIPE_ELITE_MONTHLY_PRICE_ID`, `STRIPE_ELITE_ANNUAL_PRICE_ID`.
- Ensure every value used for checkout line items starts with `price_`.

## 5) Ingest window + provider key cleanup
- Keep `INGEST_DROP_EVENTS_OLDER_THAN_DAYS` and `INGEST_MAX_FUTURE_GAME_DAYS` set to realistic production values.
- Set `THERUNDOWN_API_KEY` only when you intend to enable TheRundown.
- Set `SPORTMONKS_KEY` only when you intend to enable SportMonks.
- Set Redis deterministically:
  - `CACHE_REDIS_URL` for API cache (optional; falls back to `REDIS_URL`)
  - `CELERY_REDIS_URL` for Celery broker/backend (optional; falls back to cache Redis)

## Railway MCP-assisted verification
- Validate env presence and format:
  - `railway variables --json`
  - confirm required keys exist and forbidden combinations are absent (`BYPASS_AUTH=true` in prod).
- Validate deploy/restart:
  - trigger deploy or restart service from Railway dashboard/MCP
  - confirm latest deployment reaches healthy state.
- Validate post-deploy health:
  - `GET /health`
  - `GET /api/health`
  - `GET /api/health/deps`
  - `GET /api/admin/system-health` (with admin bearer)
