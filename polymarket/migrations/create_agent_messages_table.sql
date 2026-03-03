-- Create agent_messages table for Trading Floor
CREATE TABLE IF NOT EXISTS agent_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    agent_id TEXT NOT NULL,
    theme TEXT,
    message_type TEXT NOT NULL CHECK (message_type IN ('thesis', 'conflict', 'consensus', 'alert', 'analyzing', 'chat')),
    content TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_agent_messages_created_at ON agent_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_messages_agent_id ON agent_messages(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_messages_theme ON agent_messages(theme);
CREATE INDEX IF NOT EXISTS idx_agent_messages_type ON agent_messages(message_type);

-- Enable RLS (Row Level Security)
ALTER TABLE agent_messages ENABLE ROW LEVEL SECURITY;

-- Policy: Allow anonymous read access (for Trading Floor dashboard)
CREATE POLICY "Allow anonymous read access to agent_messages"
ON agent_messages FOR SELECT
TO anon
USING (true);

-- Policy: Allow service role full access (for agents posting messages)
CREATE POLICY "Allow service role full access to agent_messages"
ON agent_messages FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Policy: Allow authenticated users read access
CREATE POLICY "Allow authenticated read access to agent_messages"
ON agent_messages FOR SELECT
TO authenticated
USING (true);

COMMENT ON TABLE agent_messages IS 'Real-time agent messages for Trading Floor display';
COMMENT ON COLUMN agent_messages.agent_id IS 'Agent identifier (e.g., geopolitical-analyst-1)';
COMMENT ON COLUMN agent_messages.theme IS 'Theme/category (e.g., geopolitics, crypto, us-politics, weather)';
COMMENT ON COLUMN agent_messages.message_type IS 'Message type: thesis, conflict, consensus, alert, analyzing, chat';
COMMENT ON COLUMN agent_messages.content IS 'Message content/summary';
COMMENT ON COLUMN agent_messages.metadata IS 'Structured data (market_question, conviction, reasoning, etc.)';
