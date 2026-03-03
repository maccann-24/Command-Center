# Theme Portfolio System - Complete Guide

**Version:** 1.0  
**Last Updated:** 2026-03-02  
**System:** BASED MONEY Theme-Based Portfolio Management

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Theme System](#theme-system)
4. [Agent Specializations](#agent-specializations)
5. [Reallocation Rules](#reallocation-rules)
6. [Performance Tracking](#performance-tracking)
7. [Adding New Themes](#adding-new-themes)
8. [Adding New Agents](#adding-new-agents)
9. [Dashboard Usage](#dashboard-usage)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Theme Portfolio System is a sophisticated capital allocation framework that organizes trading agents by domain expertise (themes) and automatically reallocates capital based on performance.

### Key Concepts

- **Theme:** A market domain or category (Geopolitical, US Politics, Crypto, Weather)
- **Agent:** An institutional-style trading agent specialized in a specific strategy
- **Portfolio:** $10,000 total capital divided equally among 4 themes ($2,500 each)
- **Reallocation:** Weekly (within themes) and monthly (between themes) capital adjustments

### Benefits

- ✅ **Diversification:** Capital spread across uncorrelated market categories
- ✅ **Performance-based:** Winners get more capital, losers get less
- ✅ **Risk management:** Automatic probation and pause mechanisms
- ✅ **Scalability:** Easy to add new themes and agents
- ✅ **Transparency:** Full dashboard visualization of performance

---

## System Architecture

```
Portfolio ($10,000)
├── Geopolitical Theme ($2,500)
│   ├── TwoSigma Geo Agent (~$833)
│   ├── Goldman Geo Agent (~$833)
│   └── Bridgewater Geo Agent (~$833)
│
├── US Politics Theme ($2,500)
│   ├── Renaissance Politics Agent (~$833)
│   ├── JPMorgan Politics Agent (~$833)
│   └── Goldman Politics Agent (~$833)
│
├── Crypto Theme ($2,500)
│   ├── MorganStanley Crypto Agent (~$833)
│   ├── Renaissance Crypto Agent (~$833)
│   └── Citadel Crypto Agent (~$833)
│
└── Weather Theme ($2,500)
    ├── Renaissance Weather Agent (~$833)
    ├── MorganStanley Weather Agent (~$833)
    └── Bridgewater Weather Agent (~$833)
```

### Data Flow

```
Agents Generate Theses
        ↓
Orchestrator Routes by Theme
        ↓
Risk Engine Evaluates
        ↓
Execution Engine Executes
        ↓
Positions Tagged (agent_id + theme)
        ↓
Performance Tracker Records Results
        ↓
Weekly/Monthly Reallocation
        ↓
Capital Redistributed
```

---

## Theme System

### Current Themes

#### 1. **Geopolitical** 🌍
- **Focus:** International events, conflicts, elections, sanctions
- **Markets:** Global politics, international relations
- **Time Horizon:** Medium-term (weeks to months)

#### 2. **US Politics** 🇺🇸
- **Focus:** US elections, legislation, congressional action
- **Markets:** US political outcomes, policy decisions
- **Time Horizon:** Short to medium-term

#### 3. **Crypto** ₿
- **Focus:** Cryptocurrency prices, adoption, regulation
- **Markets:** BTC/ETH price predictions, regulatory outcomes
- **Time Horizon:** Short-term (days to weeks)

#### 4. **Weather** 🌦️
- **Focus:** Temperature, precipitation, extreme events
- **Markets:** Weather outcomes, climate events
- **Time Horizon:** Short to medium-term

### Theme Lifecycle

1. **ACTIVE** (Normal operation)
   - Full capital allocation
   - All agents competing
   - Weekly reallocation enabled

2. **PROBATION** (Warning state)
   - Triggered by 2 consecutive losing weeks
   - Capital reduced by 20%
   - Increased monitoring

3. **PAUSED** (Temporarily disabled)
   - Triggered by 2+ consecutive losing months
   - Capital reallocated to winning themes
   - Can be manually reactivated

---

## Agent Specializations

Each theme has 3 agents with different strategies to ensure diversification.

### Geopolitical Agents

**1. TwoSigma Geo (Macro Strategist)**
- **Strategy:** Macro geopolitical analysis
- **Edge:** 3% minimum
- **Conviction:** 60% minimum
- **Approach:** Big-picture trends, systemic analysis

**2. Goldman Geo (Fundamental Analyst)**
- **Strategy:** Fundamental political analysis
- **Edge:** 4% minimum
- **Conviction:** 65% minimum
- **Approach:** Deep research, long-term positioning

**3. Bridgewater Geo (Risk Analyst)**
- **Strategy:** Risk-focused geopolitical assessment
- **Edge:** 3% minimum
- **Conviction:** 55% minimum
- **Approach:** Downside protection, tail risk

### US Politics Agents

**1. Renaissance Politics (Quantitative)**
- **Strategy:** Multi-factor quantitative model
- **Edge:** 4% minimum
- **Conviction:** 65% minimum
- **Approach:** Data-driven, statistical patterns

**2. JPMorgan Politics (Event Catalyst)**
- **Strategy:** Event-driven catalyst trading
- **Edge:** 3% minimum
- **Conviction:** 60% minimum
- **Approach:** News reaction, momentum

**3. Goldman Politics (Fundamental)**
- **Strategy:** Political fundamental analysis
- **Edge:** 5% minimum
- **Conviction:** 70% minimum
- **Approach:** Structural analysis, long-term trends

### Crypto Agents

**1. MorganStanley Crypto (Technical)**
- **Strategy:** Technical analysis of odds movements
- **Edge:** 4% minimum
- **Conviction:** 60% minimum
- **Approach:** Chart patterns, indicators

**2. Renaissance Crypto (Quantitative)**
- **Strategy:** Multi-factor quant for crypto
- **Edge:** 5% minimum
- **Conviction:** 65% minimum
- **Approach:** On-chain metrics, correlations

**3. Citadel Crypto (Cycle Positioning)**
- **Strategy:** Crypto market cycle analysis
- **Edge:** 4% minimum
- **Conviction:** 65% minimum
- **Approach:** Fed policy, regulatory cycles

### Weather Agents

**1. Renaissance Weather (Quantitative)**
- **Strategy:** Climate data quant analysis
- **Edge:** 5% minimum
- **Conviction:** 65% minimum
- **Approach:** Historical patterns, anomaly detection

**2. MorganStanley Weather (Technical)**
- **Strategy:** Meteorological technical analysis
- **Edge:** 4% minimum
- **Conviction:** 60% minimum
- **Approach:** Trend analysis, pattern recognition

**3. Bridgewater Weather (Risk)**
- **Strategy:** Weather impact risk analysis
- **Edge:** 3% minimum
- **Conviction:** 55% minimum
- **Approach:** Correlation analysis, hedging

---

## Reallocation Rules

### Weekly Reallocation (Within Themes)

**Timing:** Every Sunday at 00:00 UTC

**Process:**
1. Calculate each agent's 7-day performance
2. Assign allocation percentages:
   - **Top Performer** (≥60% win rate, ≥5% profit): 40% of theme capital
   - **Good Performer** (≥50% win rate, ≥5% profit): 35% of theme capital
   - **Underperformer** (<50% win rate OR <5% profit): 25% of theme capital
3. Redistribute theme capital among agents
4. Apply minimum capital constraints ($100 per agent)

**Theme Capital Adjustments:**
- **Winner** (≥5% profit, ≥55% win rate): +10% capital
- **Underperformer** (negative profit): -5% capital
- **Probation** (2+ losing weeks): -20% capital

### Monthly Reallocation (Between Themes)

**Timing:** 1st of each month at 00:00 UTC

**Process:**
1. Calculate each theme's 30-day performance
2. Rank themes by profit percentage
3. Apply rotation rules:
   - **Top theme** receives 10% from bottom theme
   - **Bottom theme** with 2+ losing months → PAUSED
4. Rebalance to ensure no theme exceeds 50% of portfolio

### Capital Constraints

- **Minimum Theme Capital:** $500
- **Minimum Agent Capital:** $100
- **Maximum Theme Percentage:** 50% of portfolio
- **Total Portfolio:** $10,000 (constant)

---

## Performance Tracking

### Metrics Tracked

**Per Agent:**
- Win rate (% of profitable trades)
- 7-day P&L ($)
- 30-day P&L ($)
- Total trades
- Sharpe ratio
- Profit percentage (P&L / allocated capital)

**Per Theme:**
- Aggregate win rate (all agents combined)
- 7-day P&L ($)
- 30-day P&L ($)
- Total trades (all agents)
- Active agent count
- Status (ACTIVE, PROBATION, PAUSED)

### Database Tables

**agent_performance:**
```sql
- agent_id: Agent identifier
- theme: Theme name
- timestamp: Trade timestamp
- trade_result: Boolean (win/loss)
- pnl: Profit/loss in dollars
- thesis_id: Reference to thesis
```

**theme_allocations:**
```sql
- theme: Theme name
- capital: Current capital allocation
- allocation_pct: Percentage of portfolio
- week_start: Week starting date
```

---

## Adding New Themes

### Step 1: Define Theme

Create theme specification in `SYSTEM_DESIGN.md`:
```python
THEME_NAME = "example_theme"
THEME_ICON = "🔥"
INITIAL_CAPITAL = 2500.0  # $2,500 (adjust if >4 themes)
```

### Step 2: Create Theme in ThemeManager

Edit `core/theme_portfolio.py`:
```python
self.themes: Dict[str, ThemePortfolio] = {
    "geopolitical": ThemePortfolio("geopolitical", initial_allocation),
    "us_politics": ThemePortfolio("us_politics", initial_allocation),
    "crypto": ThemePortfolio("crypto", initial_allocation),
    "weather": ThemePortfolio("weather", initial_allocation),
    "example_theme": ThemePortfolio("example_theme", initial_allocation),  # NEW
}
```

### Step 3: Add Agents

Create 2-3 agents for the theme (see "Adding New Agents" below).

### Step 4: Update Dashboard

Add theme to Command Center dashboards:
- `command-center/app/trading/themes/page.tsx`
- `command-center/lib/supabase/trading.ts`

Add theme icon to icon mapping:
```typescript
const themeIcons: Record<string, string> = {
  geopolitical: "🌍",
  us_politics: "🇺🇸",
  crypto: "₿",
  weather: "🌦️",
  example_theme: "🔥",  // NEW
}
```

---

## Adding New Agents

### Step 1: Create Agent Class

Create new file `agents/example_agent.py`:
```python
from agents.base import BaseAgent
from models import Market, Thesis

class ExampleAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="example_agent",
            theme="example_theme",
            mandate="Detailed description of agent strategy"
        )
        self.min_edge = 0.04  # 4% minimum edge
        self.min_conviction = 0.65  # 65% minimum conviction
    
    def generate_thesis(self, market: Market, news: List, odds_history: List) -> Optional[Thesis]:
        """Generate thesis for a single market."""
        # Your analysis logic here
        # Return Thesis object or None
        pass
    
    def update_theses(self) -> List[Thesis]:
        """Update all theses for this agent."""
        # Fetch markets, generate theses
        # Return list of Thesis objects
        pass
```

### Step 2: Register Agent

Edit `main.py`:
```python
from agents.example_agent import ExampleAgent

# In initialize_agents():
if ExampleAgent:
    try:
        agent = ExampleAgent()
        all_agent_instances.append(agent)
        theme_manager.add_agent_to_theme("example_theme", agent.agent_id)
        print(f"✓ ExampleAgent")
    except Exception as e:
        print(f"⚠️ ExampleAgent failed: {e}")
```

### Step 3: Create Tests

Create `tests/test_example_agents.py`:
```python
def test_agent_initialization():
    agent = ExampleAgent()
    assert agent.agent_id == "example_agent"
    assert agent.theme == "example_theme"
    assert agent.min_edge >= 0.03
    
def test_thesis_generation():
    agent = ExampleAgent()
    theses = agent.update_theses()
    # Verify theses structure
```

### Step 4: Update Documentation

- Add agent to `SYSTEM_DESIGN.md`
- Update this guide with agent specialization
- Document strategy and thresholds

---

## Dashboard Usage

### Accessing Dashboards

**Command Center URL:** `http://localhost:3000` (or production URL)

**Theme Dashboard:** `/trading/themes`
- View all 4 theme performance cards
- See capital allocation breakdown
- Track historical allocation over 12 weeks
- Monitor theme status (ACTIVE/PROBATION/PAUSED)

**Agent Dashboard:** `/trading/agents`
- View agent leaderboard (sortable)
- Filter by theme
- See top performer highlight
- Track win rate distribution
- Compare performance by theme

### Key Metrics

**On Theme Cards:**
- Current capital allocation
- 7-day and 30-day P&L
- Aggregate win rate
- Number of active agents
- Theme status badge

**On Agent Leaderboard:**
- Rank (with color coding)
- Agent name and theme
- Win rate percentage
- 7-day P&L
- Total trades executed
- Capital allocation

### Interpreting Performance

**Win Rate:**
- ≥60%: Excellent (top performer)
- 50-59%: Good (solid performance)
- 40-49%: Acceptable (room for improvement)
- <40%: Poor (probation risk)

**Profit Percentage:**
- ≥5% weekly: Strong performance
- 2-5%: Moderate performance
- 0-2%: Weak performance
- <0%: Losing (reallocation triggered)

**Theme Status:**
- 🟢 **ACTIVE:** Normal operation
- 🟡 **PROBATION:** 2 losing weeks (capital reduced 20%)
- 🔴 **PAUSED:** 2+ losing months (capital reallocated)

---

## Troubleshooting

### Problem: Agent not generating theses

**Possible Causes:**
- Database connection issue
- No markets match agent criteria
- Edge threshold too high
- Market data stale

**Solutions:**
1. Check database connection: `clawdbot status`
2. Lower min_edge temporarily for testing
3. Verify markets table has recent data
4. Check agent logs in event_log table

### Problem: Reallocation not happening

**Possible Causes:**
- Scheduler not running
- No performance data in database
- Theme has no agents registered

**Solutions:**
1. Verify scheduler is active: Check orchestrator logs
2. Manually trigger: `orchestrator.weekly_reallocation_check()`
3. Check agent_performance table for trades
4. Verify agents registered to themes in theme_allocations table

### Problem: Dashboard showing "No data"

**Possible Causes:**
- No trades executed yet
- Database query failing
- Missing agent_performance records

**Solutions:**
1. Execute some test trades
2. Check Supabase connection in Command Center
3. Verify agent_performance table exists and has data
4. Check browser console for errors

### Problem: Theme stuck in PROBATION

**Possible Causes:**
- Agents consistently underperforming
- Markets not favorable
- Agent thresholds too conservative

**Solutions:**
1. Review agent performance in dashboard
2. Adjust agent min_edge / min_conviction
3. Add more aggressive agents to theme
4. Manually reset status (if warranted)
5. Let system run longer (needs winning week to exit probation)

---

## Best Practices

### Capital Management

1. **Don't over-allocate:** Keep max theme at 50% of portfolio
2. **Respect minimums:** Never reduce agent below $100
3. **Let it run:** Give agents 2-4 weeks before judging performance
4. **Monitor weekly:** Review dashboards every Sunday after reallocation

### Agent Design

1. **Differentiation:** Each theme needs distinct strategies
2. **Thresholds:** Set min_edge at 3-5% for quality over quantity
3. **Conviction:** Require 55-70% conviction to avoid noise
4. **Backtesting:** Test agents on historical data before deployment

### Performance Tracking

1. **Track everything:** Every trade should be logged to agent_performance
2. **Weekly review:** Check agent leaderboard for surprises
3. **Monthly audit:** Verify capital allocations match expectations
4. **Document changes:** Note when you add/remove agents or change rules

---

## Summary

The Theme Portfolio System provides:
- ✅ **Automated capital allocation** based on performance
- ✅ **Risk management** through probation and pause mechanisms
- ✅ **Diversification** across 4 uncorrelated themes
- ✅ **Scalability** to add new themes and agents easily
- ✅ **Transparency** via comprehensive dashboards
- ✅ **Backtesting** framework for validation

**Current Status:**
- 4 themes active
- 12 institutional agents operational
- Weekly/monthly reallocation scheduled
- Full dashboard visualization available
- Production-ready system

---

**For Questions:**
- Review `SYSTEM_DESIGN.md` for architecture details
- Check `README.md` for setup instructions
- See `tests/` for usage examples
- Consult code comments in `core/theme_portfolio.py`

**Last Updated:** 2026-03-02 01:05 UTC
