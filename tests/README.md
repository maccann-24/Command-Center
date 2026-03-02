# Trading Floor Test Scripts

## Setup

Install Python dependencies:

```bash
pip install -r tests/requirements.txt
```

Make sure your Supabase environment variables are set:

```bash
export NEXT_PUBLIC_SUPABASE_URL="your-supabase-url"
export NEXT_PUBLIC_SUPABASE_ANON_KEY="your-anon-key"
```

Or load from `.env.local`:

```bash
source .env.local
```

## test_trading_floor.py

Populates the Trading Floor with 15 realistic fake agent messages.

**Features:**
- Mix of message types: thesis, conflict, consensus, alert, analyzing
- Multiple agents: geopolitical analysts, crypto bots, US politics trackers, weather forecasters
- Different themes: geopolitics, us-politics, crypto, weather
- Realistic metadata: conviction scores, market questions, reasoning
- Timestamps spread over last 25 minutes

**Run:**

```bash
python tests/test_trading_floor.py
```

**Output:**
- Inserts messages into `agent_messages` table
- Prints summary of each message
- Shows link to view Trading Floor

**Test Coverage:**
- ✅ At least 2 conflicts (divergent agent views)
- ✅ At least 3 consensus messages (agreement signals)
- ✅ Multiple thesis messages with edge calculations
- ✅ Alert messages for urgent developments
- ✅ Analyzing messages (work in progress)

After running, visit `/trading/floor` to see the messages populate in real-time!
