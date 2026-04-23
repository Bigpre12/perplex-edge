-- Supabase-compatible quota audit tables + RPCs (apply if not already present in project SQL editor).
-- Safe to re-run: IF NOT EXISTS / CREATE OR REPLACE.

CREATE TABLE IF NOT EXISTS api_quota_config (
  id INTEGER PRIMARY KEY DEFAULT 1,
  monthly_limit INTEGER NOT NULL DEFAULT 20000,
  daily_soft_cap INTEGER NOT NULL DEFAULT 600,
  daily_hard_cap INTEGER NOT NULL DEFAULT 800,
  warn_pct DOUBLE PRECISION NOT NULL DEFAULT 0.80,
  critical_pct DOUBLE PRECISION NOT NULL DEFAULT 0.95,
  hard_stop_pct DOUBLE PRECISION NOT NULL DEFAULT 0.95,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO api_quota_config (id) VALUES (1)
ON CONFLICT (id) DO NOTHING;

CREATE TABLE IF NOT EXISTS api_quota_usage (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  sport VARCHAR(64),
  market VARCHAR(256),
  endpoint_path TEXT,
  requests_used INTEGER,
  requests_remaining INTEGER,
  month_key VARCHAR(7)
);
CREATE INDEX IF NOT EXISTS idx_api_quota_usage_created ON api_quota_usage (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_quota_usage_month ON api_quota_usage (month_key, created_at DESC);

CREATE TABLE IF NOT EXISTS quota_alerts (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  level VARCHAR(32) NOT NULL,
  message TEXT,
  pct_used DOUBLE PRECISION,
  requests_used INTEGER,
  requests_remaining INTEGER,
  monthly_limit INTEGER
);
CREATE INDEX IF NOT EXISTS idx_quota_alerts_created ON quota_alerts (created_at DESC);

-- Per-day counts from api_quota_usage (last 30 days)
CREATE OR REPLACE FUNCTION get_daily_quota_usage()
RETURNS TABLE(day date, request_count bigint)
LANGUAGE sql
STABLE
AS $$
  SELECT (created_at AT TIME ZONE 'utc')::date AS day, count(*)::bigint AS request_count
  FROM api_quota_usage
  WHERE created_at > NOW() - INTERVAL '30 days'
  GROUP BY 1
  ORDER BY 1 DESC;
$$;

-- Monthly roll-up from odds_api_usage + config (headers remain canonical for "used")
CREATE OR REPLACE FUNCTION get_monthly_quota_summary()
RETURNS jsonb
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
  m text := to_char(timezone('utc', now()), 'YYYY-MM');
  lim int := 20000;
  wp double precision := 0.80;
  cp double precision := 0.95;
  hp double precision := 0.95;
  u int := 0;
  r int;
  pct numeric;
  st text := 'ok';
BEGIN
  SELECT monthly_limit, warn_pct, critical_pct, hard_stop_pct
  INTO lim, wp, cp, hp
  FROM api_quota_config WHERE id = 1;
  IF lim IS NULL OR lim <= 0 THEN lim := 20000; END IF;
  IF wp IS NULL THEN wp := 0.80; END IF;
  IF cp IS NULL THEN cp := 0.95; END IF;
  IF hp IS NULL THEN hp := 0.95; END IF;

  SELECT requests_used, requests_remaining INTO u, r
  FROM odds_api_usage WHERE month = m LIMIT 1;
  u := COALESCE(u, 0);
  IF r IS NULL THEN
    r := GREATEST(0, lim - u);
  END IF;

  IF lim > 0 THEN
    pct := round((u::numeric / lim::numeric), 4);
  ELSE
    pct := 0;
  END IF;

  IF u >= lim THEN
    st := 'exhausted';
  ELSIF lim > 0 AND (u::numeric / lim) >= hp THEN
    st := 'hard_stop';
  ELSIF lim > 0 AND (u::numeric / lim) >= cp THEN
    st := 'critical';
  ELSIF lim > 0 AND (u::numeric / lim) >= wp THEN
    st := 'warning';
  END IF;

  RETURN jsonb_build_object(
    'month', m,
    'used', u,
    'limit', lim,
    'remaining', r,
    'pct_used', pct,
    'status', st
  );
END;
$$;
