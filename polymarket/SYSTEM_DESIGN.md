# Based Money - System Design Package

**Version:** 1.0  
**Date:** February 27, 2026  
**Target:** Polymarket Fund Operating System

---

## 1. CONTEXT DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                        BASED MONEY SYSTEM                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  DATA SOURCES   │
├─────────────────┤
│ • Polymarket API│──┐
│ • Twitter/X     │  │
│ • News Feeds    │  │
│ • Predictfolio  │  │
│ • Binance       │  │
└─────────────────┘  │
                     │
                     ▼
              ┌──────────────┐
              │   INGESTION  │
              │    ENGINE    │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │   DATABASE   │
              │  (Supabase)  │
              └──────┬───────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
    │  GEO   │  │ COPY   │  │ CORR   │  │ CRYPTO │
    │ AGENT  │  │ AGENT  │  │ AGENT  │  │ AGENT  │
    └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘
        │           │           │           │
        └───────────┼───────────┼───────────┘
                    │
                    ▼
            ┌───────────────┐
            │ ORCHESTRATOR  │
            │   (Main Loop) │
            └───────┬───────┘
                    │
        ┌───────────┼───────────┐
        │                       │
        ▼                       ▼
   ┌─────────┐           ┌──────────┐
   │  RISK   │           │ THESIS   │
   │ ENGINE  │           │  STORE   │
   └────┬────┘           └──────────┘
        │
        ▼
   ┌─────────┐
   │EXECUTION│
   │ ENGINE  │
   └────┬────┘
        │
        ├──────────┐
        │          │
        ▼          ▼
   ┌────────┐  ┌────────┐
   │ PAPER  │  │ POLY-  │
   │ BROKER │  │ MARKET │
   │ADAPTER │  │ADAPTER │
   └────────┘  └────────┘
        │
        ▼
   ┌─────────┐
   │  EVENT  │
   │   LOG   │
   └────┬────┘
        │
        ▼
   ┌─────────────────┐
   │  BASED MONEY    │
   │     DESK UI     │
   │ (Command Center)│
   └─────────────────┘
        │
        ▼
   ┌─────────┐
   │  HUMAN  │
   │APPROVAL │
   └─────────┘
```

---

## 2. COMPONENT DESCRIPTIONS

### 2.1 Data Ingestion Engine
**Purpose:** Continuously fetch, normalize, and store market data

**Responsibilities:**
- Poll Polymarket API every 5 minutes for market odds
- Monitor Twitter for geopolitical keywords (every 1 min)
- Fetch trader performance from Predictfolio (every 15 min)
- Get crypto prices from Binance (for correlation checks)
- Normalize into unified schema

**Technology:** Python + APScheduler for cron-style scheduling

**Output:** Writes to `markets`, `news_events`, `trader_performance` tables

---

### 2.2 Research Agents (4 Specialized)

**GeopoliticalAgent**
- Mandate: Russia/Ukraine, US-China, Iran, elections
- Reads: news_events, markets (category=geopolitical)
- Maintains: Live theses on political markets
- Updates: On breaking news or odds change >5%

**CopyAgent**
- Mandate: Follow top traders (>55% win rate)
- Reads: trader_performance, recent_bets
- Maintains: Theses to copy profitable traders
- Updates: When tracked traders place new bets

**CorrelationAgent**
- Mandate: Find mispriced correlated markets
- Reads: markets (same category, different timeframes)
- Maintains: Arbitrage opportunities
- Updates: When odds diverge >threshold

**CryptoAgent**
- Mandate: BTC/ETH price markets
- Reads: markets (category=crypto), Binance prices
- Maintains: Theses on crypto price predictions
- Updates: When crypto price moves >2%

**Agent Interface:**
```python
class BaseAgent:
    def __init__(self, mandate: str):
        self.mandate = mandate
        self.theses = {}
    
    def update_theses(self) -> List[Thesis]:
        """Called by orchestrator, returns updated theses"""
        pass
    
    def generate_thesis(self, market) -> Thesis:
        """Create/update thesis for market"""
        pass
```

---

### 2.3 Orchestrator (Main Loop)

**Purpose:** Coordinate agents, trigger decision cycles

**Workflow:**
```python
while True:
    # 1. Trigger all agents to update theses
    for agent in agents:
        new_theses = agent.update_theses()
        thesis_store.save(new_theses)
    
    # 2. Get high-conviction theses (>70%)
    high_conviction = thesis_store.get_actionable()
    
    # 3. Risk evaluation
    for thesis in high_conviction:
        decision = risk_engine.evaluate(thesis, portfolio)
        if decision.approved:
            # 4. Execute (or queue for approval)
            if thesis.conviction > 0.85:
                execution_engine.execute(decision)
            else:
                approval_queue.add(decision)
    
    # 5. Generate IC memo
    ic_memo_generator.create_daily_memo()
    
    # 6. Sleep until next cycle
    time.sleep(60)  # 1 min cycles
```

**Pattern:** Orchestrated (not decentralized mesh)
- Central orchestrator coordinates agents
- Agents don't communicate directly
- Simplifies debugging and auditability
- MVP-appropriate (can evolve to mesh later)

---

### 2.4 Thesis Store

**Purpose:** Central repository of all agent theses

**Schema:**
```python
class Thesis:
    id: str
    agent_id: str
    market_id: str
    thesis_text: str
    fair_value: float
    current_odds: float
    edge: float
    conviction: float  # 0-1
    horizon: str  # "hours", "days", "weeks"
    key_drivers: List[str]
    proposed_action: ProposedAction
    created_at: datetime
    updated_at: datetime
    status: str  # "active", "executed", "expired"
```

**Operations:**
- `save(thesis)` - Create or update
- `get_actionable(conviction_threshold=0.70)` - High-conviction theses
- `get_by_market(market_id)` - All theses for a market
- `get_by_agent(agent_id)` - Agent's current view

---

### 2.5 Risk Engine

**Purpose:** Enforce position limits and risk rules

**Checks:**
```python
def evaluate_proposed_action(thesis, portfolio):
    checks = [
        check_position_size(thesis.size_pct),
        check_total_deployed(portfolio),
        check_category_exposure(thesis.market.category),
        check_conviction_threshold(thesis.conviction),
        check_daily_loss_limit(portfolio),
        check_stop_loss_proximity(thesis)
    ]
    
    if all(checks):
        return RiskDecision(
            approved=True,
            action=thesis.proposed_action,
            notes=generate_risk_notes(checks)
        )
    else:
        return RiskDecision(
            approved=False,
            rejection_reason=failed_check_reason(checks)
        )
```

**Configuration:**
```python
RISK_PARAMS = {
    "max_position_pct": 0.30,
    "max_deployed_pct": 0.60,
    "max_category_pct": 0.40,
    "min_conviction": 0.70,
    "stop_loss_pct": -0.50,
    "daily_loss_limit": -0.10,
    "circuit_breaker_drawdown": -0.30
}
```

---

### 2.6 Execution Engine

**Purpose:** Translate approved trades into broker orders

**Workflow:**
```python
class ExecutionEngine:
    def __init__(self, broker_adapter):
        self.broker = broker_adapter
    
    def execute(self, risk_decision):
        action = risk_decision.action
        
        # Calculate order details
        order = self.build_order(action, portfolio)
        
        # Send to broker
        execution = self.broker.execute_order(order)
        
        # Update portfolio
        portfolio.add_position(execution)
        
        # Log to event log
        event_log.record({
            "type": "trade_executed",
            "thesis_id": action.thesis_id,
            "execution": execution,
            "timestamp": now()
        })
        
        return execution
```

---

### 2.7 Broker Adapter Interface

**Purpose:** Abstract broker-specific details

**Interface:**
```python
class BrokerAdapter(ABC):
    @abstractmethod
    def execute_order(self, order) -> Execution:
        pass
    
    @abstractmethod
    def get_position(self, market_id) -> Position:
        pass
    
    @abstractmethod
    def cancel_order(self, order_id) -> bool:
        pass
```

**Implementations:**

**PaperBroker:**
```python
class PaperBroker(BrokerAdapter):
    def execute_order(self, order):
        # Simulate fill with slippage
        fill_price = order.price * (1 + 0.01)  # 1% slippage
        return Execution(
            order_id=order.id,
            fill_price=fill_price,
            shares=order.size / fill_price,
            timestamp=now(),
            status="FILLED"
        )
```

**PolymarketBroker:**
```python
class PolymarketBroker(BrokerAdapter):
    def __init__(self, api_key, private_key):
        self.client = ClobClient(api_key, private_key)
    
    def execute_order(self, order):
        response = self.client.create_order(
            market_id=order.market_id,
            side="BUY" if order.action == "BUY_YES" else "SELL",
            amount=order.size,
            price=order.price
        )
        return Execution.from_api_response(response)
```

---

### 2.8 IC Memo Generator

**Purpose:** Auto-generate investment committee memos

**Triggers:**
- Daily (end of day summary)
- After major trade execution
- On request (user clicks "Generate Memo")

**Content:**
```markdown
# Based Money IC Memo – {date}

## Portfolio Summary
- Total Value: ${portfolio.total_value}
- P&L Today: ${portfolio.daily_pnl} ({portfolio.daily_pnl_pct}%)
- Cash: ${portfolio.cash}
- Deployed: ${portfolio.deployed} ({portfolio.deployed_pct}%)

## Active Theses
{for each high-conviction thesis}
### {market.question}
- Agent: {thesis.agent_id}
- Fair Value: {thesis.fair_value}
- Current Odds: {thesis.current_odds}
- Edge: {thesis.edge}%
- Thesis: {thesis.thesis_text}
- Key Drivers: {thesis.key_drivers}

## Risk Status
- Max Drawdown Today: {portfolio.max_drawdown}
- Circuit Breaker: {risk_engine.circuit_breaker_status}
- Stop Losses Triggered: {count}

## Trades Executed
{for each trade}
- {trade.market}: {trade.action} {trade.shares} @ ${trade.fill_price}
  - Thesis ID: {trade.thesis_id}
  - Agent: {trade.agent_id}
  - Risk Approval: {trade.risk_decision}

## Upcoming Events
{events from calendar}

---
Generated: {timestamp}
Compliance: Full audit trail in event_log
```

---

### 2.9 Event Log (Append-Only)

**Purpose:** Immutable audit trail of all decisions

**Schema:**
```sql
CREATE TABLE event_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    event_type TEXT NOT NULL,
    agent_id TEXT,
    thesis_id TEXT,
    market_id TEXT,
    data JSONB NOT NULL,
    memo_id TEXT,
    INDEX idx_timestamp (timestamp),
    INDEX idx_event_type (event_type),
    INDEX idx_thesis (thesis_id)
);
```

**Event Types:**
- `thesis_created` - Agent generated new thesis
- `thesis_updated` - Agent updated existing thesis
- `risk_evaluated` - Risk engine decision
- `trade_approved` - Human or auto-approved
- `trade_executed` - Order filled
- `position_closed` - Exit position
- `memo_generated` - IC memo created
- `circuit_breaker_triggered` - Risk limit hit

**Example Event:**
```json
{
  "type": "trade_executed",
  "timestamp": "2026-02-27T03:15:00Z",
  "agent_id": "geopolitical",
  "thesis_id": "thesis-geo-20260227-001",
  "market_id": "russia-ukraine-ceasefire-march",
  "data": {
    "action": "BUY_YES",
    "size_usd": 23.63,
    "shares": 59,
    "fill_price": 0.41,
    "edge": 0.15,
    "conviction": 0.75,
    "risk_decision": "APPROVED",
    "thesis_text": "Trump-Putin call scheduled..."
  },
  "memo_id": "memo-20260227"
}
```

---

### 2.10 Based Money Desk UI

**Purpose:** Human supervision interface

**Pages:**

**1. Today (Dashboard)**
- P&L widget
- Risk snapshot
- Active positions table
- Upcoming events calendar

**2. Theses (Pipeline)**
- Table of all active theses
- Columns: Market, Agent, Edge, Conviction, Action
- Filter by: Agent, Category, Conviction
- Sort by: Edge, Conviction, Updated
- Action buttons: Approve, Reject, Details

**3. Positions**
- Open positions with live P&L
- Entry price, current price, unrealized P&L
- Stop-loss levels
- Quick-close buttons

**4. IC Memos**
- List of all memos (newest first)
- Filter by date range, symbol, agent
- Click to view full memo
- Export to PDF

**5. Audit Trail**
- Event log viewer
- Filter by event type, agent, market
- Full JSONB data inspector
- Search functionality

**Technology:** Command Center (existing Next.js app) + new Based Money module

---

## 3. MULTI-AGENT PATTERN

### Pattern Choice: **Orchestrated** (not Decentralized Mesh)

**Why Orchestrated:**

**Pros:**
- ✅ Clear control flow (easier to debug)
- ✅ Centralized decision point (risk engine)
- ✅ Simple to audit (all decisions flow through orchestrator)
- ✅ MVP-appropriate (can evolve later)
- ✅ Human oversight easier (single approval queue)

**Cons:**
- ❌ Single point of failure (orchestrator down = system down)
- ❌ Not as scalable (but we're not HFT)
- ❌ Agents can't collaborate directly

**vs Decentralized Mesh:**
- Mesh would let agents negotiate directly (e.g., GeoAgent and CopyAgent coordinate on same market)
- But adds complexity for MVP
- Can migrate to mesh in v2 if needed

**Implementation:**
```python
class Orchestrator:
    def __init__(self, agents, risk_engine, execution_engine):
        self.agents = agents
        self.risk_engine = risk_engine
        self.execution_engine = execution_engine
        self.thesis_store = ThesisStore()
    
    def run_cycle(self):
        # 1. Collect theses from all agents
        all_theses = []
        for agent in self.agents:
            theses = agent.update_theses()
            all_theses.extend(theses)
            self.thesis_store.save_batch(theses)
        
        # 2. Rank by conviction * edge
        ranked = self.thesis_store.rank_by_score()
        
        # 3. Risk evaluate top N
        approved_actions = []
        for thesis in ranked[:10]:  # Top 10
            decision = self.risk_engine.evaluate(thesis, portfolio)
            if decision.approved:
                approved_actions.append(decision)
        
        # 4. Execute or queue for approval
        for action in approved_actions:
            if action.auto_execute:
                self.execution_engine.execute(action)
            else:
                approval_queue.add(action)
```

---

## 4. DATA MODEL

### 4.1 Core Tables

**markets**
```sql
CREATE TABLE markets (
    id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    category TEXT NOT NULL,
    yes_price DECIMAL NOT NULL,
    no_price DECIMAL NOT NULL,
    volume_24h BIGINT,
    liquidity TEXT,
    resolution_date TIMESTAMPTZ,
    resolved BOOLEAN DEFAULT FALSE,
    outcome TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**news_events**
```sql
CREATE TABLE news_events (
    id TEXT PRIMARY KEY,
    headline TEXT NOT NULL,
    source TEXT NOT NULL,
    url TEXT,
    timestamp TIMESTAMPTZ NOT NULL,
    category TEXT,
    impact_markets TEXT[],
    sentiment TEXT,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**trader_performance**
```sql
CREATE TABLE trader_performance (
    trader_id TEXT PRIMARY KEY,
    name TEXT,
    win_rate DECIMAL,
    total_volume BIGINT,
    total_trades INTEGER,
    avg_profit DECIMAL,
    recent_bets JSONB,
    copy_confidence DECIMAL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**theses**
```sql
CREATE TABLE theses (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    market_id TEXT REFERENCES markets(id),
    thesis_text TEXT NOT NULL,
    fair_value DECIMAL NOT NULL,
    current_odds DECIMAL NOT NULL,
    edge DECIMAL NOT NULL,
    conviction DECIMAL NOT NULL,
    horizon TEXT,
    key_drivers TEXT[],
    proposed_action JSONB,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**portfolio**
```sql
CREATE TABLE portfolio (
    id SERIAL PRIMARY KEY,
    cash DECIMAL NOT NULL,
    total_value DECIMAL NOT NULL,
    daily_pnl DECIMAL,
    total_deployed DECIMAL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE positions (
    id TEXT PRIMARY KEY,
    market_id TEXT REFERENCES markets(id),
    side TEXT NOT NULL,
    shares DECIMAL NOT NULL,
    entry_price DECIMAL NOT NULL,
    current_price DECIMAL,
    pnl DECIMAL,
    pnl_pct DECIMAL,
    thesis_id TEXT REFERENCES theses(id),
    opened_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    status TEXT DEFAULT 'open'
);
```

**ic_memos**
```sql
CREATE TABLE ic_memos (
    id TEXT PRIMARY KEY,
    date DATE NOT NULL,
    content TEXT NOT NULL,
    trades_count INTEGER,
    portfolio_snapshot JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**event_log** (append-only)
```sql
CREATE TABLE event_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type TEXT NOT NULL,
    agent_id TEXT,
    thesis_id TEXT,
    market_id TEXT,
    data JSONB NOT NULL,
    memo_id TEXT,
    CONSTRAINT no_updates CHECK (timestamp = created_at)
);

CREATE INDEX idx_event_timestamp ON event_log(timestamp DESC);
CREATE INDEX idx_event_type ON event_log(event_type);
CREATE INDEX idx_event_thesis ON event_log(thesis_id);
```

---

### 4.2 Event Persistence Pattern

**Every action creates event:**
```python
def record_event(event_type, agent_id, thesis_id, market_id, data):
    db.execute("""
        INSERT INTO event_log (timestamp, event_type, agent_id, thesis_id, market_id, data)
        VALUES (NOW(), $1, $2, $3, $4, $5)
    """, event_type, agent_id, thesis_id, market_id, json.dumps(data))
```

**Event reconstruction:**
```python
def replay_events(thesis_id):
    """Reconstruct thesis history from events"""
    events = db.query("""
        SELECT * FROM event_log
        WHERE thesis_id = $1
        ORDER BY timestamp ASC
    """, thesis_id)
    
    return [
        {
            "timestamp": e.timestamp,
            "type": e.event_type,
            "data": e.data
        }
        for e in events
    ]
```

**Auditability:**
- Every decision has trail: thesis_created → risk_evaluated → trade_executed
- Can answer: "Why did we make this trade?"
- Can recreate: Portfolio state at any point in time
- Compliance: Full event log exportable to CSV/JSON

---

## 5. EXTENSIBILITY

### 5.1 Adding New Agents

**Pattern:**
```python
# 1. Create new agent class
class SportsAgent(BaseAgent):
    mandate = "NFL, NBA prediction markets"
    
    def update_theses(self):
        # Implementation
        pass

# 2. Register in orchestrator
orchestrator.add_agent(SportsAgent())

# 3. No other code changes needed
```

**Requirements:**
- Inherit from `BaseAgent`
- Implement `update_theses()` method
- Return list of `Thesis` objects
- Agent automatically integrated into decision loop

---

### 5.2 Adding New Data Sources

**Pattern:**
```python
# 1. Create new fetcher
class PredictItFetcher:
    def fetch(self):
        data = requests.get("https://predictit.org/api/markets")
        return self.normalize(data)
    
    def normalize(self, data):
        # Convert to our schema
        return [
            Market(
                id=m['id'],
                question=m['name'],
                yes_price=m['lastTradePrice'],
                ...
            )
            for m in data
        ]

# 2. Register in ingestion engine
ingestion_engine.add_source(PredictItFetcher())

# 3. Agents automatically see new data
```

**Requirements:**
- Implement `fetch()` method
- Normalize to unified schema
- Data appears in database tables
- Agents query tables (don't know source)

---

### 5.3 Adding New Broker Adapters

**Pattern:**
```python
# 1. Implement BrokerAdapter interface
class KalshiBroker(BrokerAdapter):
    def execute_order(self, order):
        # Kalshi API call
        response = kalshi_client.place_order(...)
        return Execution.from_kalshi_response(response)
    
    def get_position(self, market_id):
        # Implementation
        pass
    
    def cancel_order(self, order_id):
        # Implementation
        pass

# 2. Swap in config
execution_engine = ExecutionEngine(
    broker_adapter=KalshiBroker(api_key, secret)
)

# 3. Everything else works identically
```

**Requirements:**
- Implement 3 methods: `execute_order`, `get_position`, `cancel_order`
- Return standardized `Execution` and `Position` objects
- Execution engine doesn't know broker details

---

### 5.4 Adding New Risk Rules

**Pattern:**
```python
# 1. Add new constraint
RISK_PARAMS["max_correlation"] = 0.50  # Max 50% in correlated markets

# 2. Add new check function
def check_correlation_limit(thesis, portfolio):
    correlated_exposure = sum(
        p.size for p in portfolio.positions
        if p.category == thesis.market.category
    )
    if correlated_exposure + thesis.size > RISK_PARAMS["max_correlation"]:
        return RiskCheck(passed=False, reason="Correlation limit")
    return RiskCheck(passed=True)

# 3. Add to evaluation pipeline
risk_engine.add_check(check_correlation_limit)
```

**Requirements:**
- Check function takes (thesis, portfolio)
- Returns `RiskCheck` object
- Automatically enforced in decision flow

---

## 6. DEPLOYMENT ARCHITECTURE

### Development
```
Local Machine
├── Python backend (localhost:8000)
├── Supabase local (localhost:54321)
└── Command Center UI (localhost:3000)
```

### Production
```
VPS (DigitalOcean/AWS)
├── Docker Compose
│   ├── based-money-backend (Python)
│   ├── based-money-db (Postgres)
│   └── nginx (reverse proxy)
├── Supabase Cloud (database)
└── Vercel (Command Center UI)
```

### File Structure
```
/home/ubuntu/clawd/agents/coding/polymarket/
├── config/
│   ├── credentials.env
│   └── risk_params.json
├── agents/
│   ├── base.py
│   ├── geopolitical.py
│   ├── copy_trading.py
│   ├── correlation.py
│   └── crypto.py
├── core/
│   ├── orchestrator.py
│   ├── risk_engine.py
│   ├── execution_engine.py
│   ├── thesis_store.py
│   └── ic_memo.py
├── brokers/
│   ├── base.py
│   ├── paper.py
│   └── polymarket.py
├── ingestion/
│   ├── polymarket.py
│   ├── twitter.py
│   ├── news.py
│   └── scheduler.py
├── models/
│   ├── thesis.py
│   ├── market.py
│   ├── portfolio.py
│   └── execution.py
├── main.py
└── requirements.txt
```

---

## 7. SUCCESS CRITERIA

**MVP is complete when:**
1. ✅ All 4 agents generating theses continuously
2. ✅ Risk engine approving/rejecting correctly
3. ✅ Paper trading executing without errors
4. ✅ IC memos auto-generating daily
5. ✅ Based Money Desk showing live data
6. ✅ Event log capturing all decisions
7. ✅ Can run for 7 days unattended
8. ✅ User can approve trades from dashboard

**Production-ready when:**
1. ✅ Polymarket broker adapter tested with real $
2. ✅ Performance validated (profitable over 30 days)
3. ✅ Error handling robust (handles API failures)
4. ✅ Monitoring/alerting set up
5. ✅ Backup/restore procedures documented

---

**This is the complete system design.** All components defined, data model specified, extensibility planned. Ready to code or need more prompts?
