# Phase 5+ Cutover Checklist

## Advanced Domain Endpoint Alignment

Use `apps/web/src/lib/domainEndpointMap.ts` as the canonical frontend mapping for advanced pages.

Each page must confirm:

1. All network calls are mapped to backend endpoints from `DOMAIN_ENDPOINT_MAP`.
2. Page loading/error/empty states are explicit and retryable.
3. No page relies on undeclared response fields.
4. Backend degradation states are surfaced in-page instead of failing silently.

## Worker and Pipeline Reliability Guardrails

1. Classify retries strictly:
   - auth/config failures: fail fast
   - transient failures: bounded exponential backoff
2. Preserve idempotent writes for ingestion pipelines.
3. Keep stale-ID invalidation for external providers (Odds API and ESPN).
4. Keep log-throttled degraded-state warnings to avoid alert noise.

## Release Verification

1. `/health` and `/api/health/deps` return semantically correct degradation payloads.
2. Scanner, player props, EV, and live pages show fresh timestamps and retry states.
3. OpenAPI snapshot check passes in CI before merge.
4. Background workers can run with providers degraded without crashing scheduler loops.

