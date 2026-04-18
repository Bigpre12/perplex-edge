-- =============================================================================
-- Production schema reconciliation (Supabase / Postgres)
-- =============================================================================
-- Run manually in the Supabase SQL editor (or psql) against your production DB.
--
-- ORDER:
--   1) If not already applied, run: 20260416_align_whale_moves_edges_ev_history.sql
--   2) Run this file (idempotent where possible).
--
-- The API also applies some of this on boot via main.py (Postgres only); this
-- file is the source of truth for one-shot DBA runs and fresh environments.
-- =============================================================================

-- Grader expects these columns (see services/grader.py).
ALTER TABLE IF EXISTS public.props_live ADD COLUMN IF NOT EXISTS steam_signal boolean DEFAULT false;
ALTER TABLE IF EXISTS public.props_live ADD COLUMN IF NOT EXISTS whale_signal boolean DEFAULT false;
ALTER TABLE IF EXISTS public.props_live ADD COLUMN IF NOT EXISTS sharp_conflict boolean DEFAULT false;

-- Legacy NOT NULL on market_label caused inserts to fail when upstream omitted labels.
-- App code now always derives a label, but this keeps old DBs compatible.
ALTER TABLE IF EXISTS public.edges_ev_history ALTER COLUMN market_label DROP NOT NULL;
