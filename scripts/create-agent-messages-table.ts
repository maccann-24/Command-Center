#!/usr/bin/env tsx
/**
 * Create agent_messages table in Supabase
 * Run: npx tsx scripts/create-agent-messages-table.ts
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'http://localhost:54321'
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'anon'

const supabase = createClient(supabaseUrl, supabaseKey)

const sql = `
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
DROP POLICY IF EXISTS "Allow anonymous read access to agent_messages" ON agent_messages;
CREATE POLICY "Allow anonymous read access to agent_messages"
ON agent_messages FOR SELECT
TO anon
USING (true);

-- Policy: Allow authenticated users read access
DROP POLICY IF EXISTS "Allow authenticated read access to agent_messages" ON agent_messages;
CREATE POLICY "Allow authenticated read access to agent_messages"
ON agent_messages FOR SELECT
TO authenticated
USING (true);

-- Policy: Allow anonymous insert (for agents posting messages)
DROP POLICY IF EXISTS "Allow anonymous insert to agent_messages" ON agent_messages;
CREATE POLICY "Allow anonymous insert to agent_messages"
ON agent_messages FOR INSERT
TO anon
WITH CHECK (true);
`

async function main() {
  console.log('='..repeat(70))
  console.log('Creating agent_messages table...')
  console.log('='..repeat(70))
  console.log()

  try {
    // Execute SQL using Supabase RPC or raw query
    // Note: This requires the SQL to be executed via Supabase Dashboard
    // or a custom RPC function
    
    console.log('⚠️  Supabase JS client cannot execute arbitrary SQL for security.')
    console.log()
    console.log('📋 Execute this SQL in Supabase Dashboard → SQL Editor:')
    console.log()
    console.log(sql)
    console.log()
    console.log('='..repeat(70))
    console.log('After running SQL, test with:')
    console.log('  cd /home/ubuntu/clawd/agents/coding/polymarket')
    console.log('  source .venv/bin/activate')
    console.log('  python3 test_trading_floor_post.py')
    
  } catch (error) {
    console.error('❌ Error:', error)
    process.exit(1)
  }
}

main()
