-- Run in Supabase SQL editor or psql — safe to re-run (IF NOT EXISTS)

ALTER TABLE modelpicks ADD COLUMN IF NOT EXISTS closing_odds           NUMERIC(10,4);
ALTER TABLE modelpicks ADD COLUMN IF NOT EXISTS clv_percentage         NUMERIC(10,4);
ALTER TABLE modelpicks ADD COLUMN IF NOT EXISTS roi_percentage         NUMERIC(10,4);
ALTER TABLE modelpicks ADD COLUMN IF NOT EXISTS opening_odds           NUMERIC(10,4);
ALTER TABLE modelpicks ADD COLUMN IF NOT EXISTS line_movement          NUMERIC(10,4);
ALTER TABLE modelpicks ADD COLUMN IF NOT EXISTS sharp_money_indicator  NUMERIC(10,4);
ALTER TABLE modelpicks ADD COLUMN IF NOT EXISTS best_book_odds         NUMERIC(10,4);
ALTER TABLE modelpicks ADD COLUMN IF NOT EXISTS best_book_name         VARCHAR(50);
ALTER TABLE modelpicks ADD COLUMN IF NOT EXISTS ev_improvement         NUMERIC(10,4);

CREATE TABLE IF NOT EXISTS brainbusinessmetrics (
    id              SERIAL PRIMARY KEY,
    metric_name     VARCHAR(100) NOT NULL,
    metric_value    NUMERIC(15,4),
    metric_category VARCHAR(50),
    sport_id        INTEGER,
    recorded_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS brainanomalies (
    id            SERIAL PRIMARY KEY,
    anomaly_type  VARCHAR(100) NOT NULL,
    severity      VARCHAR(20) CHECK (severity IN ('low','medium','high','critical')),
    description   TEXT,
    component     VARCHAR(100),
    resolved      BOOLEAN DEFAULT FALSE,
    detected_at   TIMESTAMPTZ DEFAULT NOW(),
    resolved_at   TIMESTAMPTZ
);

-- Verify: should return 9 rows
SELECT column_name FROM information_schema.columns
WHERE table_name = 'modelpicks'
AND column_name IN (
    'closing_odds','clv_percentage','roi_percentage','opening_odds',
    'line_movement','sharp_money_indicator','best_book_odds',
    'best_book_name','ev_improvement'
) ORDER BY column_name;
