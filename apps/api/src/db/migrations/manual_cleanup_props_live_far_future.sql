-- One-off cleanup: props_live rows with game_start_time far in the future (bad ingest / placeholders).
-- Default window: 7 days ahead of "now" in UTC. Adjust the interval if you use a longer lookahead.
-- Run manually in Supabase SQL editor after reviewing row counts:
--   SELECT count(*) FROM public.props_live
--   WHERE game_start_time IS NOT NULL
--     AND game_start_time > (timezone('utc', now()) + interval '7 days');

DELETE FROM public.props_live
WHERE game_start_time IS NOT NULL
  AND game_start_time > (timezone('utc', now()) + interval '7 days');

-- If your deployment uses a generated column `game_date` derived from game_start_time,
-- re-run your materialized view refresh or rely on the next ingest overwrite as appropriate.
