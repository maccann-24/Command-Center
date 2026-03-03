# Based Money Runbook

**Production deployment and operations guide for the Based Money prediction market trading system.**

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.10+** installed
- **Supabase account** (free tier is sufficient)
- **News source access:**
  - Option 1: Twitter API v2 (free tier) for real-time market sentiment
  - Option 2: RSS feeds (no API key needed, good for testing)
- **For live trading only:**
  - Polymarket account
  - Polymarket API key
  - Funded wallet (start with $100-500)

---

## Setup

### 1. Clone the Repository

```bash
git clone <repo_url>
cd based-money
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```ini
# Supabase (required)
SUPABASE_URL=<your_supabase_project_url>
SUPABASE_KEY=<your_supabase_anon_key>

# Trading mode (start with paper)
TRADING_MODE=paper

# News source (start with RSS for simplicity)
NEWS_SOURCE=rss

# If using Twitter:
# NEWS_SOURCE=twitter
# TWITTER_BEARER_TOKEN=<your_token>

# For live trading (add later):
# POLYMARKET_API_KEY=<your_api_key>
# POLYMARKET_PRIVATE_KEY=<your_wallet_private_key>
```

---

## Database Setup

### 1. Open Supabase SQL Editor

Navigate to your Supabase project → SQL Editor.

### 2. Run Schema

Copy the contents of `schema.sql` and execute in the SQL Editor.

### 3. Verify Tables Created

You should see **9 tables**:
- `markets`
- `historical_markets`
- `news_events`
- `theses`
- `portfolio`
- `positions`
- `ic_memos`
- `event_log`
- `trader_performance`

---

## Running Backtest (MANDATORY FIRST STEP)

**⚠️ DO NOT skip backtesting. This validates your agent logic before risking real capital.**

### 1. Collect Historical Data

```bash
python -m backtesting.data_loader
```

This fetches historical market data and stores it in `historical_markets` table.

### 2. Run Backtest

```bash
python -m backtesting.run_backtest --agent geo --days 90
```

This simulates 90 days of trading using historical data.

### 3. Review Performance Report

Check terminal output for:
- **Win rate** (target: >52%)
- **Sharpe ratio** (target: >1.0)
- **Max drawdown** (target: <15%)
- **Total return**

### 4. Gate Check

**If validation fails:**
- ❌ DO NOT proceed to paper trading
- Iterate on agent logic in `agents/geo.py`
- Adjust risk parameters in `config.py`
- Re-run backtest until performance targets are met

**If validation passes:**
- ✅ Proceed to paper trading

---

## Running Paper Trading

Paper trading simulates live operations without real money.

### 1. Ensure Paper Mode

Verify `.env` has:
```ini
TRADING_MODE=paper
```

### 2. Start the System

```bash
python main.py
```

### 3. Monitor Output

Watch terminal for:
- Market fetching cycles
- News event processing
- Thesis generation
- Trade execution logs

### 4. Check Database Activity

Open Supabase and verify data flowing into:
- `news_events`
- `theses`
- `positions`
- `ic_memos`

### 5. Validation Period

**Run paper trading for minimum 2 weeks.**

Track:
- Win rate (target: >52%)
- Position sizing behavior
- Risk engine enforcement
- Edge calculation accuracy

---

## Switching to Live Trading

**⚠️ Only proceed after successful paper trading validation.**

### Prerequisites

1. ✅ Paper trading completed (2+ weeks)
2. ✅ Win rate >52%
3. ✅ Risk engine working as expected
4. ✅ Polymarket account set up
5. ✅ Wallet funded with $100-500 (start small)

### 1. Add Live Trading Credentials

Update `.env`:

```ini
TRADING_MODE=live
POLYMARKET_API_KEY=<your_api_key>
POLYMARKET_PRIVATE_KEY=<your_wallet_private_key>
```

### 2. Restart System

```bash
python main.py
```

### 3. Start Small

**First week limits:**
- Max position size: 10% of portfolio
- Max deployed capital: 30% of portfolio
- Monitor every trade closely

### 4. Scale Gradually

After 1 week of stable live trading:
- Increase max deployed to 50%
- Increase position sizes if win rate holds

---

## Troubleshooting

### "No markets fetched"

**Possible causes:**
- Polymarket API downtime
- Network connectivity issues
- Rate limiting

**Solutions:**
- Check [status.polymarket.com](https://status.polymarket.com)
- Verify internet connection
- Wait 5 minutes and retry

---

### "Supabase connection failed"

**Possible causes:**
- Incorrect credentials in `.env`
- Network firewall blocking Supabase
- Project paused (free tier inactivity)

**Solutions:**
- Double-check `SUPABASE_URL` and `SUPABASE_KEY`
- Test connection: `curl $SUPABASE_URL/rest/v1/`
- Log into Supabase dashboard and verify project is active

---

### "No theses generated"

**Possible causes:**
- Empty `news_events` table
- GeoAgent not seeing relevant markets
- Model API key missing/invalid

**Solutions:**
- Check `news_events` table has data
- Verify news source is configured (`NEWS_SOURCE=rss` or `twitter`)
- Check logs for thesis generation attempts
- Review `agents/geo.py` for thesis criteria

---

### "All trades rejected by risk engine"

**Possible causes:**
- Portfolio fully deployed (hit 50% deployment limit)
- Position size exceeds limits
- Edge below minimum threshold

**Solutions:**
- Check `portfolio.deployed_pct` in Supabase
- If >50%, wait for positions to close before new trades
- Review `config.py` risk parameters
- Lower position sizes in agent logic

---

## Self-Test

**To validate this runbook:**

1. Provision a fresh Linux VM or Docker container
2. Follow this runbook step-by-step from Prerequisites → Paper Trading
3. Note any:
   - Missing steps
   - Ambiguous instructions
   - Dependency conflicts
   - Error messages not covered in Troubleshooting
4. Update this document with fixes

**Success criteria:**
- System runs paper trading for 24 hours without crashes
- All 9 database tables populated with data
- At least 1 thesis generated and evaluated

---

## Support

For issues not covered here:
1. Check `logs/` directory for detailed error traces
2. Review `event_log` table in Supabase for system events
3. Open an issue in the repo with:
   - Error message
   - Relevant log excerpt
   - Steps to reproduce

---

**Last updated:** 2026-02-27
