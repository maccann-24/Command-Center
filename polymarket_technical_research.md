# Polymarket Technical Research Report
**Date:** February 27, 2026
**Purpose:** Deep dive into Polymarket market mechanics, API capabilities, and technical constraints

---

## 1. MARKET RESOLUTION MECHANICS

### How Markets Actually Resolve

**Resolution System: UMA Optimistic Oracle**
- Polymarket uses UMA's Optimistic Oracle V2 (and Managed OOv2) for decentralized resolution
- Markets resolve through a **propose → dispute → settle** workflow

**Resolution Process (Step-by-Step):**

1. **Market Close:** Trading stops at scheduled timestamp
2. **Outcome Proposal:** 
   - Anyone can propose an outcome by posting a **bond in USDC**
   - Proposer must reference resolution source/evidence
   - Bond is forfeited if proposal is successfully disputed
   
3. **Challenge Period:** 
   - **2-hour** dispute window after proposal
   - Others can challenge by posting matching collateral
   
4. **Settlement:**
   - **No dispute:** Proposal accepted, proposer gets bond back + reward
   - **Disputed:** Escalates to UMA's Data Verification Mechanism (DVM)

**DVM Dispute Resolution:**
- UMA token stakers vote using **commit-reveal mechanism**
- Voting typically takes **48-96 hours** (commit phase + reveal phase)
- Voters reference UMIPs (UMA Improvement Proposals) for methodology
- Winning side receives half the losing side's bond
- Incorrect/non-participating voters face slashing

**Resolution Types:**
- **YES_OR_NO_QUERY:** Binary outcomes (returns 1 or 0)
- **MULTIPLE_VALUES:** Up to 7 integers in single request (for multi-outcome events)

**Key Constraint:** Resolution is NOT instant. From market close to final settlement:
- Uncontested: ~2 hours minimum
- Disputed: 2-5 days typical
- Settlement happens on-chain via smart contracts

**Resolution Fee Structure:**
- Proposer posts bond (typically USDC)
- Successful proposers earn rewards
- Failed proposers lose bond to disputers

---

## 2. PY-CLOB-CLIENT API DOCUMENTATION

### Order Types & Execution

**Supported Order Types:**

1. **GTC (Good Till Canceled)**
   - Standard limit order
   - Stays on book until filled or manually canceled
   - Used via: `OrderType.GTC`

2. **FOK (Fill or Kill)**
   - Market order must fill completely or reject
   - No partial fills
   - Used for market orders: `OrderType.FOK`

3. **Post-Only**
   - Order only accepted if it adds liquidity (maker)
   - Rejected if would immediately execute (taker)

**Order Creation Flow:**

```python
# Limit Order
order = OrderArgs(
    token_id="<token-id>",
    price=0.01,           # Price in USD (0.00-1.00)
    size=5.0,             # Number of shares
    side=BUY              # BUY or SELL
)
signed = client.create_order(order)
resp = client.post_order(signed, OrderType.GTC)

# Market Order (by dollar amount)
mo = MarketOrderArgs(
    token_id="<token-id>",
    amount=25.0,          # Dollar amount to spend
    side=BUY,
    order_type=OrderType.FOK
)
signed = client.create_market_order(mo)
resp = client.post_order(signed, OrderType.FOK)
```

### API Limits & Constraints

**Rate Limits (from GitHub issues):**
- Active discussion about burst vs throttle limits for `/order` endpoint
- No official public documentation on exact rate limits
- Community reports suggest careful rate management needed for high-frequency trading

**Order Size Limits:**
- Minimum order size: Market-dependent (query via `/book` endpoint)
- Maximum: Limited by wallet balance and market liquidity
- Tick size: Typically $0.001 increments (varies by market)

**Batch Operations:**
- Batch order endpoint allows **up to 15 orders** per request (increased from 5 in 2025)
- POST `/orders` (plural) for batch placement

### Authentication Levels

**L1 Authentication (EIP-712 signature):**
- Used ONCE to create/derive API credentials
- Private key required
- Generates: API key, secret, passphrase

**L2 Authentication (HMAC-SHA256):**
- Used for all trading operations
- Headers required:
  - `POLY_ADDRESS`: Wallet address
  - `POLY_SIGNATURE`: HMAC-SHA256 of request
  - `POLY_TIMESTAMP`: Unix timestamp
  - `POLY_API_KEY`: Your API key
  - `POLY_PASSPHRASE`: Your passphrase

**Signature Types:**
- `0`: EOA (MetaMask, hardware wallets) - you pay gas
- `1`: POLY_PROXY (Magic Link email login)
- `2`: GNOSIS_SAFE (browser wallets, most common)

**Funder Address:**
- For proxy wallets: specify address holding actual funds
- Different from signing key for security

### Critical Setup: Token Allowances (EOA/MetaMask Users)

**MUST SET BEFORE TRADING:**

1. **USDC Approval:**
   - Token: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`
   - Approve for:
     - `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` (Main exchange)
     - `0xC5d563A36AE78145C45a50134d48A1215220f80a` (Neg risk markets)
     - `0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296` (Neg risk adapter)

2. **Conditional Tokens Approval:**
   - Token: `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045`
   - Approve for same three contracts above

**Common Error:** `PolyApiException[status_code=400, error_message={'error': 'not enough balance / allowance'}]`
- Usually means allowances not set

---

## 3. FEE STRUCTURES & COSTS

### Trading Fees

**Fee-Free Markets (MOST MARKETS):**
- **No trading fees** on most prediction markets
- No deposit/withdrawal fees (USDC on Polygon)
- Zero maker fees
- Zero taker fees

**Fee-Enabled Markets (as of Feb 2026):**

1. **15-minute crypto markets**
2. **5-minute crypto markets**
3. **NCAAB (college basketball)** - started Feb 18, 2026
4. **Serie A (soccer)** - started Feb 18, 2026

**Fee Formula:**
```
fee = C × feeRate × (p × (1 - p))^exponent

Where:
- C = number of shares traded
- p = price of shares (0.00 to 1.00)
```

**Fee Parameters:**

| Market Type | Fee Rate | Exponent | Maker Rebate | Max Effective Rate |
|-------------|----------|----------|--------------|-------------------|
| Sports (NCAAB, Serie A) | 0.0175 | 1 | 25% | 0.44% @ 50% prob |
| Crypto (5-min, 15-min) | 0.25 | 2 | 20% | 1.56% @ 50% prob |

**Key Insights:**
- Fees **peak at 50% probability** (most uncertain)
- Fees **approach zero** at extremes (0.01 or 0.99)
- Collected in **shares on buy orders**, **USDC on sell orders**
- Maker rebates paid daily from taker fees
- Minimum fee: $0.0001 USDC

**Polymarket US (Regulated Exchange):**
- Taker fee: **10 basis points (0.10%)**
- Maker fee: **0%**
- Minimum fee: $0.0010
- Calculated on Total Contract Premium (contracts × price)

### Gas Costs (Polygon)

**Network Fees:**
- Polygon gas fees: **< $0.01 to $0.05** per transaction (typical)
- Trading via CLOB: **NO gas fees** (off-chain matching, gasless via relayer)
- On-chain operations (deposits, withdrawals, token splits): **~$0.01-0.05**

**Gasless Trading:**
- Polymarket uses **proxy wallets** and **relayers**
- Users sign orders off-chain (EIP-712)
- Relayer submits to blockchain
- User pays NO POL for gas on trades

**When You Need POL:**
- Direct EOA interaction with contracts
- Manual on-chain cancellations
- Bridge operations from Ethereum L1

---

## 4. LIQUIDITY DEPTH & ORDER BOOKS

### Order Book Structure

**Access via CLOB API:**
```
GET https://clob.polymarket.com/book?token_id={token_id}

Response:
{
  "bids": [
    {"price": "0.64", "size": "1000"},
    {"price": "0.63", "size": "2500"},
    ...
  ],
  "asks": [
    {"price": "0.66", "size": "800"},
    {"price": "0.67", "size": "1200"},
    ...
  ],
  "market": {
    "min_order_size": "1.0",
    "tick_size": "0.001",
    "neg_risk": false
  }
}
```

**Key Metrics:**
- `volume`: Total volume traded (USD)
- `liquidity`: Current available liquidity
- `openInterest`: Total outstanding shares
- `bestBid` / `bestAsk`: Top of book
- `spread`: bestAsk - bestBid

### Liquidity Patterns (from research)

**High-Volume Markets:**
- Presidential elections, major sports: Deep liquidity
- Spreads: 1-2 cents typical
- Order book: 5-10 levels each side with $1k-$100k+ per level

**Low-Volume Markets:**
- Niche events: Thin liquidity
- Spreads: Can be 5-10 cents or more
- Order book: 1-3 levels, hundreds of dollars per level

**Liquidity Varies By:**
- Event popularity
- Time to resolution
- Market maker participation
- Fee structure (fee markets attract more MMs due to rebates)

### Slippage Patterns

**Market Orders:**
- Small orders (<$100): Minimal slippage on liquid markets
- Medium orders ($500-$5k): 0.5-2% typical slippage
- Large orders (>$10k): Can move market significantly on thin markets

**Best Practice:**
- Use limit orders for size
- Check order book depth before large trades
- Use batch API to query multiple markets at once

---

## 5. EXECUTION TIMES & LATENCY

### Recent Critical Change (Feb 18, 2026)

**500ms Delay REMOVED:**
- Previously: All taker orders had **500ms execution delay**
- Now: **IMMEDIATE execution** (no cancellation window)
- Impact: Made most existing arbitrage bots obsolete overnight

### Current Latency Benchmarks

**REST API (Gamma):**
- Data indexing latency: **~1 second**
- HTTP request round-trip: **50-200ms** typical
- **NOT suitable for high-frequency trading**

**WebSocket Feeds:**
- Market updates: **~100ms** latency
- Order fills/cancellations: Real-time push
- **Required for competitive trading**

**Order Execution:**
- Order placement: **50-200ms** (network + matching)
- Cancel/replace loop: **MUST be <100ms** to avoid adverse selection
- Professional HFT: **Sub-millisecond** to low single-digit ms

**Latency Sources:**
1. **Network:** Home Wi-Fi: 150ms+, VPS near server: <5ms
2. **API Processing:** Order validation, matching engine
3. **Blockchain Settlement:** Happens async after match

**Real-World Performance:**
- **Retail setup:** 10-100ms latency
- **Professional HFT:** Sub-1ms execution
- **Co-located VPS:** 0.5-5ms network latency

**WebSocket Endpoints:**
- Market channel: `wss://ws-subscriptions-clob.polymarket.com/ws/`
- User channel: Authenticated, pushes personal order updates
- RTDS: `wss://ws-live-data.polymarket.com` (crypto prices, comments)

---

## 6. TECHNICAL CONSTRAINTS & LIMITATIONS

### Rate Limits

**CLOB API:**
- No official public docs on exact limits
- GitHub Issue #147 discusses burst vs throttle for `/order` endpoint
- Community practice: Rate management essential for HFT
- Batch endpoint helps (15 orders/request)

### Order Constraints

**Tick Size:**
- Minimum price increment: **$0.001** (typical)
- Market-specific, query via `/book` endpoint
- Cannot place orders between ticks

**Order Size:**
- Minimum: Varies by market (typically $1-5)
- Maximum: Limited by:
  - Available liquidity
  - Wallet balance
  - No hard platform cap

**Fee Rate Changes:**
- **NEVER hardcode fees**
- Must query `GET /fee-rate?token_id={token_id}` before EACH trade
- Polymarket can change fees anytime
- Orders must include `feeRateBps` in signature
- Signature validation will reject mismatched fee rates

### Blockchain Constraints

**Settlement Time:**
- Off-chain matching: Immediate
- On-chain settlement: Async (within seconds to minutes)
- Polygon block time: ~2 seconds
- Settlement finality: ~1 minute typical

**Contract Addresses (Polygon):**
- USDC: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`
- Conditional Tokens: `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045`
- Main Exchange: `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E`

### API Architecture Constraints

**Data Feeds (by latency):**

| Feed | Latency | Use Case | Access |
|------|---------|----------|--------|
| WebSocket | ~100ms | Market making, HFT | Public |
| CLOB REST | ~1s | Price queries, order placement | Public (auth for trading) |
| Gamma API | ~1s | Market discovery, metadata | Public |
| Blockchain | ~2-5s | Settlement, resolution | Public |

**No Support For:**
- Streaming historical trade data (use Data API or subgraph)
- Real-time P&L tracking (must calculate client-side)
- Guaranteed fills (all orders can fail)

---

## 7. REAL-WORLD DEVELOPER EXPERIENCES

### Common Issues (from GitHub/Forums)

**1. Allowance Problems (EOA Users):**
- Most common error: "not enough balance / allowance"
- Solution: Must approve USDC + Conditional Tokens for 3 contracts
- Only needed ONCE per wallet
- Example gist available: https://gist.github.com/poly-rodr/44313920481de58d5a3f6d1f8226bd5e

**2. Fee Rate Signature Failures:**
- Orders rejected in fee-enabled markets
- Cause: Missing or incorrect `feeRateBps` in order payload
- Solution: Always query fee rate, include in signature

**3. Bot Performance Issues:**
- Old bots broke when 500ms delay removed (Feb 2026)
- Taker arbitrage strategies now unprofitable due to fees
- Solution: Shift to market making (maker rebates)

**4. Latency Competition:**
- Home setups: 150ms+ latency
- VPS near infrastructure: <5ms
- Critical for cancel/replace loops

### Successful Strategies (from research)

**Market Making:**
- Place maker orders both sides (YES/NO)
- Earn rebates (20-25% of taker fees)
- Keep cancel/replace loop <100ms
- Use WebSocket for real-time updates

**5-Minute BTC Markets:**
- 288 markets per day (every 5 minutes)
- Direction often determined T-10 seconds before close
- Strategy: Maker orders at 0.90-0.95 on likely outcome
- Profit: $0.05-$0.10 per contract + rebates

**Avoiding Losses:**
- Use WebSocket, NOT REST polling
- Always include `feeRateBps` in signatures
- Run on VPS (not home Wi-Fi)
- Don't market-make near 50% probability (adverse selection risk)
- Consolidate YES/NO positions (avoid locked funds)

---

## 8. KEY DOCUMENTATION SOURCES

### Official Documentation
- **CLOB API:** https://docs.polymarket.com/trading/overview
- **Gamma Markets API:** https://docs.polymarket.com/developers/gamma-markets-api/overview
- **Fee Documentation:** https://docs.polymarket.com/trading/fees
- **Resolution Info:** https://help.polymarket.com/en/articles/13364518

### GitHub Resources
- **py-clob-client:** https://github.com/Polymarket/py-clob-client
- **Examples:** https://github.com/Polymarket/py-clob-client/tree/main/examples
- **Issue Tracker:** https://github.com/Polymarket/py-clob-client/issues

### Third-Party Research
- **UMA Oracle Deep Dive:** https://rocknblock.io/blog/how-prediction-markets-resolution-works-uma-optimistic-oracle-polymarket
- **API Architecture:** Medium article by @gwrx2005 (comprehensive technical overview)
- **Trading Bot Guide:** @_dominatos on X (recent rule changes)

---

## 9. CRITICAL TECHNICAL FACTS SUMMARY

### What Makes Polymarket Different

1. **Hybrid Architecture:**
   - Off-chain matching (CLOB)
   - On-chain settlement (Polygon)
   - Non-custodial (users control funds)

2. **Resolution:**
   - Decentralized via UMA Oracle
   - 2-hour challenge minimum
   - Dispute resolution: 2-5 days
   - NOT instant, NOT centralized

3. **Fee Revolution (2026):**
   - Most markets: FREE
   - Crypto/sports markets: Dynamic fees
   - Shifted meta from taker arb to maker rebates

4. **Execution Speed:**
   - 500ms delay removed Feb 2026
   - Now immediate execution
   - Requires <100ms cancel/replace
   - Professional edge: sub-ms latency

5. **API Ecosystem:**
   - Gamma API: Market discovery
   - CLOB API: Trading
   - Data API: User data
   - WebSocket: Real-time
   - Subgraph: On-chain verification

### Technical Gotchas

❌ **Don't:**
- Hardcode fee rates
- Use REST for HFT
- Skip token allowances (EOA)
- Forget `feeRateBps` in signatures
- Run on home internet for serious trading

✅ **Do:**
- Query fee rates dynamically
- Use WebSocket for real-time
- Set allowances before first trade
- Include proper fee fields
- Use VPS for low latency
- Build as maker, not taker (2026 meta)

---

## 10. CONCLUSION

Polymarket's technical infrastructure is **more complex than traditional prediction markets**:

- **Resolution is trustless but slow** (UMA Oracle: 2hrs-5 days)
- **Trading is fast but nuanced** (immediate execution, dynamic fees)
- **API is comprehensive but evolving** (breaking changes like 500ms removal)
- **Profitability shifted** (from taker arb to maker rebates)

**For developers building on Polymarket:**
- Recent rule changes made most guides obsolete
- Focus on market making, not arbitrage
- Low latency infrastructure is critical
- Fee-aware order signing is mandatory
- WebSocket is required for competitive trading

**Gas costs are negligible**, but **trading fees matter significantly** in crypto/sports markets (up to 1.56% at 50% probability).

The platform is **actively evolving** - February 2026 changes broke most existing bots overnight. Always verify current rules before deploying.
