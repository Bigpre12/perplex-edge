-- One-time stale operational data cleanup.
DELETE FROM odds_snapshots WHERE captured_at < NOW() - INTERVAL '21 days';
DELETE FROM market_edges WHERE updated_at < NOW() - INTERVAL '7 days';
DELETE FROM ev_opportunities WHERE updated_at < NOW() - INTERVAL '7 days';
DELETE FROM player_props WHERE updated_at < NOW() - INTERVAL '3 days';
