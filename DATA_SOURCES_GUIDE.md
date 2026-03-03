# Data Sources & APIs Guide for BASED MONEY

**Purpose:** Provide agents with high-quality, real-time data for thesis generation  
**Priority:** Speed + Coverage > Depth (on prediction markets, news breaks fast)  
**Last Updated:** 2026-03-02

---

## Table of Contents

1. [Geopolitical Theme Data Sources](#geopolitical-theme)
2. [US Politics Theme Data Sources](#us-politics-theme)
3. [Crypto Theme Data Sources](#crypto-theme)
4. [Weather Theme Data Sources](#weather-theme)
5. [Cross-Cutting Data Sources](#cross-cutting)
6. [Polymarket-Specific Data](#polymarket-data)
7. [Implementation Priority](#implementation-priority)
8. [Cost Analysis](#cost-analysis)
9. [Integration Guide](#integration-guide)

---

## Geopolitical Theme

### 🔥 **Critical (High Alpha)**

#### 1. **Twitter/X API (Essential)**
- **Why:** First to break geopolitical news, often 15-60 min before traditional media
- **What to track:**
  - Verified diplomats, government officials
  - Top foreign policy journalists (NYT, WSJ, Reuters, BBC)
  - Think tanks (CFR, Brookings, CSIS)
  - Regional experts
- **API:** Twitter API v2 (Elevated access ~$100/mo for real-time)
- **Implementation:** 
  - Create Twitter lists by region/topic
  - Stream tweets with keyword filters
  - Parse sentiment, urgency signals
- **Example handles:**
  - @JakeSullivan46 (US NSA)
  - @ReutersWorld
  - @AFP
  - @BBCBreaking
  - Regional experts per market

#### 2. **Reuters News API**
- **Why:** Fast, reliable, global coverage
- **API:** Reuters Connect (enterprise, contact sales)
- **Alternative:** NewsAPI.org ($449/mo for live articles)
- **Coverage:** Breaking news, politics, conflicts, elections
- **Latency:** ~2-5 minutes from event

#### 3. **GDELT Project (FREE)**
- **Why:** Monitors global news in 100 languages, tracks events/conflicts
- **API:** https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/
- **Data:**
  - Event database (CAMEO codes for conflict, cooperation)
  - Tone/sentiment of news
  - Geographic mapping
- **Latency:** 15-minute updates
- **Cost:** FREE (!!!)
- **Integration:** Query by country, event type, date range

#### 4. **ACLED (Armed Conflict Location & Event Data)**
- **Why:** Best database for tracking conflicts, protests, violence
- **API:** https://acleddata.com/data-export-tool/
- **Data:** Real-time conflict events, casualties, locations
- **Cost:** Free for < 5,000 requests/day
- **Use case:** Track escalation/de-escalation in conflict zones

#### 5. **UN/WHO/Government Press Releases**
- **Sources:**
  - UN News (https://news.un.org/en/feed)
  - WHO updates (https://www.who.int/feeds)
  - State Department (https://www.state.gov/rss-feeds/)
  - UK Foreign Office (https://www.gov.uk/government/latest)
- **Format:** RSS feeds (FREE)
- **Latency:** 15-60 minutes
- **Use case:** Official announcements before they hit mainstream news

### 📊 **Medium Priority**

- **Google Trends API:** Track search interest spikes (free)
- **Reddit API:** r/geopolitics, r/worldnews sentiment (free)
- **Al Jazeera RSS:** MENA-focused coverage (free)
- **Telegram channels:** War monitors (Ukraine, Israel, etc.) - manual scraping

---

## US Politics Theme

### 🔥 **Critical (High Alpha)**

#### 1. **FiveThirtyEight Polls API**
- **Why:** Most comprehensive US political polling aggregator
- **Data:** Presidential, Senate, House, gubernatorial polls
- **API:** No official API, but data available at https://projects.fivethirtyeight.com/polls/
- **Scraping:** Parse JSON from their site (they don't block reasonable scraping)
- **Frequency:** Daily updates
- **Cost:** FREE

#### 2. **ProPublica Congress API (FREE)**
- **Why:** Official congressional data - bills, votes, members
- **API:** https://projects.propublica.org/api-docs/congress-api/
- **Data:**
  - Recent bills
  - Roll call votes
  - Member statements
  - Committee schedules
- **Rate limit:** 5,000 requests/day (free)
- **Latency:** Same-day updates
- **Use case:** Track legislative momentum on Polymarket questions

#### 3. **Twitter Political Feeds**
- **Why:** Politicians announce intentions/positions directly
- **Who to follow:**
  - All Senators/Representatives
  - Campaign accounts
  - Political journalists (Politico, The Hill, CNN, Fox)
  - Campaign strategists
- **API:** Twitter API v2 (same as geopolitical)
- **Filters:** Keywords like "announce", "support", "oppose", "will vote"

#### 4. **PredictIt API (Competitor Markets)**
- **Why:** Cross-market arbitrage, sentiment comparison
- **API:** https://www.predictit.org/api/marketdata/all/
- **Data:** All market odds, volume, last trade time
- **Frequency:** Every 60 seconds
- **Cost:** FREE
- **Use case:** Detect when PredictIt moves before Polymarket (or vice versa)

#### 5. **Ballotpedia API**
- **Why:** Comprehensive election data, ballot measures, candidate info
- **API:** https://ballotpedia.org/API-documentation
- **Data:** Elections, candidates, positions, endorsements
- **Cost:** Free tier available
- **Use case:** Research candidates for state/local markets

#### 6. **RealClearPolitics Data**
- **Why:** Poll aggregation, electoral college forecasts
- **Source:** https://www.realclearpolitics.com/
- **Format:** Scrape (no official API)
- **Frequency:** Daily
- **Cost:** FREE

### 📊 **Medium Priority**

- **FEC API (Campaign Finance):** Track fundraising as proxy for viability (free)
- **Google Civic Info API:** Election dates, polling places (free)
- **The Hill / Politico RSS:** Breaking political news (free)
- **C-SPAN Schedule:** Track hearings, votes (free scraping)

---

## Crypto Theme

### 🔥 **Critical (High Alpha)**

#### 1. **CoinGecko API**
- **Why:** Most comprehensive free crypto data
- **API:** https://www.coingecko.com/en/api
- **Data:**
  - Price, volume, market cap (all coins)
  - 24h change, ATH/ATL
  - Social metrics (Twitter followers, Reddit subscribers)
- **Rate limit:** 10-50 calls/min (free tier)
- **Pro plan:** $129/mo for higher limits
- **Latency:** ~30 seconds

#### 2. **Glassnode API (On-Chain Metrics)**
- **Why:** On-chain data predicts price moves
- **API:** https://docs.glassnode.com/api/
- **Data:**
  - Exchange flows (whales moving coins)
  - Active addresses
  - MVRV ratio (market value vs realized value)
  - Miner revenue/flows
  - HODLer behavior
- **Cost:** $29-$799/mo (expensive but high alpha)
- **Use case:** Detect accumulation/distribution before price moves

#### 3. **Nansen API (Whale Tracking)**
- **Why:** Track smart money (VCs, funds, whales)
- **API:** https://docs.nansen.ai/
- **Data:**
  - Wallet labels ("Smart Money", "Fund")
  - Token flows
  - DEX trades by wallet type
- **Cost:** $150-$1,000/mo
- **High alpha potential:** See what VCs are buying before retail

#### 4. **Dune Analytics API**
- **Why:** Custom on-chain queries (DeFi, NFTs, protocols)
- **API:** https://dune.com/docs/api/
- **Data:** Custom SQL queries on Ethereum, Polygon, etc.
- **Cost:** $99-$390/mo for API access
- **Use case:** Build custom dashboards for specific Polymarket questions

#### 5. **CryptoQuant API**
- **Why:** Exchange reserve tracking (supply shock indicator)
- **API:** https://cryptoquant.com/api-doc
- **Data:**
  - Exchange reserves (BTC/ETH leaving = bullish)
  - Miner flows
  - Stablecoin supply
- **Cost:** $39-$799/mo

#### 6. **Twitter Crypto Sentiment**
- **Who to follow:**
  - @VitalikButerin
  - @APompliano
  - @CryptoCobain
  - @saylor (MicroStrategy)
  - SEC/regulatory accounts
- **API:** Same Twitter API v2

#### 7. **CoinMarketCap API (Backup to CoinGecko)**
- **API:** https://coinmarketcap.com/api/
- **Free tier:** 333 calls/day
- **Pro tier:** $79-$2,999/mo

### 📊 **Medium Priority**

- **Whale Alert (Twitter bot):** Free whale movement tracking
- **Alternative.me Crypto Fear & Greed Index:** Market sentiment (free)
- **CryptoCompare API:** Another price/volume source (free tier)
- **DeFi Llama API:** TVL tracking (free)
- **Reddit API:** r/cryptocurrency, r/bitcoin sentiment (free)

---

## Weather Theme

### 🔥 **Critical (High Alpha)**

#### 1. **NOAA APIs (FREE, US-focused)**
- **Why:** Most authoritative US weather data
- **APIs:**
  - **Weather.gov API:** https://www.weather.gov/documentation/services-web-api
  - **NOAA CDO (Climate Data Online):** https://www.ncdc.noaa.gov/cdo-web/webservices/v2
- **Data:**
  - Current conditions
  - 7-day forecasts
  - Severe weather alerts
  - Historical data
- **Cost:** FREE
- **Rate limit:** Generous (no hard limit, just be reasonable)
- **Coverage:** USA only

#### 2. **OpenWeatherMap API**
- **Why:** Global coverage, historical + forecast
- **API:** https://openweathermap.org/api
- **Data:**
  - Current weather (200+ countries)
  - 5-day / 3-hour forecast
  - 16-day daily forecast
  - Historical data (40 years)
  - Extreme weather alerts
- **Free tier:** 1,000 calls/day (60/min)
- **Paid:** $40-$180/mo for more calls
- **Latency:** ~10 minutes

#### 3. **Visual Crossing Weather API**
- **Why:** Best free historical data, excellent for backtesting
- **API:** https://www.visualcrossing.com/weather-api
- **Data:**
  - 15-day forecast
  - Historical weather (1970-present)
  - Weather timeline queries
- **Free tier:** 1,000 records/day
- **Paid:** $50-$600/mo
- **Use case:** "Will it rain more than X inches in May?" - check historical May data

#### 4. **Windy API (Forecast Models)**
- **Why:** Shows multiple forecast models (GFS, ECMWF) - consensus vs outliers
- **API:** https://api.windy.com/
- **Data:**
  - Point forecasts
  - Model comparison (GFS vs ECMWF)
  - Wind, precipitation, temperature
- **Free tier:** 100 calls/day
- **Paid:** €25-€100/mo
- **Use case:** "European model says snow, US model says no snow" - detect uncertainty

#### 5. **WeatherAPI.com**
- **Why:** Simple, reliable, generous free tier
- **API:** https://www.weatherapi.com/
- **Data:**
  - Current conditions
  - 10-day forecast
  - Astronomy (sunrise/sunset)
  - Alerts
  - Historical (2015-present)
- **Free tier:** 1M calls/mo (!)
- **Paid:** $4-$40/mo
- **Best value for money**

#### 6. **European Centre (ECMWF) Data**
- **Why:** Often more accurate than US models for global forecasts
- **Source:** https://www.ecmwf.int/
- **Access:** Through partner APIs (Windy, Meteomatics)
- **Cost:** Via partners (not directly accessible for free)

### 📊 **Medium Priority**

- **Dark Sky API (now Apple):** Hyper-local, minute-by-minute (deprecated but archives available)
- **Meteomatics API:** Professional weather data (expensive, €500+/mo)
- **Weather Underground (IBM):** Historical data (free tier limited)
- **National Hurricane Center RSS:** Tropical forecasts (free)

---

## Cross-Cutting Data Sources

### Essential for All Themes

#### 1. **NewsAPI.org**
- **Why:** Aggregates 80,000+ news sources globally
- **API:** https://newsapi.org/
- **Data:** Headlines, full articles, sources by category/keyword
- **Free tier:** 100 requests/day (development only)
- **Paid:** $449/mo (business tier with live articles)
- **Coverage:** All themes

#### 2. **Google News RSS**
- **Why:** Free, fast, comprehensive
- **Format:** RSS feeds by topic/keyword
- **Example:** https://news.google.com/rss/search?q=biden
- **Cost:** FREE
- **Latency:** 5-15 minutes
- **Parse with:** feedparser (Python library)

#### 3. **Reddit API**
- **Why:** Crowdsourced intelligence, early meme detection
- **API:** https://www.reddit.com/dev/api/
- **Relevant subs:**
  - r/worldnews, r/geopolitics (geopolitical)
  - r/politics, r/Conservative (US politics)
  - r/cryptocurrency, r/bitcoin (crypto)
  - r/weather (weather)
- **Free tier:** 60 requests/min
- **Latency:** Real-time

#### 4. **Telegram Scraping**
- **Why:** Many news channels, war monitors, crypto alpha groups
- **How:** Telethon library (Python)
- **Channels:**
  - War monitors (Ukraine, Israel)
  - Crypto alpha groups
  - Political insiders
- **Cost:** FREE (self-host)
- **Legal:** Check ToS, scrape public channels only

#### 5. **Google Trends API**
- **Why:** Detect sudden interest spikes (leading indicator)
- **API:** pytrends (unofficial Python library)
- **Data:** Search interest over time, related queries
- **Cost:** FREE
- **Use case:** "Kim Jong-un health" search spike → NK leadership market

---

## Polymarket-Specific Data

### 1. **Polymarket CLOB API**
- **Why:** Your primary data source for odds, volume, liquidity
- **API:** py-clob-client (already integrated)
- **Data:**
  - Real-time odds (bid/ask)
  - Trade volume
  - Open interest
  - Market metadata
- **Frequency:** Poll every 5-30 seconds
- **Cost:** FREE

### 2. **Polymarket Historical Data**
- **Why:** Backtesting, pattern recognition
- **Source:** Archive market snapshots in your database
- **Schema:**
  ```sql
  CREATE TABLE market_snapshots (
    market_id TEXT,
    timestamp TIMESTAMP,
    yes_price DECIMAL,
    no_price DECIMAL,
    volume_24h DECIMAL,
    liquidity DECIMAL
  );
  ```
- **Frequency:** Every 5-15 minutes
- **Use case:** "Odds moved 10% in 1 hour → news broke"

### 3. **Polymarket Activity Feed**
- **Why:** See large trades, new markets
- **API:** Via CLOB API
- **Data:** Recent trades, sizes, directions
- **Use case:** "Whale just bought $50k YES → investigate why"

---

## Implementation Priority

### Phase 1: Foundation (Week 1)
**Goal:** Get basic news + Polymarket data flowing

**High Priority:**
1. ✅ Polymarket CLOB API (already done)
2. Google News RSS (free, fast)
3. Twitter API v2 (essential for all themes)
4. Reddit API (free, useful)
5. Basic news scraping (Reuters, BBC RSS)

**Output:** Agents receive:
- Current Polymarket odds
- Breaking news (15-30 min latency)
- Social sentiment signals

---

### Phase 2: Theme-Specific (Week 2-3)
**Goal:** Add theme-specialized data

**Geopolitical:**
- GDELT Project (free, excellent)
- ACLED conflict data (free)
- UN/government RSS feeds

**US Politics:**
- FiveThirtyEight polls (free scraping)
- ProPublica Congress API (free)
- PredictIt API (free competitor data)

**Crypto:**
- CoinGecko API (free tier)
- Glassnode (paid, start with $29/mo tier)
- Whale Alert Twitter (free)

**Weather:**
- NOAA Weather.gov API (free, US)
- OpenWeatherMap (free tier)
- Visual Crossing (free tier)

**Output:** Agents receive theme-specific signals

---

### Phase 3: Premium Data (Month 2+)
**Goal:** Add high-alpha paid sources

**Budget ~$500-1,000/mo:**
- NewsAPI.org business tier ($449/mo) - real-time news
- Glassnode (crypto on-chain) ($79/mo)
- Nansen (whale tracking) ($150/mo)
- Dune Analytics ($99/mo)
- Remaining budget: Twitter Blue API, weather upgrades

**Output:** 15-60 minute alpha advantage

---

### Phase 4: Advanced (Month 3+)
**Goal:** Custom data pipelines, ML models

- Sentiment analysis on all text data
- Custom Dune queries
- Historical backtesting database
- Real-time alert system (Telegram/Discord)
- Automated thesis generation triggers

---

## Cost Analysis

### Free Tier (Month 1)
**Total Cost:** $0-100/mo (just Twitter API)

**Data Sources:**
- Google News RSS (free)
- Reddit API (free)
- GDELT Project (free)
- ACLED (free tier)
- ProPublica Congress (free)
- FiveThirtyEight (free scraping)
- PredictIt API (free)
- NOAA/Weather.gov (free)
- OpenWeatherMap (free tier)
- Visual Crossing (free tier)
- CoinGecko (free tier)
- Polymarket CLOB (free)

**Coverage:** ~70% of critical data

---

### Basic Paid Tier (Month 2)
**Total Cost:** ~$250-350/mo

**Add:**
- Twitter API v2 Elevated ($100/mo)
- Glassnode Starter ($29/mo)
- Dune Analytics Basic ($99/mo)
- OpenWeatherMap upgrade ($40/mo)
- Weather API Pro ($4/mo)

**Coverage:** ~85% of critical data

---

### Premium Tier (Month 3+)
**Total Cost:** ~$750-1,200/mo

**Add:**
- NewsAPI.org Business ($449/mo)
- Nansen Core ($150/mo)
- Glassnode Advanced ($79/mo)
- CryptoQuant Pro ($79/mo)

**Coverage:** ~95% of critical data
**Alpha advantage:** 15-60 minutes on breaking news

---

## Integration Guide

### Step 1: Create Ingestion Module

**File:** `ingestion/data_sources.py`

```python
"""
Unified data ingestion for all sources.
"""

import os
import requests
import feedparser
from datetime import datetime
from typing import List, Dict
import tweepy

class DataIngestion:
    def __init__(self):
        self.twitter_client = self._init_twitter()
        self.news_sources = self._init_news_feeds()
        
    def _init_twitter(self):
        """Initialize Twitter API client."""
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        return tweepy.Client(bearer_token=bearer_token)
    
    def _init_news_feeds(self):
        """Initialize RSS feed URLs."""
        return {
            'reuters': 'https://www.reutersagency.com/feed/',
            'bbc': 'http://feeds.bbci.co.uk/news/world/rss.xml',
            'un': 'https://news.un.org/feed/subscribe/en/news/all/rss.xml',
            'google_politics': 'https://news.google.com/rss/search?q=politics',
        }
    
    def get_breaking_news(self, keywords: List[str], hours: int = 24) -> List[Dict]:
        """Fetch breaking news matching keywords."""
        articles = []
        
        # RSS feeds
        for source, url in self.news_sources.items():
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:  # Latest 10
                if any(kw.lower() in entry.title.lower() for kw in keywords):
                    articles.append({
                        'source': source,
                        'title': entry.title,
                        'link': entry.link,
                        'published': entry.published,
                        'summary': entry.get('summary', '')
                    })
        
        return articles
    
    def search_twitter(self, query: str, max_results: int = 100) -> List[Dict]:
        """Search recent tweets."""
        tweets = self.twitter_client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=['created_at', 'public_metrics', 'author_id']
        )
        
        return [
            {
                'text': tweet.text,
                'created_at': tweet.created_at,
                'likes': tweet.public_metrics['like_count'],
                'retweets': tweet.public_metrics['retweet_count']
            }
            for tweet in tweets.data or []
        ]
    
    def get_congress_bills(self, days: int = 7) -> List[Dict]:
        """Fetch recent congressional bills."""
        api_key = os.getenv('PROPUBLICA_API_KEY')
        url = f"https://api.propublica.org/congress/v1/bills/recent.json"
        
        headers = {'X-API-Key': api_key}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()['results'][0]['bills'][:20]
        return []
    
    def get_crypto_prices(self, coins: List[str] = ['bitcoin', 'ethereum']) -> Dict:
        """Fetch crypto prices from CoinGecko."""
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': ','.join(coins),
            'vs_currencies': 'usd',
            'include_24hr_change': True,
            'include_24hr_vol': True
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return {}
    
    def get_weather_forecast(self, lat: float, lon: float) -> Dict:
        """Fetch weather forecast from NOAA."""
        # Get grid point
        url = f"https://api.weather.gov/points/{lat},{lon}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            forecast_url = data['properties']['forecast']
            
            # Get forecast
            forecast_response = requests.get(forecast_url)
            if forecast_response.status_code == 200:
                return forecast_response.json()
        
        return {}
```

---

### Step 2: Update Agent Base Class

**File:** `agents/base.py` (modify)

```python
class BaseAgent:
    def __init__(self, agent_id: str, theme: str, mandate: str):
        self.agent_id = agent_id
        self.theme = theme
        self.mandate = mandate
        self.data_ingestion = DataIngestion()  # NEW
    
    def gather_context(self, market: Market) -> Dict:
        """
        Gather relevant context for a market.
        Override in subclass for theme-specific data.
        """
        context = {
            'market': market,
            'news': [],
            'social': [],
            'specialist_data': {}
        }
        
        # Default: fetch news matching market question
        keywords = self._extract_keywords(market.question)
        context['news'] = self.data_ingestion.get_breaking_news(keywords, hours=24)
        
        return context
    
    def _extract_keywords(self, question: str) -> List[str]:
        """Extract keywords from market question."""
        # Simple keyword extraction (can be improved with NLP)
        stopwords = {'will', 'the', 'be', 'in', 'on', 'at', 'by', 'to', 'of', 'a', 'an'}
        words = question.lower().split()
        return [w for w in words if w not in stopwords and len(w) > 3]
```

---

### Step 3: Add Theme-Specific Data Methods

**Example: Crypto Agent**

```python
class RenaissanceCryptoAgent(BaseAgent):
    def gather_context(self, market: Market) -> Dict:
        """Gather crypto-specific data."""
        context = super().gather_context(market)
        
        # Crypto-specific data
        if 'bitcoin' in market.question.lower() or 'btc' in market.question.lower():
            context['specialist_data']['price'] = self.data_ingestion.get_crypto_prices(['bitcoin'])
            context['social'] = self.data_ingestion.search_twitter('#Bitcoin', max_results=50)
        
        if 'ethereum' in market.question.lower() or 'eth' in market.question.lower():
            context['specialist_data']['price'] = self.data_ingestion.get_crypto_prices(['ethereum'])
        
        return context
```

---

### Step 4: Store Ingested Data

**Schema:** `ingestion_log` table

```sql
CREATE TABLE ingestion_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    source TEXT NOT NULL,          -- 'twitter', 'rss', 'api'
    data_type TEXT NOT NULL,        -- 'news', 'social', 'price', 'weather'
    theme TEXT,                     -- 'geopolitical', 'crypto', etc.
    content JSONB NOT NULL,         -- Raw data
    keywords TEXT[],                -- For searching
    relevance_score DECIMAL         -- Optional: ML-scored relevance
);

CREATE INDEX idx_ingestion_timestamp ON ingestion_log(timestamp DESC);
CREATE INDEX idx_ingestion_theme ON ingestion_log(theme);
CREATE INDEX idx_ingestion_keywords ON ingestion_log USING GIN(keywords);
```

---

## Best Practices

### 1. **Rate Limiting**
- Always respect API rate limits
- Use exponential backoff on failures
- Cache responses when possible

### 2. **Data Freshness**
- News: Refresh every 5-15 minutes
- Social media: Stream real-time or poll every 1-5 minutes
- Prices: Real-time or every 30-60 seconds
- Weather: Refresh every 30-60 minutes (forecasts don't change that fast)

### 3. **Deduplication**
- Hash article titles/content to avoid processing duplicates
- Store in `ingestion_log` with unique constraint

### 4. **Relevance Filtering**
- Not all news is relevant to active markets
- Score articles by keyword match to open positions
- Only send high-relevance data to agents

### 5. **Error Handling**
- Don't let one API failure crash the whole system
- Log errors, continue with available data
- Fallback to secondary sources

---

## Quick Start Recommendation

**Start with this stack (all FREE except Twitter):**

1. **Twitter API v2** ($100/mo) - Essential for all themes
2. **Google News RSS** (free) - Breaking news
3. **Reddit API** (free) - Social sentiment
4. **GDELT** (free) - Geopolitical events
5. **ProPublica Congress** (free) - US politics
6. **PredictIt** (free) - Competitor data
7. **CoinGecko** (free) - Crypto prices
8. **NOAA Weather.gov** (free) - US weather
9. **OpenWeatherMap** (free tier) - Global weather

**Total cost:** ~$100/mo  
**Coverage:** 70%+ of critical data  
**Speed:** 5-30 minute latency on breaking news

Then **gradually add premium sources** as you prove alpha:
- Month 2: +NewsAPI ($449) for real-time news
- Month 3: +Glassnode ($79) for crypto on-chain
- Month 4: +Nansen ($150) for whale tracking

---

## Summary

**Speed hierarchy (fastest to slowest):**
1. Twitter (0-5 min from event)
2. Telegram (0-10 min)
3. NewsAPI/Reuters (2-15 min)
4. Google News RSS (5-30 min)
5. Reddit (10-60 min)
6. Official announcements (15-120 min)

**Value hierarchy (highest alpha per $):**
1. Twitter API (essential, $100/mo)
2. GDELT (excellent, FREE)
3. ProPublica Congress (excellent, FREE)
4. PredictIt API (excellent, FREE)
5. CoinGecko (great, FREE)
6. NOAA (great, FREE)
7. NewsAPI (good, $449/mo)
8. Glassnode (good, $79+/mo)

**Start cheap, scale up as you prove ROI!**

---

**Last Updated:** 2026-03-02  
**Next Review:** After 1 month of live trading (to optimize based on what actually generates alpha)
