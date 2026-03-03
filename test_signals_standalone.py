#!/usr/bin/env python3
"""
Standalone test of signal generator (no external dependencies)
Tests keyword extraction and impact calculation logic
"""

import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta


# Mock classes for testing
class Market:
    def __init__(self, id, question, category, yes_price, no_price, volume_24h):
        self.id = id
        self.question = question
        self.category = category
        self.yes_price = yes_price
        self.no_price = no_price
        self.volume_24h = volume_24h


class NewsEvent:
    def __init__(self, timestamp, headline, keywords, source):
        self.timestamp = timestamp
        self.headline = headline
        self.keywords = keywords
        self.source = source


# Copy of functions from agents/signals.py for standalone testing
def extract_keywords_from_question(question: str):
    """Extract keywords from question (copy from signals.py)"""
    STOP_WORDS = {
        'will', 'the', 'be', 'in', 'on', 'at', 'to', 'a', 'an',
        'is', 'are', 'was', 'were', 'has', 'have', 'had',
        'do', 'does', 'did', 'for', 'of', 'by', 'from',
        'this', 'that', 'these', 'those', 'it', 'its',
        'and', 'or', 'but', 'not', 'if', 'when', 'where',
        'how', 'what', 'who', 'which', 'why',
        'before', 'after', 'during', 'while',
        '?', '!', '.', ',', ';', ':', '-', '(', ')', '[', ']'
    }
    
    words = question.lower().split()
    keywords = [
        word.strip('.,;:!?()[]{}$#@%&*')  # Remove punctuation including $
        for word in words
        if len(word) >= 3 and word.lower() not in STOP_WORDS
    ]
    
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword and keyword not in seen:
            seen.add(keyword)
            unique_keywords.append(keyword)
    
    return unique_keywords


def has_keyword_overlap(market_keywords, news_keywords):
    """Check for keyword overlap (copy from signals.py)"""
    market_set = set(keyword.lower() for keyword in market_keywords)
    news_set = set(keyword.lower() for keyword in news_keywords)
    return len(market_set & news_set) > 0


def calculate_event_impact(market, news_events):
    """Calculate impact score (copy from signals.py)"""
    if not news_events:
        return 0.0
    
    market_keywords = extract_keywords_from_question(market.question)
    
    if not market_keywords:
        return 0.0
    
    matching_events = 0
    
    for news_event in news_events:
        if has_keyword_overlap(market_keywords, news_event.keywords):
            matching_events += 1
    
    if matching_events == 0:
        impact_score = 0.0
    else:
        impact_score = 0.20 * matching_events
        impact_score = min(0.40, impact_score)
    
    return impact_score


def test_basic_case():
    """Test: Basic case from task spec"""
    print("\n" + "=" * 60)
    print("TEST 1: BASIC CASE (Task Specification)")
    print("=" * 60)
    
    # Create mock market about "Russia Ukraine"
    market = Market(
        id="test1",
        question="Will Russia invade Ukraine?",
        category="geopolitical",
        yes_price=0.50,
        no_price=0.50,
        volume_24h=100000
    )
    
    # Create mock news event with "Ukraine" in headline
    news_event = NewsEvent(
        timestamp=datetime.utcnow() - timedelta(hours=1),
        headline="Ukraine military reports border activity",
        keywords=["ukraine", "military"],  # Has "ukraine"
        source="reuters"
    )
    
    # Calculate impact
    impact_score = calculate_event_impact(market, [news_event])
    
    print(f"\nMarket question: '{market.question}'")
    print(f"News headline: '{news_event.headline}'")
    print(f"News keywords: {news_event.keywords}")
    print(f"Impact score: {impact_score}")
    
    # Verify impact_score = 0.20
    if impact_score == 0.20:
        print("\n✅ PASSED: impact_score = 0.20 (as specified)")
        return True
    else:
        print(f"\n❌ FAILED: impact_score = {impact_score} (expected 0.20)")
        return False


def test_keyword_extraction():
    """Test: Keyword extraction"""
    print("\n" + "=" * 60)
    print("TEST 2: KEYWORD EXTRACTION")
    print("=" * 60)
    
    test_cases = [
        ("Will Russia invade Ukraine?", ["russia", "invade", "ukraine"]),
        ("Will Bitcoin reach $100k in 2026?", ["bitcoin", "reach", "100k", "2026"]),  # $ stripped
        ("The quick brown fox", ["quick", "brown", "fox"]),
    ]
    
    all_passed = True
    for question, expected in test_cases:
        keywords = extract_keywords_from_question(question)
        
        # Check if all expected keywords are present
        if set(keywords) >= set(expected):
            print(f"✅ '{question}'")
            print(f"   Keywords: {keywords}")
        else:
            print(f"❌ '{question}'")
            print(f"   Got: {keywords}, Expected: {expected}")
            all_passed = False
    
    return all_passed


def test_no_overlap():
    """Test: No keyword overlap"""
    print("\n" + "=" * 60)
    print("TEST 3: NO OVERLAP")
    print("=" * 60)
    
    market = Market(
        id="test2",
        question="Will Bitcoin reach $100k?",
        category="crypto",
        yes_price=0.60,
        no_price=0.40,
        volume_24h=200000
    )
    
    # News about Russia (no overlap with Bitcoin)
    news_event = NewsEvent(
        timestamp=datetime.utcnow(),
        headline="Russia announces new policy",
        keywords=["russia", "policy"],
        source="reuters"
    )
    
    impact_score = calculate_event_impact(market, [news_event])
    
    print(f"\nMarket: '{market.question}'")
    print(f"News: '{news_event.headline}'")
    print(f"Impact score: {impact_score}")
    
    if impact_score == 0.0:
        print("\n✅ PASSED: impact_score = 0.0 (no overlap)")
        return True
    else:
        print(f"\n❌ FAILED: impact_score = {impact_score} (expected 0.0)")
        return False


def test_multiple_events():
    """Test: Multiple matching events"""
    print("\n" + "=" * 60)
    print("TEST 4: MULTIPLE EVENTS")
    print("=" * 60)
    
    market = Market(
        id="test3",
        question="Will Russia invade Ukraine?",
        category="geopolitical",
        yes_price=0.50,
        no_price=0.50,
        volume_24h=100000
    )
    
    news_events = [
        NewsEvent(
            timestamp=datetime.utcnow() - timedelta(hours=1),
            headline="Russia military buildup",
            keywords=["russia", "military"],
            source="reuters"
        ),
        NewsEvent(
            timestamp=datetime.utcnow() - timedelta(hours=2),
            headline="Ukraine NATO request",
            keywords=["ukraine", "nato"],
            source="ap"
        ),
    ]
    
    impact_score = calculate_event_impact(market, news_events)
    
    print(f"\nMarket: '{market.question}'")
    print(f"News events: {len(news_events)}")
    print(f"Impact score: {impact_score}")
    
    # 2 events * 0.20 = 0.40
    if impact_score == 0.40:
        print("\n✅ PASSED: impact_score = 0.40 (2 events * 0.20)")
        return True
    else:
        print(f"\n❌ FAILED: impact_score = {impact_score} (expected 0.40)")
        return False


def test_capping():
    """Test: Score capping at 0.40"""
    print("\n" + "=" * 60)
    print("TEST 5: SCORE CAPPING")
    print("=" * 60)
    
    market = Market(
        id="test4",
        question="Will Russia invade Ukraine?",
        category="geopolitical",
        yes_price=0.50,
        no_price=0.50,
        volume_24h=100000
    )
    
    # 3 matching events (should cap at 0.40)
    news_events = [
        NewsEvent(
            timestamp=datetime.utcnow() - timedelta(hours=i),
            headline=f"Russia Ukraine news {i}",
            keywords=["russia", "ukraine"],
            source="reuters"
        )
        for i in range(3)
    ]
    
    impact_score = calculate_event_impact(market, news_events)
    
    print(f"\nMarket: '{market.question}'")
    print(f"News events: {len(news_events)} (all matching)")
    print(f"Impact score: {impact_score}")
    
    # 3 events * 0.20 = 0.60, but capped at 0.40
    if impact_score == 0.40:
        print("\n✅ PASSED: impact_score = 0.40 (capped from 0.60)")
        return True
    else:
        print(f"\n❌ FAILED: impact_score = {impact_score} (expected 0.40)")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SIGNAL GENERATOR VALIDATION (Standalone)")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Basic Case", test_basic_case()))
    results.append(("Keyword Extraction", test_keyword_extraction()))
    results.append(("No Overlap", test_no_overlap()))
    results.append(("Multiple Events", test_multiple_events()))
    results.append(("Score Capping", test_capping()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("\n💡 Signal generator ready for:")
        print("   - GeopoliticalAgent (Task 11)")
        print("   - Other agents using news signals")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
