-- Quota hardening observability and control tables.

CREATE TABLE IF NOT EXISTS external_api_call_log (
    id BIGSERIAL PRIMARY KEY,
    provider TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    sport TEXT NULL,
    markets TEXT NULL,
    regions TEXT NULL,
    event_count INTEGER NULL,
    status_code INTEGER NOT NULL,
    x_requests_remaining INTEGER NULL,
    x_requests_used INTEGER NULL,
    x_requests_last INTEGER NULL,
    cache_hit BOOLEAN NOT NULL DEFAULT FALSE,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    request_key TEXT NULL
);

CREATE INDEX IF NOT EXISTS idx_external_api_call_log_provider_time
    ON external_api_call_log (provider, completed_at DESC);

CREATE TABLE IF NOT EXISTS external_api_cache_index (
    key TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    sport TEXT NULL,
    markets TEXT NULL,
    regions TEXT NULL,
    ttl_seconds INTEGER NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quota_budget_state (
    provider TEXT NOT NULL,
    bucket TEXT NOT NULL,
    period_start TIMESTAMPTZ NOT NULL,
    used_calls INTEGER NOT NULL DEFAULT 0,
    budget_limit INTEGER NOT NULL DEFAULT 0,
    protection_mode TEXT NOT NULL DEFAULT 'normal',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (provider, bucket, period_start)
);

CREATE TABLE IF NOT EXISTS ingestion_job_runs (
    id BIGSERIAL PRIMARY KEY,
    job_key TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ NULL,
    status TEXT NOT NULL DEFAULT 'running',
    rows_written INTEGER NOT NULL DEFAULT 0,
    error_message TEXT NULL
);

CREATE INDEX IF NOT EXISTS idx_ingestion_job_runs_job_started
    ON ingestion_job_runs (job_key, started_at DESC);

CREATE TABLE IF NOT EXISTS provider_health_state (
    provider TEXT PRIMARY KEY,
    state TEXT NOT NULL DEFAULT 'healthy',
    failure_count INTEGER NOT NULL DEFAULT 0,
    lockout_until TIMESTAMPTZ NULL,
    last_error TEXT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
