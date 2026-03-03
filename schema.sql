-- BASED MONEY - Database Schema
-- PostgreSQL/Supabase Schema
-- 9 tables: markets, historical_markets, news_events, trader_performance, theses, portfolio, positions, ic_memos, event_log

-- ============================================================
-- MARKETS TABLE
-- Stores current/active Polymarket markets
-- ============================================================
CREATE TABLE IF NOT EXISTS markets (
    id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    category TEXT,
    yes_price DECIMAL(10, 6),
    no_price DECIMAL(10, 6),
    volume_24h DECIMAL(15, 2),
    resolution_date TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    liquidity_score DECIMAL(5, 3),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_markets_category ON markets(category);
CREATE INDEX idx_markets_volume ON markets(volume_24h DESC);
CREATE INDEX idx_markets_resolved ON markets(resolved);
CREATE INDEX idx_markets_resolution_date ON markets(resolution_date);


-- ============================================================
-- HISTORICAL_MARKETS TABLE
-- Stores resolved markets for backtesting
-- ============================================================
CREATE TABLE IF NOT EXISTS historical_markets (
    id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    category TEXT,
    yes_price DECIMAL(10, 6),
    no_price DECIMAL(10, 6),
    volume_24h DECIMAL(15, 2),
    resolution_date TIMESTAMP NOT NULL,
    resolution_value DECIMAL(3, 2) NOT NULL, -- 1.0 for YES, 0.0 for NO
    resolved_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_historical_markets_category ON historical_markets(category);
CREATE INDEX idx_historical_markets_resolution_date ON historical_markets(resolution_date);
CREATE INDEX idx_historical_markets_resolved_at ON historical_markets(resolved_at);


-- ============================================================
-- NEWS_EVENTS TABLE
-- Stores news from Twitter/RSS feeds
-- ============================================================
CREATE TABLE IF NOT EXISTS news_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    headline TEXT NOT NULL,
    keywords TEXT[], -- Array of extracted keywords
    source TEXT, -- 'twitter', 'reuters', 'ap', etc.
    sentiment_score DECIMAL(3, 2) DEFAULT 0.0, -- -1.0 to 1.0 (placeholder for v1)
    url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_news_events_timestamp ON news_events(timestamp DESC);
CREATE INDEX idx_news_events_keywords ON news_events USING GIN(keywords); -- GIN index for array searches
CREATE INDEX idx_news_events_source ON news_events(source);


-- ============================================================
-- TRADER_PERFORMANCE TABLE
-- Stores top trader stats for copy trading agent
-- ============================================================
CREATE TABLE IF NOT EXISTS trader_performance (
    trader_id TEXT PRIMARY KEY,
    username TEXT,
    win_rate DECIMAL(5, 2), -- e.g., 65.50 for 65.5%
    total_trades INTEGER DEFAULT 0,
    total_volume DECIMAL(15, 2),
    avg_position_size DECIMAL(15, 2),
    sharpe_ratio DECIMAL(5, 2),
    last_active TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_trader_performance_win_rate ON trader_performance(win_rate DESC);
CREATE INDEX idx_trader_performance_total_volume ON trader_performance(total_volume DESC);


-- ============================================================
-- THESES TABLE
-- Stores agent-generated trade ideas
-- ============================================================
CREATE TABLE IF NOT EXISTS theses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL, -- 'geo', 'copy', 'sentiment', etc.
    market_id TEXT NOT NULL,
    thesis_text TEXT NOT NULL,
    fair_value DECIMAL(10, 6) NOT NULL,
    current_odds DECIMAL(10, 6) NOT NULL,
    edge DECIMAL(10, 6) NOT NULL, -- fair_value - current_odds
    conviction DECIMAL(3, 2) NOT NULL, -- 0.0 to 1.0
    horizon TEXT, -- 'short', 'medium', 'long'
    proposed_action JSONB NOT NULL, -- {"side": "YES", "size_pct": 0.15}
    status TEXT DEFAULT 'active', -- 'active', 'executed', 'expired', 'rejected'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (market_id) REFERENCES markets(id) ON DELETE CASCADE
);

CREATE INDEX idx_theses_agent_id ON theses(agent_id);
CREATE INDEX idx_theses_market_id ON theses(market_id);
CREATE INDEX idx_theses_status ON theses(status);
CREATE INDEX idx_theses_conviction ON theses(conviction DESC);
CREATE INDEX idx_theses_created_at ON theses(created_at DESC);


-- ============================================================
-- PORTFOLIO TABLE
-- Stores current portfolio state (single row, updated)
-- ============================================================
CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY DEFAULT 1, -- Single row table
    cash DECIMAL(15, 2) NOT NULL DEFAULT 1000.00,
    total_value DECIMAL(15, 2) NOT NULL DEFAULT 1000.00,
    deployed_pct DECIMAL(5, 2) DEFAULT 0.00, -- Percentage of capital deployed
    daily_pnl DECIMAL(15, 2) DEFAULT 0.00,
    all_time_pnl DECIMAL(15, 2) DEFAULT 0.00,
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT single_portfolio CHECK (id = 1) -- Ensure only one row
);

-- Insert initial portfolio row
INSERT INTO portfolio (id, cash, total_value, deployed_pct, daily_pnl, all_time_pnl)
VALUES (1, 1000.00, 1000.00, 0.00, 0.00, 0.00)
ON CONFLICT (id) DO NOTHING;


-- ============================================================
-- POSITIONS TABLE
-- Stores open and closed trading positions
-- ============================================================
CREATE TABLE IF NOT EXISTS positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    market_id TEXT NOT NULL,
    thesis_id UUID,
    side TEXT NOT NULL, -- 'YES' or 'NO'
    shares DECIMAL(15, 6) NOT NULL,
    entry_price DECIMAL(10, 6) NOT NULL,
    current_price DECIMAL(10, 6) NOT NULL,
    pnl DECIMAL(15, 2) DEFAULT 0.00,
    status TEXT DEFAULT 'open', -- 'open', 'closed', 'stopped_out'
    opened_at TIMESTAMP DEFAULT NOW(),
    closed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (market_id) REFERENCES markets(id) ON DELETE CASCADE,
    FOREIGN KEY (thesis_id) REFERENCES theses(id) ON DELETE SET NULL
);

CREATE INDEX idx_positions_market_id ON positions(market_id);
CREATE INDEX idx_positions_thesis_id ON positions(thesis_id);
CREATE INDEX idx_positions_status ON positions(status);
CREATE INDEX idx_positions_opened_at ON positions(opened_at DESC);

-- Add agent_id and theme columns for theme-based portfolio tracking
ALTER TABLE positions ADD COLUMN IF NOT EXISTS agent_id TEXT;
ALTER TABLE positions ADD COLUMN IF NOT EXISTS theme TEXT;
CREATE INDEX IF NOT EXISTS idx_positions_agent_id ON positions(agent_id);
CREATE INDEX IF NOT EXISTS idx_positions_theme ON positions(theme);


-- ============================================================
-- IC_MEMOS TABLE
-- Stores daily investment committee memos
-- ============================================================
CREATE TABLE IF NOT EXISTS ic_memos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL UNIQUE,
    memo_text TEXT NOT NULL, -- Markdown formatted
    portfolio_summary JSONB, -- Snapshot of portfolio state
    trades_count INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 2),
    daily_return DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ic_memos_date ON ic_memos(date DESC);


-- ============================================================
-- EVENT_LOG TABLE
-- Append-only audit log for all system events
-- ============================================================
CREATE TABLE IF NOT EXISTS event_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    event_type TEXT NOT NULL, -- 'market_fetched', 'thesis_generated', 'trade_executed', 'stop_loss_triggered', etc.
    agent_id TEXT,
    market_id TEXT,
    thesis_id UUID,
    position_id UUID,
    details JSONB, -- Flexible JSON for event-specific data
    severity TEXT DEFAULT 'info', -- 'info', 'warning', 'error', 'critical'
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT append_only CHECK (timestamp = created_at) -- Enforce append-only
);

CREATE INDEX idx_event_log_timestamp ON event_log(timestamp DESC);
CREATE INDEX idx_event_log_event_type ON event_log(event_type);
CREATE INDEX idx_event_log_severity ON event_log(severity);
CREATE INDEX idx_event_log_market_id ON event_log(market_id);
CREATE INDEX idx_event_log_thesis_id ON event_log(thesis_id);


-- ============================================================
-- AGENT_PERFORMANCE TABLE
-- Tracks individual agent trade results for performance analysis
-- ============================================================
CREATE TABLE IF NOT EXISTS agent_performance (
    id BIGSERIAL PRIMARY KEY,
    agent_id TEXT NOT NULL,
    theme TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    trade_result BOOLEAN NOT NULL,
    pnl DECIMAL(15, 2) NOT NULL,
    thesis_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_performance_agent_id ON agent_performance(agent_id);
CREATE INDEX idx_agent_performance_theme ON agent_performance(theme);
CREATE INDEX idx_agent_performance_timestamp ON agent_performance(timestamp DESC);


-- ============================================================
-- THEME_ALLOCATIONS TABLE
-- Stores weekly capital allocation snapshots per theme
-- ============================================================
CREATE TABLE IF NOT EXISTS theme_allocations (
    id SERIAL PRIMARY KEY,
    theme TEXT NOT NULL,
    capital DECIMAL(15, 2) NOT NULL,
    allocation_pct DECIMAL(5, 2) NOT NULL,
    week_start DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_theme_allocations_week ON theme_allocations(week_start DESC);
CREATE INDEX idx_theme_allocations_theme ON theme_allocations(theme);


-- ============================================================
-- FUNCTIONS & TRIGGERS
-- Auto-update updated_at timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_markets_updated_at BEFORE UPDATE ON markets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_theses_updated_at BEFORE UPDATE ON theses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trader_performance_updated_at BEFORE UPDATE ON trader_performance
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- GRANTS (for Supabase anon key access if needed)
-- Adjust based on your auth strategy
-- ============================================================
-- Example: Grant read access to anon role, write to authenticated
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO anon;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO authenticated;


-- ============================================================
-- SCHEMA VALIDATION
-- Quick sanity check
-- ============================================================
DO $$
BEGIN
    ASSERT (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN 
        ('markets', 'historical_markets', 'news_events', 'trader_performance', 'theses', 'portfolio', 'positions', 'ic_memos', 'event_log', 'agent_performance', 'theme_allocations')
    ) = 11, 'Schema creation failed: missing tables';
    
    RAISE NOTICE 'Schema validation passed: All 11 tables created successfully';
END $$;
