-- Run in Supabase SQL editor (or any Postgres) if production schema predates ORM columns.
-- Safe to re-run: uses IF NOT EXISTS / IF EXISTS guards where applicable.

-- edges_ev_history: ensure snapshot_at is never NULL on insert without explicit value
ALTER TABLE IF EXISTS public.edges_ev_history
  ALTER COLUMN snapshot_at SET DEFAULT now();

-- whale_moves: align with SQLAlchemy model used by alert_writer / persistence_helpers
ALTER TABLE IF EXISTS public.whale_moves ADD COLUMN IF NOT EXISTS event_id text;
ALTER TABLE IF EXISTS public.whale_moves ADD COLUMN IF NOT EXISTS market_key text;
ALTER TABLE IF EXISTS public.whale_moves ADD COLUMN IF NOT EXISTS selection text;
ALTER TABLE IF EXISTS public.whale_moves ADD COLUMN IF NOT EXISTS bookmaker text;
ALTER TABLE IF EXISTS public.whale_moves ADD COLUMN IF NOT EXISTS books_involved text;
ALTER TABLE IF EXISTS public.whale_moves ADD COLUMN IF NOT EXISTS price_before double precision;
ALTER TABLE IF EXISTS public.whale_moves ADD COLUMN IF NOT EXISTS price_after double precision;
ALTER TABLE IF EXISTS public.whale_moves ADD COLUMN IF NOT EXISTS move_type text;
ALTER TABLE IF EXISTS public.whale_moves ADD COLUMN IF NOT EXISTS whale_label text;
ALTER TABLE IF EXISTS public.whale_moves ADD COLUMN IF NOT EXISTS amount_estimate double precision;
-- severity may already exist as float in older alembic; app uses string 'High' / 'Medium'
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'whale_moves' AND column_name = 'severity'
  ) THEN
    ALTER TABLE public.whale_moves ADD COLUMN severity text;
  END IF;
END $$;
