"""
BASED MONEY - Signal Generator
Calculate market impact scores from news events
"""

from typing import List
import sys

sys.path.insert(0, "..")

from models import Market, NewsEvent


def calculate_event_impact(market: Market, news_events: List[NewsEvent]) -> float:
    """
    Calculate the impact score of news events on a market.

    Analyzes keyword overlap between market question and recent news events
    to determine if news provides a trading signal.

    Algorithm:
    1. Extract keywords from market question (lowercase, split on spaces)
    2. Check each news event for keyword overlap
    3. Count matching events
    4. Calculate impact score:
       - 0.0 if no matches
       - 0.20 per matching event (baseline signal strength)
       - Capped at 0.40 (max 2 events worth of signal)

    Args:
        market: Market object to analyze
        news_events: List of NewsEvent objects from last 24h

    Returns:
        Impact score (float, 0.0 to 1.0 scale)
        - 0.0 = No news impact
        - 0.20 = One relevant news event
        - 0.40 = Multiple relevant news events (capped)

    Example:
        >>> market = Market(question="Will Russia invade Ukraine?")
        >>> news = [NewsEvent(headline="Russia announces military mobilization")]
        >>> score = calculate_event_impact(market, news)
        >>> # score = 0.20 (one matching event)
    """
    if not news_events:
        return 0.0

    # Step 1: Extract keywords from market question
    market_keywords = extract_keywords_from_question(market.question)

    if not market_keywords:
        return 0.0

    # Step 2: Check each news event for keyword overlap
    matching_events = 0

    for news_event in news_events:
        # Check if any market keyword appears in news event keywords
        if has_keyword_overlap(market_keywords, news_event.keywords):
            matching_events += 1

    # Step 3: Calculate impact score
    if matching_events == 0:
        impact_score = 0.0
    else:
        # Baseline: 0.20 per matching event
        impact_score = 0.20 * matching_events

        # Cap at 0.40 (diminishing returns after 2 events)
        impact_score = min(0.40, impact_score)

    return impact_score


def extract_keywords_from_question(question: str) -> List[str]:
    """
    Extract keywords from a market question.

    Simple extraction via:
    1. Lowercase the question
    2. Split on whitespace
    3. Remove common stop words
    4. Filter out very short words (<3 chars)

    Args:
        question: Market question text

    Returns:
        List of keyword strings

    Example:
        >>> extract_keywords_from_question("Will Bitcoin reach $100k?")
        ['bitcoin', 'reach', '100k']
    """
    # Common stop words to filter out
    STOP_WORDS = {
        "will",
        "the",
        "be",
        "in",
        "on",
        "at",
        "to",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "has",
        "have",
        "had",
        "do",
        "does",
        "did",
        "for",
        "of",
        "by",
        "from",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "and",
        "or",
        "but",
        "not",
        "if",
        "when",
        "where",
        "how",
        "what",
        "who",
        "which",
        "why",
        "before",
        "after",
        "during",
        "while",
        "?",
        "!",
        ".",
        ",",
        ";",
        ":",
        "-",
        "(",
        ")",
        "[",
        "]",
    }

    # Lowercase and split
    words = question.lower().split()

    # Filter: remove stop words and short words
    keywords = [
        word.strip(".,;:!?()[]{}$#@%&*")  # Remove punctuation including $
        for word in words
        if len(word) >= 3 and word.lower() not in STOP_WORDS
    ]

    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword and keyword not in seen:
            seen.add(keyword)
            unique_keywords.append(keyword)

    return unique_keywords


def has_keyword_overlap(market_keywords: List[str], news_keywords: List[str]) -> bool:
    """
    Check if there's any keyword overlap between market and news.

    Args:
        market_keywords: Keywords from market question
        news_keywords: Keywords from news event

    Returns:
        True if any keyword appears in both lists
    """
    # Convert to sets for efficient intersection
    market_set = set(keyword.lower() for keyword in market_keywords)
    news_set = set(keyword.lower() for keyword in news_keywords)

    # Check for intersection
    return len(market_set & news_set) > 0


def get_matching_keywords(
    market_keywords: List[str], news_keywords: List[str]
) -> List[str]:
    """
    Get the list of keywords that match between market and news.

    Useful for debugging and explanation of why a signal was generated.

    Args:
        market_keywords: Keywords from market question
        news_keywords: Keywords from news event

    Returns:
        List of matching keywords
    """
    market_set = set(keyword.lower() for keyword in market_keywords)
    news_set = set(keyword.lower() for keyword in news_keywords)

    return sorted(list(market_set & news_set))


# ============================================================
# TESTING UTILITIES
# ============================================================


def test_signal_generator():
    """
    Test signal generator with sample data.
    Run with: python -m agents.signals
    """
    from datetime import datetime, timedelta

    print("=" * 60)
    print("SIGNAL GENERATOR TEST")
    print("=" * 60)

    # Test 1: Single matching event
    print("\n1. Testing single matching event...")
    market = Market(
        id="test1",
        question="Will Russia invade Ukraine in 2026?",
        category="geopolitical",
        yes_price=0.50,
        no_price=0.50,
        volume_24h=100000,
    )

    news_event = NewsEvent(
        timestamp=datetime.utcnow() - timedelta(hours=1),
        headline="Russia announces military mobilization near Ukraine border",
        keywords=["russia", "military", "ukraine"],
        source="reuters",
    )

    impact = calculate_event_impact(market, [news_event])

    if impact == 0.20:
        print(f"   ✅ PASSED: impact_score = {impact:.2f} (expected 0.20)")
    else:
        print(f"   ❌ FAILED: impact_score = {impact:.2f} (expected 0.20)")
        return False

    # Test 2: Multiple matching events
    print("\n2. Testing multiple matching events...")
    news_events = [
        NewsEvent(
            timestamp=datetime.utcnow() - timedelta(hours=1),
            headline="Russia military buildup near Ukraine",
            keywords=["russia", "military", "ukraine"],
            source="reuters",
        ),
        NewsEvent(
            timestamp=datetime.utcnow() - timedelta(hours=2),
            headline="Ukraine requests NATO support amid Russia tensions",
            keywords=["ukraine", "nato", "russia"],
            source="ap",
        ),
        NewsEvent(
            timestamp=datetime.utcnow() - timedelta(hours=3),
            headline="Russia and Ukraine hold talks",
            keywords=["russia", "ukraine"],
            source="ap",
        ),
    ]

    impact = calculate_event_impact(market, news_events)

    if impact == 0.40:  # 3 events * 0.20, capped at 0.40
        print(f"   ✅ PASSED: impact_score = {impact:.2f} (expected 0.40, capped)")
    else:
        print(f"   ❌ FAILED: impact_score = {impact:.2f} (expected 0.40)")
        return False

    # Test 3: No matching events
    print("\n3. Testing no matching events...")
    market2 = Market(
        id="test2",
        question="Will Bitcoin reach $100k?",
        category="crypto",
        yes_price=0.60,
        no_price=0.40,
        volume_24h=200000,
    )

    # News about Russia (no overlap with Bitcoin)
    impact = calculate_event_impact(market2, news_events)

    if impact == 0.0:
        print(f"   ✅ PASSED: impact_score = {impact:.2f} (expected 0.00)")
    else:
        print(f"   ❌ FAILED: impact_score = {impact:.2f} (expected 0.00)")
        return False

    # Test 4: Keyword extraction
    print("\n4. Testing keyword extraction...")
    keywords = extract_keywords_from_question("Will Russia invade Ukraine in 2026?")

    expected = ["russia", "invade", "ukraine", "2026"]
    if set(keywords) == set(expected):
        print(f"   ✅ PASSED: keywords = {keywords}")
    else:
        print(f"   ❌ FAILED: keywords = {keywords} (expected {expected})")
        return False

    # Test 5: Keyword overlap detection
    print("\n5. Testing keyword overlap...")
    market_kw = ["russia", "ukraine"]
    news_kw = ["russia", "military"]

    if has_keyword_overlap(market_kw, news_kw):
        print(f"   ✅ PASSED: overlap detected (russia)")
        matches = get_matching_keywords(market_kw, news_kw)
        print(f"   ✅ Matching keywords: {matches}")
    else:
        print(f"   ❌ FAILED: should detect overlap")
        return False

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    import sys

    success = test_signal_generator()
    sys.exit(0 if success else 1)
