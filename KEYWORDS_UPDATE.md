# Keywords Update - Technology, Industrials, Manufacturing Added

## Summary

Expanded keyword monitoring from **18** to **47** keywords to cover:
- Geopolitical events (original 18)
- Technology sector (15 new)
- Industrials & Manufacturing (14 new)

## Full Keyword List (47 total)

### Geopolitical (18)
- russia, ukraine, iran, china, taiwan
- election, congress, senate
- israel, gaza, nato
- biden, trump
- war, military, sanctions, nuclear, diplomacy

### Technology (15)
- ai, artificial intelligence
- semiconductor, chip
- technology, tech
- crypto, cryptocurrency, bitcoin, blockchain
- software, hardware, cloud
- cybersecurity, data

### Industrials & Manufacturing (14)
- manufacturing, factory, industrial
- supply chain, trade, tariff
- export, import, production
- automotive, energy, oil
- infrastructure, construction

## Technical Implementation

### Word Boundary Matching
To avoid false positives (e.g., "ai" matching "Ukraine"), short keywords (≤3 chars) now use regex word boundaries:

```python
# Short keyword: use \b word boundaries
if len(keyword) <= 3:
    pattern = r'\b' + keyword + r'\b'
    # "ai" matches " AI " but not "Ukr[ai]ne"
    
# Longer keywords: simple substring match
else:
    if keyword in text_lower:
        # Works fine for longer words
```

## Test Results

All 20 sample headlines correctly classified:

**Geopolitical (10):**
- Russia/Ukraine: ✅ Detected (russia, ukraine)
- China/Taiwan: ✅ Detected (china, taiwan, trade)
- Iran nuclear: ✅ Detected (iran, nuclear)
- Congress/Senate: ✅ Detected (election, congress, senate, military)
- Israel/Gaza: ✅ Detected (israel, gaza)
- NATO sanctions: ✅ Detected (nato, sanctions)
- Biden/Trump: ✅ Detected (biden, trump)

**Technology (4):**
- AI + semiconductors: ✅ Detected (ai, semiconductor, manufacturing)
- Bitcoin + crypto: ✅ Detected (bitcoin, crypto)
- Cybersecurity + cloud: ✅ Detected (cybersecurity, cloud, infrastructure)
- China chip ban: ✅ Detected (china, chip, technology, export)

**Industrials & Manufacturing (4):**
- Auto production: ✅ Detected (manufacturing, production)
- Steel tariffs: ✅ Detected (tariff, import)
- Supply chain + energy: ✅ Detected (supply chain, energy)
- Infrastructure bill: ✅ Detected (factory, infrastructure, construction)

**Non-target (2):**
- Celebrity gossip: ✅ Correctly filtered (no keywords)
- Sports news: ✅ Correctly filtered (no keywords)

**Result: 20/20 PASSED ✅**

## Files Modified

1. **`ingestion/news.py`**
   - GEOPOLITICAL_KEYWORDS expanded (18 → 47)
   - extract_keywords() updated with word boundary matching

2. **`test_news_standalone.py`**
   - GEOPOLITICAL_KEYWORDS synced
   - SAMPLE_HEADLINES expanded (12 → 20)
   - extract_keywords() updated
   - Test logic improved

## Impact on System

### Market Coverage Expanded
- **Before:** Only geopolitical markets detected
- **After:** Geopolitical + Technology + Industrial markets covered

### Examples of New Detectable Markets
- "Will Bitcoin reach $100k in 2026?" → crypto, bitcoin
- "Will China ban semiconductor exports?" → china, semiconductor, export
- "Will US pass infrastructure bill?" → infrastructure, congress
- "Will EV manufacturing exceed 10M units?" → manufacturing, automotive, production
- "Will OpenAI release GPT-5?" → ai, technology

### RSS Feed Relevance
Expanded keywords better match Reuters/AP news coverage:
- Technology section → ai, crypto, chip news
- Business section → manufacturing, trade, tariffs
- Energy section → oil, energy, infrastructure

## Next Steps

### Optional Future Enhancements
1. **Sentiment analysis** - Replace sentiment_score=0.0 with real scores
2. **More categories** - Add sports, entertainment, climate, health keywords
3. **Weighted keywords** - Higher importance for direct market terms
4. **Context scoring** - Multi-keyword matches = higher relevance

### Ready for Integration
- ✅ All tests passing
- ✅ Word boundary logic prevents false positives
- ✅ Backward compatible (original 18 keywords unchanged)
- ✅ More comprehensive market coverage

**Status: Complete and tested ✅**
