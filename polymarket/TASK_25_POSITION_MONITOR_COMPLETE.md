# Task 25: Position Monitor — COMPLETE ✅

**Status:** Complete  
**Time:** ~15 minutes  
**Files Created:**
- `core/positions.py`
- `test_position_monitor.py`
- Updated `core/__init__.py`

---

## What Was Built

### PositionMonitor Class (`core/positions.py`)

Position monitoring system that tracks open positions, updates P&L, and triggers stop-losses.

**Constructor:**
```python
def __init__(self, broker_adapter: BrokerAdapter)
```

**Two core methods:**

1. **`update_positions() -> List[Position]`**
2. **`check_stop_losses(positions, stop_loss_pct=0.15) -> List[Order]`**

---

## Method 1: update_positions()

**Purpose:** Fetch all open positions, update prices and P&L from broker/market data.

**Process:**
```python
1. Fetch open positions from DB (status="open")
2. For each position:
   a. Get current price from broker.get_position(market_id)
   b. Calculate P&L = (current_price - entry_price) * shares
   c. Update position.current_price and position.pnl
   d. Save position to DB (best effort)
3. Return list of updated positions
```

**Implementation:**
```python
def update_positions(self) -> List[Position]:
    # Fetch from DB
    positions = get_positions(filters={"status": "open"})
    
    for position in positions:
        # Get current price from broker
        broker_position = self.broker.get_position(position.market_id)
        current_price = broker_position.current_price if broker_position else position.current_price
        
        # Calculate P&L
        current_pnl = (current_price - position.entry_price) * position.shares
        
        # Update and save
        position.current_price = current_price
        position.pnl = current_pnl
        save_position(position)  # best effort
    
    return positions
```

**Graceful degradation:**
- If DB unavailable: returns empty list
- If broker data unavailable: keeps existing current_price
- If position save fails: continues with other positions

---

## Method 2: check_stop_losses()

**Purpose:** Check positions for stop-loss triggers and generate exit orders.

**Parameters:**
- `positions`: List of positions to check
- `stop_loss_pct`: Threshold percentage (default 15.0 = 15%)

**Stop-loss calculation:**
```python
position_cost = entry_price * shares
loss_pct = (pnl / position_cost) * 100

# Trigger when: loss_pct < -stop_loss_pct
# Example: -20% loss triggers 15% threshold
```

**Exit order generation:**
```python
if loss_pct < -stop_loss_pct:
    exit_side = "NO" if position.side == "YES" else "YES"
    
    exit_order = Order(
        market_id=position.market_id,
        side=exit_side,
        size=position.shares,  # Exit entire position
        order_type="MARKET",
        limit_price=position.current_price,
        client_order_id=f"stop-loss-{position.id}",
    )
```

**Event logging:**
```python
record_event(
    event_type="stop_loss_triggered",
    position_id=position.id,
    details={
        "loss_pct": -20.0,
        "pnl": -10.0,
        "position_cost": 50.0,
        "entry_price": 0.50,
        "current_price": 0.40,
        "stop_loss_threshold": 15.0,
    },
    severity="warning",
)
```

---

## Test Coverage

**Test file:** `test_position_monitor.py`

Tests verify:

1. ✅ **Instantiation** — PositionMonitor created with broker
2. ✅ **No positions** — Returns empty list when DB has no positions
3. ✅ **No trigger** — Small loss (5%) doesn't trigger 15% threshold
4. ✅ **Trigger** — Large loss (20%) triggers 15% threshold
5. ✅ **Opposite side** — YES exits with NO, NO exits with YES
6. ✅ **Multiple positions** — Correctly identifies 2/5 positions to exit
7. ✅ **Custom threshold** — 12% loss triggers 10% but not 15%
8. ✅ **P&L calculation** — Consistent with Position.pnl_percentage()

**All tests passed:**
```
🎉 ALL TESTS PASSED!
```

---

## Example Usage

### Basic Monitoring Loop

```python
from core.positions import PositionMonitor
from brokers import PaperBroker

# Initialize
broker = PaperBroker()
monitor = PositionMonitor(broker_adapter=broker)

# Update positions with current prices
positions = monitor.update_positions()

# Check for stop-loss triggers
exit_orders = monitor.check_stop_losses(positions, stop_loss_pct=15.0)

# Execute stop-loss exits
for order in exit_orders:
    execution = broker.execute_order(order)
    print(f"Stop-loss executed: {execution.market_id}")
```

### Output Example

```
Updating 3 open positions...
  Updated btc-100k: $-5.00 (-10.00%)
  Updated eth-5k: $+2.50 (+5.00%)
  Updated trump-2024: $-12.00 (-24.00%)

🛑 STOP-LOSS TRIGGERED: trump-2024
   Loss: $-12.00 (-24.00%)
   Threshold: 15.00%

📋 Generated 1 stop-loss exit orders
```

---

## Stop-Loss Logic

### Calculation Breakdown

**Example Position:**
- Entry: 100 shares @ $0.50 = $50 cost
- Current: $0.40
- P&L: (0.40 - 0.50) × 100 = -$10
- Loss %: (-10 / 50) × 100 = -20%

**Threshold check:**
```python
if -20.0 < -15.0:  # True
    # Trigger stop-loss
```

### Opposite Side Logic

**Why exit with opposite side?**

Polymarket prediction markets have YES and NO tokens. To close a position:
- **Entered YES** → Sell by buying **NO** (equivalent to selling YES)
- **Entered NO** → Sell by buying **YES** (equivalent to selling NO)

**Implementation:**
```python
exit_side = "NO" if position.side == "YES" else "YES"
```

### Edge Cases Handled

1. **Exact threshold (15% loss):**
   - Uses `<` not `<=`
   - -15.0% loss does NOT trigger 15.0% threshold
   - Prevents premature exits

2. **Zero position cost:**
   - Skips position (prevents division by zero)
   - Shouldn't happen in practice

3. **Profitable positions:**
   - Positive P&L → positive loss_pct
   - Never triggers stop-loss

---

## Integration Points

**Consumed by:**
- Trading orchestrator (monitoring loop)
- Position reconciliation
- Portfolio rebalancing

**Depends on:**
- `brokers.base.BrokerAdapter` (get_position)
- `models.portfolio.Position`
- `database.db` (get_positions, save_position, record_event)

**Produces:**
- Updated positions (for portfolio state)
- Exit orders (for execution engine)

---

## Design Decisions

### 1. Separate update and check methods

**Why not combined?**
- Allows independent testing
- Update can run frequently (every minute)
- Check can run less frequently (every 5 minutes)
- Separation of concerns

### 2. Best-effort DB operations

**Why non-fatal?**
- Position monitoring should continue even if DB unavailable
- In-memory state is authoritative during session
- DB is for persistence between restarts

### 3. Exit entire position on stop-loss

**Why not partial exit?**
- Simpler logic (no position size management)
- Clean break (no zombie positions)
- Standard risk management practice
- Can be extended to partial exits later

### 4. Market orders for exits

**Why not limit orders?**
- Stop-losses need immediate execution
- Don't want to wait for limit fill
- Slippage acceptable for risk management
- Can be overridden by caller

---

## Performance Considerations

**Database calls:**
- One SELECT for all open positions
- One UPDATE per position
- One INSERT for each stop-loss event

**Optimization opportunities:**
- Batch position updates (single UPDATE query)
- Cache broker position data (reduce API calls)
- Skip update if current_price hasn't changed

**Recommended update frequency:**
- Position updates: Every 1-5 minutes
- Stop-loss checks: Every 5-15 minutes
- Adjust based on market volatility

---

## Next Steps

With position monitoring complete, we can now build:

1. **Automated monitoring loop** (Task 26) — Runs update + check on schedule
2. **Position reconciliation** — Sync with broker to detect drift
3. **Portfolio rebalancing** — Close winners, add new positions
4. **Full orchestration** — Ingestion → Thesis → Risk → Execution → Monitoring

**Ready for Task 26: Trading Orchestrator / Monitoring Loop**
