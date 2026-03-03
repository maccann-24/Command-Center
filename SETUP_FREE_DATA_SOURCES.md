# Setup Guide: Free Data Sources (Step-by-Step)

**Time required:** ~30 minutes  
**Cost:** $0 (all free, no credit card needed)  
**Result:** Your agents get breaking news, social sentiment, political data, crypto prices, weather forecasts

---

## 📋 **Checklist**

- [ ] Twitter API v2 (Essential - breaking news)
- [ ] ProPublica Congress API (US Politics data)
- [ ] OpenWeatherMap API (Weather forecasts)
- [ ] Google News RSS (No signup - already works!)
- [ ] Reddit API (No signup - already works!)
- [ ] PredictIt API (No signup - already works!)
- [ ] CoinGecko API (No signup - already works!)
- [ ] NOAA Weather.gov (No signup - already works!)

**3 require signup, 5 work immediately!**

---

## 🚀 **Step 1: Twitter API v2 (MOST IMPORTANT)**

**Why:** First to break news (0-5 min latency), essential for all themes  
**Free tier:** 500,000 tweets/month (plenty for our use case)

### **1.1 Create Twitter Developer Account**

**Go to:** https://developer.twitter.com/en/portal/petition/essential/basic-info

**You'll see a form. Fill it out like this:**

**Question: What is your name?**
```
[Your full name]
```

**Question: What country do you live in?**
```
[Your country]
```

**Question: What is your use case?**
```
Select: "Making a bot"
```

**Question: Will you make Twitter content or derived information available to a government entity?**
```
Select: "No"
```

Click **"Next"**

---

### **1.2 Describe Your Use Case**

**Question: In your own words, describe how you plan to use Twitter data:**

**Paste this (modify as needed):**
```
I am building an automated trading system that analyzes prediction markets 
(like Polymarket). My system uses Twitter data to:

1. Monitor breaking news in real-time (geopolitics, US politics, crypto, weather)
2. Track sentiment around specific events/topics related to active markets
3. Identify early signals before they appear in mainstream media
4. Aggregate opinions from verified accounts (politicians, journalists, analysts)

The data will be used internally for algorithmic trading decisions. No Twitter 
content will be displayed publicly or shared with third parties. I will respect 
all rate limits and Terms of Service.

Expected usage: ~10,000 API calls per day (well within free tier limits).
```

**Question: Will your app use Tweet, Retweet, Like, Follow, or Direct Message functionality?**
```
Select: "No"
```

**Question: Do you plan to analyze Twitter data?**
```
Select: "Yes"
```

**Question: Will your analysis make Twitter content or derived information available to a government entity?**
```
Select: "No"
```

Click **"Next"**

---

### **1.3 Review and Submit**

- Read the Developer Agreement
- Check "I have read and agree to the Developer Agreement"
- Check your email checkbox
- Click **"Submit"**

**You'll receive an email to verify your email address. Click the link!**

---

### **1.4 Create an App**

After verification, you'll be logged into the Developer Portal.

**Click:** "Create Project"

**Project name:**
```
BASED-MONEY-Trading
```

**Use case:**
```
Select: "Making a bot"
```

**Description:**
```
Automated prediction market trading system using real-time Twitter data
```

Click **"Next"**

**App environment:**
```
Select: "Development"
```

**App name:**
```
based-money-bot
```

Click **"Next"**

---

### **1.5 Get Your Keys**

You'll see a screen with:
- API Key
- API Key Secret
- Bearer Token ← **THIS IS WHAT YOU NEED!**

**Copy the Bearer Token** (starts with `AAAAAAAAAA...`)

**Important:** Save it somewhere! Twitter only shows it once.

If you lose it, you can regenerate it later from the "Keys and tokens" tab.

---

### **1.6 Add to .env File**

**Open your .env file:**
```bash
nano /home/ubuntu/clawd/agents/coding/.env
```

**Add this line:**
```bash
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAxxxxxx_YOUR_TOKEN_HERE
```

**Save and exit:** Ctrl+X, then Y, then Enter

---

### **1.7 (Optional) Apply for Elevated Access**

**Free tier limits:**
- 500,000 tweets/month (caps at ~16,000/day)

**Elevated access (still free!):**
- 2,000,000 tweets/month (caps at ~66,000/day)

**If you want Elevated access:**

1. Go to Developer Portal
2. Click "Products" → "Twitter API v2"
3. Click "Apply for Elevated"
4. Fill out similar form (same answers as before)
5. **Approval usually within 24-48 hours**

**You can skip this for now and apply later if needed!**

---

## 📜 **Step 2: ProPublica Congress API**

**Why:** Official US Congressional data (bills, votes, members)  
**Free tier:** 5,000 requests/day (more than enough)

### **2.1 Request API Key**

**Go to:** https://www.propublica.org/datastore/api/propublica-congress-api

**Scroll down to the form and fill it out:**

**Your name:**
```
[Your name]
```

**Email address:**
```
[Your email]
```

**Organization (optional):**
```
Independent
```

**How will you use the API:**
```
Building an automated prediction market trading system that analyzes US political 
events. Will use the API to track congressional bills, votes, and legislative 
activity to inform trading decisions on political outcome markets.
```

**Click:** "Request API Key"

---

### **2.2 Check Email**

**You'll receive an email instantly** with your API key.

Subject: "Your ProPublica Congress API Key"

**Copy the API key** from the email (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

---

### **2.3 Add to .env File**

**Open .env:**
```bash
nano /home/ubuntu/clawd/agents/coding/.env
```

**Add this line:**
```bash
PROPUBLICA_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Save and exit:** Ctrl+X, then Y, then Enter

---

## 🌦️ **Step 3: OpenWeatherMap API**

**Why:** Global weather forecasts (current + 5-day)  
**Free tier:** 1,000 calls/day, 60 calls/minute

### **3.1 Create Account**

**Go to:** https://home.openweathermap.org/users/sign_up

**Fill out the form:**

**Username:**
```
[choose a username]
```

**Email:**
```
[your email]
```

**Password:**
```
[create a password]
```

**Check:** "I am 16 years old and over"  
**Check:** "I agree with Privacy Policy, Terms and Conditions"  
**Uncheck:** "I consent to receive news and special offers" (optional)

**Complete the CAPTCHA**

**Click:** "Create Account"

---

### **3.2 Verify Email**

Check your email for verification link from OpenWeatherMap.

**Click the verification link** in the email.

---

### **3.3 Get API Key**

After verifying, you'll be logged in.

**Click your username** (top right) → **"My API Keys"**

You'll see a default API key already created!

**Copy the API key** (format: 32-character hex string)

**Note:** New API keys take ~2 hours to activate. If you get "Invalid API key" errors, wait a bit!

---

### **3.4 Add to .env File**

**Open .env:**
```bash
nano /home/ubuntu/clawd/agents/coding/.env
```

**Add this line:**
```bash
OPENWEATHER_API_KEY=your_32_character_api_key_here
```

**Save and exit:** Ctrl+X, then Y, then Enter

---

## ✅ **Step 4: Verify Your .env File**

**Check your .env file:**
```bash
cat /home/ubuntu/clawd/agents/coding/.env
```

**You should see these 3 lines (plus your existing Supabase config):**

```bash
# Your existing config
TRADING_MODE=paper
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key

# NEW - Data sources
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAxxxxxx
PROPUBLICA_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
OPENWEATHER_API_KEY=your_32_character_key_here
```

**If it looks like that, you're good! ✅**

---

## 🧪 **Step 5: Test Everything**

**Run the test script:**
```bash
cd /home/ubuntu/clawd/agents/coding
python3 ingestion/multi_source_ingestion.py
```

**Expected output:**

```
============================================================
MULTI-SOURCE INGESTION DEMO
============================================================
✅ MultiSourceIngestion initialized
✅ Twitter API client initialized

1. Breaking News (keywords: 'Trump', 'Biden')
  - [reuters] Trump announces...
  - [bbc_politics] Biden signs...
  - [un_news] UN report...

2. Google News (query: 'Ukraine war')
  - Latest Ukraine updates...
  - Russia strikes...

3. Twitter Search (query: '#Bitcoin')
  - @user123: Bitcoin price hits...
  - @analyst456: Market analysis...

4. Reddit r/politics (keywords: ['Trump', 'election'])
  - [1250 upvotes] Trump rally in...
  - [890 upvotes] New poll shows...

5. Recent Congressional Bills
  - [house] H.R.1234: Infrastructure bill...
  - [senate] S.567: Climate legislation...

6. PredictIt Markets (first 3)
  - 2024 Presidential Election
      Donald Trump: $0.45
      Joe Biden: $0.38

7. Crypto Prices
  - bitcoin: $52,340.50 (+2.45%)
  - ethereum: $2,890.20 (+1.89%)

8. Trending Crypto
  - Solana (SOL) - Rank #5
  - Cardano (ADA) - Rank #9

9. Full Context Gathering (example market)
  Keywords extracted: ['Trump', 'win', '2024', 'presidential', 'election']
  News articles found: 12
  Specialist data keys: ['bills', 'predictit']

============================================================
DEMO COMPLETE
============================================================
```

**If you see this, everything is working! 🎉**

---

## 🚨 **Troubleshooting**

### **Issue: "Twitter API not configured"**

**Fix:** Make sure `TWITTER_BEARER_TOKEN` is in `.env` file  
**Check:** `cat .env | grep TWITTER`

If it's there but not working:
- Make sure there's no space after `=`
- Make sure the token starts with `AAAAAAAAAA`
- Try restarting the script

---

### **Issue: "ProPublica API key not set"**

**Fix:** Make sure `PROPUBLICA_API_KEY` is in `.env`  
**Check:** `cat .env | grep PROPUBLICA`

---

### **Issue: "OpenWeatherMap API key not set"**

**Fix:** Make sure `OPENWEATHER_API_KEY` is in `.env`  
**Check:** `cat .env | grep OPENWEATHER`

**Note:** New OpenWeatherMap keys take ~2 hours to activate!

---

### **Issue: "Invalid API key" from OpenWeatherMap**

**Cause:** New API keys need time to activate (up to 2 hours)

**Fix:** Wait 2 hours and try again

**Temporary workaround:** The demo will still work for Twitter, ProPublica, and free sources!

---

### **Issue: Demo shows "⚠️" warnings but continues**

**This is normal!** The demo tries all sources. If some aren't configured, it shows warnings but continues.

**As long as you see some data, you're good!**

---

## 📚 **Sources That Work Immediately (No Signup)**

These are already integrated and require **zero configuration:**

✅ **Google News RSS** - Breaking news  
✅ **Reddit API** - Social sentiment (public data)  
✅ **PredictIt API** - Competitor market odds  
✅ **CoinGecko API** - Crypto prices (free tier, no key)  
✅ **NOAA Weather.gov** - US weather forecasts (free, no key)

**They're already working in the demo script!**

---

## 🎯 **What You Get With Free Tier**

### **Speed:**
- Twitter: 0-5 min from event
- Google News: 5-30 min
- Reddit: 10-60 min

### **Coverage:**
- ✅ Breaking news (all themes)
- ✅ Social sentiment (Twitter + Reddit)
- ✅ US political data (bills, votes)
- ✅ Crypto prices (real-time)
- ✅ Weather forecasts (US + global)
- ✅ Competitor market odds

**This is ~70% of what you need to profitably trade!**

---

## 📊 **Next Steps**

### **After Setup:**

1. ✅ Run demo script to verify everything works
2. ✅ Review `DATA_SOURCES_GUIDE.md` for full details on each source
3. ✅ Update your agents to use the ingestion system:

```python
from ingestion.multi_source_ingestion import MultiSourceIngestion

class YourAgent(BaseAgent):
    def __init__(self):
        super().__init__(...)
        self.ingestion = MultiSourceIngestion()
    
    def generate_thesis(self, market):
        context = self.ingestion.gather_context_for_market(
            market.question,
            self.theme
        )
        # context now has news, social data, specialist data
        # Use it to make better decisions!
```

---

## 💰 **Later: Add Paid Sources (Optional)**

**Only after you prove alpha with free tier!**

**Month 2+:**
- NewsAPI.org ($449/mo) - Faster news (2-5 min latency)
- Glassnode ($29-79/mo) - Crypto on-chain metrics

**Month 3+:**
- Nansen ($150/mo) - Whale tracking
- Dune Analytics ($99/mo) - Custom crypto queries

**Start free → Prove ROI → Scale up!**

---

## ✅ **Summary**

**You just set up:**
- ✅ Twitter API (breaking news, social sentiment)
- ✅ ProPublica API (US Congress data)
- ✅ OpenWeatherMap API (weather forecasts)
- ✅ 5 other sources that work automatically

**Total cost:** $0/month  
**Total time:** ~30 minutes  
**Coverage:** 70% of critical data for profitable trading

**Your agents can now access real-time data! 🚀**

---

**Questions?** 
- Review `INGESTION_SETUP.md` for detailed troubleshooting
- Review `DATA_SOURCES_GUIDE.md` for source details
- Test with: `python3 ingestion/multi_source_ingestion.py`

**Last Updated:** 2026-03-02
