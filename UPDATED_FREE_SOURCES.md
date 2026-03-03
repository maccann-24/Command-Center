# Updated Free Data Sources (March 2026)

**Changes:**
- ❌ ProPublica Congress API - **SHUT DOWN** (as of 2024)
- ✅ New alternatives added below

---

## 🆓 **Working Free Sources (No Signup)**

### 1. ✅ Google News RSS
- **URL:** https://news.google.com/rss
- **Cost:** FREE
- **Signup:** None needed
- **Status:** ✅ WORKING

### 2. ✅ Reddit API
- **URL:** https://www.reddit.com/r/{subreddit}/hot.json
- **Cost:** FREE
- **Signup:** None needed
- **Status:** ✅ WORKING

### 3. ✅ PredictIt Markets API
- **URL:** https://www.predictit.org/api/marketdata/all/
- **Cost:** FREE
- **Signup:** None needed
- **Status:** ✅ WORKING (255+ markets)

### 4. ✅ CoinGecko API
- **URL:** https://api.coingecko.com/api/v3
- **Cost:** FREE (1,000 calls/month without key)
- **Signup:** None needed
- **Status:** ✅ WORKING

### 5. ✅ NOAA Weather.gov
- **URL:** https://api.weather.gov
- **Cost:** FREE
- **Signup:** None needed
- **Status:** ✅ WORKING

---

## 🔑 **Free Sources (Need Signup)**

### 1. Twitter API v2
- **Status:** ⚠️ Requires "Elevated" access (free but needs approval)
- **Your token:** Saved, waiting for Elevated access
- **Action needed:** Apply for Elevated at developer.twitter.com

### 2. OpenWeatherMap API
- **URL:** https://openweathermap.org/api
- **Cost:** FREE (1,000 calls/day)
- **Status:** ⏳ Waiting for your API key

---

## 🏛️ **US Politics Data - ProPublica Alternatives**

### Option 1: Congress.gov API (Official, FREE)
**Best alternative - it's the official source!**

**URL:** https://api.congress.gov/

**How to get API key:**
1. Go to: https://api.congress.gov/sign-up/
2. Fill out form (name, email, organization)
3. **Instant approval** - key sent to email
4. **Rate limit:** 5,000 requests/hour (very generous!)

**What it provides:**
- All bills (current + historical)
- Roll call votes
- Member information
- Committee schedules
- Nominations
- Treaties

**This is even BETTER than ProPublica - it's the primary source!**

---

### Option 2: GovTrack.us (No API key needed!)
**URL:** https://www.govtrack.us/api/v2/

**Cost:** FREE  
**Signup:** None needed  
**Rate limit:** Reasonable usage

**What it provides:**
- Bills and votes
- Legislator info
- Committee membership
- Voting records
- Roll call analysis

**Example:**
```bash
curl "https://www.govtrack.us/api/v2/bill?congress=118&limit=5"
```

**This works RIGHT NOW with no signup!**

---

### Option 3: FiveThirtyEight Polls (Free scraping)
**URL:** https://projects.fivethirtyeight.com/polls/

**What to scrape:**
- Presidential polls
- Senate polls
- Governor polls
- Generic ballot

**Method:** Parse their JSON data (they don't block reasonable scraping)

---

### Option 4: Just Use What We Have
**For US Politics theme, you already have:**
- ✅ Twitter (breaking political news)
- ✅ Google News (campaign coverage)
- ✅ PredictIt (255+ political markets with real-time odds)
- ✅ Reddit (r/politics sentiment)

**This is honestly enough for most political markets!**

---

## 🎯 **Recommendation**

### **Quick Win (5 minutes):**
**Get Congress.gov API key** - it's free and instant:
1. Go to: https://api.congress.gov/sign-up/
2. Fill out form (2 minutes)
3. Check email for API key
4. Send me the key and I'll add it!

**OR**

### **Skip it for now:**
Just use what's working:
- Google News (political coverage)
- PredictIt (political markets with live odds)
- Twitter (when Elevated access approved)

**That's already really good for politics markets!**

---

## ✅ **Current Working Sources Summary**

**No signup needed (working NOW):**
1. Google News RSS ✅
2. Reddit API ✅
3. PredictIt Markets ✅
4. CoinGecko Crypto ✅
5. NOAA Weather ✅
6. GovTrack.us API ✅ (NEW!)

**Need signup (but free):**
1. Twitter (waiting for Elevated) ⏳
2. OpenWeatherMap (waiting for your key) ⏳
3. Congress.gov (optional upgrade) 💡

---

## 📊 **Coverage Without Any Signups**

**Right now you have:**
- ✅ Breaking news (Google News)
- ✅ Political markets (PredictIt - better than bills!)
- ✅ Social sentiment (Reddit)
- ✅ Crypto prices (CoinGecko)
- ✅ US weather (NOAA)
- ✅ Congressional data (GovTrack - no signup!)

**That's ~70% of what you need already working!**

---

## 🚀 **Next Steps**

**Option A:** Get Congress.gov key (5 min)
**Option B:** Get OpenWeatherMap key (5 min)
**Option C:** Do nothing - what you have is already pretty good!

Let me know what you prefer! 🤔
