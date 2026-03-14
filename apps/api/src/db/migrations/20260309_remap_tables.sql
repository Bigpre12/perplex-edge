-- C:\Users\preio\OneDrive\Documents\Untitled\perplex_engine\perplex-edge\apps\api\src\db\migrations\20260309_remap_tables.sql

-- 1. CLV Snapshots Table
CREATE TABLE IF NOT EXISTS clv_snapshots (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    sport text NOT NULL,
    player text NOT NULL,
    stat_type text NOT NULL,
    open_line numeric,
    open_over_odds integer,
    open_under_odds integer,
    current_line numeric,
    current_over_odds integer,
    current_under_odds integer,
    close_line numeric,
    close_over_odds integer,
    close_under_odds integer,
    clv_value numeric,
    game_id text NOT NULL,
    sportsbook text,
    recorded_at timestamptz DEFAULT now(),
    game_date date DEFAULT CURRENT_DATE
);

CREATE INDEX IF NOT EXISTS idx_clv_date ON clv_snapshots(game_date DESC);
CREATE INDEX IF NOT EXISTS idx_clv_game_player ON clv_snapshots(game_id, player);

-- 2. Whale Moves Table
CREATE TABLE IF NOT EXISTS whale_moves (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    sport text NOT NULL,
    player text NOT NULL,
    stat_type text NOT NULL,
    line_before numeric,
    line_after numeric,
    odds_before integer,
    odds_after integer,
    move_size numeric,
    time_detected timestamptz DEFAULT now(),
    game_id text NOT NULL,
    sportsbook text,
    whale_rating text DEFAULT 'SUSPECTED',
    confirmed boolean DEFAULT false
);

CREATE INDEX IF NOT EXISTS idx_whale_time ON whale_moves(time_detected DESC);
CREATE INDEX IF NOT EXISTS idx_whale_game ON whale_moves(game_id);

-- 3. Sharp Signals Table
CREATE TABLE IF NOT EXISTS sharp_signals (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    sport text NOT NULL,
    player text NOT NULL,
    stat_type text NOT NULL,
    public_pct_over numeric,
    line_direction text,
    sharp_side text,
    signal_strength text,
    detected_at timestamptz DEFAULT now(),
    game_id text NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sharp_detected ON sharp_signals(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_sharp_game ON sharp_signals(game_id);
