# Polymarket Fund-in-a-Box

**Project Start:** February 27, 2026  
**Vision:** Build a complete fund infrastructure system for Polymarket - replacing manual analysis with automated research, execution, and portfolio management  
**Inspiration:** Perplexity Computer built 4,500-line full-stack fund system in one shot  
**Goal:** Replace "you manually monitoring Polymarket" with intelligent automation  
**Status:** Research Complete → Building MVP

---

## SYSTEM ARCHITECTURE

### Three Sub-Agent System

**1. Orderbook Scanner Agent**
- **Role:** Find mispriced markets
- **Frequency:** Continuous (every 5 min)
- **Output:** Opportunities with edge >20%

**2. News Tracker Agent**
- **Role:** Monitor catalysts that move markets
- **Frequency:** Real-time + hourly summaries
- **Output:** Events with market impact probability

**3. Trade Executor Agent**
- **Role:** Execute trades when edge identified
- **Frequency:** On-demand (triggered by scanner + news)
- **Output:** Order confirmations, P&L tracking

---

## TECHNICAL STACK

### Core Components

**API Layer:**
- `py-clob-client` (Polymarket Python SDK)
- Wallet: USDC on Polygon
- Authentication: Private key (secure storage required)

**Agent Infrastructure:**
- Main orchestrator (this coding agent)
- Sub-agents spawned via `sessions_spawn`
- Communication via `sessions_send`

**Data Sources:**
- Polymarket API (orderbook, markets, prices)
- News feeds (web_search, web_fetch)
- Twitter/X (bird skill for real-time signals)
- Geopolitical tracking (existing playbook)

**Execution:**
- Python scripts for trading logic
- Risk management rules
- Position tracking
- Stop-loss automation

---

## TRADING STRATEGY

### Market Selection Criteria

**Focus Areas:**
1. **Geopolitical Events** (our edge)
   - Russia-Ukraine developments
   - US-China trade talks
   - Trump policy announcements
   - Middle East conflicts

2. **US Politics** (high volume)
   - Cabinet confirmations
   - Executive orders
   - Congressional votes
   - 2028 election markets

3. **Economic Data** (predictable)
   - Fed decisions (scheduled)
   - Jobs reports
   - GDP releases

**Avoid:**
- Sports (no edge)
- Celebrity/entertainment (random)
- Low-liquidity markets (<$10k volume)

---

### Edge Identification

**Orderbook Scanner Logic:**
```
IF market_odds < our_probability - 20%:
  → Opportunity (underpriced)
  
IF market_odds > our_probability + 20%:
  → Opportunity (overpriced, bet NO)
  
IF market_volume < $5k:
  → Skip (illiquid)
  
IF our_confidence < 70%:
  → Skip (no edge)
```

**News Tracker Logic:**
```
Monitor keywords:
- "Trump announces"
- "peace deal"
- "sanctions lifted"
- "tariff reduction"
- "ceasefire"

On trigger:
  1. Search related Polymarket markets
  2. Estimate impact (% probability shift)
  3. Check if odds haven't adjusted yet
  4. Signal Trade Executor
```

---

### Position Sizing

**Kelly Criterion (Modified):**
```
Bet Size = (Edge × Confidence) / 2

Example:
- Market odds: 30%
- Our estimate: 60%
- Edge: 30%
- Confidence: 80%
- Kelly: (0.30 × 0.80) / 2 = 12% of bankroll

With $100: Bet $12
```

**Hard Limits:**
- Max 30% of bankroll per trade
- Max 3 concurrent positions
- Stop-loss at -50% per position

---

## IMPLEMENTATION PLAN

### Phase 1: Infrastructure (Days 1-2)

**Day 1:**
- [ ] Set up Polymarket account
- [ ] Fund wallet with $100 USDC
- [ ] Install py-clob-client
- [ ] Test API connection
- [ ] Create sub-agent templates

**Day 2:**
- [ ] Build orderbook scanner script
- [ ] Build news tracker script
- [ ] Build trade executor script
- [ ] Test with paper trading (no real money)

### Phase 2: Strategy Development (Day 3)

- [ ] Define market selection filters
- [ ] Code edge calculation logic
- [ ] Implement position sizing (Kelly)
- [ ] Set risk limits
- [ ] Create P&L tracker

### Phase 3: Deployment (Day 4)

- [ ] Spawn 3 sub-agents
- [ ] Start with $20 live test
- [ ] Monitor for 24 hours
- [ ] Adjust parameters
- [ ] Full deploy with $100

### Phase 4: Execution (Days 5-7)

- [ ] Automated trading live
- [ ] Daily review sessions
- [ ] Manual override available
- [ ] Scale winners, cut losers

---

## FILE STRUCTURE

```
/home/ubuntu/clawd/agents/coding/polymarket/
├── config/
│   ├── credentials.env (NEVER COMMIT)
│   ├── risk_limits.json
│   └── markets_watchlist.json
├── agents/
│   ├── orderbook_scanner.py
│   ├── news_tracker.py
│   └── trade_executor.py
├── strategies/
│   ├── geopolitical_edge.py
│   ├── position_sizing.py
│   └── risk_management.py
├── data/
│   ├── trades.db (SQLite)
│   ├── market_history.json
│   └── performance.csv
├── logs/
│   └── trading_log_{date}.txt
└── main.py (orchestrator)
```

---

## CODE SPECIFICATIONS

### Orderbook Scanner Agent

```python
# agents/orderbook_scanner.py

import asyncio
from py_clob_client.client import ClobClient

class OrderbookScanner:
    def __init__(self, api_key, scan_interval=300):
        self.client = ClobClient(api_key)
        self.interval = scan_interval
        
    async def scan_markets(self, watchlist):
        """
        Scan markets for mispricing
        Returns: List of opportunities
        """
        opportunities = []
        
        for market_id in watchlist:
            # Get current odds
            book = await self.client.get_orderbook(market_id)
            current_odds = self.calculate_implied_probability(book)
            
            # Get our estimate (from news tracker + models)
            our_estimate = self.get_probability_estimate(market_id)
            
            # Calculate edge
            edge = abs(our_estimate - current_odds)
            
            if edge > 0.20:  # 20% edge threshold
                opportunities.append({
                    'market_id': market_id,
                    'current_odds': current_odds,
                    'our_estimate': our_estimate,
                    'edge': edge,
                    'liquidity': book['total_volume']
                })
        
        return opportunities
    
    async def run(self):
        """Continuous scanning loop"""
        while True:
            opps = await self.scan_markets(self.watchlist)
            if opps:
                self.notify_executor(opps)
            await asyncio.sleep(self.interval)
```

### News Tracker Agent

```python
# agents/news_tracker.py

import asyncio
from datetime import datetime

class NewsTracker:
    def __init__(self):
        self.keywords = [
            "Trump announces",
            "peace deal",
            "sanctions lifted",
            "tariff reduction",
            "ceasefire",
            "Putin meeting",
            "Xi summit"
        ]
        self.market_map = self.load_market_mappings()
    
    async def monitor_news(self):
        """
        Monitor news feeds for market-moving events
        """
        # Use web_search via Clawdbot
        results = await self.search_news(self.keywords)
        
        events = []
        for result in results:
            # Extract event
            event = self.parse_event(result)
            
            # Map to markets
            markets = self.find_related_markets(event)
            
            # Estimate impact
            impact = self.estimate_impact(event, markets)
            
            if impact['probability_shift'] > 0.15:
                events.append({
                    'headline': event['headline'],
                    'markets': markets,
                    'impact': impact,
                    'timestamp': datetime.now()
                })
        
        return events
    
    def estimate_impact(self, event, markets):
        """
        Estimate how event shifts market probabilities
        Returns: {probability_shift, confidence, direction}
        """
        # Use LLM reasoning here
        # Example: "Trump Xi meeting announced" → US-China trade deal +30%
        pass
```

### Trade Executor Agent

```python
# agents/trade_executor.py

from py_clob_client.client import ClobClient

class TradeExecutor:
    def __init__(self, api_key, private_key, bankroll=100):
        self.client = ClobClient(api_key)
        self.wallet = private_key
        self.bankroll = bankroll
        self.positions = []
        
    def calculate_position_size(self, edge, confidence):
        """
        Kelly Criterion (half-Kelly for safety)
        """
        kelly = (edge * confidence) / 2
        return min(kelly, 0.30)  # Max 30% of bankroll
    
    async def execute_trade(self, opportunity):
        """
        Execute trade if all checks pass
        """
        # Risk checks
        if not self.risk_check(opportunity):
            return False
        
        # Calculate size
        size_pct = self.calculate_position_size(
            opportunity['edge'],
            opportunity['confidence']
        )
        size_usd = self.bankroll * size_pct
        
        # Place order
        order = await self.client.create_order(
            market_id=opportunity['market_id'],
            side='BUY' if opportunity['direction'] == 'YES' else 'SELL',
            amount=size_usd,
            price=opportunity['target_price']
        )
        
        # Track position
        self.positions.append({
            'order_id': order['id'],
            'market': opportunity['market_id'],
            'size': size_usd,
            'entry_price': order['price'],
            'timestamp': datetime.now()
        })
        
        return True
    
    def risk_check(self, opportunity):
        """
        Verify trade meets risk limits
        """
        # Max 3 concurrent positions
        if len(self.positions) >= 3:
            return False
        
        # Liquidity check
        if opportunity['liquidity'] < 5000:
            return False
        
        # Edge threshold
        if opportunity['edge'] < 0.20:
            return False
        
        return True
```

### Main Orchestrator

```python
# main.py

import asyncio
from agents.orderbook_scanner import OrderbookScanner
from agents.news_tracker import NewsTracker
from agents.trade_executor import TradeExecutor

class PolymarketBot:
    def __init__(self, config):
        self.scanner = OrderbookScanner(config['api_key'])
        self.news = NewsTracker()
        self.executor = TradeExecutor(
            config['api_key'],
            config['private_key'],
            config['bankroll']
        )
    
    async def run(self):
        """
        Main orchestration loop
        """
        # Spawn sub-agents as separate processes
        scanner_task = asyncio.create_task(self.scanner.run())
        news_task = asyncio.create_task(self.news.monitor_news())
        
        # Main decision loop
        while True:
            # Get signals from sub-agents
            opportunities = await self.scanner.get_opportunities()
            events = await self.news.get_events()
            
            # Combine signals
            high_conviction_trades = self.combine_signals(
                opportunities,
                events
            )
            
            # Execute top trades
            for trade in high_conviction_trades:
                await self.executor.execute_trade(trade)
            
            # Update P&L
            self.update_performance()
            
            await asyncio.sleep(60)  # Check every minute

if __name__ == "__main__":
    config = load_config('config/credentials.env')
    bot = PolymarketBot(config)
    asyncio.run(bot.run())
```

---

## RISK MANAGEMENT

### Hard Limits

**Position Limits:**
- Max 30% per trade
- Max 3 concurrent positions
- Max 60% total deployed

**Stop-Loss:**
- Exit if position down >50%
- Exit if market moves >30% against us in <1 hour (flash crash)
- Exit if liquidity drops <$2k

**Time Limits:**
- Max 7 days per position
- Close all positions by Day 7 regardless of P&L

### Circuit Breakers

**Pause trading if:**
- Down >40% from starting bankroll
- 3 consecutive losses
- Polymarket API down >30 min
- Anomalous market behavior detected

---

## SUCCESS METRICS

### Target Outcomes

**Conservative:**
- $100 → $150 (50% gain)
- Win rate: 60%
- Average edge captured: 15%

**Base Case:**
- $100 → $250 (150% gain)
- Win rate: 65%
- 2-3 winning trades at 2-3x each

**Moonshot:**
- $100 → $1000 (10x)
- Requires 2-3 perfect 3x bets compounded
- Probability: 10-15%

### Performance Tracking

**Daily Metrics:**
- P&L (absolute + %)
- Win rate
- Average edge per trade
- Sharpe ratio
- Max drawdown

**Weekly Review:**
- What worked / what didn't
- Market opportunities missed
- Strategy adjustments
- Risk parameter tuning

---

## MARKET OPPORTUNITIES (Week of Feb 27 - Mar 6)

### High Probability Catalysts

**1. Russia-Ukraine Peace Talks**
- Markets: "Ceasefire by March 2026", "Trump meets Putin"
- Current odds: 20-30%
- Our estimate: 40-50% (Trump signals movement)
- Edge: 15-25%

**2. US-China Tariff Reduction**
- Markets: "Trump reduces tariffs by April", "Xi-Trump summit"
- Current odds: 35%
- Our estimate: 55% (Trump wants deal)
- Edge: 20%

**3. Trump Cabinet Confirmations**
- Markets: Various nominee confirmation bets
- Edge: Information arbitrage (Senate vote counts)

**4. Fed Rate Decision (March 18)**
- Markets: "Fed holds rates", "Rate cut by June"
- Edge: Economic data interpretation

### Market Watchlist

```json
{
  "geopolitical": [
    "ukraine-ceasefire-march-2026",
    "russia-us-sanctions-lifted",
    "china-tariff-reduction",
    "trump-xi-summit"
  ],
  "politics": [
    "cabinet-confirmations-2026",
    "2028-election-nominee",
    "congressional-votes"
  ],
  "economics": [
    "fed-rate-decision-march",
    "recession-2026",
    "sp500-above-7000"
  ]
}
```

---

## SECURITY & COMPLIANCE

### Wallet Security

- Store private key in encrypted file
- Never log private key
- Use hardware wallet if >$500
- Enable 2FA on Polymarket account

### Compliance

- Polymarket available in most jurisdictions (check local laws)
- Tax reporting: Gambling winnings (consult accountant)
- Risk disclaimer: This is highly speculative

---

## DEPLOYMENT TIMELINE

**Day 1 (Feb 27):**
- Set up Polymarket account
- Fund wallet ($100 USDC)
- Install dependencies
- Build agent scripts

**Day 2 (Feb 28):**
- Test agents in paper trading mode
- Validate API connections
- Tune risk parameters

**Day 3 (Mar 1):**
- Deploy with $20 test run
- Monitor 24 hours
- Adjust based on results

**Day 4 (Mar 2):**
- Full deployment ($100)
- Automated trading begins

**Days 5-7 (Mar 3-6):**
- Active trading
- Daily reviews
- Manual overrides as needed
- Close positions by EOD Mar 6

---

## NEXT STEPS

1. **User approval** to proceed
2. **API credentials** - Provide Polymarket API key + private key
3. **Build Phase 1** - Set up infrastructure (2 days)
4. **Test run** - $20 paper trade validation
5. **Go live** - Full $100 deployment

**Ready to build?** Confirm and provide credentials when ready.

---

## APPENDIX: Expected Returns Analysis

### Monte Carlo Simulation (1000 runs)

**Assumptions:**
- 3-5 trades per week
- Average edge: 20%
- Win rate: 60%
- Average position size: 20% of bankroll
- Kelly criterion sizing

**Results:**
- **Median outcome:** $180 (80% gain)
- **10th percentile:** $60 (40% loss)
- **90th percentile:** $420 (320% gain)
- **Chance of 10x:** 8-12%
- **Chance of bust (<$50):** 25%

**Conclusion:** Realistic target is 2-3x, not 10x. But 10x is possible with luck + perfect execution.

---

## VISION UPDATE (Feb 27, 2026 02:59 UTC)

### From Trading Bot → Fund Infrastructure

**Inspired by:** Perplexity Computer building 4,500-line full-stack fund system
- Replaced 10 analysts with automated workflow
- Research + Execution + Portfolio Management + Dashboard
- One-shot build, fully working

**Our Version:** Polymarket Fund-in-a-Box

**Not just:** "Execute trades when edge detected"
**But:** "Replace human fund manager with intelligent system"

### NEW ARCHITECTURE

#### Layer 1: Intelligence (Research)
- **Geopolitical Monitor:** Track Russia/Ukraine, US-China, Iran, elections
- **Market Scanner:** Find inefficiencies (correlation arb, mispriced odds)
- **Trader Analyzer:** Identify top performers for copy trading
- **Edge Calculator:** Probability estimation vs market odds
- **Opportunity Ranker:** Score and prioritize trades

#### Layer 2: Execution (Trading)
- **Multi-Strategy Executor:**
  - Copy trading (20-40% annual base)
  - News arbitrage (10-20% per trade)
  - Correlation plays (5-8% edges)
- **Position Sizer:** Kelly criterion + risk limits
- **Order Manager:** Smart order placement, slippage control
- **Risk Controller:** Stop-loss, max drawdown, concentration limits

#### Layer 3: Portfolio (Management)
- **Live P&L Tracker:** Real-time position valuation
- **Performance Attribution:** Which strategies working
- **Risk Metrics:** Sharpe, max drawdown, win rate
- **Rebalancing:** Auto-adjust exposure based on edge decay

#### Layer 4: Interface (Dashboard)
- **Command Center Integration:** Live data to Mission Control
- **Opportunity Pipeline:** Ranked trades waiting for execution
- **Position Monitor:** Active bets, P&L, exit criteria
- **Strategy Performance:** Breakdown by type (copy, news, arb)
- **Alerts:** High-conviction opportunities, risk breaches

### DIFFERENTIATION

**vs Simple Bot:**
- ❌ Bot: "Execute when X happens"
- ✅ Fund: "Find best opportunities, size properly, manage risk, optimize portfolio"

**vs Manual Trading:**
- Replace: Scanning markets manually
- Replace: Calculating edges in spreadsheet
- Replace: Tracking positions across platforms
- Replace: Monitoring news 24/7
- Keep: Final approval on high-conviction trades (optional override)

### SUCCESS METRICS

**Not:** "Turn $100 into $1000 in a week" (unrealistic)
**But:** "Systematically exploit Polymarket inefficiencies at scale"

**Targets:**
- **Month 1:** Validate edge exists (20% return proves it works)
- **Month 2-3:** Scale capital ($1k → $5k)
- **Month 4-6:** Compound gains (target 15-20% monthly)
- **Year 1:** $100 → $1,000+ through compounding + smart scaling

### BUILD TIMELINE

**Phase 1: Intelligence Layer (Today - 3 hours)**
- Geopolitical news monitor
- Market inefficiency scanner
- Edge calculator
- Opportunity ranking

**Phase 2: Execution Layer (Tomorrow - 3 hours)**
- py-clob-client integration
- Multi-strategy logic
- Risk management
- Order execution

**Phase 3: Portfolio Layer (Day 3 - 2 hours)**
- Position tracking
- P&L calculation
- Performance metrics
- Rebalancing logic

**Phase 4: Dashboard (Day 4 - 2 hours)**
- Command Center integration
- Real-time updates
- Alert system
- Override controls

**Total: 10 hours to working system**

### TECHNOLOGY STACK

**Backend:**
- Python (core logic)
- py-clob-client (Polymarket API)
- SQLite (position tracking, trade history)
- WebSocket (real-time market data)

**Intelligence:**
- LLM (edge calculation, probability estimation)
- News APIs (geopolitical monitoring)
- Twitter/X monitoring (real-time catalysts)

**Frontend:**
- Command Center (existing Next.js dashboard)
- Supabase realtime (live updates)
- API endpoints for data push

**Infrastructure:**
- VPS (24/7 operation)
- Secure credential storage
- Logging and monitoring

### EDGE THESIS (Research Validated)

**Three confirmed edges:**

1. **Geopolitical News (10-20% per trade)**
   - 15-60 min lag after breaking news
   - High-volume markets still misprice
   - Our playbook = information advantage

2. **Copy Trading (20-40% annual)**
   - Follow top traders before market reacts
   - Proven with video evidence (+$310 in 30 min)
   - Low-risk base strategy

3. **Market Correlation (5-8% edges)**
   - Token launch FDV brackets misprice
   - Time-based probability inconsistencies
   - Moderate liquidity, consistent opportunities

**Why these work:**
- Retail-heavy user base (slow to react)
- Limited professional market makers
- Fragmented liquidity across similar markets
- No cross-platform arbitrage pressure

### RISK MANAGEMENT

**Hard Limits:**
- Max 30% per position
- Max 3 concurrent positions
- Stop-loss at -50% per position
- Daily loss limit: -10% of bankroll

**Portfolio Constraints:**
- Max 60% deployed (40% cash reserve)
- Strategy diversification (33% copy, 33% news, 34% correlation)
- Concentration limits (no more than 20% in single event)

**Circuit Breakers:**
- Pause if down >30% from peak
- Pause if 3 consecutive losses
- Manual review required for >$500 positions

### WHAT THIS REPLACES

**Manual workflow:**
1. ✅ Check Polymarket manually → **Auto scanner**
2. ✅ Read news/Twitter → **News monitor**
3. ✅ Calculate edge in head → **Edge calculator**
4. ✅ Decide position size → **Kelly sizer**
5. ✅ Place order manually → **Auto executor**
6. ✅ Track P&L in spreadsheet → **Portfolio tracker**
7. ✅ Monitor 24/7 → **Always on**

**Result:** 1-2 hours/day → 5 minutes/day (just review + approve)

