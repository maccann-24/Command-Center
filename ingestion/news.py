"""
BASED MONEY - News Monitor
Fetch news from RSS feeds for geopolitical market signals
"""

import feedparser
import sys
from typing import List
from datetime import datetime, timedelta

sys.path.insert(0, '..')

from models import NewsEvent
from database import save_news_event, record_event


# RSS Feed URLs
RSS_FEEDS = {
    "reuters": "https://www.reutersagency.com/feed/?best-topics=international-news&post_type=best",
    "ap_world": "https://www.ap.org/news-feed/?category=world-news",
    "ap_politics": "https://www.ap.org/news-feed/?category=politics",
    # Fallback/alternative feeds
    "reuters_world": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
}

# Keywords to monitor (geopolitical, technology, industrials, manufacturing)
GEOPOLITICAL_KEYWORDS = [
    # Geopolitical
    "russia",
    "ukraine",
    "iran",
    "china",
    "taiwan",
    "election",
    "congress",
    "senate",
    "israel",
    "gaza",
    "nato",
    "biden",
    "trump",
    "war",
    "military",
    "sanctions",
    "nuclear",
    "diplomacy",
    # Technology
    "ai",
    "artificial intelligence",
    "semiconductor",
    "chip",
    "technology",
    "tech",
    "crypto",
    "cryptocurrency",
    "bitcoin",
    "blockchain",
    "software",
    "hardware",
    "cloud",
    "cybersecurity",
    "data",
    # Industrials & Manufacturing
    "manufacturing",
    "factory",
    "industrial",
    "supply chain",
    "trade",
    "tariff",
    "export",
    "import",
    "production",
    "automotive",
    "energy",
    "oil",
    "infrastructure",
    "construction",
]


def fetch_news(hours_back: int = 24) -> List[NewsEvent]:
    """
    Fetch news events from RSS feeds.
    
    Args:
        hours_back: How many hours of news to fetch (default 24)
    
    Returns:
        List of NewsEvent objects from last N hours
    """
    print(f"📰 Fetching news from RSS feeds (last {hours_back} hours)...")
    
    all_events = []
    cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
    
    # Fetch from each RSS feed
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            events = fetch_from_rss(feed_url, source_name, cutoff_time)
            all_events.extend(events)
            print(f"  ✓ {source_name}: {len(events)} events")
        except Exception as e:
            print(f"  ⚠️ {source_name}: Failed ({str(e)[:50]}...)")
            # Log error but continue with other feeds
            record_event(
                event_type="news_fetch_error",
                details={
                    "source": source_name,
                    "error": str(e),
                    "feed_url": feed_url
                },
                severity="warning"
            )
            continue
    
    # Remove duplicates (same headline)
    unique_events = remove_duplicates(all_events)
    
    # Save to database
    saved_count = 0
    for event in unique_events:
        if save_news_event(event):
            saved_count += 1
    
    print(f"✅ Fetched {len(unique_events)} unique news events, saved {saved_count}")
    
    # Log summary
    record_event(
        event_type="news_fetched",
        details={
            "total_events": len(unique_events),
            "saved_count": saved_count,
            "sources": list(RSS_FEEDS.keys()),
            "hours_back": hours_back
        },
        severity="info"
    )
    
    return unique_events


def fetch_from_rss(feed_url: str, source_name: str, cutoff_time: datetime) -> List[NewsEvent]:
    """
    Fetch news from a single RSS feed.
    
    Args:
        feed_url: RSS feed URL
        source_name: Source identifier
        cutoff_time: Only return news after this time
    
    Returns:
        List of NewsEvent objects
    """
    events = []
    
    try:
        # Parse RSS feed
        feed = feedparser.parse(feed_url)
        
        # Check for feed errors
        if hasattr(feed, 'bozo_exception'):
            # Feed has parsing issues but may still have entries
            print(f"    ⚠️ Feed parsing warning: {feed.bozo_exception}")
        
        # Process each entry
        for entry in feed.entries:
            try:
                # Extract headline
                headline = entry.get("title", "").strip()
                if not headline:
                    continue
                
                # Extract timestamp
                timestamp = parse_entry_time(entry)
                
                # Skip if too old
                if timestamp and timestamp < cutoff_time:
                    continue
                
                # Extract keywords from headline
                keywords = extract_keywords(headline)
                
                # Only include if has geopolitical keywords
                if not keywords:
                    continue
                
                # Extract URL
                url = entry.get("link") or entry.get("id")
                
                # Create NewsEvent
                event = NewsEvent(
                    timestamp=timestamp or datetime.utcnow(),
                    headline=headline,
                    keywords=keywords,
                    source=source_name,
                    sentiment_score=0.0,  # Placeholder for v1
                    url=url
                )
                
                events.append(event)
            
            except Exception as e:
                # Skip individual entry errors
                print(f"    ⚠️ Error parsing entry: {str(e)[:50]}")
                continue
        
        return events
    
    except Exception as e:
        print(f"    ❌ RSS fetch failed: {str(e)[:80]}")
        raise


def parse_entry_time(entry: dict) -> datetime:
    """
    Parse timestamp from RSS entry.
    
    RSS feeds use various time field names and formats.
    Try multiple fields and formats.
    
    Args:
        entry: RSS feed entry
    
    Returns:
        datetime object or None
    """
    import time
    
    # Try different timestamp fields
    time_fields = ["published_parsed", "updated_parsed", "created_parsed"]
    
    for field in time_fields:
        if field in entry and entry[field]:
            try:
                # Convert struct_time to datetime
                time_struct = entry[field]
                timestamp = datetime.fromtimestamp(time.mktime(time_struct))
                return timestamp
            except:
                continue
    
    # Try string fields
    string_fields = ["published", "updated", "created"]
    for field in string_fields:
        if field in entry and entry[field]:
            try:
                # Try parsing ISO format
                timestamp = datetime.fromisoformat(entry[field].replace("Z", "+00:00"))
                return timestamp
            except:
                continue
    
    # Default to now if no timestamp found
    return datetime.utcnow()


def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords from text via whole-word matching.
    
    Args:
        text: Text to search (headline)
    
    Returns:
        List of matched keywords
    """
    import re
    
    text_lower = text.lower()
    keywords = []
    
    for keyword in GEOPOLITICAL_KEYWORDS:
        # Use word boundary matching for short keywords to avoid false positives
        # For multi-word keywords or longer words, use simple substring match
        if len(keyword) <= 3 and ' ' not in keyword:
            # Short keyword: use word boundaries (e.g., "ai" shouldn't match "Ukraine")
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                keywords.append(keyword)
        else:
            # Longer keyword or phrase: simple substring match is fine
            if keyword in text_lower:
                keywords.append(keyword)
    
    return keywords


def remove_duplicates(events: List[NewsEvent]) -> List[NewsEvent]:
    """
    Remove duplicate news events based on headline similarity.
    
    Args:
        events: List of NewsEvent objects
    
    Returns:
        List with duplicates removed
    """
    seen_headlines = set()
    unique = []
    
    for event in events:
        # Normalize headline for comparison
        normalized = event.headline.lower().strip()
        
        if normalized not in seen_headlines:
            seen_headlines.add(normalized)
            unique.append(event)
    
    return unique


def test_news_fetch():
    """
    Test news fetching and verify results.
    Run with: python -m ingestion.news
    """
    print("=" * 60)
    print("NEWS FETCH TEST")
    print("=" * 60)
    
    # Fetch news from last 24 hours
    events = fetch_news(hours_back=24)
    
    if not events:
        print("\n⚠️ No news events fetched")
        print("   This could mean:")
        print("   - RSS feeds are down/changed")
        print("   - No geopolitical news in last 24h (unlikely)")
        print("   - Network connectivity issues")
        return False
    
    print(f"\n📊 Fetched {len(events)} news events\n")
    
    # Show sample
    print("Sample of news events:")
    for i, event in enumerate(events[:5], 1):
        print(f"\n{i}. {event.headline[:80]}...")
        print(f"   Source: {event.source}")
        print(f"   Keywords: {', '.join(event.keywords)}")
        print(f"   Time: {event.timestamp.strftime('%Y-%m-%d %H:%M UTC')}")
        if event.url:
            print(f"   URL: {event.url[:60]}...")
    
    # Verify we got enough events
    if len(events) >= 10:
        print(f"\n✅ SUCCESS: Fetched {len(events)} events (target: 10+)")
    else:
        print(f"\n⚠️ WARNING: Only {len(events)} events (target: 10+)")
        print("   May need to adjust hours_back or add more feeds")
    
    # Keyword distribution
    keyword_counts = {}
    for event in events:
        for keyword in event.keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    print(f"\n📈 Keyword distribution:")
    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    for keyword, count in sorted_keywords[:10]:
        print(f"   {keyword}: {count}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete")
    print("=" * 60)
    
    return len(events) >= 10


if __name__ == "__main__":
    success = test_news_fetch()
    sys.exit(0 if success else 1)
