-- Apply after 20260424_gap_tables.sql (Supabase SQL editor or migration runner).

-- Monte Carlo persistence + list endpoint backing
CREATE TABLE IF NOT EXISTS monte_carlo_results (
  id SERIAL PRIMARY KEY,
  event_id VARCHAR(100),
  sport VARCHAR(50),
  market VARCHAR(50),
  outcome TEXT,
  odds INTEGER,
  true_prob DOUBLE PRECISION,
  win_rate DOUBLE PRECISION,
  avg_roi DOUBLE PRECISION,
  roi_std_dev DOUBLE PRECISION,
  roi_p5 DOUBLE PRECISION,
  roi_p95 DOUBLE PRECISION,
  confidence_score DOUBLE PRECISION,
  num_simulations INTEGER DEFAULT 10000,
  simulated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_mc_sport ON monte_carlo_results(sport, simulated_at DESC);
CREATE INDEX IF NOT EXISTS idx_mc_confidence ON monte_carlo_results(confidence_score DESC);

-- Live scores: abbreviations (optional; used by cache upserts)
ALTER TABLE live_scores ADD COLUMN IF NOT EXISTS home_abbr VARCHAR(10);
ALTER TABLE live_scores ADD COLUMN IF NOT EXISTS away_abbr VARCHAR(10);
CREATE INDEX IF NOT EXISTS idx_live_sport ON live_scores(sport, last_updated DESC);

-- Arbitrage: 20m TTL + query index (existing rows keep their expires_at)
ALTER TABLE arbitrage_opportunities
  ALTER COLUMN expires_at SET DEFAULT (NOW() + INTERVAL '20 minutes');
CREATE INDEX IF NOT EXISTS idx_arb_sport_active ON arbitrage_opportunities(sport, expires_at DESC);
