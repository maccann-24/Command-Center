-- Migration: Create agent_messages table for Trading Floor
-- Created: 2026-03-02
-- Description: Stores all agent communications, theses, conflicts, and alerts

-- Create agent_messages table
CREATE TABLE IF NOT EXISTS agent_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Agent information
    agent_id TEXT NOT NULL,
    theme TEXT NOT NULL,
    
    -- Message metadata
    message_type TEXT NOT NULL CHECK (message_type IN ('thesis', 'conflict', 'consensus', 'alert', 'analyzing')),
    status TEXT,
    tags TEXT[],
    
    -- Market information
    market_question TEXT,
    market_id TEXT,
    
    -- Trading data
    current_odds DECIMAL(10, 6),
    thesis_odds DECIMAL(10, 6),
    edge DECIMAL(10, 6),
    conviction DECIMAL(10, 6),
    capital_allocated DECIMAL(12, 2),
    
    -- Content
    reasoning TEXT,
    signals JSONB,
    
    -- Relationships
    related_thesis_id UUID
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_messages_timestamp ON agent_messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_agent_messages_agent_id ON agent_messages(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_messages_theme ON agent_messages(theme);
CREATE INDEX IF NOT EXISTS idx_agent_messages_type ON agent_messages(message_type);
CREATE INDEX IF NOT EXISTS idx_agent_messages_market_id ON agent_messages(market_id) WHERE market_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_agent_messages_status ON agent_messages(status) WHERE status IS NOT NULL;

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_agent_messages_theme_timestamp ON agent_messages(theme, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_agent_messages_type_timestamp ON agent_messages(message_type, timestamp DESC);

-- Add comment to table
COMMENT ON TABLE agent_messages IS 'Stores all agent communications for the Trading Floor including theses, conflicts, consensus plays, and alerts';

-- Add comments to important columns
COMMENT ON COLUMN agent_messages.message_type IS 'Type of message: thesis, conflict, consensus, alert, or analyzing';
COMMENT ON COLUMN agent_messages.signals IS 'JSON object containing data sources, news articles, social signals, etc.';
COMMENT ON COLUMN agent_messages.related_thesis_id IS 'Links message to a specific thesis in the theses table';

-- Enable Row Level Security (RLS)
ALTER TABLE agent_messages ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust based on your security needs)
CREATE POLICY "Enable read access for all users" ON agent_messages
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for authenticated users" ON agent_messages
    FOR INSERT WITH CHECK (true);

-- Grant permissions (adjust based on your setup)
-- GRANT SELECT ON agent_messages TO anon, authenticated;
-- GRANT INSERT, UPDATE ON agent_messages TO authenticated;
