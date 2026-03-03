# TASK 11: Geopolitical Agent - COMPLETE

## Files Created

### 1. `agents/geo.py` (11.6KB)
Complete GeopoliticalAgent implementation extending BaseAgent.

#### Class: `GeopoliticalAgent(BaseAgent)`

**Configuration:**
```python
agent_id = "geo"
mandate = "Russia/Ukraine, US-China, Iran, elections, geopolitical events"
min_volume = 100000.0  # $100k minimum 24h volume
min_impact = 0.15  # Minimum news impact to generate thesis
min_edge = 0.05  # Minimum edge to return thesis
```

**Implemented Methods:**

**`update_theses() -> List[Thesis]`**

Workflow:
1. Fetch geopolitical markets (category="geopolitical", volume > $100k)
2. Fetch news events from last 24 hours
3. For each market:
   - Calculate news impact via `calculate_event_impact()`
   - If impact > 0.15: generate thesis
   - If edge > 0.05: include in results
4. Return list of actionable theses

**`generate_thesis(market, news_events) -> Thesis`**

Thesis generation logic:
1. Calculate `impact_score = calculate_event_impact(market, news_events)`
2. Check if `impact_score > 0.15` (minimum threshold)
3. If yes:
   - `fair_value = min(0.95, current_odds + impact_score)` *(capped at 95%)*
   - `edge = fair_value - current_odds`
   - `conviction = min(0.80, impact_score * 3.0)` *(scaled, capped at 80%)*
   - `thesis_text = f"Market underpriced based on {count} recent events: {headlines}..."`
   - `size_pct = conviction * 0.15` *(position size scales with conviction)*
4. Create and return Thesis object

**Helper Methods:**
- `_count_matching_events()` - Count news events matching market keywords
- `_get_event_headlines()` - Get concatenated headlines (truncated to 100 chars)

### 2. `test_geo_agent.py` (11.0KB)
Comprehensive test suite (standalone tests without DB).

### 3. Updated `agents/__init__.py`
Added GeopoliticalAgent export.

## Calculation Examples

### Example 1: Strong Signal (2 matching events)
```
Market: "Will Russia invade Ukraine?"
Current odds: 0.50 (50%)
News: 2 events matching keywords
Impact: 0.40 (2 × 0.20)

Calculations:
- fair_value = min(0.95, 0.50 + 0.40) = 0.90 (90%)
- edge = 0.90 - 0.50 = 0.40 (40%)
- conviction = min(0.80, 0.40 × 3.0) = 0.80 (80%)
- size_pct = 0.80 × 0.15 = 0.12 (12%)

Result: Strong thesis generated ✅
```

### Example 2: Weak Signal (1 event, low impact)
```
Market: "Will peace talks succeed?"
Current odds: 0.60
News: 1 weak event (impact < 0.15)
Impact: 0.10

Check: impact_score (0.10) <= min_impact (0.15)
Result: No thesis generated (signal too weak) ✅
```

### Example 3: No Signal (no keyword overlap)
```
Market: "Will Bitcoin reach $100k?"
News: Geopolitical events (Russia, Ukraine, etc.)

Check: No keyword overlap
Impact: 0.0
Result: No thesis generated ✅
```

## Implementation Details

### Database Queries

**Markets Query:**
```python
markets = get_markets(filters={
    "category": "geopolitical",
    "min_volume": 100000.0,
    "resolved": False
})
```

**News Query:**
```python
news_events = get_news_events(filters={
    "hours_back": 24
})
```

### Thesis Text Generation

Format: `"Market underpriced based on {count} recent events: {headlines}..."`

Example:
```
"Market underpriced based on 2 recent events: Russia announces military 
mobilization near Ukraine border; Ukraine requests emergency NATO meeting..."
```

Headlines truncated to 100 characters if too long.

### Position Sizing

Position size scales with conviction:
- Conviction 60% → Position size 9% (0.60 × 0.15)
- Conviction 70% → Position size 10.5% (0.70 × 0.15)
- Conviction 80% → Position size 12% (0.80 × 0.15)

Maximum position: 12% (when conviction = 80%)

## Risk Controls

### Built-in Caps

1. **Fair Value Cap:** `min(0.95, calculated_value)`
   - Prevents overconfidence
   - Never assumes >95% probability

2. **Conviction Cap:** `min(0.80, impact × 3)`
   - Maximum 80% conviction
   - Leaves room for uncertainty

3. **Position Size Cap:** `conviction × 0.15`
   - Maximum 12% of portfolio (at 80% conviction)
   - Scales down with lower conviction

### Filtering

1. **Minimum Impact:** Signal must be >0.15 to generate thesis
2. **Minimum Edge:** Thesis must have >5% edge to be actionable
3. **Minimum Volume:** Only analyzes markets with >$100k volume

## Usage Example

### Standalone Usage
```python
from agents.geo import GeopoliticalAgent
from database import get_markets, get_news_events

# Create agent
agent = GeopoliticalAgent()

# Generate theses
theses = agent.update_theses()

# Process theses
for thesis in theses:
    print(f"Market: {thesis.market_id}")
    print(f"Edge: {thesis.edge:.2%}")
    print(f"Conviction: {thesis.conviction:.0%}")
    print(f"Size: {thesis.proposed_action['size_pct']:.1%}")
```

### Integration with Orchestrator
```python
# In orchestrator
agents = [
    GeopoliticalAgent(),
    # Other agents...
]

for agent in agents:
    theses = agent.update_theses()
    
    for thesis in theses:
        # Risk evaluation
        decision = risk_engine.evaluate(thesis, portfolio)
        
        # Execute if approved
        if decision.approved:
            execution_engine.execute(decision, thesis)
```

## Verification Checklist

- ✅ Created `agents/geo.py`
- ✅ Extends BaseAgent
- ✅ Mandate set to "Russia/Ukraine, US-China, Iran, elections, geopolitical events"
- ✅ Implements `update_theses()` method
- ✅ Fetches geopolitical markets (category filter)
- ✅ Filters by volume > 100,000
- ✅ Fetches 24h news events
- ✅ Uses `calculate_event_impact()` from signals.py
- ✅ Filters by impact > 0.15
- ✅ Calculates fair_value: `min(0.95, current_odds + impact)`
- ✅ Calculates edge: `fair_value - current_odds`
- ✅ Calculates conviction: `min(0.80, impact × 3.0)`
- ✅ Generates thesis_text with event count and headlines
- ✅ Calculates position size: `conviction × 0.15`
- ✅ Creates Thesis objects
- ✅ Filters by edge > 0.05
- ✅ Returns List[Thesis]
- ✅ Code compiles without errors
- ✅ Exported in agents/__init__.py

## Output Example

When running `agent.update_theses()`:

```
============================================================
🌍 GEOPOLITICAL AGENT - Updating Theses
============================================================
📊 Fetched 15 geopolitical markets (volume > $100,000)
📰 Fetched 23 news events (last 24h)
✅ Thesis generated: Will Russia invade Ukraine in 2026?... (edge: 40.00%)
✅ Thesis generated: Will US impose new China sanctions?... (edge: 25.00%)
⏭️  Skipped: Will Iran nuclear talks succeed?... (no signal or low edge)
⏭️  Skipped: Will there be peace by year end?... (no signal or low edge)

📈 Generated 2 actionable theses
============================================================
```

## Integration Points

### With Thesis Store (Task 13)
```python
from core.thesis_store import ThesisStore

agent = GeopoliticalAgent()
store = ThesisStore()

theses = agent.update_theses()
for thesis in theses:
    store.save(thesis)
```

### With Risk Engine (Task 14-15)
```python
from core.risk import RiskEngine

risk_engine = RiskEngine()
agent = GeopoliticalAgent()

theses = agent.update_theses()
for thesis in theses:
    decision = risk_engine.evaluate(thesis, portfolio)
    
    if decision.approved:
        print(f"Approved: {thesis.thesis_text[:50]}...")
    else:
        print(f"Rejected: {decision.reason}")
```

## Next Steps

### TASK 12: Copy Trading Agent Stub (15 min)
- Create `agents/copy.py` extending BaseAgent
- Mandate: "Follow top traders >55% win rate"
- Stub implementation (returns empty list)
- TODO comment for future implementation

### TASK 13: Thesis Store (10 min)
- Create `core/thesis_store.py`
- Methods: save(), get_actionable(), get_by_market()

### Future Enhancements (v2)
1. **More sophisticated signal scoring**
   - Weight by source credibility
   - Sentiment integration
   - Recency weighting

2. **Category-specific logic**
   - Different formulas for elections vs conflicts
   - Event-type specific adjustments

3. **Multi-timeframe analysis**
   - Short-term signals (last 6h)
   - Medium-term signals (last 24h)
   - Long-term signals (last week)

## Files Summary

```
polymarket/agents/
├── __init__.py                  - Updated exports
├── base.py                      - ✅ BaseAgent (Task 9)
├── signals.py                   - ✅ Signal generator (Task 10)
└── geo.py                       - ✅ GeopoliticalAgent (Task 11)

polymarket/
├── test_geo_agent.py            - ✅ Test suite
└── TASK_11_SUMMARY.md           - Documentation
```

**TASK 11 STATUS: COMPLETE ✅**

All requirements met:
- GeopoliticalAgent extends BaseAgent
- Mandate defined correctly
- update_theses() implemented
- Signal-based thesis generation
- All calculations match specification
- Risk controls in place
- Ready for orchestrator integration

Ready for TASK 12 (Copy Trading Agent Stub).
