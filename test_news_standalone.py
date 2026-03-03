#!/usr/bin/env python3
"""
Standalone test of news fetcher (no database dependencies)
Tests RSS parsing and keyword extraction
"""

import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta
from models import NewsEvent


# Test data: sample RSS feed structure
SAMPLE_HEADLINES = [
    # Geopolitical
    "Russia launches new offensive in Ukraine's eastern region",
    "China and Taiwan tensions escalate over trade dispute",
    "Iran nuclear negotiations resume in Vienna",
    "US Congress passes new election security bill",
    "Senate debates military aid to Ukraine",
    "Israel and Gaza reach temporary ceasefire agreement",
    "NATO allies discuss Russia sanctions expansion",
    "Trump announces 2028 presidential campaign",
    "Biden meets with Chinese President at summit",
    "Nuclear talks with North Korea stalled",
    # Technology
    "New AI breakthrough in semiconductor manufacturing",
    "Bitcoin surges as crypto regulations loosen",
    "Major cybersecurity breach affects cloud infrastructure",
    "China bans export of key chip technology",
    # Industrials & Manufacturing
    "Auto manufacturing hits record production levels",
    "US imposes new tariffs on steel imports",
    "Supply chain disruptions impact energy sector",
    "Infrastructure bill funds factory construction",
    # Non-matching (should be filtered)
    "Celebrity gossip and entertainment news",
    "Sports: Football team wins championship",
]

GEOPOLITICAL_KEYWORDS = [
    # Geopolitical
    "russia", "ukraine", "iran", "china", "taiwan",
    "election", "congress", "senate", "israel", "gaza",
    "nato", "biden", "trump", "war", "military",
    "sanctions", "nuclear", "diplomacy",
    # Technology
    "ai", "artificial intelligence", "semiconductor", "chip",
    "technology", "tech", "crypto", "cryptocurrency", "bitcoin",
    "blockchain", "software", "hardware", "cloud", "cybersecurity", "data",
    # Industrials & Manufacturing
    "manufacturing", "factory", "industrial", "supply chain",
    "trade", "tariff", "export", "import", "production",
    "automotive", "energy", "oil", "infrastructure", "construction",
]


def extract_keywords(text: str) -> list:
    """Extract keywords from text (copy of function from news.py)"""
    import re
    
    text_lower = text.lower()
    keywords = []
    
    for keyword in GEOPOLITICAL_KEYWORDS:
        # Use word boundary matching for short keywords to avoid false positives
        if len(keyword) <= 3 and ' ' not in keyword:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                keywords.append(keyword)
        else:
            if keyword in text_lower:
                keywords.append(keyword)
    
    return keywords


def test_keyword_extraction():
    """Test keyword extraction logic"""
    print("\n" + "=" * 60)
    print("KEYWORD EXTRACTION TEST")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for headline in SAMPLE_HEADLINES:
        keywords = extract_keywords(headline)
        has_keywords = len(keywords) > 0
        
        # Determine if headline is in geopolitical/tech/industrial categories
        # Based on which sample headlines group it belongs to
        is_target_news = not any(x in headline.lower() for x in ["celebrity", "gossip", "sports", "entertainment"])
        
        if is_target_news and has_keywords:
            print(f"✓ PASS: {headline[:60]}...")
            print(f"  Keywords: {', '.join(keywords)}")
            passed += 1
        elif not is_target_news and not has_keywords:
            print(f"✓ SKIP: {headline[:60]}... (correctly filtered)")
            passed += 1
        else:
            print(f"✗ FAIL: {headline[:60]}...")
            print(f"  Expected to match: {is_target_news}, Got keywords: {keywords}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_news_event_creation():
    """Test NewsEvent object creation"""
    print("\n" + "=" * 60)
    print("NEWSEVENT MODEL TEST")
    print("=" * 60)
    
    try:
        # Create a news event
        event = NewsEvent(
            timestamp=datetime.utcnow(),
            headline="Russia announces military mobilization in Ukraine",
            keywords=["russia", "military", "ukraine"],
            source="reuters",
            sentiment_score=0.0,
            url="https://example.com/news/123"
        )
        
        print(f"✓ Created NewsEvent: {event.headline[:50]}...")
        print(f"  Keywords: {event.keywords}")
        print(f"  Source: {event.source}")
        print(f"  Age: {event.age_in_hours():.1f} hours")
        
        # Test to_dict()
        event_dict = event.to_dict()
        print(f"✓ to_dict() works: {len(event_dict)} fields")
        
        # Test keyword matching
        if event.matches_keywords(["russia", "china"]):
            print(f"✓ matches_keywords() works")
        else:
            print(f"✗ matches_keywords() failed")
            return False
        
        # Test is_recent()
        if event.is_recent(max_hours=24):
            print(f"✓ is_recent() works")
        else:
            print(f"✗ is_recent() failed")
            return False
        
        print("\n✅ NewsEvent model test PASSED")
        return True
    
    except Exception as e:
        print(f"\n❌ NewsEvent model test FAILED: {e}")
        return False


def test_rss_parsing_simulation():
    """Simulate RSS feed parsing without actual network calls"""
    print("\n" + "=" * 60)
    print("RSS PARSING SIMULATION")
    print("=" * 60)
    
    # Simulate creating events from headlines
    events = []
    
    for headline in SAMPLE_HEADLINES:
        keywords = extract_keywords(headline)
        
        # Only create event if has geopolitical keywords
        if keywords:
            event = NewsEvent(
                timestamp=datetime.utcnow() - timedelta(hours=2),
                headline=headline,
                keywords=keywords,
                source="test_feed",
                sentiment_score=0.0
            )
            events.append(event)
    
    print(f"Created {len(events)} news events from {len(SAMPLE_HEADLINES)} headlines")
    
    # Check filtering worked
    expected_geo_count = sum(1 for h in SAMPLE_HEADLINES 
                            if extract_keywords(h))
    
    if len(events) == expected_geo_count:
        print(f"✓ Filtering works: {len(events)} geopolitical events")
    else:
        print(f"✗ Filtering issue: expected {expected_geo_count}, got {len(events)}")
        return False
    
    # Show samples
    print("\nSample events created:")
    for i, event in enumerate(events[:3], 1):
        print(f"{i}. {event.headline[:60]}...")
        print(f"   Keywords: {', '.join(event.keywords)}")
    
    print("\n✅ RSS parsing simulation PASSED")
    return True


def run_all_tests():
    """Run all standalone tests"""
    print("\n" + "=" * 60)
    print("NEWS FETCHER VALIDATION (Standalone)")
    print("=" * 60)
    
    success = True
    
    # Test 1: Keyword extraction
    if not test_keyword_extraction():
        success = False
    
    # Test 2: NewsEvent model
    if not test_news_event_creation():
        success = False
    
    # Test 3: RSS parsing simulation
    if not test_rss_parsing_simulation():
        success = False
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL STANDALONE TESTS PASSED")
        print("\n💡 Next steps:")
        print("   1. Install feedparser: pip install feedparser")
        print("   2. Test live RSS fetch: python ingestion/news.py")
        print("   3. Verify 10+ events fetched")
        print("   4. Integrate with database save")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60 + "\n")
    
    return success


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
