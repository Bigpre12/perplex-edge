-- Kalshi Elite Integration Tables

-- 1. kalshi_markets
CREATE TABLE IF NOT EXISTS kalshi_markets (
    ticker TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    series TEXT,
    yes_bid INTEGER, -- Prices in cents
    yes_ask INTEGER,
    last_price INTEGER,
    volume INTEGER DEFAULT 0,
    open_interest INTEGER DEFAULT 0,
    close_time TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. kalshi_ev_signals
CREATE TABLE IF NOT EXISTS kalshi_ev_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker TEXT NOT NULL REFERENCES kalshi_markets(ticker) ON DELETE CASCADE,
    prop_label TEXT,
    player_name TEXT,
    sport TEXT,
    kalshi_prob FLOAT,
    book_prob FLOAT,
    edge FLOAT,
    recommendation TEXT, -- "BUY YES", "BUY NO", "No Edge"
    book_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. kalshi_arb_alerts
CREATE TABLE IF NOT EXISTS kalshi_arb_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker TEXT NOT NULL,
    player_name TEXT,
    kalshi_yes INTEGER, -- Price in cents
    book_no_implied FLOAT, -- Implied probability
    profit_margin FLOAT,
    status TEXT DEFAULT 'active', -- 'active', 'expired'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. kalshi_orders
CREATE TABLE IF NOT EXISTS kalshi_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL, -- Clerk User ID
    ticker TEXT NOT NULL,
    side TEXT CHECK (side IN ('yes', 'no')),
    count INTEGER NOT NULL,
    price INTEGER NOT NULL, -- Price in cents
    status TEXT DEFAULT 'pending', -- 'pending', 'filled', 'cancelled'
    kalshi_order_id TEXT, -- External ID from Kalshi API
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on sensitive tables
ALTER TABLE kalshi_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE kalshi_ev_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE kalshi_arb_alerts ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can only view their own Kalshi orders"
ON kalshi_orders FOR SELECT
USING (auth.uid()::text = user_id);

CREATE POLICY "Elite users can view all EV signals"
ON kalshi_ev_signals FOR SELECT
USING (true); -- Tier check handled at API layer, but RLS can be stricter if needed

CREATE POLICY "Elite users can view all arb alerts"
ON kalshi_arb_alerts FOR SELECT
USING (true);
