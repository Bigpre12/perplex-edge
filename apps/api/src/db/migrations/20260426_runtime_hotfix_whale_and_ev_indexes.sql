-- Runtime hotfix: align whale_moves columns and ev_signals indexes with production queries.

-- 1) Whale schema drift guard
ALTER TABLE IF EXISTS whale_moves
  ADD COLUMN IF NOT EXISTS market_key TEXT;

ALTER TABLE IF EXISTS whale_moves
  ADD COLUMN IF NOT EXISTS selection TEXT;

-- 2) Ensure ev_signals conflict targets used by grader exist.
-- Player rows (player_name NOT NULL)
CREATE UNIQUE INDEX IF NOT EXISTS uix_ev_unique
ON ev_signals (sport, event_id, player_name, market_key, outcome_key, bookmaker, engine_version)
WHERE player_name IS NOT NULL;

-- Team rows (player_name IS NULL)
CREATE UNIQUE INDEX IF NOT EXISTS uix_ev_team_unique
ON ev_signals (sport, event_id, market_key, outcome_key, bookmaker, engine_version)
WHERE player_name IS NULL;

