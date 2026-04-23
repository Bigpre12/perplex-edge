-- Gap tables (audit plan). Apply in Supabase SQL editor after 20260423_brain_governor_tables.sql.
-- Do NOT recreate sharp_signals — canonical schema matches models.brain.SharpSignal.

-- Whale signals (dual-write alongside whale_moves)
CREATE TABLE IF NOT EXISTS whale_signals (
  id SERIAL PRIMARY KEY,
  event_id VARCHAR(100),
  sport VARCHAR(50),
  player VARCHAR(100),
  market VARCHAR(50),
  line DOUBLE PRECISION,
  bookmaker VARCHAR(50),
  odds INTEGER,
  trust_level DOUBLE PRECISION,
  signal_type VARCHAR(50),
  is_sharp_money BOOLEAN DEFAULT FALSE,
  detected_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_whale_signals_sport ON whale_signals(sport, detected_at DESC);

-- Raw odds snapshots for line movement (separate from line_ticks ORM)
CREATE TABLE IF NOT EXISTS line_movement_history (
  id SERIAL PRIMARY KEY,
  event_id VARCHAR(100),
  sport VARCHAR(50),
  market VARCHAR(50),
  outcome TEXT,
  bookmaker VARCHAR(50),
  odds INTEGER,
  line DOUBLE PRECISION,
  recorded_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_line_movement_event ON line_movement_history(event_id, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_line_movement_sport ON line_movement_history(sport, recorded_at DESC);

-- Persisted arbitrage opportunities from ingest
CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
  id SERIAL PRIMARY KEY,
  event_id VARCHAR(100),
  sport VARCHAR(50),
  market VARCHAR(50),
  outcome_a TEXT,
  outcome_b TEXT,
  book_a VARCHAR(50),
  book_b VARCHAR(50),
  odds_a INTEGER,
  odds_b INTEGER,
  arb_pct DOUBLE PRECISION,
  profit_per_100 DOUBLE PRECISION,
  detected_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '15 minutes'
);
CREATE INDEX IF NOT EXISTS idx_arb_opp_sport ON arbitrage_opportunities(sport, detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_arb_opp_expires ON arbitrage_opportunities(expires_at);

-- Graded pick history (user_id matches public.users.id INTEGER)
CREATE TABLE IF NOT EXISTS pick_results (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
  event_id VARCHAR(100),
  sport VARCHAR(50),
  player VARCHAR(100),
  market VARCHAR(50),
  line DOUBLE PRECISION,
  odds INTEGER,
  pick_direction VARCHAR(10),
  result VARCHAR(10),
  actual_value DOUBLE PRECISION,
  ev_at_pick DOUBLE PRECISION,
  clv_at_close DOUBLE PRECISION,
  stake DOUBLE PRECISION DEFAULT 1.0,
  payout DOUBLE PRECISION,
  graded_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pick_results_user ON pick_results(user_id, graded_at DESC);
CREATE INDEX IF NOT EXISTS idx_pick_results_sport ON pick_results(sport);

-- Live scores cache
CREATE TABLE IF NOT EXISTS live_scores (
  id SERIAL PRIMARY KEY,
  event_id VARCHAR(100) UNIQUE,
  sport VARCHAR(50),
  home_team VARCHAR(100),
  away_team VARCHAR(100),
  home_score INTEGER DEFAULT 0,
  away_score INTEGER DEFAULT 0,
  status VARCHAR(50),
  period VARCHAR(20),
  clock VARCHAR(20),
  last_updated TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_live_scores_sport ON live_scores(sport);
