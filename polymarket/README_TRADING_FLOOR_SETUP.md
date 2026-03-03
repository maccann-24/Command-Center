# Trading Floor Integration Setup

## Overview

The Trading Floor integration allows agents to post real-time messages to the Command Center dashboard for live monitoring.

## Step 1: Create agent_messages Table

The `agent_messages` table stores messages from trading agents for display on the Trading Floor.

### Option A: Run SQL in Supabase Dashboard

1. Go to your Supabase Dashboard → SQL Editor
2. Copy the contents of `migrations/create_agent_messages_table.sql`
3. Paste and run the SQL

### Option B: Use psql

```bash
# Export connection string (get from Supabase Dashboard → Settings → Database)
export DATABASE_URL="postgresql://..."

# Run migration
psql $DATABASE_URL < migrations/create_agent_messages_table.sql
```

## Step 2: Verify Table Creation

Run the test script:

```bash
source .venv/bin/activate
python3 test_trading_floor_post.py
```

Expected output:
```
1. Posting 'analyzing' message...
   Result: ✅ Success

2. Posting 'thesis' message...
   Result: ✅ Success
```

## Step 3: Test Agent Integration

Run the geo agent test:

```bash
source .venv/bin/activate
python3 test_geo_trading_floor.py
```

This will:
- Post an "analyzing" message when the agent starts
- Post "thesis" messages for each generated thesis
- Display metadata (market question, edge, conviction, etc.)

## Step 4: View on Trading Floor

Open the Command Center:
```
http://localhost:3000/trading/floor
```

You should see:
- Real-time messages appearing without page refresh
- Color-coded message types (thesis=blue, alert=red, etc.)
- Expandable reasoning text
- Conviction badges
- Theme filtering

## Step 5: Integrate into All Agents

Once verified, add Trading Floor integration to the remaining 11 agents:

1. Import functions in agent's `update_theses()` method
2. Post "analyzing" message at start
3. Post "thesis" messages when theses are generated
4. Use appropriate agent_id and theme

Example:
```python
def update_theses(self):
    # Import Trading Floor functions
    try:
        from database import post_analyzing_message, post_thesis_message
        trading_floor_enabled = True
    except ImportError:
        trading_floor_enabled = False
    
    # Post analyzing message
    if trading_floor_enabled:
        post_analyzing_message(
            agent_id="your-agent-id",
            theme="your-theme",
            content="Analyzing markets..."
        )
    
    # ... generate theses ...
    
    # Post thesis messages
    if trading_floor_enabled and thesis:
        post_thesis_message(
            agent_id="your-agent-id",
            theme="your-theme",
            thesis_text=thesis.thesis_text,
            market_question=market.question,
            current_odds=thesis.current_odds,
            fair_value=thesis.fair_value,
            edge=thesis.edge,
            conviction=thesis.conviction,
            reasoning=thesis.thesis_text,
            capital_allocated=capital
        )
```

## Troubleshooting

### Import Error

If you get `ImportError: cannot import name 'post_analyzing_message'`:
- Ensure `database/trading_floor.py` exists
- Check `database/__init__.py` exports the functions
- Use `sys.path.insert(0, '.')` if needed

### DNS Error / Connection Failed

If you get `Name or service not known`:
- Check SUPABASE_URL is correct
- Verify network connectivity
- Ensure Supabase project is active

### Table Not Found

If you get `Could not find the table 'agent_messages'`:
- Run the migration SQL (Step 1)
- Verify table exists in Supabase Dashboard → Table Editor

### Messages Not Appearing

If messages don't show on Trading Floor:
- Check browser console for errors
- Verify Supabase Realtime is enabled (Project Settings → API)
- Confirm RLS policies allow read access
