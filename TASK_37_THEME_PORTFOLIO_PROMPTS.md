# TASK 37: Theme-Based Portfolio System - Execution Prompts

**Goal:** Transform the Polymarket trading bot into a multi-theme, multi-agent hedge fund structure with institutional-grade research adapted for prediction markets.

**System Design:**
- 4 themes: Geopolitical, US Politics, Crypto, Weather
- 11 agents total (2-3 per theme)
- Performance tracking with weekly/monthly reallocation
- Institutional analysis styles (Goldman, Morgan Stanley, Renaissance, etc.)

---

## PHASE 1: Theme Portfolio Foundation (4 hours)

**Prompt:**
```
Build the theme-based portfolio infrastructure:

1. **Create `core/theme_portfolio.py`:**
   - ThemePortfolio class:
     - Properties: name, initial_capital, current_capital, agents[], weekly_pnl[], monthly_pnl[], losing_weeks, status
     - Methods:
       - add_agent(agent) - register agent to theme
       - calculate_performance() - compute win rate, P&L, Sharpe for theme
       - get_agent_allocations() - distribute theme capital among agents by performance
       - reallocate_capital() - update agent allocations based on last week's performance
   - ThemeManager class:
     - Manages all 4 themes (Geopolitical, US Politics, Crypto, Weather)
     - weekly_reallocation() - adjust agent capital within themes
     - monthly_theme_rotation() - pause/boost themes based on 30-day performance
     - get_theme_leaderboard() - rank themes by performance

2. **Create `core/performance_tracker.py`:**
   - PerformanceTracker class:
     - track_trade(agent_id, theme, thesis_id, result: bool, pnl: float)
     - get_agent_stats(agent_id, period='7d'|'30d') -> {win_rate, total_pnl, sharpe, trades_count}
     - get_theme_stats(theme_name, period) -> aggregate agent performance
     - get_leaderboard(period) -> ranked list of all agents
     - trigger_weekly_reallocation() -> identify winners/losers for capital adjustment
   - Store in new database table: agent_performance
     - agent_id, theme, timestamp, trade_result, pnl, thesis_id

3. **Update `schema.sql`:**
   - Add agent_performance table:
     ```sql
     CREATE TABLE agent_performance (
       id BIGSERIAL PRIMARY KEY,
       agent_id TEXT NOT NULL,
       theme TEXT NOT NULL,
       timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
       trade_result BOOLEAN NOT NULL,
       pnl DECIMAL(15,2) NOT NULL,
       thesis_id UUID,
       created_at TIMESTAMPTZ DEFAULT NOW()
     );
     CREATE INDEX idx_agent_performance_agent_id ON agent_performance(agent_id);
     CREATE INDEX idx_agent_performance_theme ON agent_performance(theme);
     CREATE INDEX idx_agent_performance_timestamp ON agent_performance(timestamp DESC);
     ```
   - Add theme_allocations table:
     ```sql
     CREATE TABLE theme_allocations (
       id SERIAL PRIMARY KEY,
       theme TEXT NOT NULL,
       capital DECIMAL(15,2) NOT NULL,
       allocation_pct DECIMAL(5,2) NOT NULL,
       week_start DATE NOT NULL,
       created_at TIMESTAMPTZ DEFAULT NOW()
     );
     CREATE INDEX idx_theme_allocations_week ON theme_allocations(week_start DESC);
     ```

4. **Create reallocation rules config:**
   - File: `config/reallocation_rules.py`
   - Weekly rules:
     - Win rate ≥60% AND profit ≥5% → +40% capital
     - Win rate ≥50% AND profit ≥5% → +35% capital
     - Win rate <50% OR profit <0% → +25% capital
   - Probation rules:
     - 2 consecutive losing weeks → reduce theme allocation -20%
     - Agent win rate <40% for 2 weeks → reduce to minimum allocation (10% of theme capital)
   - Monthly rules:
     - Theme losing 2+ months → pause (reallocate to winners)
     - Top theme gets +10% from bottom theme

**Deliverables:**
- core/theme_portfolio.py (ThemePortfolio + ThemeManager classes)
- core/performance_tracker.py (tracking + leaderboard logic)
- Updated schema.sql with new tables
- config/reallocation_rules.py
- All with type hints, docstrings, and unit tests

**Test:**
- Create 4 ThemePortfolio instances
- Add mock agents to each
- Simulate trades and verify performance calculation
- Run weekly_reallocation() and verify capital shifts

When complete, commit with "TASK 37 Phase 1: Theme portfolio foundation" and notify me.
```

---

## PHASE 2: Institutional Agent Prompts (Geopolitical) (3 hours)

**Prompt:**
```
Create the first 3 institutional agents for the Geopolitical theme, adapting institutional analysis prompts to prediction markets:

1. **Create `agents/twosigma_geo.py` (TwoSigmaGeoAgent):**
   - Inherits from BaseAgent
   - agent_id = "twosigma_geo"
   - theme = "geopolitical"
   - Adapted "Two Sigma Macro Market Outlook" prompt:
     - Focus: Economic indicators → geopolitical event catalysts
     - Assess: GDP growth, unemployment, inflation → conflict escalation indicators, diplomatic tensions, sanction impacts
     - Federal Reserve analysis → Central bank policy impacts on geopolitical markets
     - Market breadth → Prediction market sentiment across related geopolitical events
     - Sentiment indicators → News sentiment, social media trends, insider trading patterns
   - generate_thesis(market) method:
     - Analyzes macro context for geopolitical market
     - Returns thesis with macro-driven conviction score
   - System prompt template (in docstring):
     ```
     You are a senior macro strategist at Two Sigma analyzing geopolitical prediction markets.
     
     For each market, assess:
     1. Economic context: How do current economic indicators (GDP, inflation, unemployment) affect this geopolitical outcome?
     2. Central bank policy: Is Fed/ECB/PBOC policy creating conditions that make this outcome more/less likely?
     3. Cross-market signals: Are related prediction markets pricing in similar or divergent outcomes?
     4. Sentiment analysis: What are news sentiment, social media trends, and institutional positioning telling us?
     5. Seasonal/historical patterns: What does historical data say about similar geopolitical events?
     
     Output format:
     - Fair value estimate (0-100%)
     - Conviction (0-1)
     - Key macro drivers (list)
     - Bull case / Bear case
     - 7-day and 30-day outlook
     ```

2. **Create `agents/goldman_geo.py` (GoldmanGeoAgent):**
   - agent_id = "goldman_geo"
   - theme = "geopolitical"
   - Adapted "Goldman Sachs Fundamental Analysis" prompt:
     - Business model → Event outcome model (who benefits, who loses)
     - Revenue streams → Geopolitical actor incentives and capabilities
     - Balance sheet health → Nation/actor resources (military, economic, diplomatic)
     - Competitive advantages → Strategic positioning, alliances, leverage
     - Management quality → Leadership assessment (decision-making track record)
     - Valuation → Is current market price fair given fundamental analysis?
   - System prompt:
     ```
     You are a senior geopolitical analyst at Goldman Sachs evaluating prediction markets.
     
     For each geopolitical market, analyze:
     1. Outcome model: What are the fundamental drivers that determine this outcome?
     2. Actor analysis: Who are the key players (nations, leaders, organizations)? What are their capabilities, incentives, constraints?
     3. Resource assessment: What military, economic, diplomatic resources do actors have? How does this affect outcome probability?
     4. Strategic positioning: Who has leverage? What alliances or dependencies matter?
     5. Leadership quality: Historical decision-making patterns of key leaders
     6. Timeline analysis: What are critical dates, events, or thresholds that will determine the outcome?
     
     Output:
     - Fair value with confidence interval
     - Bull case (outcome happens) with probability
     - Bear case (outcome doesn't happen) with probability
     - Key catalysts to watch
     - 12-month outlook
     ```

3. **Create `agents/bridgewater_geo.py` (BridgewaterGeoAgent):**
   - agent_id = "bridgewater_geo"
   - theme = "geopolitical"
   - Adapted "Bridgewater Risk Assessment" prompt:
     - Volatility profile → Outcome probability volatility over time
     - Correlation analysis → How this market correlates with other geopolitical markets
     - Maximum drawdown → Worst-case scenario impact
     - Sector concentration → Geographic/thematic concentration in portfolio
     - Stress test → What happens if this market is mispriced by 20%?
     - Hedging recommendation → Related markets to hedge exposure
   - System prompt:
     ```
     You are a senior risk analyst at Bridgewater Associates evaluating geopolitical prediction markets.
     
     For each market, assess:
     1. Volatility: How much has the market price fluctuated? Is it stable or erratic?
     2. Correlation: How does this market move relative to other geopolitical markets in the portfolio?
     3. Drawdown risk: What's the maximum loss if our thesis is wrong?
     4. Geographic concentration: Are we overexposed to one region (Russia, Middle East, Asia)?
     5. Stress testing: How does this position perform in:
        - Escalation scenario (war, sanctions, diplomatic breakdown)
        - De-escalation scenario (peace talks, treaties, normalization)
     6. Hedging: What related markets could we take opposite positions in to reduce risk?
     
     Output:
     - Risk-adjusted fair value
     - Correlation to portfolio (0-1)
     - Maximum drawdown estimate
     - Recommended hedge positions
     - Risk score (1-10)
     ```

4. **Update `main.py`:**
   - Import new agents: TwoSigmaGeoAgent, GoldmanGeoAgent, BridgewaterGeoAgent
   - Register to "geopolitical" theme in ThemeManager
   - Pass theme and agent_id to each agent constructor

**Deliverables:**
- agents/twosigma_geo.py
- agents/goldman_geo.py
- agents/bridgewater_geo.py
- All with adapted institutional prompts in docstrings
- update_theses() methods that call LLM with system prompt + market data
- Type hints, error handling, logging

**Test:**
- Instantiate each agent
- Call update_theses() on sample geopolitical markets
- Verify thesis generation with institutional analysis style
- Check that theses are tagged with correct agent_id and theme

When complete, commit with "TASK 37 Phase 2: Geopolitical institutional agents" and notify me.
```

---

## PHASE 3: US Politics Agents (3 hours)

**Prompt:**
```
Create 3 institutional agents for the US Politics theme:

1. **Create `agents/renaissance_politics.py` (RenaissancePoliticsAgent):**
   - Adapted "Renaissance Technologies Quantitative Screener"
   - Multi-factor analysis:
     - Polling factors: Aggregate polls, poll quality weighting, historical poll accuracy
     - Momentum factors: Polling trend direction, prediction market momentum, fundraising trends
     - Quality factors: Candidate fundamentals (approval ratings, name recognition, debate performance)
     - Sentiment factors: Social media sentiment, endorsement patterns, media coverage tone
   - System prompt focused on statistical pattern detection in political markets

2. **Create `agents/jpmorgan_politics.py` (JPMorganPoliticsAgent):**
   - Adapted "JPMorgan Earnings Analyzer"
   - Event catalyst analysis:
     - Debate analysis: Pre-debate expectations, post-debate polling impact, historical debate effects
     - Primary results: State-by-state breakdown, delegate math, momentum shifts
     - Policy announcements: Market reaction to campaign platform changes
     - Scandal/news events: Historical impact of similar events on candidate odds
   - System prompt focused on pre/post-event analysis patterns

3. **Create `agents/goldman_politics.py` (GoldmanPoliticsAgent):**
   - Adapted "Goldman Sachs Fundamental Analysis"
   - Candidate fundamentals:
     - Electoral map analysis: State-by-state probabilities, swing state dynamics
     - Demographics: Voter bloc breakdown, historical turnout patterns
     - Campaign organization: Ground game strength, fundraising efficiency, volunteer network
     - Endorsement quality: Party establishment, labor unions, influential figures
   - System prompt focused on fundamental political analysis

**Deliverables:**
- agents/renaissance_politics.py
- agents/jpmorgan_politics.py
- agents/goldman_politics.py
- Register in ThemeManager under "us_politics" theme

When complete, commit with "TASK 37 Phase 3: US Politics agents" and notify me.
```

---

## PHASE 4: Crypto Agents (3 hours)

**Prompt:**
```
Create 3 institutional agents for the Crypto theme:

1. **Create `agents/morganstanley_crypto.py` (MorganStanleyCryptoAgent):**
   - Adapted "Morgan Stanley Technical Analysis Dashboard"
   - Apply technical analysis to crypto prediction market odds:
     - Trend analysis: Odds trend on 1-day, 7-day, 30-day timeframes
     - Support/resistance: Price levels where odds historically bounce or stall
     - Moving averages: 7-day, 30-day odds moving averages
     - RSI: Relative strength index applied to odds changes
     - Volume analysis: Is betting volume confirming or contradicting odds movement?
   - System prompt focused on chart patterns in prediction market odds

2. **Create `agents/renaissance_crypto.py` (RenaissanceCryptoAgent):**
   - Adapted "Renaissance Quantitative Screener"
   - Multi-factor crypto analysis:
     - On-chain factors: Transaction volume, active addresses, exchange inflows/outflows
     - Market factors: Spot price momentum, futures basis, options implied volatility
     - Sentiment factors: Social media mentions, Fear & Greed Index, institutional flow
     - Correlation factors: BTC correlation to equities, gold, DXY
   - System prompt focused on quantitative crypto market analysis

3. **Create `agents/citadel_crypto.py` (CitadelCryptoAgent):**
   - Adapted "Citadel Sector Rotation Strategist"
   - Crypto cycle positioning:
     - Market cycle: Bull, bear, accumulation, distribution phase detection
     - Fed policy impact: Rate hikes → crypto bearish, rate cuts → crypto bullish
     - Regulatory cycle: Clarity → bullish, crackdowns → bearish
     - Altcoin rotation: BTC dominance trends, altcoin season signals
   - System prompt focused on crypto macro cycles

**Deliverables:**
- agents/morganstanley_crypto.py
- agents/renaissance_crypto.py
- agents/citadel_crypto.py
- Register in ThemeManager under "crypto" theme

When complete, commit with "TASK 37 Phase 4: Crypto agents" and notify me.
```

---

## PHASE 5: Weather Agents (3 hours)

**Prompt:**
```
Create 2-3 institutional agents for the Weather theme:

1. **Create `agents/renaissance_weather.py` (RenaissanceWeatherAgent):**
   - Adapted "Renaissance Quantitative Screener"
   - Multi-factor weather analysis:
     - Historical data: 10-year average temperatures, precipitation patterns for location/date
     - Climate models: NOAA, ECMWF, GFS model consensus
     - Seasonal factors: El Niño/La Niña status, historical analog years
     - Satellite data: Current weather patterns, jet stream positioning
     - Anomaly detection: Is this year tracking normal, hot, or cold vs baseline?
   - System prompt focused on quantitative meteorological analysis

2. **Create `agents/morganstanley_weather.py` (MorganStanleyWeatherAgent):**
   - Adapted "Morgan Stanley Technical Analysis"
   - Technical patterns in weather futures/prediction markets:
     - Temperature trend analysis: Is temperature trending up/down vs historical average?
     - Moving averages: 7-day, 30-day temperature moving averages
     - Momentum: Is the trend accelerating or decelerating?
     - Pattern recognition: Heatwave buildup patterns, cold snap precursors
   - System prompt focused on technical weather pattern analysis

3. **Create `agents/bridgewater_weather.py` (BridgewaterWeatherAgent):**
   - Adapted "Bridgewater Risk Assessment"
   - Weather market risk analysis:
     - Geographic correlation: Hurricane → power outage → agricultural impact chains
     - Seasonal concentration: Are we overexposed to summer weather markets?
     - Model uncertainty: How much do weather models disagree? (Higher disagreement = higher uncertainty)
     - Hedging: Related weather markets to offset risk
   - System prompt focused on weather market risk management

**Deliverables:**
- agents/renaissance_weather.py
- agents/morganstanley_weather.py
- agents/bridgewater_weather.py (optional, if time permits)
- Register in ThemeManager under "weather" theme

When complete, commit with "TASK 37 Phase 5: Weather agents" and notify me.
```

---

## PHASE 6: Orchestrator Integration (3 hours)

**Prompt:**
```
Update the orchestrator to manage theme-based portfolio with weekly/monthly reallocation:

1. **Update `core/orchestrator.py`:**
   - Add ThemeManager initialization in __init__
   - Initialize all 11 agents and register to themes
   - Modify run_cycle() to:
     - Route thesis generation by theme
     - Tag each thesis with agent_id + theme
     - Track trade results per agent/theme
   - Add weekly_reallocation_check():
     - Runs every Sunday at midnight (use cron or scheduler)
     - Calls ThemeManager.weekly_reallocation()
     - Logs capital changes to event_log
   - Add monthly_theme_review():
     - Runs 1st of month at midnight
     - Calls ThemeManager.monthly_theme_rotation()
     - Pauses underperforming themes, boosts winners
     - Logs theme status changes

2. **Create `core/scheduler.py`:**
   - CronScheduler class using APScheduler
   - Schedule weekly reallocation (Sundays 00:00 UTC)
   - Schedule monthly review (1st of month 00:00 UTC)
   - Schedule daily IC memo generation

3. **Update execution flow:**
   - When a thesis is executed:
     - Record to agent_performance table
     - Update PerformanceTracker with result
     - Tag position with agent_id + theme in positions table

4. **Add schema updates:**
   - Add agent_id and theme columns to positions table:
     ```sql
     ALTER TABLE positions ADD COLUMN agent_id TEXT;
     ALTER TABLE positions ADD COLUMN theme TEXT;
     CREATE INDEX idx_positions_agent_id ON positions(agent_id);
     CREATE INDEX idx_positions_theme ON positions(theme);
     ```

**Deliverables:**
- Updated core/orchestrator.py with theme management
- core/scheduler.py for cron jobs
- Updated positions table schema
- Integration tests for reallocation logic

When complete, commit with "TASK 37 Phase 6: Orchestrator theme integration" and notify me.
```

---

## PHASE 7: Dashboard Enhancements (4 hours)

**Prompt:**
```
Add theme and agent performance dashboards to Command Center:

1. **Create `app/trading/themes/page.tsx`:**
   - Server Component fetching theme performance data
   - 4 theme cards showing:
     - Theme name + icon
     - Current capital allocation
     - 7-day P&L ($ and %)
     - 30-day P&L
     - Win rate (all agents aggregated)
     - Agent count
     - Status badge (Active, Probation, Paused)
   - Capital allocation chart (pie chart showing theme distribution)
   - Historical allocation chart (area chart showing capital flow over time)

2. **Create `app/trading/agents/page.tsx`:**
   - Server Component fetching all agent performance
   - Agent leaderboard table:
     - Rank, Agent Name, Theme, Win Rate, 7d P&L, 30d P&L, Total Trades, Capital Allocation
     - Sortable by any column
     - Color-coded ranks (top 3 = green, bottom 3 = red)
   - Filter by theme dropdown
   - "Top Performer" badge on #1 agent

3. **Create `app/trading/components/ThemeCard.tsx`:**
   - Display theme performance summary
   - Shows capital trend sparkline (last 30 days)
   - Click to drill down into theme's agents

4. **Create `app/trading/components/AgentLeaderboard.tsx`:**
   - Table of all agents with performance metrics
   - Expandable rows showing recent trades
   - Link to agent-specific thesis history

5. **Extend `lib/supabase/trading.ts`:**
   - Add getThemePerformance(theme_name, period) query
   - Add getAgentPerformance(agent_id, period) query
   - Add getCapitalAllocationHistory() query

6. **Update sidebar:**
   - Add "Themes" and "Agents" to Trading subsections

**Deliverables:**
- app/trading/themes/page.tsx
- app/trading/agents/page.tsx
- ThemeCard and AgentLeaderboard components
- Updated trading.ts with new queries
- Updated sidebar navigation

When complete, commit with "TASK 37 Phase 7: Theme dashboard complete" and notify me.
```

---

## PHASE 8: Testing & Polish (2 hours)

**Prompt:**
```
Final testing and polish for theme-based portfolio system:

1. **Create test suite:**
   - tests/test_theme_portfolio.py - test ThemePortfolio class
   - tests/test_performance_tracker.py - test tracking logic
   - tests/test_reallocation.py - test weekly/monthly reallocation
   - tests/test_institutional_agents.py - test all 11 agents generate valid theses

2. **Integration test:**
   - Create test_theme_system_integration.py:
     - Simulate 4 weeks of trading across all themes
     - Verify capital reallocation happens correctly
     - Verify theme probation triggers after 2 losing weeks
     - Verify agent capital distribution within themes

3. **Documentation:**
   - Update SYSTEM_DESIGN.md with theme portfolio architecture
   - Create THEME_PORTFOLIO_GUIDE.md:
     - Explanation of theme system
     - Agent specializations
     - Reallocation rules
     - How to add new themes/agents
   - Update README.md with new architecture overview

4. **Polish:**
   - Add loading states to theme/agent dashboards
   - Add empty states ("No trades yet for this agent")
   - Add error handling for missing performance data
   - Ensure all theme/agent pages are mobile responsive

**Deliverables:**
- Full test suite passing
- Updated documentation
- Polished dashboard UI
- Build successful

When complete:
1. Run full test suite: `pytest tests/`
2. Run build: `npm run build` in command-center
3. Commit with "TASK 37 Phase 8: Testing & polish complete - Theme system ready"
4. Create summary document showing:
   - All 11 agents working
   - Theme performance tracking functional
   - Reallocation logic tested
   - Dashboard pages rendering

This completes TASK 37. 🎉
```

---

## Quick Reference

**Execution Order:**
1. Phase 1: Theme portfolio foundation (infrastructure)
2. Phase 2: Geopolitical agents (first 3 agents)
3. Phase 3: US Politics agents
4. Phase 4: Crypto agents
5. Phase 5: Weather agents
6. Phase 6: Orchestrator integration (connect everything)
7. Phase 7: Dashboard enhancements (UI for themes/agents)
8. Phase 8: Testing & polish (production-ready)

**Total Time Estimate:** 25 hours (3-4 days focused work)

**Completion Criteria:**
- All 11 institutional agents generating theses
- 4 themes tracking performance independently
- Weekly agent capital reallocation working
- Monthly theme rotation logic functional
- Dashboard showing theme/agent leaderboards
- All tests passing
- Documentation complete
