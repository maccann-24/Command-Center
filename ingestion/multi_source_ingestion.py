"""
Multi-Source Data Ingestion for BASED MONEY
Integrates news, social, on-chain, weather, and political data
"""

import os
import sys
import time
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import tweepy
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()


class MultiSourceIngestion:
    """
    Unified data ingestion from multiple sources.
    
    Sources supported:
    - Twitter (real-time social)
    - Google News RSS (free breaking news)
    - Reddit (social sentiment)
    - GDELT (geopolitical events)
    - ProPublica Congress (US politics)
    - PredictIt (competitor market data)
    - CoinGecko (crypto prices)
    - NOAA Weather (US weather)
    - OpenWeatherMap (global weather)
    """
    
    def __init__(self):
        # Initialize API clients
        self.twitter_client = self._init_twitter()
        
        # RSS feed URLs
        self.rss_feeds = {
            'reuters': 'https://www.reutersagency.com/feed/',
            'bbc_world': 'http://feeds.bbci.co.uk/news/world/rss.xml',
            'bbc_politics': 'http://feeds.bbci.co.uk/news/politics/rss.xml',
            'un_news': 'https://news.un.org/feed/subscribe/en/news/all/rss.xml',
            'state_dept': 'https://www.state.gov/rss-channel/press-releases/',
            'cnn_politics': 'http://rss.cnn.com/rss/cnn_allpolitics.rss',
        }
        
        # API keys (from env)
        self.propublica_key = os.getenv('PROPUBLICA_API_KEY')
        self.openweather_key = os.getenv('OPENWEATHER_API_KEY')
        
        print("✅ MultiSourceIngestion initialized")
    
    # ========================================
    # INITIALIZATION
    # ========================================
    
    def _init_twitter(self) -> Optional[tweepy.Client]:
        """Initialize Twitter API v2 client."""
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        if not bearer_token:
            print("⚠️  Twitter API not configured (set TWITTER_BEARER_TOKEN)")
            return None
        
        try:
            client = tweepy.Client(bearer_token=bearer_token)
            print("✅ Twitter API client initialized")
            return client
        except Exception as e:
            print(f"⚠️  Failed to initialize Twitter: {e}")
            return None
    
    # ========================================
    # NEWS SOURCES
    # ========================================
    
    def get_breaking_news(self, keywords: List[str], hours: int = 24, 
                          max_articles: int = 50) -> List[Dict]:
        """
        Fetch breaking news from RSS feeds matching keywords.
        
        Args:
            keywords: List of keywords to match (case-insensitive)
            hours: Only return articles from last N hours
            max_articles: Maximum articles to return
        
        Returns:
            List of article dicts with title, link, published, summary
        """
        articles = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for source_name, feed_url in self.rss_feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    # Check if any keyword matches
                    title_lower = entry.title.lower()
                    summary_lower = entry.get('summary', '').lower()
                    
                    if any(kw.lower() in title_lower or kw.lower() in summary_lower 
                           for kw in keywords):
                        
                        # Parse published date (if available)
                        published_dt = None
                        if hasattr(entry, 'published_parsed'):
                            published_dt = datetime(*entry.published_parsed[:6])
                        
                        # Skip if too old
                        if published_dt and published_dt < cutoff_time:
                            continue
                        
                        articles.append({
                            'source': source_name,
                            'title': entry.title,
                            'link': entry.link,
                            'published': entry.get('published', 'Unknown'),
                            'summary': entry.get('summary', ''),
                            'timestamp': published_dt or datetime.now()
                        })
                
            except Exception as e:
                print(f"⚠️  Error fetching {source_name}: {e}")
                continue
        
        # Sort by timestamp (newest first)
        articles.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return articles[:max_articles]
    
    def get_google_news(self, query: str, max_articles: int = 20) -> List[Dict]:
        """
        Fetch Google News RSS for a specific query.
        
        Args:
            query: Search query (e.g., "Trump indictment")
            max_articles: Max articles to return
        
        Returns:
            List of article dicts
        """
        url = f"https://news.google.com/rss/search?q={query}"
        
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:max_articles]:
                articles.append({
                    'source': 'google_news',
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.get('published', 'Unknown'),
                    'summary': entry.get('summary', ''),
                    'timestamp': datetime.now()
                })
            
            return articles
        
        except Exception as e:
            print(f"⚠️  Error fetching Google News: {e}")
            return []
    
    # ========================================
    # SOCIAL MEDIA
    # ========================================
    
    def search_twitter(self, query: str, max_results: int = 100) -> List[Dict]:
        """
        Search recent tweets (last 7 days).
        
        Args:
            query: Twitter search query (supports operators like from:, #hashtag, etc.)
            max_results: Max tweets to return (10-100)
        
        Returns:
            List of tweet dicts
        """
        if not self.twitter_client:
            return []
        
        try:
            response = self.twitter_client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),  # API limit
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                expansions=['author_id'],
                user_fields=['username', 'verified']
            )
            
            if not response.data:
                return []
            
            # Map author_id to username
            users = {user.id: user for user in response.includes.get('users', [])}
            
            tweets = []
            for tweet in response.data:
                author = users.get(tweet.author_id)
                
                tweets.append({
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'author_id': tweet.author_id,
                    'author_username': author.username if author else 'unknown',
                    'author_verified': author.verified if author else False,
                    'likes': tweet.public_metrics.get('like_count', 0),
                    'retweets': tweet.public_metrics.get('retweet_count', 0),
                    'replies': tweet.public_metrics.get('reply_count', 0)
                })
            
            return tweets
        
        except Exception as e:
            print(f"⚠️  Error searching Twitter: {e}")
            return []
    
    def get_reddit_posts(self, subreddit: str, keywords: List[str], 
                         limit: int = 25) -> List[Dict]:
        """
        Fetch recent Reddit posts matching keywords.
        
        Args:
            subreddit: Subreddit name (without r/)
            keywords: Keywords to match in title
            limit: Max posts to fetch
        
        Returns:
            List of post dicts
        """
        url = f"https://www.reddit.com/r/{subreddit}/hot.json"
        headers = {'User-Agent': 'BASED-MONEY/1.0'}
        
        try:
            response = requests.get(url, headers=headers, params={'limit': limit})
            if response.status_code != 200:
                return []
            
            data = response.json()
            posts = []
            
            for child in data['data']['children']:
                post = child['data']
                title_lower = post['title'].lower()
                
                # Check keyword match
                if any(kw.lower() in title_lower for kw in keywords):
                    posts.append({
                        'title': post['title'],
                        'author': post['author'],
                        'score': post['score'],
                        'num_comments': post['num_comments'],
                        'url': f"https://reddit.com{post['permalink']}",
                        'created': datetime.fromtimestamp(post['created_utc']),
                        'selftext': post.get('selftext', '')[:500]  # Truncate
                    })
            
            return posts
        
        except Exception as e:
            print(f"⚠️  Error fetching Reddit: {e}")
            return []
    
    # ========================================
    # GEOPOLITICAL
    # ========================================
    
    def get_gdelt_events(self, country_code: str = None, 
                         event_type: str = None, days: int = 7) -> List[Dict]:
        """
        Fetch GDELT events (conflicts, cooperation, protests, etc.).
        
        Args:
            country_code: ISO 2-letter country code (e.g., 'US', 'RU', 'CN')
            event_type: CAMEO event code (e.g., '14' = protest, '19' = fight)
            days: Last N days of events
        
        Returns:
            List of event dicts
        
        Note: This is a simplified version. Full GDELT integration requires
        downloading daily files and parsing them.
        """
        # Placeholder - GDELT requires more complex integration
        # See: https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/
        print("⚠️  GDELT integration not yet implemented (requires file download/parse)")
        return []
    
    # ========================================
    # US POLITICS
    # ========================================
    
    def get_congress_bills(self, chamber: str = 'both', days: int = 7) -> List[Dict]:
        """
        Fetch recent congressional bills from ProPublica.
        
        Args:
            chamber: 'house', 'senate', or 'both'
            days: Last N days
        
        Returns:
            List of bill dicts
        """
        if not self.propublica_key:
            print("⚠️  ProPublica API key not set (PROPUBLICA_API_KEY)")
            return []
        
        bills = []
        chambers = ['house', 'senate'] if chamber == 'both' else [chamber]
        
        for ch in chambers:
            url = f"https://api.propublica.org/congress/v1/{ch}/bills/introduced.json"
            headers = {'X-API-Key': self.propublica_key}
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    for bill in data['results'][0]['bills'][:20]:
                        bills.append({
                            'chamber': ch,
                            'bill_id': bill['bill_id'],
                            'title': bill['short_title'] or bill['title'],
                            'sponsor': bill['sponsor_name'],
                            'introduced': bill['introduced_date'],
                            'summary': bill.get('summary', 'No summary'),
                            'latest_action': bill.get('latest_major_action', '')
                        })
            
            except Exception as e:
                print(f"⚠️  Error fetching {ch} bills: {e}")
        
        return bills
    
    def get_predictit_markets(self) -> List[Dict]:
        """
        Fetch all PredictIt market data (competitor to Polymarket).
        
        Returns:
            List of market dicts with current prices
        """
        url = "https://www.predictit.org/api/marketdata/all/"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                markets = []
                
                for market in data['markets']:
                    markets.append({
                        'id': market['id'],
                        'name': market['name'],
                        'url': market['url'],
                        'status': market['status'],
                        'contracts': [
                            {
                                'name': c['name'],
                                'last_trade_price': c['lastTradePrice'],
                                'best_buy_yes': c['bestBuyYesCost'],
                                'best_sell_yes': c['bestSellYesCost']
                            }
                            for c in market['contracts']
                        ]
                    })
                
                return markets
        
        except Exception as e:
            print(f"⚠️  Error fetching PredictIt: {e}")
            return []
    
    # ========================================
    # CRYPTO
    # ========================================
    
    def get_crypto_prices(self, coin_ids: List[str] = ['bitcoin', 'ethereum']) -> Dict:
        """
        Fetch crypto prices from CoinGecko (free tier).
        
        Args:
            coin_ids: List of CoinGecko coin IDs
        
        Returns:
            Dict of coin -> price data
        """
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': 'usd',
            'include_24hr_change': True,
            'include_24hr_vol': True,
            'include_market_cap': True
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
        
        except Exception as e:
            print(f"⚠️  Error fetching crypto prices: {e}")
        
        return {}
    
    def get_crypto_trending(self) -> List[Dict]:
        """
        Get trending coins on CoinGecko.
        
        Returns:
            List of trending coin dicts
        """
        url = "https://api.coingecko.com/api/v3/search/trending"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        'id': coin['item']['id'],
                        'name': coin['item']['name'],
                        'symbol': coin['item']['symbol'],
                        'market_cap_rank': coin['item']['market_cap_rank']
                    }
                    for coin in data['coins']
                ]
        
        except Exception as e:
            print(f"⚠️  Error fetching trending coins: {e}")
        
        return []
    
    # ========================================
    # WEATHER
    # ========================================
    
    def get_noaa_forecast(self, lat: float, lon: float) -> Dict:
        """
        Fetch NOAA weather forecast for US location (FREE).
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Dict with forecast data
        """
        try:
            # Step 1: Get grid point
            point_url = f"https://api.weather.gov/points/{lat},{lon}"
            headers = {'User-Agent': 'BASED-MONEY/1.0'}
            
            response = requests.get(point_url, headers=headers)
            if response.status_code != 200:
                return {}
            
            data = response.json()
            forecast_url = data['properties']['forecast']
            
            # Step 2: Get forecast
            time.sleep(0.5)  # Rate limiting
            forecast_response = requests.get(forecast_url, headers=headers)
            if forecast_response.status_code == 200:
                return forecast_response.json()
        
        except Exception as e:
            print(f"⚠️  Error fetching NOAA forecast: {e}")
        
        return {}
    
    def get_openweather_forecast(self, lat: float, lon: float) -> Dict:
        """
        Fetch OpenWeatherMap forecast (global coverage).
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Dict with forecast data
        """
        if not self.openweather_key:
            print("⚠️  OpenWeatherMap API key not set (OPENWEATHER_API_KEY)")
            return {}
        
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.openweather_key,
            'units': 'metric'  # Celsius
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
        
        except Exception as e:
            print(f"⚠️  Error fetching OpenWeatherMap: {e}")
        
        return {}
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def gather_context_for_market(self, market_question: str, theme: str) -> Dict:
        """
        Gather all relevant data for a market question.
        
        Args:
            market_question: The market question text
            theme: Theme name (geopolitical, us_politics, crypto, weather)
        
        Returns:
            Dict with all relevant data
        """
        keywords = self._extract_keywords(market_question)
        
        context = {
            'market_question': market_question,
            'theme': theme,
            'keywords': keywords,
            'timestamp': datetime.now(),
            'news': [],
            'social': {},
            'specialist_data': {}
        }
        
        # Always fetch breaking news
        context['news'] = self.get_breaking_news(keywords, hours=24, max_articles=20)
        
        # Theme-specific data
        if theme == 'geopolitical':
            context['social']['twitter'] = self.search_twitter(' OR '.join(keywords[:3]), max_results=50)
            context['social']['reddit'] = self.get_reddit_posts('worldnews', keywords, limit=10)
        
        elif theme == 'us_politics':
            context['specialist_data']['bills'] = self.get_congress_bills(days=7)
            context['specialist_data']['predictit'] = self.get_predictit_markets()[:10]
            context['social']['twitter'] = self.search_twitter(' OR '.join(keywords[:3]), max_results=50)
        
        elif theme == 'crypto':
            # Extract coin names
            coin_keywords = [kw for kw in keywords if kw.lower() in ['bitcoin', 'ethereum', 'btc', 'eth']]
            if coin_keywords:
                context['specialist_data']['prices'] = self.get_crypto_prices(['bitcoin', 'ethereum'])
            context['specialist_data']['trending'] = self.get_crypto_trending()
            context['social']['twitter'] = self.search_twitter(' OR '.join(keywords[:3]) + ' crypto', max_results=50)
        
        elif theme == 'weather':
            # Try to extract location (simplified)
            # In production, use NLP to extract location entities
            context['specialist_data']['note'] = "Weather forecasts require lat/lon - use get_noaa_forecast() or get_openweather_forecast()"
        
        return context
    
    def _extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """
        Extract keywords from text (simple version).
        
        In production, use NLP (spaCy, NLTK) for better extraction.
        """
        stopwords = {
            'will', 'the', 'be', 'in', 'on', 'at', 'by', 'to', 'of', 'a', 'an',
            'and', 'or', 'but', 'if', 'for', 'with', 'as', 'is', 'are', 'was',
            'were', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'can',
            'could', 'would', 'should', 'may', 'might', 'must', 'shall', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        words = text.lower().replace('?', '').replace('.', '').split()
        return [w for w in words if w not in stopwords and len(w) >= min_length]


# ========================================
# DEMO / TESTING
# ========================================

def demo():
    """Demo the multi-source ingestion."""
    print("\n" + "=" * 60)
    print("MULTI-SOURCE INGESTION DEMO")
    print("=" * 60)
    
    ingestion = MultiSourceIngestion()
    
    # Test 1: Breaking news
    print("\n1. Breaking News (keywords: 'Trump', 'Biden')")
    news = ingestion.get_breaking_news(['Trump', 'Biden'], hours=48, max_articles=5)
    for article in news:
        print(f"  - [{article['source']}] {article['title']}")
    
    # Test 2: Google News
    print("\n2. Google News (query: 'Ukraine war')")
    google_news = ingestion.get_google_news('Ukraine war', max_articles=5)
    for article in google_news:
        print(f"  - {article['title']}")
    
    # Test 3: Twitter (if configured)
    if ingestion.twitter_client:
        print("\n3. Twitter Search (query: '#Bitcoin')")
        tweets = ingestion.search_twitter('#Bitcoin', max_results=5)
        for tweet in tweets:
            print(f"  - @{tweet['author_username']}: {tweet['text'][:100]}...")
    
    # Test 4: Reddit
    print("\n4. Reddit r/politics (keywords: ['Trump', 'election'])")
    reddit_posts = ingestion.get_reddit_posts('politics', ['Trump', 'election'], limit=5)
    for post in reddit_posts:
        print(f"  - [{post['score']} upvotes] {post['title']}")
    
    # Test 5: Congress bills (if API key set)
    if ingestion.propublica_key:
        print("\n5. Recent Congressional Bills")
        bills = ingestion.get_congress_bills(days=7)[:3]
        for bill in bills:
            print(f"  - [{bill['chamber']}] {bill['bill_id']}: {bill['title'][:80]}...")
    
    # Test 6: PredictIt markets
    print("\n6. PredictIt Markets (first 3)")
    predictit = ingestion.get_predictit_markets()[:3]
    for market in predictit:
        print(f"  - {market['name']}")
        for contract in market['contracts'][:2]:
            print(f"      {contract['name']}: ${contract['last_trade_price']:.2f}")
    
    # Test 7: Crypto prices
    print("\n7. Crypto Prices")
    prices = ingestion.get_crypto_prices(['bitcoin', 'ethereum'])
    for coin, data in prices.items():
        print(f"  - {coin}: ${data['usd']:,.2f} ({data['usd_24h_change']:+.2f}%)")
    
    # Test 8: Trending crypto
    print("\n8. Trending Crypto")
    trending = ingestion.get_crypto_trending()[:5]
    for coin in trending:
        print(f"  - {coin['name']} ({coin['symbol']}) - Rank #{coin['market_cap_rank']}")
    
    # Test 9: Gather context for a market
    print("\n9. Full Context Gathering (example market)")
    context = ingestion.gather_context_for_market(
        "Will Trump win the 2024 presidential election?",
        "us_politics"
    )
    print(f"  Keywords extracted: {context['keywords']}")
    print(f"  News articles found: {len(context['news'])}")
    print(f"  Specialist data keys: {list(context['specialist_data'].keys())}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    demo()
