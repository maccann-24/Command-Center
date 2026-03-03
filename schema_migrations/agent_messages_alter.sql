-- Migration: Update agent_messages table for Trading Floor (ALTER version)
-- Created: 2026-03-02
-- Description: Adds missing columns to existing agent_messages table

-- Add missing columns (safe: won't error if column already exists due to IF NOT EXISTS)
DO $$ 
BEGIN
    -- Timestamp (use created_at if it exists, or add timestamp)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='agent_messages' AND column_name='timestamp') THEN
        ALTER TABLE agent_messages ADD COLUMN timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL;
    END IF;

    -- Status
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='agent_messages' AND column_name='status') THEN
        ALTER TABLE agent_messages ADD COLUMN status TEXT;
    END IF;

    -- Tags
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='agent_messages' AND column_name='tags') THEN
        ALTER TABLE agent_messages ADD COLUMN tags TEXT[];
    END IF;

    -- Market question
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='agent_messages' AND column_name='market_question') THEN
        ALTER TABLE agent_messages ADD COLUMN market_question TEXT;
    END IF;

    -- Market ID
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='agent_messages' AND column_name='market_id') THEN
        ALTER TABLE agent_messages ADD COLUMN market_id TEXT;
    END IF;

    -- Current odds
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='agent_messages' AND column_name='current_odds') THEN
        ALTER TABLE agent_messages ADD COLUMN current_odds DECIMAL(10, 6);
    END IF;

    -- Thesis odds
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='agent_messages' AND column_name='thesis_odds') THEN
        ALTER TABLE agent_messages ADD COLUMN thesis_odds DECIMAL(10, 6);
    END IF;

    -- Edge
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='agent_messages' AND column_name='edge') THEN
        ALTER TABLE agent_messages ADD COLUMN edge DECIMAL(10, 6);
    END IF;

    -- Conviction
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='agent_messages' AND column_name='conviction') THEN
        ALTER TABLE agent_messages ADD COLUMN conviction DECIMAL(10, 6);
    END IF;

    -- Capital allocated
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='agent_messages' AND column_name='capital_allocated') THEN
        ALTER TABLE agent_messages ADD COLUMN capital_allocated DECIMAL(12, 2);
    END IF;

    -- Reasoning
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='agent_messages' AND column_name='reasoning') THEN
        ALTER TABLE agent_messages ADD COLUMN reasoning TEXT;
    END IF;

    -- Signals
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='agent_messages' AND column_name='signals') THEN
        ALTER TABLE agent_messages ADD COLUMN signals JSONB;
    END IF;

    -- Related thesis ID
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='agent_messages' AND column_name='related_thesis_id') THEN
        ALTER TABLE agent_messages ADD COLUMN related_thesis_id UUID;
    END IF;

END $$;

-- Add check constraint for message_type (safe: won't error if already exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.constraint_column_usage 
        WHERE table_name = 'agent_messages' 
        AND constraint_name = 'agent_messages_message_type_check'
    ) THEN
        ALTER TABLE agent_messages 
        ADD CONSTRAINT agent_messages_message_type_check 
        CHECK (message_type IN ('thesis', 'conflict', 'consensus', 'alert', 'analyzing', 'chat', 'directive'));
    END IF;
END $$;

-- Create indexes (safe: IF NOT EXISTS prevents errors)
CREATE INDEX IF NOT EXISTS idx_agent_messages_timestamp ON agent_messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_agent_messages_created_at ON agent_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_messages_agent_id ON agent_messages(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_messages_theme ON agent_messages(theme);
CREATE INDEX IF NOT EXISTS idx_agent_messages_type ON agent_messages(message_type);
CREATE INDEX IF NOT EXISTS idx_agent_messages_market_id ON agent_messages(market_id) WHERE market_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_agent_messages_status ON agent_messages(status) WHERE status IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_agent_messages_theme_timestamp ON agent_messages(theme, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_agent_messages_type_timestamp ON agent_messages(message_type, timestamp DESC);

-- Copy created_at to timestamp if timestamp was just added and is NULL
UPDATE agent_messages SET timestamp = created_at WHERE timestamp IS NULL;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ agent_messages table migration complete!';
    RAISE NOTICE 'Added columns: timestamp, status, tags, market_question, market_id, current_odds, thesis_odds, edge, conviction, capital_allocated, reasoning, signals, related_thesis_id';
END $$;
