# TASK 10: Signal Generator - COMPLETE

## Files Created

### 1. `agents/signals.py` (9.2KB)
Signal generation functions for calculating news event impact on markets.

#### Main Function:

**`calculate_event_impact(market, news_events) -> float`**

Calculates impact score (0.0 to 1.0) based on keyword overlap between market question and news events.

**Algorithm:**
1. Extract keywords from market question
2. Check each news event for keyword overlap
3. Count matching events
4. Calculate score: 0.20 per event, capped at 0.40

**Returns:**
- `0.0` = No news impact
- `0.20` = One relevant news event
- `0.40` = Multiple relevant news events (capped)

**Example:**
```python
market = Market(question="Will Russia invade Ukraine?")
news = [NewsEvent(headline="Ukraine reports border activity", keywords=["ukraine"])]
score = calculate_event_impact(market, news)
# score = 0.20 (one matching event)
```

#### Helper Functions:

**`extract_keywords_from_question(question) -> List[str]`**

Extracts keywords from market question:
1. Lowercase and split on whitespace
2. Remove stop words (will, the, be, etc.)
3. Strip punctuation (including $, #, @)
4. Filter short words (<3 chars)
5. Remove duplicates

**Example:**
```python
extract_keywords_from_question("Will Bitcoin reach $100k in 2026?")
# Returns: ['bitcoin', 'reach', '100k', '2026']
```

**`has_keyword_overlap(market_keywords, news_keywords) -> bool`**

Checks if any keywords overlap between market and news.

**`get_matching_keywords(market_keywords, news_keywords) -> List[str]`**

Returns list of matching keywords (useful for debugging).

### 2. `test_signals_standalone.py` (9.6KB)
Comprehensive standalone test suite.

### 3. Updated `agents/__init__.py`
Added signal function exports.

## Signal Scoring Logic

### Basic Case (Task Specification)
```
Market: "Will Russia invade Ukraine?"
News: headline contains "Ukraine"
Result: impact_score = 0.20 ✅
```

### Multiple Events
```
Market: "Will Russia invade Ukraine?"
News Events: 2 matching events
Calculation: 2 × 0.20 = 0.40
Result: impact_score = 0.40 ✅
```

### Capping
```
Market: "Will Russia invade Ukraine?"
News Events: 3+ matching events
Calculation: 3 × 0.20 = 0.60 → capped at 0.40
Result: impact_score = 0.40 ✅
```

### No Overlap
```
Market: "Will Bitcoin reach $100k?"
News: about Russia (no crypto keywords)
Result: impact_score = 0.0 ✅
```

## Keyword Extraction

### Stop Words Filtered (30+)
Common words removed:
- Articles: the, a, an
- Verbs: will, be, is, are, was, were, has, have, had, do, does, did
- Prepositions: in, on, at, to, for, of, by, from
- Conjunctions: and, or, but, not
- Question words: what, who, which, where, when, how, why
- Time: before, after, during, while
- Pronouns: this, that, these, those, it, its

### Punctuation Stripped
All punctuation removed:
- Standard: .,;:!?()[]{}
- Financial: $#@%&*
- Hyphens and quotes

### Length Filter
Words must be ≥3 characters after stripping.

## Test Results

### All Tests Passed (5/5) ✅

**Test 1: Basic Case (Task Spec)**
```
Market: "Will Russia invade Ukraine?"
News: "Ukraine military reports border activity"
Keywords match: ['ukraine']
✅ PASSED: impact_score = 0.20
```

**Test 2: Keyword Extraction**
```
✅ "Will Russia invade Ukraine?" → ['russia', 'invade', 'ukraine']
✅ "Will Bitcoin reach $100k in 2026?" → ['bitcoin', 'reach', '100k', '2026']
✅ "The quick brown fox" → ['quick', 'brown', 'fox']
```

**Test 3: No Overlap**
```
Market: "Will Bitcoin reach $100k?"
News: "Russia announces new policy"
✅ PASSED: impact_score = 0.0 (no matching keywords)
```

**Test 4: Multiple Events**
```
Market: "Will Russia invade Ukraine?"
News: 2 events matching
✅ PASSED: impact_score = 0.40 (2 × 0.20)
```

**Test 5: Score Capping**
```
Market: "Will Russia invade Ukraine?"
News: 3+ events matching
✅ PASSED: impact_score = 0.40 (capped from 0.60)
```

## Usage Examples

### Basic Usage
```python
from agents.signals import calculate_event_impact
from database import get_markets, get_news_events

# Get market and recent news
market = get_markets(filters={"id": "market_123"})[0]
news = get_news_events(filters={"hours_back": 24})

# Calculate impact
impact = calculate_event_impact(market, news)

if impact > 0.15:
    print(f"Strong signal detected: {impact:.2%}")
```

### Integration with Agent
```python
from agents.signals import calculate_event_impact
from agents.base import BaseAgent

class MyAgent(BaseAgent):
    def generate_thesis(self, market):
        # Get recent news
        news = get_news_events(filters={"hours_back": 24})
        
        # Calculate impact
        impact = calculate_event_impact(market, news)
        
        if impact > 0.15:
            # Detected signal, generate thesis
            fair_value = market.yes_price + impact
            edge = fair_value - market.yes_price
            
            return Thesis(
                agent_id=self.agent_id,
                market_id=market.id,
                thesis_text=f"News impact detected: {impact:.0%}",
                fair_value=fair_value,
                current_odds=market.yes_price,
                edge=edge,
                conviction=min(0.80, impact * 2),
                proposed_action={"side": "YES", "size_pct": 0.15}
            )
```

### Debugging Signal
```python
from agents.signals import (
    calculate_event_impact,
    get_matching_keywords,
    extract_keywords_from_question
)

# Extract market keywords
market_kw = extract_keywords_from_question(market.question)
print(f"Market keywords: {market_kw}")

# Check each news event
for news in news_events:
    matches = get_matching_keywords(market_kw, news.keywords)
    if matches:
        print(f"Match found: {matches}")
        print(f"  News: {news.headline}")
```

## Signal Strength Interpretation

| Score | Interpretation | Recommended Action |
|-------|---------------|-------------------|
| 0.0 | No signal | Skip market |
| 0.20 | Weak signal (1 event) | Consider if other factors align |
| 0.40 | Strong signal (2+ events) | High priority for analysis |

## Integration Points

### With GeopoliticalAgent (Task 11)
```python
class GeopoliticalAgent(BaseAgent):
    def update_theses(self):
        markets = get_markets(filters={"category": "geopolitical"})
        news = get_news_events(filters={"hours_back": 24})
        
        theses = []
        for market in markets:
            impact = calculate_event_impact(market, news)
            
            if impact > 0.15:  # Minimum signal threshold
                thesis = self.generate_thesis(market)
                theses.append(thesis)
        
        return theses
```

### With Thesis Store
Signal scores can be stored in thesis.details for later analysis:
```python
thesis.details = {
    "signal_score": impact,
    "matching_events": len(matching_events),
    "signal_source": "news_impact"
}
```

## Verification Checklist

- ✅ Created `agents/signals.py`
- ✅ Implemented `calculate_event_impact(market, news_events)`
- ✅ Extracts keywords from market.question (lowercase, split)
- ✅ Checks for keyword overlap with news events
- ✅ Returns 0.20 for single match
- ✅ Returns min(0.40, 0.20 × match_count) for multiple
- ✅ Returns 0.0 for no overlap
- ✅ Test: Mock market "Russia Ukraine" + news with "Ukraine"
- ✅ Test verification: impact_score = 0.20
- ✅ All 5 tests passing
- ✅ Code compiles without errors
- ✅ Exported in agents/__init__.py

## Future Enhancements (v2)

### Signal Sophistication
1. **Weighted keywords** - Important terms weighted higher
2. **Recency decay** - Older news has less impact
3. **Sentiment integration** - Use sentiment_score field
4. **Source credibility** - Reuters weighted higher than unknown sources

### Advanced Matching
1. **Fuzzy matching** - "Ukraine" matches "Ukrainian"
2. **Synonyms** - "Bitcoin" matches "BTC", "crypto"
3. **Entity extraction** - Recognize proper nouns
4. **Context analysis** - Positive vs negative news

### Multi-Signal
1. **Combine multiple signal types** - News + trader activity + market momentum
2. **Signal confidence** - Bayesian updating
3. **Signal decay** - Reduce impact over time

## Files Summary

```
polymarket/agents/
├── __init__.py                  - Updated exports
├── base.py                      - ✅ BaseAgent (Task 9)
└── signals.py                   - ✅ Signal generator (Task 10)

polymarket/
├── test_signals_standalone.py   - ✅ Test suite (5/5 passed)
└── TASK_10_SUMMARY.md           - Documentation
```

**TASK 10 STATUS: COMPLETE ✅**

All requirements met:
- Signal generator implemented
- Keyword extraction working
- Impact scoring correct (0.20 baseline, 0.40 cap)
- Test case validated (0.20 for single match)
- All tests passing
- Ready for agent integration

Ready for TASK 11 (Geopolitical Agent).
