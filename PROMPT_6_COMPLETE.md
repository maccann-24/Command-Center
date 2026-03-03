# PROMPT 6 COMPLETE ✅

**Date:** 2026-03-02  
**Status:** Multi-Turn Debates Implemented  
**Model:** GPT-4o-mini (OpenAI)

---

## ✅ What Was Built

### 1. **Debate State Tracking** - `agents/base.py`

**Added to `BaseAgent.__init__()`:**

```python
# Debate tracking state
self._active_debates: Dict[str, Dict] = {}  # market_id -> debate_state
# debate_state: {
#   'participants': [agent_id1, agent_id2],
#   'turn_count': int,
#   'max_turns': 3,
#   'started_at': datetime,
#   'last_turn_at': datetime,
#   'exchanges': [{'agent': str, 'message': str, 'timestamp': datetime}]
# }
self._debate_cooldowns: Dict[str, datetime] = {}  # market_id -> cooldown_end
```

**Features:**
- ✅ Tracks active debates per market
- ✅ Stores participant list
- ✅ Counts turns (max 3)
- ✅ Records full exchange history
- ✅ Timestamps for each turn
- ✅ 15-minute cooldown after closure

---

### 2. **Debate Context Detection** - Updated `respond_to_mention_with_context()`

**Method signature updated:**

```python
def respond_to_mention_with_context(
    self,
    sender: str,
    question: str,
    message_tags: List[str] = None  # ← NEW parameter
) -> None:
```

**Logic:**
1. Check if message has `'debate'` tag
2. Find market_id from tags
3. If debate is active → Call `_respond_to_debate()`
4. Otherwise → Use regular mention response

**Example:**
```python
# Debate message with tags
respond_to_mention_with_context(
    sender="renaissance_crypto",
    question="My model shows -12% edge...",
    message_tags=['debate', 'btc_100k_march']  # Triggers debate logic
)
```

---

### 3. **Debate-Specific Responses** - `_respond_to_debate()`

**New method in `agents/chat_mixin.py`:**

```python
def _respond_to_debate(self, sender: str, question: str, market_id: str) -> None:
    """
    Respond to a debate message (part of ongoing debate).
    
    Uses debate-specific prompt with:
    - Debate history
    - Data-driven counter-arguments
    - Respectful tone
    - Turn tracking
    """
```

**Features:**
- ✅ Loads full debate history
- ✅ Increments turn count
- ✅ Uses debate-specific LLM prompt
- ✅ Records exchange in history
- ✅ Checks for max turns (3)
- ✅ Triggers closure on final turn

**Debate Prompt:**
```
You're in Turn {turn_count} of a debate.

Debate history:
[Turn 1] goldman_politics: @renaissance_crypto I see +15% edge...
[Turn 2] renaissance_crypto: @goldman_politics My quant model shows...

{sender} just said:
{question}

Generate a data-driven counter-argument (under 200 chars) that:
- Addresses their specific point
- Cites your model/analysis
- Asks a follow-up question
- Stays respectful and analytical

Be professional, not combative.
```

---

### 4. **Graceful Debate Closure** - `_close_debate()`

**New method in `agents/chat_mixin.py`:**

```python
def _close_debate(self, market_id: str, other_agent: str) -> None:
    """
    Close a debate gracefully after max turns reached.
    
    Posts a summary acknowledging different approaches are valid.
    Sets cooldown to prevent immediate re-debate.
    """
```

**Closing Messages (randomly selected):**
- `"@{other_agent} Different models, both valid approaches. Good discussion! 🤝"`
- `"@{other_agent} Interesting debate. We'll see how it plays out. May the best model win! 📊"`
- `"@{other_agent} Appreciate the exchange. Different angles, both data-driven. 👍"`
- `"@{other_agent} Fair points. Time will tell which signals matter more. Good debate! ✅"`

**Actions:**
1. Posts closing message with `['debate_closed', market_id]` tags
2. Removes market from `_active_debates`
3. Sets 15-minute cooldown in `_debate_cooldowns`

---

### 5. **Cooldown Enforcement** - Updated `initiate_debate()`

**Cooldown Logic:**

```python
def initiate_debate(...):
    # Check if debate is on cooldown
    if market_id in self._debate_cooldowns:
        cooldown_end = self._debate_cooldowns[market_id]
        if datetime.utcnow() < cooldown_end:
            print(f"⏳ Debate on {market_id} is on cooldown until {cooldown_end}")
            return  # Block new debate
    
    # Check if debate already active
    if market_id in self._active_debates:
        print(f"⚠️ Debate already active on {market_id}")
        return  # Block duplicate debate
    
    # Create new debate state...
```

**Prevents:**
- ✅ Re-debating same market within 15 minutes
- ✅ Multiple simultaneous debates on same market
- ✅ Infinite debate loops

---

### 6. **Updated Mention Detection** - `detect_mentions()`

**Returns tags now:**

```python
def detect_mentions(self, messages: List[Dict]) -> List[tuple]:
    """
    Returns:
        List of (message_id, sender, question, tags) tuples  # ← tags added
    """
    mentions = []
    
    for msg in messages:
        ...
        tags = msg.get('tags') or []
        mentions.append((message_id, sender, question, tags))  # ← tags included
    
    return mentions
```

**Updated callers:**
```python
# Old
for message_id, sender, question in mentions:
    respond_to_mention_with_context(sender, question)

# New
for message_id, sender, question, tags in mentions:
    respond_to_mention_with_context(sender, question, message_tags=tags)
```

---

## 🧪 Test Results

### **test_multi_turn_debates.py:**

```bash
$ python3 test_multi_turn_debates.py
```

**TEST 1: Initialize debate state** ✅
- Debate state created
- Participants: `['goldman_politics', 'renaissance_crypto']`
- Turn count: 1
- Max turns: 3
- Exchanges: 1

**TEST 2: Turn 1 - Renaissance responds** ✅
- Renaissance debate state updated
- Turn count: 2
- Exchanges: 2
- Sample response:
  ```
  My model indicates +3.1σ bearish pressure from declining on-chain activity
  and negative funding rates. What macro trends are you weighting most?
  ```

**TEST 3: Turn 2 - Goldman counter-response** ✅
- Goldman responds (Turn 3)
- Debate closes automatically after max turns

**TEST 4: Turn 3 (Final) - Debate closure** ✅
- Debate closed after max turns
- Cooldown set (15 minutes remaining)

**TEST 5: Cooldown prevention** ✅
- Re-debate blocked by cooldown
- Message: `⏳ Debate on test_debate_btc_march is on cooldown until 2026-03-02 23:44:09`

**TEST 6: Verify database messages** ✅
- Debate messages found: 4
- Closing messages found: 1
- Sample closing: `@renaissance_crypto Different models, both valid approaches. Good discussion! 🤝`

---

## 📋 Complete Multi-Turn Debate Flow

### **Scenario: Goldman vs Renaissance on BTC**

**Turn 1 - Goldman initiates:**
```
[goldman_politics]: @renaissance_crypto My analysis shows strong institutional
interest and macro trends favoring BTC. I see +15.0% edge. What factors drive
your -12.0% bearish view?

Tags: ['debate', 'btc_100k_march']
Debate state created: turn_count=1, max_turns=3
```

**Turn 2 - Renaissance responds:**
```
[renaissance_crypto]: @goldman_politics My quant model shows +3.1σ bearish
pressure from declining on-chain activity and negative funding rates. What
macro trends are you weighting most?

Tags: ['debate', 'btc_100k_march']
Debate state updated: turn_count=2
Exchange recorded in history
```

**Turn 3 - Goldman counter-responds:**
```
[goldman_politics]: @renaissance_crypto My model weights institutional inflows
(+20% YoY) and ETF adoption. Your on-chain signals valid short-term, but macro
dominates here. Still think fundamentals win long-term.

Tags: ['debate', 'btc_100k_march']
Debate state updated: turn_count=3 (MAX REACHED)
```

**Turn 3 triggers closure - Goldman posts closing:**
```
[goldman_politics]: @renaissance_crypto Different models, both valid approaches.
Good discussion! 🤝

Tags: ['debate_closed', 'btc_100k_march']
Debate removed from _active_debates
Cooldown set: 15 minutes
```

**15 minutes later - Goldman tries to re-debate:**
```
goldman.initiate_debate(...)
→ ⏳ Debate on btc_100k_march is on cooldown until 2026-03-02 23:44:09
→ Blocked
```

**After cooldown expires:**
```
goldman.initiate_debate(...)
→ ✅ New debate allowed
→ Fresh debate state created
```

---

## 🎯 Key Features

### **State Management:**
- ✅ Per-market debate tracking
- ✅ Turn counting (1 → 2 → 3)
- ✅ Full exchange history
- ✅ Timestamps for each turn

### **Debate-Specific Prompts:**
- ✅ Uses debate history as context
- ✅ Encourages data-driven arguments
- ✅ Enforces respectful tone
- ✅ Asks follow-up questions
- ✅ Avoids combative language

### **Loop Prevention:**
- ✅ Max 3 turns per debate
- ✅ Automatic closure after turn 3
- ✅ 15-minute cooldown
- ✅ Prevents duplicate debates

### **Graceful Closure:**
- ✅ "Different models, both valid" messaging
- ✅ Acknowledges learning from debate
- ✅ Tags with `debate_closed`
- ✅ Friendly, professional tone

---

## 📂 Files Created/Modified

**New Files:**
- `test_multi_turn_debates.py` (270 lines) - Comprehensive test suite
- `PROMPT_6_COMPLETE.md` (this file)

**Modified:**
- `agents/base.py` - Added debate state tracking:
  * `self._active_debates`
  * `self._debate_cooldowns`
- `agents/chat_mixin.py` - Added debate methods:
  * Updated `respond_to_mention_with_context()` to detect debates
  * Added `_respond_to_debate()` for debate-specific responses
  * Added `_close_debate()` for graceful closure
  * Updated `initiate_debate()` to create debate state
  * Updated `detect_mentions()` to return tags

---

## 📊 Comparison: Before vs After

| Aspect | PROMPT 5 | PROMPT 6 |
|--------|----------|----------|
| **Debate turns** | Single exchange | Multi-turn (up to 3) |
| **State tracking** | None | Full history |
| **Prompt style** | Generic | Debate-specific |
| **Closure** | None | Automatic after turn 3 |
| **Re-debates** | Unlimited | 15-min cooldown |
| **Context** | Recent chat | Full debate history |
| **Loop prevention** | None | Max turns + cooldown |

---

## ✅ Success Criteria Met

- ✅ Debate state tracking in `agents/base.py`
- ✅ `_active_debates` dict with participants, turn_count, max_turns
- ✅ `respond_to_mention()` detects debate context
- ✅ Debate-specific LLM prompt used
- ✅ Debate history included in context
- ✅ Data-driven counter-arguments generated
- ✅ Debate closes after 3 turns
- ✅ Closing message: "Different models, both valid approaches"
- ✅ Max 3 exchanges enforced
- ✅ 15-minute cooldown prevents re-debate
- ✅ Respectful tone enforced via system prompt
- ✅ Test shows 3-turn exchange + closure

---

## 🚀 What's Next (PROMPT 7+)

**Potential enhancements:**
- Debate winner determination (which model was closer?)
- Multi-agent debates (>2 participants)
- Debate summaries for observers
- Learning from debates (update model weights)
- Debate quality scoring
- Public debate transcripts

---

## 🎉 PROMPT 6 COMPLETE!

**Multi-turn debates fully functional!**

**Key takeaway:** Agents now engage in structured, respectful debates with:
- **3-turn limit** (prevents endless loops)
- **Full history tracking** (context-aware responses)
- **Debate-specific prompts** (data-driven, analytical)
- **Graceful closure** (agree to disagree)
- **Cooldown enforcement** (15-minute pause)

**Example Exchange:**
```
[Turn 1] Goldman: I see +15% edge due to institutional inflows...
[Turn 2] Renaissance: My quant model shows -12% from on-chain signals...
[Turn 3] Goldman: Fair points, but macro fundamentals dominate...
[Closure] Renaissance: Different models, both valid. Good discussion! 🤝
```

---

**Commit:** `TBD` - "Enable multi-turn debates between agents (PROMPT 6)"

---

**Test it:**
```bash
python3 test_multi_turn_debates.py
```

**Expected output:**
```
✅ Features Verified:
  - ✅ Debate state tracking (participants, turns, history)
  - ✅ Turn counting (1 → 2 → 3)
  - ✅ Debate-specific prompts used
  - ✅ Debate closes after max turns (3)
  - ✅ Graceful closure message posted
  - ✅ 15-minute cooldown set
  - ✅ Cooldown prevents re-debate
  - ✅ Debate messages tagged properly

✅ PROMPT 6 COMPLETE - Multi-turn debates working!
```
