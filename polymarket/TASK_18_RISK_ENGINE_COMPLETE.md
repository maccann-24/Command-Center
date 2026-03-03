# TASK 18: Risk Engine - COMPLETE ✅

## Summary

Created comprehensive pre-trade risk engine with 4 critical safety checks to prevent capital destruction. Evaluates position size, total deployment, conviction, and edge before allowing trades.

## Files Created

### 1. `core/risk.py` (9 KB)

**Key Components:**

#### `RISK_PARAMS`
```python
{
    'max_position_pct': 20.0,      # Max single position (% of capital)
    'max_deployed_pct': 60.0,      # Max total deployed (% of capital)
    'min_conviction': 0.70,        # Minimum conviction threshold
    'min_edge': 0.05,              # Minimum edge required (5%)
}
```

#### `RiskDecision` dataclass
- `approved`: bool (pass/fail)
- `reason`: str (explanation)
- `risk_notes`: List[str] (detailed check results)
- `recommended_size`: float (suggested position size)

#### `RiskEngine` class
Main risk evaluation engine with:
- `evaluate(thesis, portfolio)` - Run all 4 checks
- `get_max_position_size(portfolio)` - Calculate max allowed size
- `suggest_position_size(thesis, portfolio)` - Kelly-like sizing
- `update_params(**kwargs)` - Dynamic parameter updates

### 2. `test_risk_engine.py` (12 KB)

Comprehensive test suite:
- ✅ All checks pass
- ✅ Position size too large
- ✅ Total deployed too high
- ✅ Conviction too low
- ✅ Edge too small
- ✅ Multiple failures
- ✅ Custom risk parameters
- ✅ Max position calculation
- ✅ Position size suggestion
- ✅ Convenience functions
- ✅ Parameter updates

**All 11 tests passing!**

### 3. Updated `core/__init__.py`

Added exports:
```python
from .risk import (
    RiskEngine,
    RiskDecision,
    RISK_PARAMS,
    check_risk,
    is_trade_safe,
)
```

## The 4 Critical Checks

### ✓ Check 1: Position Size
```python
proposed_size <= max_position_pct (20%)
```
**Prevents:** Concentration risk (too much in one trade)

### ✓ Check 2: Total Deployment
```python
current_deployed + proposed_size <= max_deployed_pct (60%)
```
**Prevents:** Over-leverage (running out of capital)

### ✓ Check 3: Conviction
```python
conviction >= min_conviction (0.70)
```
**Prevents:** Low-confidence trades (shooting in the dark)

### ✓ Check 4: Minimum Edge
```python
edge > min_edge (0.05 = 5%)
```
**Prevents:** Trading without advantage (burning fees)

## Usage Examples

### Basic Risk Check
```python
from core import RiskEngine

risk_engine = RiskEngine()

# Evaluate a thesis
decision = risk_engine.evaluate(thesis, portfolio)

if decision.approved:
    # Execute trade
    execute_trade(thesis, decision.recommended_size)
else:
    # Log rejection
    print(f"❌ Trade rejected: {decision.reason}")
```

### Quick Safety Check
```python
from core import is_trade_safe

if is_trade_safe(thesis, portfolio):
    execute_trade(thesis)
else:
    skip_trade()
```

### Get Detailed Report
```python
from core import check_risk

decision = check_risk(thesis, portfolio)

print(f"Status: {decision}")
print("\nDetailed checks:")
for note in decision.risk_notes:
    print(f"  {note}")
```

### Custom Risk Parameters
```python
# More conservative settings
conservative_params = {
    'max_position_pct': 10.0,
    'max_deployed_pct': 40.0,
    'min_conviction': 0.80,
    'min_edge': 0.10,
}

engine = RiskEngine(conservative_params)
decision = engine.evaluate(thesis, portfolio)
```

### Dynamic Position Sizing
```python
risk_engine = RiskEngine()

# Get maximum allowed size
max_size = risk_engine.get_max_position_size(portfolio)
print(f"Max position: {max_size}%")

# Get Kelly-like suggested size
suggested = risk_engine.suggest_position_size(thesis, portfolio)
print(f"Suggested position: {suggested:.2f}%")
```

## Example Outputs

### ✅ Approved Trade
```
✅ APPROVED - Size: 15.0%
Reason: All risk checks passed

Risk Notes:
  ✓ Position size 15.0% ≤ 20.0%
  ✓ Total deployed 45.0% ≤ 60.0%
  ✓ Conviction 0.85 ≥ 0.70
  ✓ Edge 12.00% > 5.00%
```

### ❌ Position Too Large
```
❌ REJECTED - Failed: Position size 25.0% exceeds limit 20.0%

Risk Notes:
  ✗ Position size 25.0% > 20.0%
  ✓ Total deployed 35.0% ≤ 60.0%
  ✓ Conviction 0.90 ≥ 0.70
  ✓ Edge 20.00% > 5.00%
```

### ❌ Multiple Failures
```
❌ REJECTED - Failed: Position size 25.0% exceeds limit 20.0%; 
Total deployed 75.0% exceeds limit 60.0%; 
Conviction 0.60 below minimum 0.70; 
Edge 2.00% insufficient (minimum 5.00%)

Risk Notes:
  ✗ Position size 25.0% > 20.0%
  ✗ Total deployed 75.0% > 60.0%
  ✗ Conviction 0.60 < 0.70
  ✗ Edge 2.00% ≤ 5.00%
```

## Integration with Agent Workflow

```python
from agents import GeopoliticalAgent
from core import RiskEngine, thesis_store
from models import Portfolio

# Initialize
agent = GeopoliticalAgent()
risk_engine = RiskEngine()
portfolio = Portfolio(cash=1000.0, positions=[], ...)

# 1. Agent generates thesis
thesis = agent.generate_thesis(market)
thesis_store.add(thesis)

# 2. Risk check BEFORE execution
decision = risk_engine.evaluate(thesis, portfolio)

if decision.approved:
    # 3. Execute trade with approved size
    execute_trade(
        market=market,
        side=thesis.proposed_action['side'],
        size_pct=decision.recommended_size
    )
    print(f"✅ Trade executed: {decision.recommended_size}%")
else:
    # 3. Log rejection and skip
    print(f"❌ Trade blocked: {decision.reason}")
    thesis_store.update_status(thesis.id, 'rejected', decision.reason)
```

## Kelly-Like Position Sizing

The `suggest_position_size()` method uses a Kelly-inspired approach:

```python
suggested_size = conviction × edge × max_allowed
```

**Example:**
- Conviction: 0.90 (90% confident)
- Edge: 0.20 (20% expected advantage)
- Max allowed: 20% (position limit)
- **Suggested:** 0.90 × 0.20 × 20% = **3.6%**

This automatically scales position size based on:
- **Confidence** (conviction)
- **Expected profit** (edge)
- **Available capital** (portfolio state)

## Risk Parameter Guidelines

### Conservative (Retail)
```python
{
    'max_position_pct': 10.0,
    'max_deployed_pct': 40.0,
    'min_conviction': 0.80,
    'min_edge': 0.10,
}
```

### Default (Recommended)
```python
{
    'max_position_pct': 20.0,
    'max_deployed_pct': 60.0,
    'min_conviction': 0.70,
    'min_edge': 0.05,
}
```

### Aggressive (Experienced)
```python
{
    'max_position_pct': 30.0,
    'max_deployed_pct': 80.0,
    'min_conviction': 0.60,
    'min_edge': 0.03,
}
```

## Testing Results

```
✅ TEST 1: All Checks Pass - PASS
✅ TEST 2: Position Size Too Large - PASS
✅ TEST 3: Total Deployed Too High - PASS
✅ TEST 4: Conviction Too Low - PASS
✅ TEST 5: Edge Too Small - PASS
✅ TEST 6: Multiple Failures - PASS
✅ TEST 7: Custom Risk Parameters - PASS
✅ TEST 8: Max Position Size Calculation - PASS
✅ TEST 9: Suggest Position Size - PASS
✅ TEST 10: Convenience Functions - PASS
✅ TEST 11: Update Parameters - PASS

🎉 ALL 11 TESTS PASSED!
```

## Why This Matters

**Before Risk Engine:**
- Agent could bet 50% on one trade (concentration risk)
- Could deploy 100% of capital (no reserves)
- Could trade with 0.60 conviction (low confidence)
- Could trade 1% edge (barely profitable after fees)

**After Risk Engine:**
- ✅ Max 20% per position (diversification)
- ✅ Max 60% deployed (40% reserves)
- ✅ Min 70% conviction (high confidence only)
- ✅ Min 5% edge (meaningful advantage)

**Result:** Sustainable, disciplined trading that protects capital.

## Key Features

✅ **4 Safety Checks**: Position, deployment, conviction, edge  
✅ **Detailed Feedback**: Every check explained in risk_notes  
✅ **Custom Parameters**: Override defaults for any risk profile  
✅ **Smart Sizing**: Kelly-like position calculation  
✅ **Convenience API**: Quick checks and boolean helpers  
✅ **Dynamic Updates**: Change params on the fly  
✅ **Comprehensive Testing**: All edge cases covered  

## Next Steps

Ready for:
- **Task 19**: Full system integration with risk gates
- **Task 20**: Live trading with risk monitoring
- **Dashboard**: Real-time risk exposure tracking

---

**Status**: ✅ COMPLETE  
**Time**: 20 minutes  
**Next Task**: Task 19 - System Integration
