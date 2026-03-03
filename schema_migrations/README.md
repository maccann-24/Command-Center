# Database Migrations

This directory contains SQL migration files for the BASED MONEY trading system.

---

## Current Migrations

### `agent_messages.sql` - Trading Floor Messages

**Created:** 2026-03-02  
**Purpose:** Store all agent communications for the Trading Floor feature

**Tables:**
- `agent_messages` - Main table for agent messages

**Features:**
- Real-time messaging between agents
- Thesis generation tracking
- Conflict detection
- Consensus identification
- Alert system

---

## How to Apply Migrations

### Option 1: Supabase Dashboard (Easiest)

1. Go to your Supabase project: https://app.supabase.com
2. Navigate to **SQL Editor** in the left sidebar
3. Click **New Query**
4. Copy the contents of `agent_messages.sql`
5. Paste into the editor
6. Click **Run** or press `Ctrl+Enter`

**You should see:** `Success. No rows returned`

---

### Option 2: Supabase CLI

```bash
# Install CLI (if not already installed)
npm install -g supabase

# Login to Supabase
supabase login

# Link your project
supabase link --project-ref your-project-ref

# Apply migration
supabase db push
```

---

### Option 3: Using the Helper Script

```bash
# Set environment variables
export SUPABASE_URL='https://your-project.supabase.co'
export SUPABASE_KEY='your-service-role-key'

# Run the migration script
./schema_migrations/apply_migration.sh
```

---

## Verifying the Migration

After applying, verify the table was created:

```sql
-- Run this in Supabase SQL Editor
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'agent_messages'
ORDER BY ordinal_position;
```

You should see all columns listed.

---

## Testing the Table

Insert a test message:

```sql
INSERT INTO agent_messages (
    agent_id,
    theme,
    message_type,
    market_question,
    current_odds,
    thesis_odds,
    edge,
    conviction,
    capital_allocated,
    reasoning,
    status
) VALUES (
    'twosigma_geo',
    'geopolitical',
    'thesis',
    'Will Netanyahu be Israeli PM on April 1?',
    0.78,
    0.85,
    0.042,
    0.71,
    147.00,
    'Coalition stable, no confidence vote unlikely before Passover',
    'thesis_generated'
);
```

Query it back:

```sql
SELECT * FROM agent_messages ORDER BY timestamp DESC LIMIT 1;
```

---

## Rollback (if needed)

To remove the table:

```sql
DROP TABLE IF EXISTS agent_messages CASCADE;
```

**⚠️ Warning:** This will delete all data in the table!

---

## Next Steps

After migration is applied:

1. ✅ Update `command-center/lib/supabase/trading.ts` with helper functions
2. ✅ Add `post_message()` method to `agents/base.py`
3. ✅ Create Trading Floor page in Command Center
4. ✅ Test real-time subscriptions

---

## Troubleshooting

### Error: "relation already exists"

The table already exists. Either:
- Skip this migration
- Or drop the existing table first (see Rollback above)

### Error: "permission denied"

Make sure you're using the **service_role** key, not the **anon** key.

### Error: "function uuid_generate_v4() does not exist"

Enable the uuid extension:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## Schema Details

### Indexes Created

- `idx_agent_messages_timestamp` - Fast queries by time
- `idx_agent_messages_agent_id` - Filter by agent
- `idx_agent_messages_theme` - Filter by theme
- `idx_agent_messages_type` - Filter by message type
- `idx_agent_messages_market_id` - Filter by market
- `idx_agent_messages_status` - Filter by status
- `idx_agent_messages_theme_timestamp` - Composite for theme+time queries
- `idx_agent_messages_type_timestamp` - Composite for type+time queries

### Row Level Security (RLS)

Currently set to allow all reads and authenticated inserts. Adjust the policies in `agent_messages.sql` based on your security requirements.

---

**Questions?** Check the main documentation or review the SQL file directly.
