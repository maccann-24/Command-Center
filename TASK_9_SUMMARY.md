# TASK 9: Base Agent Interface - COMPLETE

## Files Created

### 1. `agents/base.py` (2.9KB)
Abstract base class for all trading intelligence agents.

#### Class: `BaseAgent(ABC)`

**Abstract Methods (must implement):**

```python
@abstractmethod
def update_theses(self) -> List[Thesis]:
    """
    Generate or update theses based on current market conditions.
    Main entry point called by orchestrator.
    """
    pass

@abstractmethod
def generate_thesis(self, market: Market) -> Thesis:
    """
    Generate a thesis for a specific market.
    Analyzes single market for edge opportunities.
    """
    pass
```

**Abstract Property (must implement):**

```python
@property
@abstractmethod
def mandate(self) -> str:
    """
    The agent's mandate/focus area.
    Examples:
    - "Russia/Ukraine, US-China, Iran, elections"
    - "Follow top traders >55% win rate"
    """
    pass
```

**Concrete Methods (provided):**

```python
def get_cached_theses(self) -> List[Thesis]:
    """Get cached theses from last update_theses() call"""

def clear_cache(self):
    """Clear the thesis cache"""

def __repr__(self) -> str:
    """String representation of the agent"""
```

### 2. `agents/__init__.py` (148B)
Package initialization with exports.

### 3. `test_base_agent.py` (8.2KB)
Comprehensive test suite for BaseAgent.

## Design

### Abstract Base Class Pattern
- Uses Python's `abc.ABC` module
- Enforces interface contract via `@abstractmethod`
- Cannot be instantiated directly
- Subclasses must implement all abstract methods

### Agent Responsibilities

**Each agent must:**
1. Define its mandate (focus area)
2. Implement `update_theses()` to generate trade ideas
3. Implement `generate_thesis(market)` for single-market analysis
4. Return properly structured Thesis objects

**Agents should:**
- Query relevant markets from database
- Calculate fair value vs current odds
- Determine edge and conviction
- Generate actionable theses (or empty list if no opportunities)

### Thesis Cache
Agents maintain internal cache of last generated theses:
- Populated by `update_theses()`
- Accessed via `get_cached_theses()`
- Cleared via `clear_cache()`

## Usage Example

### Creating a Concrete Agent

```python
from agents.base import BaseAgent
from models import Thesis, Market
from typing import List

class MyAgent(BaseAgent):
    """Custom trading agent"""
    
    @property
    def mandate(self) -> str:
        return "My specific trading focus"
    
    def update_theses(self) -> List[Thesis]:
        # 1. Query markets
        markets = get_markets(filters={"category": "crypto"})
        
        # 2. Generate theses
        theses = []
        for market in markets:
            thesis = self.generate_thesis(market)
            if thesis.edge > 0.05:  # Only if edge detected
                theses.append(thesis)
        
        # 3. Cache and return
        self._theses_cache = theses
        return theses
    
    def generate_thesis(self, market: Market) -> Thesis:
        # Analyze market
        fair_value = self._calculate_fair_value(market)
        edge = fair_value - market.yes_price
        conviction = self._calculate_conviction(edge)
        
        # Create thesis
        return Thesis(
            agent_id="my_agent",
            market_id=market.id,
            thesis_text=f"Analysis: {market.question}",
            fair_value=fair_value,
            current_odds=market.yes_price,
            edge=edge,
            conviction=conviction,
            horizon="medium",
            proposed_action={
                "side": "YES",
                "size_pct": conviction * 0.20
            }
        )
```

### Using an Agent

```python
# Create agent instance
agent = MyAgent()

# Get agent info
print(agent.mandate)  # "My specific trading focus"
print(repr(agent))    # MyAgent(mandate='...')

# Generate theses
theses = agent.update_theses()

# Access cached theses
cached = agent.get_cached_theses()

# Clear cache when done
agent.clear_cache()
```

## Test Results

### All Tests Passed ✅

**Test 1: Required Methods**
```
✅ update_theses() defined
✅ generate_thesis() defined
✅ mandate property defined
```

**Test 2: Abstract Enforcement**
```
✅ BaseAgent cannot be instantiated directly
✅ Raises TypeError with "abstract" message
```

**Test 3: Concrete Implementation**
```
✅ TestAgent instantiates successfully
✅ mandate property returns string
✅ update_theses() returns List[Thesis]
✅ generate_thesis(market) returns Thesis
✅ Thesis cache works correctly
✅ Cache clear works
✅ __repr__() works
```

**Test 4: Type Hints**
```
✅ update_theses() return type: List[Thesis]
✅ generate_thesis() return type: Thesis
✅ generate_thesis() parameter type: Market
```

## Interface Contract

### Input: Market Objects
Agents receive Market objects with:
- id, question, category
- yes_price, no_price
- volume_24h, resolution_date
- All metadata needed for analysis

### Output: Thesis Objects
Agents return Thesis objects with:
- agent_id (identifies which agent)
- market_id (links to market)
- thesis_text (human-readable explanation)
- fair_value, current_odds, edge
- conviction (0.0 to 1.0)
- horizon ("short", "medium", "long")
- proposed_action (side + size_pct)

### Guarantees

**BaseAgent guarantees:**
- ✅ Cannot be instantiated (abstract)
- ✅ Subclasses must implement all abstract methods
- ✅ Type safety via type hints
- ✅ Thesis caching mechanism
- ✅ Consistent __repr__ across agents

**Subclasses must guarantee:**
- ✅ Return List[Thesis] from update_theses()
- ✅ Return Thesis from generate_thesis()
- ✅ Provide mandate string
- ✅ Handle errors gracefully (don't crash)

## Integration Points

### With Orchestrator
```python
# Orchestrator calls each agent
for agent in agents:
    theses = agent.update_theses()
    for thesis in theses:
        # Risk evaluation
        # Execution if approved
```

### With Database
```python
# Agents query markets
from database import get_markets, get_news_events

def update_theses(self):
    markets = get_markets(filters={"category": self.category})
    news = get_news_events(filters={"hours_back": 24})
    # Analyze and generate theses
```

### With Thesis Store
```python
# Save theses to database
from core.thesis_store import ThesisStore

store = ThesisStore()
for thesis in agent.update_theses():
    store.save(thesis)
```

## Verification Checklist

- ✅ Created `agents/base.py`
- ✅ Uses ABC module (from abc import ABC, abstractmethod)
- ✅ Defined abstract method: `update_theses()` returns List[Thesis]
- ✅ Defined abstract method: `generate_thesis(market)` returns Thesis
- ✅ Defined abstract property: `mandate` (string)
- ✅ Type hints on all methods
- ✅ Comprehensive docstrings
- ✅ Thesis caching mechanism
- ✅ Cannot instantiate BaseAgent directly
- ✅ Test suite validates interface (all tests pass)
- ✅ Code compiles without errors

## Next Steps

### TASK 10: Signal Generator (15 min)
- Create `agents/signals.py`
- Implement `calculate_event_impact(market, news_events)`
- Return impact score (0.0 to 1.0)

### TASK 11: Geopolitical Agent (25 min)
- Create `agents/geo.py` implementing BaseAgent
- Set mandate = "Russia/Ukraine, US-China, Iran, elections"
- Implement update_theses() using signal generator
- Filter markets by category="geopolitical"
- Calculate edge based on news impact

### TASK 12: Copy Trading Agent Stub (15 min)
- Create `agents/copy.py` implementing BaseAgent
- Set mandate = "Follow top traders >55% win rate"
- Stub implementation (returns empty list for now)

## Files Summary

```
polymarket/agents/
├── __init__.py           - Package exports
└── base.py               - ✅ BaseAgent abstract class (Task 9)

polymarket/
├── test_base_agent.py    - ✅ Test suite (all tests pass)
└── TASK_9_SUMMARY.md     - Documentation
```

**TASK 9 STATUS: COMPLETE ✅**

All requirements met:
- BaseAgent abstract class created
- Abstract methods defined (update_theses, generate_thesis)
- Mandate property defined
- Test suite validates interface
- Ready for agent implementations

Ready for TASK 10.
