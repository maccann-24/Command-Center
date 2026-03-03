# Backtesting Quick Start Guide

Quick reference for running backtests on the BASED MONEY Polymarket bot.

## Prerequisites

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure Supabase
cp .env.example .env
# Edit .env with your SUPABASE_URL and SUPABASE_KEY

# 3. Create database schema
# Run schema.sql in Supabase SQL editor
```

## Step 1: Load Historical Data

```python
from backtesting import fetch_historical_markets

# Fetch last 90 days of resolved markets
# Target: 200+ markets (geopolitical, crypto, sports)
count = fetch_historical_markets(
    days_back=90,
    target_count=200,
    categories=["geopolitical", "crypto", "sports"]
)

print(f"Loaded {count} historical markets")
# Expected: 200+ markets
```

## Step 2: Create or Import Agent

```python
from agents import GeoAgent  # Or your custom agent

agent = GeoAgent()
```

**Agent Requirements:**
- Must implement `generate_thesis(market)` method
- Should return Thesis with:
  - `edge` (calculated edge)
  - `conviction` (0.0 to 1.0)
  - `proposed_action` dict with:
    - `side`: "YES" or "NO"
    - `size_pct`: percentage of cash to deploy

## Step 3: Run Backtest

```python
from datetime import date
from backtesting import BacktestEngine

# Initialize engine
engine = BacktestEngine()

# Run backtest
results = engine.run_backtest(
    agent=agent,
    start_date=date(2025, 11, 1),
    end_date=date(2026, 2, 1),
    initial_capital=1000.0,
    min_conviction=0.70
)
```

## Step 4: Analyze Results

```python
# Print summary
print(results.summary())

# Access metrics
print(f"Win Rate: {results.win_rate:.1f}%")
print(f"Total P&L: ${results.total_pnl:.2f} ({results.total_pnl_pct:+.2f}%)")
print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
print(f"Max Drawdown: {results.max_drawdown_pct:.1f}%")

# Review trades
for trade in results.trades[:5]:  # First 5 trades
    print(f"{trade.date}: {trade.side} {trade.market_question[:40]}...")
    print(f"  Entry: ${trade.entry_price:.2f}, Exit: ${trade.exit_price:.2f}")
    print(f"  P&L: ${trade.pnl:+.2f} ({trade.pnl_pct:+.1f}%)")

# Access equity curve
dates, values = zip(*results.equity_curve)
# Plot with matplotlib, save to file, etc.
```

## One-Liner: Simple 90-Day Backtest

```python
from backtesting import run_simple_backtest
from agents import GeoAgent

results = run_simple_backtest(GeoAgent(), days_back=90)
print(results.summary())
```

## Output Example

```
============================================================
BACKTEST SIMULATION
============================================================
Agent: GeoAgent
Period: 2025-11-01 to 2026-02-01
Initial Capital: $1,000.00
Min Conviction: 70%

📊 Loading historical markets...
   Loaded 214 historical markets

📅 Simulating 92 trading days...

============================================================
BACKTEST RESULTS
============================================================
Agent: GeoAgent
Period: 2025-11-01 to 2026-02-01
Initial Capital: $1,000.00

PERFORMANCE
------------------------------------------------------------
Final Capital: $1,287.50
Total P&L: $287.50 (+28.75%)
Max Drawdown: $123.45 (10.21%)
Sharpe Ratio: 1.85

TRADES
------------------------------------------------------------
Total Trades: 47
Winning Trades: 29
Losing Trades: 18
Win Rate: 61.7%

ACTIVITY
------------------------------------------------------------
Markets Evaluated: 214
Theses Generated: 93
Theses Executed: 47
Execution Rate: 50.5%
============================================================
```

## Common Issues

### No Historical Markets Found
```python
# Check if data was loaded
from backtesting import get_loaded_count
print(f"Markets in DB: {get_loaded_count()}")

# If zero, run data collection first
fetch_historical_markets()
```

### Agent Errors
```python
# Test agent on single market first
from models import Market

test_market = Market(
    id="test",
    question="Will X happen?",
    category="geopolitical",
    yes_price=0.65,
    no_price=0.35,
    volume_24h=50000.0
)

thesis = agent.generate_thesis(test_market)
print(f"Conviction: {thesis.conviction}")
print(f"Edge: {thesis.edge}")
print(f"Action: {thesis.proposed_action}")
```

### Lookahead Bias Check
The engine automatically prevents lookahead bias by:
- Only showing markets with `resolution_date >= current_date`
- Not exposing future resolution values to agent
- Simulating chronological order

**To verify:**
```python
# Check that agent doesn't access resolution_value during thesis generation
# Agent should only use: question, category, current prices, volume
```

## Best Practices

1. **Start Small**: Test on 30 days before running 90-day backtests
2. **Validate Agent**: Ensure `generate_thesis()` returns valid Thesis objects
3. **Check Data**: Verify historical markets loaded (`get_loaded_count()`)
4. **Review Trades**: Inspect individual trades to understand agent behavior
5. **Compare Agents**: Run multiple agents and compare results
6. **Avoid Overfitting**: Don't optimize agent on same data you backtest on
7. **Walk Forward**: Use rolling backtests (train on past, test on future)

## Interpreting Results

### Good Signs ✅
- Win rate > 55%
- Sharpe ratio > 1.0
- Consistent equity curve (smooth upward trend)
- Reasonable drawdown (< 20%)
- High execution rate (theses actually traded)

### Warning Signs ⚠️
- Win rate < 50% (worse than random)
- Sharpe ratio < 0.5 (poor risk-adjusted returns)
- Large drawdowns (> 30%)
- Too few trades (< 10 in 90 days)
- All theses rejected (execution rate near 0%)

### Red Flags 🚩
- Win rate > 90% (likely lookahead bias!)
- Perfect equity curve (suspiciously smooth)
- Zero losing trades (data leakage)
- Implausible returns (> 1000% in 90 days)

## Next Steps After Backtest

1. **If results are good (>55% win rate, Sharpe >1.0):**
   - Run on different time periods (validate robustness)
   - Paper trade for 30 days (no real money)
   - If paper trade succeeds, consider small live deployment

2. **If results are mediocre (50-55% win rate):**
   - Review losing trades (what went wrong?)
   - Adjust conviction thresholds
   - Refine edge calculation logic
   - Iterate and retest

3. **If results are poor (<50% win rate):**
   - Fundamentally rethink agent strategy
   - Check for bugs in edge calculation
   - Consider different market categories
   - May need more data sources (news, signals)

## Files Reference

- `backtesting/data_loader.py` - Historical data fetching
- `backtesting/engine.py` - Backtest simulation
- `agents/base.py` - Agent interface
- `agents/geo.py` - Example: Geopolitical agent
- `models/thesis.py` - Thesis data structure
- `models/portfolio.py` - Portfolio & Position models

## Support

For issues or questions:
1. Check `TASK_14_HISTORICAL_DATA_COMPLETE.md` for data collection
2. Check `TASK_15_BACKTEST_ENGINE_COMPLETE.md` for engine details
3. Review agent implementation in `agents/` directory

---
**Quick Start Version**: 1.0  
**Last Updated**: 2026-02-27
