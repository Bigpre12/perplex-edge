-- FIX 16: persisted TheOddsAPI quota from x-requests-* headers (see models.odds_quota)
CREATE TABLE IF NOT EXISTS odds_api_usage (
  id SERIAL PRIMARY KEY,
  month VARCHAR(7) NOT NULL,
  requests_used INTEGER NOT NULL DEFAULT 0,
  requests_remaining INTEGER,
  quota_exhausted BOOLEAN NOT NULL DEFAULT FALSE,
  last_updated TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT uq_odds_api_usage_month UNIQUE (month)
);

INSERT INTO odds_api_usage (month, requests_used, requests_remaining, quota_exhausted)
VALUES (TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM'), 0, NULL, FALSE)
ON CONFLICT (month) DO NOTHING;
