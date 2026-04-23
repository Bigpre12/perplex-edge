-- Active Brain governor: decision log + lightweight odds cache snapshots (not full API payloads)
CREATE TABLE IF NOT EXISTS brain_decisions (
  id SERIAL PRIMARY KEY,
  sport VARCHAR(50),
  should_fetch BOOLEAN,
  should_compute_clv BOOLEAN,
  should_run_monte_carlo BOOLEAN,
  reason TEXT,
  data_age_minutes DOUBLE PRECISION,
  quota_pct_used DOUBLE PRECISION,
  decided_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_brain_decisions_sport ON brain_decisions(sport);
CREATE INDEX IF NOT EXISTS idx_brain_decisions_decided ON brain_decisions(decided_at DESC);

CREATE TABLE IF NOT EXISTS odds_cache (
  id SERIAL PRIMARY KEY,
  sport VARCHAR(50) NOT NULL,
  market VARCHAR(50) NOT NULL DEFAULT 'all',
  data JSONB NOT NULL,
  fetched_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '15 minutes'
);
CREATE INDEX IF NOT EXISTS idx_odds_cache_sport ON odds_cache(sport);
CREATE INDEX IF NOT EXISTS idx_odds_cache_expires ON odds_cache(expires_at);
