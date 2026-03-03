# Data Ingestion Setup Guide

**Quick start guide to configure data sources for BASED MONEY**

---

## Environment Variables

Create a `.env` file in your project root:

```bash
# ============================================
# TRADING
# ============================================
TRADING_MODE=paper  # or 'live'

# ============================================
# DATABASE
# ============================================
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# ============================================
# DATA SOURCES (Optional - add as needed)
# ============================================

# Twitter API v2 (RECOMMENDED - $100/mo)
# Get from: https://developer.twitter.com/en/portal/dashboard
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# ProPublica Congress API (FREE)
# Get from: https://www.propublica.org/datastore/api/propublica-congress-api
PROPUBLICA_API_KEY=your_propublica_key

# OpenWeatherMap API (FREE tier available)
# Get from: https://openweathermap.org/api
OPENWEATHER_API_KEY=your_openweather_key

# NewsAPI.org (Optional - $449/mo for real-time)
# Get from: https://newsapi.org/
NEWSAPI_KEY=your_newsapi_key

# Glassnode (Optional - $29-799/mo for crypto on-chain)
# Get from: https://glassnode.com/
GLASSNODE_API_KEY=your_glassnode_key

# CoinGecko Pro (Optional - free tier works well)
# Get from: https://www.coingecko.com/en/api
COINGECKO_API_KEY=your_coingecko_key  # Only needed for Pro tier
```

---

## Setup Steps

### 1. Free Tier (Start Here)

**No credit card required, $0/month:**

#### a) Twitter API v2 (Free tier available)

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Sign up for a developer account
3. Create a new app
4. Generate a Bearer Token
5. Add to `.env`: `TWITTER_BEARER_TOKEN=...`

**Free tier limits:**
- 500,000 tweets/month
- 10,000 tweets/month with "Elevated" access (need to apply)

**Recommended:** Apply for Elevated access (free, approved in 24-48h)

---

#### b) ProPublica Congress API

1. Go to https://www.propublica.org/datastore/api/propublica-congress-api
2. Fill out the form (instant approval)
3. Receive API key via email
4. Add to `.env`: `PROPUBLICA_API_KEY=...`

**Free tier:**
- 5,000 requests/day
- No credit card required

---

#### c) OpenWeatherMap

1. Go to https://openweathermap.org/api
2. Sign up for free account
3. Subscribe to "Free" plan (no credit card)
4. Get API key from dashboard
5. Add to `.env`: `OPENWEATHER_API_KEY=...`

**Free tier:**
- 1,000 calls/day
- 60 calls/minute
- Current weather + 5-day forecast

---

### 2. Test Your Setup

Run the demo script:

```bash
cd /home/ubuntu/clawd/agents/coding
python ingestion/multi_source_ingestion.py
```

**Expected output:**
```
MULTI-SOURCE INGESTION DEMO
============================================================

1. Breaking News (keywords: 'Trump', 'Biden')
  - [reuters] Trump announces...
  - [bbc_politics] Biden signs...

2. Google News (query: 'Ukraine war')
  - Latest updates from Ukraine...

3. Twitter Search (query: '#Bitcoin')
  - @user123: Bitcoin price hits...

... etc ...

DEMO COMPLETE
```

---

### 3. Add to Agent Workflow

#### Update `agents/base.py`:

```python
from ingestion.multi_source_ingestion import MultiSourceIngestion

class BaseAgent:
    def __init__(self, agent_id: str, theme: str, mandate: str):
        self.agent_id = agent_id
        self.theme = theme
        self.mandate = mandate
        self.ingestion = MultiSourceIngestion()  # NEW
    
    def update_theses(self) -> List[Thesis]:
        """Generate theses with real-time data."""
        theses = []
        
        # Get active markets
        markets = self.get_active_markets()
        
        for market in markets:
            # Gather context using ingestion system
            context = self.ingestion.gather_context_for_market(
                market.question,
                self.theme
            )
            
            # Generate thesis with context
            thesis = self.generate_thesis(market, context)
            if thesis:
                theses.append(thesis)
        
        return theses
```

---

## API Key Priority

### Start with these (all FREE):

1. ✅ **Twitter API** (free tier or $100/mo Elevated)
   - Most important for all themes
   - First to break news (0-5 min latency)

2. ✅ **ProPublica Congress** (free)
   - Essential for US Politics theme
   - Official government data

3. ✅ **OpenWeatherMap** (free tier)
   - Essential for Weather theme
   - 1,000 calls/day is plenty

4. ✅ **Google News RSS** (free, no key needed)
   - Already integrated
   - Works out of the box

5. ✅ **Reddit API** (free, no key needed)
   - Social sentiment
   - Already integrated

6. ✅ **PredictIt API** (free, no key needed)
   - Competitor market data
   - Already integrated

7. ✅ **CoinGecko** (free tier, no key needed)
   - Crypto prices
   - Already integrated

**Total cost: $0-100/mo** (free if you skip Twitter Elevated)

---

### Add later (paid):

8. 💰 **NewsAPI.org** ($449/mo)
   - Real-time news (2-5 min latency)
   - Only get if you need speed advantage

9. 💰 **Glassnode** ($29-799/mo)
   - Crypto on-chain metrics
   - High alpha for crypto markets

10. 💰 **Nansen** ($150-1,000/mo)
    - Whale wallet tracking
    - Very high alpha but expensive

---

## Testing Individual Sources

### Test Twitter:

```python
from ingestion.multi_source_ingestion import MultiSourceIngestion

ingestion = MultiSourceIngestion()
tweets = ingestion.search_twitter('#Bitcoin', max_results=10)

for tweet in tweets:
    print(f"@{tweet['author_username']}: {tweet['text']}")
```

### Test News:

```python
news = ingestion.get_breaking_news(['Trump', 'Biden'], hours=24)

for article in news:
    print(f"[{article['source']}] {article['title']}")
```

### Test Congress:

```python
bills = ingestion.get_congress_bills(days=7)

for bill in bills:
    print(f"{bill['bill_id']}: {bill['title']}")
```

### Test Crypto:

```python
prices = ingestion.get_crypto_prices(['bitcoin', 'ethereum'])

for coin, data in prices.items():
    print(f"{coin}: ${data['usd']:,.2f} ({data['usd_24h_change']:+.2f}%)")
```

### Test Weather (US):

```python
# Chicago coordinates
forecast = ingestion.get_noaa_forecast(41.8781, -87.6298)

if forecast:
    periods = forecast['properties']['periods']
    for period in periods[:3]:
        print(f"{period['name']}: {period['detailedForecast']}")
```

---

## Rate Limiting Best Practices

### 1. Cache Responses

```python
import time
from functools import lru_cache

class MultiSourceIngestion:
    @lru_cache(maxsize=100)
    def get_breaking_news_cached(self, keywords_tuple, hours):
        """Cached version - expires after 5 minutes."""
        return self.get_breaking_news(list(keywords_tuple), hours)
```

### 2. Respect Rate Limits

```python
import time

def rate_limited_call(func, delay_seconds=1):
    """Wrapper to add delay between calls."""
    result = func()
    time.sleep(delay_seconds)
    return result
```

### 3. Use Exponential Backoff

```python
import time

def retry_with_backoff(func, max_retries=3):
    """Retry with exponential backoff on failure."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s...")
            time.sleep(wait_time)
```

---

## Monitoring

### Log All API Calls

```python
import logging

logging.basicConfig(
    filename='ingestion.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('ingestion')

# In your code:
logger.info(f"Fetching news for keywords: {keywords}")
logger.warning(f"Rate limit hit for source: {source}")
logger.error(f"API error: {error}")
```

### Track API Usage

```sql
-- Create table to track API usage
CREATE TABLE api_usage_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    source TEXT NOT NULL,          -- 'twitter', 'newsapi', etc.
    endpoint TEXT,                   -- Specific endpoint
    status_code INT,                 -- HTTP status code
    response_time_ms INT,            -- Latency
    cost_estimate DECIMAL            -- If API has per-call cost
);

CREATE INDEX idx_api_usage_timestamp ON api_usage_log(timestamp DESC);
CREATE INDEX idx_api_usage_source ON api_usage_log(source);
```

---

## Troubleshooting

### Issue: "Twitter API not configured"

**Fix:** Add `TWITTER_BEARER_TOKEN` to `.env`

```bash
# Get token from https://developer.twitter.com/en/portal/dashboard
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAxxxxxx
```

---

### Issue: "Rate limit exceeded"

**Symptoms:** HTTP 429 errors

**Fix 1:** Add delays between calls
```python
time.sleep(1)  # 1 second between requests
```

**Fix 2:** Use caching to reduce calls
```python
@lru_cache(maxsize=100)
def cached_function(...):
    pass
```

**Fix 3:** Upgrade to paid tier (if necessary)

---

### Issue: "No news articles found"

**Possible causes:**
- Keywords too specific
- Time window too short
- RSS feeds down

**Fix:** Broaden keywords, increase time window
```python
# Instead of:
news = ingestion.get_breaking_news(['specific', 'exact', 'phrase'], hours=2)

# Try:
news = ingestion.get_breaking_news(['specific', 'exact'], hours=24)
```

---

### Issue: "NOAA forecast returns empty"

**Cause:** Location outside USA

**Fix:** Use OpenWeatherMap instead (global coverage)
```python
forecast = ingestion.get_openweather_forecast(lat, lon)
```

---

## Next Steps

1. ✅ Configure free API keys (Twitter, ProPublica, OpenWeather)
2. ✅ Run demo script to verify setup
3. ✅ Update agents to use `ingestion.gather_context_for_market()`
4. ✅ Test with real markets
5. ✅ Monitor API usage logs
6. ✅ Gradually add paid sources as you prove ROI

---

## Summary

**Free tier gives you:**
- Breaking news (15-30 min latency)
- Social sentiment (Twitter, Reddit)
- US politics data (Congress, polls)
- Crypto prices (real-time)
- Weather forecasts (global)
- Competitor markets (PredictIt)

**This is enough to start generating profitable theses!**

**Add paid sources later as you validate alpha:**
- NewsAPI → faster news (2-5 min latency)
- Glassnode → crypto on-chain signals
- Nansen → whale tracking

**Start cheap, scale up based on performance!**

---

**Last Updated:** 2026-03-02  
**Questions?** Review `DATA_SOURCES_GUIDE.md` for full source details
