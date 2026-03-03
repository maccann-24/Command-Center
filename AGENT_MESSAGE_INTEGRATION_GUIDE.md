# Agent Message Integration Guide

**How to add Trading Floor messages to your agents**

This guide shows how to integrate `post_message()` calls into all your agents to enable real-time communication on the Trading Floor.

---

## ✅ **Already Updated:**

- **TwoSigmaGeoAgent** - Full integration complete (see `agents/twosigma_geo.py`)

---

## 📋 **Pattern to Apply to All Agents:**

### **Step 1: When Starting Analysis**

Add at the **beginning** of `generate_thesis()`:

```python
def generate_thesis(self, market: Market) -> Optional[Thesis]:
    """Generate thesis for a market."""
    
    # 1️⃣ POST: Starting analysis
    self.post_message(
        'analyzing',
        market_question=market.question,
        market_id=market.id,
        current_odds=market.yes_price,
        status='analyzing'
    )
    
    # Your existing analysis logic...
```

---

### **Step 2: When Thesis is Rejected**

Add **before returning None** (for each rejection case):

#### **Insufficient Edge:**
```python
if abs(edge) < self.min_edge:
    # 2️⃣ POST: Rejected (insufficient edge)
    self.post_message(
        'alert',
        market_question=market.question,
        market_id=market.id,
        current_odds=market.yes_price,
        reasoning=f"Rejected: Edge {abs(edge):.1%} below minimum {self.min_edge:.1%}",
        status='rejected',
        tags=['rejected', 'insufficient_edge']
    )
    return None
```

#### **Low Conviction:**
```python
if conviction < self.min_conviction:
    # 2️⃣ POST: Rejected (low conviction)
    self.post_message(
        'alert',
        market_question=market.question,
        market_id=market.id,
        current_odds=market.yes_price,
        reasoning=f"Rejected: Conviction {conviction:.1%} below minimum {self.min_conviction:.1%}",
        status='rejected',
        tags=['rejected', 'low_conviction']
    )
    return None
```

#### **Other Rejections:**
```python
if some_other_condition:
    # 2️⃣ POST: Rejected (custom reason)
    self.post_message(
        'alert',
        market_question=market.question,
        reasoning=f"Rejected: {your_reason_here}",
        status='rejected',
        tags=['rejected', 'your_tag']
    )
    return None
```

---

### **Step 3: When Thesis is Generated**

Add **after creating the Thesis object, before returning it**:

```python
# Create thesis
thesis = Thesis(
    agent_id=self.agent_id,
    market_id=market.id,
    # ... other fields
)

# Estimate capital allocation (if not calculated elsewhere)
# Simple heuristic: assume $833 per agent, scale by position size
capital_allocated = 83.30 * thesis.proposed_action["size_pct"] / 0.15

# 3️⃣ POST: Thesis generated
self.post_message(
    'thesis',
    market_question=market.question,
    market_id=market.id,
    current_odds=market.yes_price,
    thesis_odds=thesis.fair_value,
    edge=thesis.edge,
    conviction=thesis.conviction,
    capital_allocated=capital_allocated,
    reasoning=thesis.thesis_text[:500],  # Truncate if too long
    signals={
        'data_source_1': 'value',
        'data_source_2': 'value',
        # Include whatever signals your agent used
    },
    status='thesis_generated',
    related_thesis_id=thesis.id,
    tags=[
        self.theme,  # e.g., 'geopolitical', 'crypto'
        'bullish' if thesis.edge > 0 else 'bearish',
        # Add agent-specific tags
    ]
)

return thesis
```

---

## 🎯 **Complete Example: Goldman Geo Agent**

Here's how to update `agents/goldman_geo.py`:

```python
def generate_thesis(self, market: Market) -> Optional[Thesis]:
    """Generate fundamental analysis thesis."""
    
    # 1️⃣ START: Analyzing
    self.post_message(
        'analyzing',
        market_question=market.question,
        market_id=market.id,
        current_odds=market.yes_price,
        status='analyzing'
    )
    
    # Your analysis logic
    news = self._fetch_news(market)
    fair_value = self._calculate_fair_value(market, news)
    edge = fair_value - market.yes_price
    conviction = self._calculate_conviction(edge, news)
    
    # 2️⃣ REJECTION: Insufficient edge
    if abs(edge) < self.min_edge:
        self.post_message(
            'alert',
            market_question=market.question,
            market_id=market.id,
            current_odds=market.yes_price,
            reasoning=f"Rejected: Edge {abs(edge):.1%} < {self.min_edge:.1%}",
            status='rejected',
            tags=['rejected', 'insufficient_edge']
        )
        return None
    
    # 2️⃣ REJECTION: Low conviction
    if conviction < self.min_conviction:
        self.post_message(
            'alert',
            market_question=market.question,
            market_id=market.id,
            current_odds=market.yes_price,
            reasoning=f"Rejected: Conviction {conviction:.1%} < {self.min_conviction:.1%}",
            status='rejected',
            tags=['rejected', 'low_conviction']
        )
        return None
    
    # Create thesis
    thesis = Thesis(
        agent_id=self.agent_id,
        market_id=market.id,
        thesis_text=f"Goldman fundamental analysis...",
        fair_value=fair_value,
        current_odds=market.yes_price,
        edge=edge,
        conviction=conviction,
        horizon="long",
        proposed_action={"side": "YES" if edge > 0 else "NO", "size_pct": 0.10}
    )
    
    # 3️⃣ SUCCESS: Thesis generated
    self.post_message(
        'thesis',
        market_question=market.question,
        market_id=market.id,
        current_odds=market.yes_price,
        thesis_odds=fair_value,
        edge=edge,
        conviction=conviction,
        capital_allocated=83.30 * 0.10 / 0.15,  # Scale by position size
        reasoning=thesis.thesis_text[:500],
        signals={'news_count': len(news), 'sentiment': 'positive'},
        status='thesis_generated',
        related_thesis_id=thesis.id,
        tags=['fundamental', 'geopolitical', 'bullish' if edge > 0 else 'bearish']
    )
    
    # 4️⃣ CHECK: Detect conflicts and consensus
    from core.message_utils import check_all_after_thesis
    check_all_after_thesis(market.id)
    
    return thesis
```

---

## 📝 **Quick Reference: All Message Types**

### **1. 'analyzing'** - Agent is researching
```python
self.post_message('analyzing',
    market_question=...,
    current_odds=...,
    status='analyzing')
```

### **2. 'thesis'** - Agent generated a trade idea
```python
self.post_message('thesis',
    market_question=...,
    market_id=...,
    current_odds=...,
    thesis_odds=...,
    edge=...,
    conviction=...,
    capital_allocated=...,
    reasoning=...,
    signals={...},
    status='thesis_generated',
    related_thesis_id=...)
```

### **3. 'alert'** - Rejection or warning
```python
self.post_message('alert',
    market_question=...,
    reasoning="Rejected: ...",
    status='rejected',
    tags=['rejected', 'reason'])
```

### **4. 'conflict'** - System-generated (don't use in agents)
Automatically created by `detect_conflicts()` in `core/message_utils.py`

### **5. 'consensus'** - System-generated (don't use in agents)
Automatically created by `detect_consensus()` in `core/message_utils.py`

---

## ✅ **Checklist: Update All 12 Agents**

Apply the pattern to each agent:

### **Geopolitical Theme:**
- [x] TwoSigmaGeoAgent (`twosigma_geo.py`) ✅ **DONE**
- [ ] GoldmanGeoAgent (`goldman_geo.py`)
- [ ] BridgewaterGeoAgent (`bridgewater_geo.py`)

### **US Politics Theme:**
- [ ] RenaissancePoliticsAgent (`renaissance_politics.py`)
- [ ] JPMorganPoliticsAgent (`jpmorgan_politics.py`)
- [ ] GoldmanPoliticsAgent (`goldman_politics.py`)

### **Crypto Theme:**
- [ ] MorganStanleyCryptoAgent (`morganstanley_crypto.py`)
- [ ] RenaissanceCryptoAgent (`renaissance_crypto.py`)
- [ ] CitadelCryptoAgent (`citadel_crypto.py`)

### **Weather Theme:**
- [ ] RenaissanceWeatherAgent (`renaissance_weather.py`)
- [ ] MorganStanleyWeatherAgent (`morganstanley_weather.py`)
- [ ] BridgewaterWeatherAgent (`bridgewater_weather.py`)

---

## 🧪 **Testing:**

After updating agents, test with:

```bash
# Run test to generate sample messages
python tests/test_trading_floor_messages.py

# Check messages in database
# (Use Supabase dashboard or query agent_messages table)
```

---

## 💡 **Tips:**

1. **Don't overthink signals** - Include whatever data sources you used:
   ```python
   signals={
       'news': 12,
       'social_sentiment': 0.65,
       'polls': [{'pollster': 'X', 'result': 0.52}]
   }
   ```

2. **Keep reasoning concise** - Truncate if needed:
   ```python
   reasoning=thesis.thesis_text[:500]  # First 500 chars
   ```

3. **Use descriptive tags** - Helps filter on Trading Floor:
   ```python
   tags=[self.theme, 'high_conviction', 'bullish', 'election']
   ```

4. **Capital allocation** - Simple heuristic works fine:
   ```python
   capital_allocated = 83.30 * proposed_action["size_pct"] / 0.15
   # Assumes $833 per agent, scales by position size
   ```

---

## 🚀 **Next Steps:**

1. Update remaining 11 agents (use TwoSigma as template)
2. Run agents to generate test messages
3. Build Trading Floor UI page
4. Add conflict/consensus detection

---

**Questions?** Check `agents/twosigma_geo.py` for the complete working example.
