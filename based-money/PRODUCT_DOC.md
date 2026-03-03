# Based Money - Product Documentation

**Systematic prediction market trading with multi-agent intelligence.**

---

## User Persona

**Who is this for?**

The serious retail Polymarket trader:

- **Portfolio size:** $1k-$10k (enough to care about edge, not enough for institutional tools)
- **Mindset:** Wants systematic advantage, not gambling. Treats prediction markets as investable assets.
- **Infrastructure tolerance:** Willing to run their own system (not looking for SaaS). Comfortable with Python, SQL, API keys.
- **Technical literacy:** Can follow a runbook, debug environment variables, read logs.
- **Goal:** Build proven edge, scale capital over time, audit every decision.

**Not for:**
- Casual bettors looking for a get-rich-quick scheme
- Non-technical users who want a mobile app
- Traders unwilling to validate strategies through backtesting

---

## Jobs-to-be-Done

### 1. Find Mispriced Markets Before the Crowd

**Current pain:** Manually scanning Polymarket for opportunities is slow. By the time you spot inefficiency, it's already arbitraged away.

**Solution:** Automated market fetching + news correlation. The GeoAgent continuously monitors geopolitical events and matches them to active markets, surfacing mispricings in real-time.

---

### 2. Calculate Precise Edge and Fair Value

**Current pain:** "This feels like a good bet" is not an investment thesis. Gut feel doesn't scale.

**Solution:** Every thesis includes:
- Calculated fair value (e.g., "Trump wins 2024: fair value 62%, market price 58%")
- Edge in basis points (400 bps = 4% edge)
- Confidence level (0-100%)
- Supporting evidence from news events

---

### 3. Size Positions Based on Conviction (Not Gut Feel)

**Current pain:** How much to risk on a 55% vs 70% edge? Over-betting destroys bankroll; under-betting leaves money on the table.

**Solution:** Kelly Criterion position sizing:
- High conviction + high edge → larger position
- Low conviction or thin edge → smaller position
- Automatic calculation, no mental math

---

### 4. Manage Risk Systematically

**Current pain:** Discipline breaks down when you're up big or down big. Emotional trading kills edge.

**Solution:** Risk engine enforces hard limits:
- Max 50% of portfolio deployed at once
- Max 20% in any single position
- Reject trades below minimum edge threshold
- Automatic stop-losses (future feature)

---

### 5. Audit Every Decision with Full Event Log

**Current pain:** "Why did I buy that?" 3 weeks later, you can't remember the thesis. Impossible to learn from mistakes.

**Solution:** Comprehensive logging:
- IC memos for every trade (thesis, edge, conviction, timestamp)
- Event log for system decisions (market fetched, thesis generated, trade executed/rejected)
- Historical positions table for post-mortem analysis

---

### 6. Scale Up Capital as Edge Validates

**Current pain:** You don't know if your strategy actually works until you risk real money. But risking real money without validation is reckless.

**Solution:** Three-stage validation pipeline:
1. **Backtest** on 90 days of historical data (win rate >52% required to proceed)
2. **Paper trade** for 2+ weeks (catch bugs, validate live data pipeline)
3. **Live trade** starting small (10% position sizes, 30% deployed max first week)

---

## End-to-End Workflow

```
[Polymarket API] → Markets DB
        ↓
[News RSS/Twitter] → News Events DB
        ↓
[Geopolitical Agent] → Generates Theses
        ↓
[Risk Engine] → Approves/Rejects
        ↓
[Execution Engine] → Paper/Live Trades
        ↓
[Event Log] → Full Audit Trail
        ↓
[IC Memos + API] → Daily Reports
```

### Step-by-Step

1. **Market Ingestion:** Fetch all active Polymarket markets via API, store in `markets` table with current prices and liquidity.

2. **News Correlation:** Pull geopolitical news (RSS or Twitter), store in `news_events` table with tags (e.g., "Ukraine", "AI regulation", "Election").

3. **Thesis Generation:** GeoAgent scans for market-news matches:
   - "Russia withdraws from Kherson" → "Ukraine reclaims territory by Dec 2024" market
   - Calculates fair value based on event implications
   - Outputs thesis with edge and confidence

4. **Risk Evaluation:** Risk engine checks:
   - Is edge above minimum threshold (50 bps default)?
   - Does position size fit portfolio limits?
   - Is total deployed capital below max (50%)?

5. **Execution:** If approved, execution engine:
   - Paper mode: Log to `positions` table with `mode=paper`
   - Live mode: Submit order to Polymarket API, update portfolio

6. **Logging:** Every decision logged to:
   - `ic_memos`: Trade rationale
   - `event_log`: System events (market fetch, thesis generation, trade execution)
   - `positions`: Position entry/exit with P&L

7. **Reporting:** Daily performance summary (future: push to Command Center dashboard).

---

## Design Decisions

### Orchestrated, Not Mesh

**Why:** Single orchestrator controls information flow (fetch → analyze → decide → execute).

**Benefits:**
- Easier to reason about system state
- No race conditions from agents acting simultaneously
- Clear responsibility: orchestrator owns the cycle

**Trade-off:** Single point of failure (mitigated by event logging for easy restarts).

---

### Backtesting-First

**Why:** No real money until strategy validates on historical data.

**Benefits:**
- Catch logic errors before they cost money
- Tune risk parameters (edge threshold, position sizing) on real market data
- Build confidence in the approach

**Gate:** Win rate >52% required to proceed to paper trading.

---

### Paper-First

**Why:** Even after backtest passes, run paper trading 2+ weeks before going live.

**Benefits:**
- Catch integration bugs (API rate limits, network timeouts, edge cases)
- Validate live data pipeline (news feeds, market updates)
- Prove the system runs reliably without babysitting

**Gate:** 2+ weeks stable operation, win rate holding above 52%.

---

### Supabase for Database

**Why:** Managed Postgres with generous free tier.

**Benefits:**
- Real-time subscriptions (future: dashboard auto-updates on new positions)
- SQL for complex queries (portfolio analytics, performance reports)
- Web UI for manual inspection (check `positions` table during trading)
- No DevOps: They handle backups, scaling, security patches

**Trade-off:** Vendor lock-in (mitigated by standard Postgres, easy migration path).

---

### Multi-Agent Architecture

**Why:** Different agents find different types of mispricings.

**Current:**
- **GeoAgent:** Geopolitical events → prediction markets

**Future:**
- **SentimentAgent:** Social media sentiment → market underreaction
- **WhaleAgent:** Large orders → front-run or fade
- **CorrelationAgent:** Cross-market inefficiencies (e.g., "Trump wins → crypto pumps")

**Benefits:** Diversified signal sources, more edge opportunities, agents can specialize.

---

## Evolution Path (v2+)

### More Agents

- **SentimentAgent:** NLP on Twitter/Reddit for crowd emotion detection
- **WhaleAgent:** Track large Polymarket wallets, detect whale positioning
- **CorrelationAgent:** Find correlated markets (e.g., "Bitcoin >$100k" vs "Trump wins 2024")

---

### Real-Time News

- **Current:** RSS feeds polled every 5 minutes
- **Future:** WebSocket subscriptions to news APIs (Bloomberg, Reuters) for sub-second latency
- **Impact:** Capture mispricings before they revert (speed edge)

---

### HFT Optimizations

- **Limit orders:** Place resting orders to capture spread instead of crossing
- **Order book analysis:** Detect liquidity imbalances, predict short-term price moves
- **Latency reduction:** Co-locate near Polymarket servers (if they allow)

---

### Multi-Platform

- **Expand to:** Kalshi (CFTC-regulated), PredictIt (politics), Manifold Markets (play money for testing)
- **Cross-platform arbitrage:** Buy on Polymarket at 58%, sell on Kalshi at 62% (risk-free profit)

---

### Auto-Rebalancing

- **Current:** Positions held until manual close
- **Future:** Automatically close winning positions to redeploy capital into new opportunities
- **Logic:** If position up 20%, close 50% and lock in profit; let the rest ride

---

## Summary

Based Money is a **systematic trading infrastructure** for prediction markets. It solves the jobs-to-be-done for serious retail traders who want edge but lack institutional tools. The architecture emphasizes **validation before risk** (backtest → paper → live), **systematic decision-making** (agents + risk engine), and **full auditability** (event logs + IC memos).

The evolution path scales from single-agent geopolitical trading to multi-agent, multi-platform HFT-style operations — but always grounded in the core principle: **edge must validate before capital deploys.**

---

**Last updated:** 2026-02-27
