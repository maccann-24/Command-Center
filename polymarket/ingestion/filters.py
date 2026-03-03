"""
BASED MONEY - Market Filtering
Filter markets by tradeability criteria
"""

from typing import List
import sys

sys.path.insert(0, "..")

from models import Market
from database import record_event


def filter_tradeable_markets(markets: List[Market]) -> List[Market]:
    """
    Filter markets by tradeability criteria.

    A market is tradeable if:
    - volume_24h >= $50,000
    - liquidity_score >= 0.3 (if available, else skip check)
    - days_to_resolution >= 2
    - resolved == False

    Args:
        markets: List of Market objects to filter

    Returns:
        List of tradeable Market objects
    """
    if not markets:
        print("⚠️ No markets to filter")
        return []

    total_count = len(markets)
    tradeable = []

    # Filter criteria from config (can be overridden)
    MIN_VOLUME = 50000.0
    MIN_LIQUIDITY = 0.3
    MIN_DAYS_TO_RESOLUTION = 2

    for market in markets:
        # Check 1: Not resolved
        if market.resolved:
            continue

        # Check 2: Sufficient volume
        if market.volume_24h < MIN_VOLUME:
            continue

        # Check 3: Liquidity score (if available)
        if market.liquidity_score > 0:  # Only check if set
            if market.liquidity_score < MIN_LIQUIDITY:
                continue

        # Check 4: Sufficient time to resolution
        days_left = market.days_to_resolution()
        if days_left is not None and days_left < MIN_DAYS_TO_RESOLUTION:
            continue

        # Passed all checks
        tradeable.append(market)

    filtered_count = len(tradeable)

    # Log summary
    print(f"📊 Filtered to {filtered_count} tradeable markets from {total_count} total")

    # Detailed breakdown (optional, for debugging)
    if filtered_count < total_count:
        filtered_out = total_count - filtered_count
        print(f"   Filtered out: {filtered_out} markets")
        print(f"   Reasons: low volume, resolved, too soon to expire, or low liquidity")

    # Record event
    record_event(
        event_type="markets_filtered",
        details={
            "total_markets": total_count,
            "tradeable_markets": filtered_count,
            "filtered_out": total_count - filtered_count,
            "criteria": {
                "min_volume": MIN_VOLUME,
                "min_liquidity": MIN_LIQUIDITY,
                "min_days": MIN_DAYS_TO_RESOLUTION,
            },
        },
        severity="info",
    )

    return tradeable


def filter_by_category(markets: List[Market], category: str) -> List[Market]:
    """
    Filter markets by category.

    Args:
        markets: List of Market objects
        category: Category to filter by (e.g., "geopolitical", "crypto")

    Returns:
        List of markets matching category
    """
    filtered = [m for m in markets if m.category.lower() == category.lower()]

    print(f"📊 Filtered to {len(filtered)} markets in category '{category}'")

    return filtered


def filter_by_volume_range(
    markets: List[Market], min_volume: float, max_volume: float = float("inf")
) -> List[Market]:
    """
    Filter markets by volume range.

    Args:
        markets: List of Market objects
        min_volume: Minimum 24h volume
        max_volume: Maximum 24h volume (default: unlimited)

    Returns:
        List of markets within volume range
    """
    filtered = [m for m in markets if min_volume <= m.volume_24h <= max_volume]

    print(
        f"📊 Filtered to {len(filtered)} markets with volume ${min_volume:,.0f}-${max_volume:,.0f}"
    )

    return filtered


def get_filtering_stats(markets: List[Market]) -> dict:
    """
    Get statistics about why markets are filtered out.

    Args:
        markets: List of Market objects

    Returns:
        Dictionary with filtering statistics
    """
    MIN_VOLUME = 50000.0
    MIN_LIQUIDITY = 0.3
    MIN_DAYS_TO_RESOLUTION = 2

    stats = {
        "total": len(markets),
        "resolved": 0,
        "low_volume": 0,
        "low_liquidity": 0,
        "too_soon": 0,
        "tradeable": 0,
    }

    for market in markets:
        if market.resolved:
            stats["resolved"] += 1
            continue

        if market.volume_24h < MIN_VOLUME:
            stats["low_volume"] += 1
            continue

        if market.liquidity_score > 0 and market.liquidity_score < MIN_LIQUIDITY:
            stats["low_liquidity"] += 1
            continue

        days_left = market.days_to_resolution()
        if days_left is not None and days_left < MIN_DAYS_TO_RESOLUTION:
            stats["too_soon"] += 1
            continue

        stats["tradeable"] += 1

    return stats


def test_filtering():
    """
    Test market filtering with sample data.
    Run with: python -m ingestion.filters
    """
    from datetime import datetime, timedelta

    print("=" * 60)
    print("MARKET FILTERING TEST")
    print("=" * 60)

    # Create sample markets
    markets = [
        # Tradeable market 1
        Market(
            id="good1",
            question="Will Bitcoin reach $100k in 2026?",
            category="crypto",
            yes_price=0.65,
            no_price=0.35,
            volume_24h=150000.0,
            liquidity_score=0.8,
            resolution_date=datetime.utcnow() + timedelta(days=30),
            resolved=False,
        ),
        # Tradeable market 2
        Market(
            id="good2",
            question="Will Trump win 2028 election?",
            category="politics",
            yes_price=0.52,
            no_price=0.48,
            volume_24h=500000.0,
            liquidity_score=0.9,
            resolution_date=datetime.utcnow() + timedelta(days=365),
            resolved=False,
        ),
        # Resolved (should be filtered)
        Market(
            id="resolved1",
            question="Did Biden run in 2024?",
            category="politics",
            yes_price=1.0,
            no_price=0.0,
            volume_24h=1000000.0,
            liquidity_score=0.9,
            resolution_date=datetime.utcnow() - timedelta(days=1),
            resolved=True,
        ),
        # Low volume (should be filtered)
        Market(
            id="low_vol",
            question="Will it rain tomorrow?",
            category="weather",
            yes_price=0.5,
            no_price=0.5,
            volume_24h=1000.0,  # < 50k
            liquidity_score=0.5,
            resolution_date=datetime.utcnow() + timedelta(days=10),
            resolved=False,
        ),
        # Too soon to resolve (should be filtered)
        Market(
            id="too_soon",
            question="Will stock market close up today?",
            category="stocks",
            yes_price=0.5,
            no_price=0.5,
            volume_24h=75000.0,
            liquidity_score=0.6,
            resolution_date=datetime.utcnow() + timedelta(days=1),  # < 2 days
            resolved=False,
        ),
        # Low liquidity (should be filtered)
        Market(
            id="low_liq",
            question="Will some obscure event happen?",
            category="other",
            yes_price=0.5,
            no_price=0.5,
            volume_24h=60000.0,
            liquidity_score=0.2,  # < 0.3
            resolution_date=datetime.utcnow() + timedelta(days=20),
            resolved=False,
        ),
    ]

    print(f"\n📊 Total sample markets: {len(markets)}")
    print("\nMarket breakdown:")
    for m in markets:
        print(f"  • {m.question[:50]}...")
        print(
            f"    Volume: ${m.volume_24h:,.0f} | Liquidity: {m.liquidity_score:.1f} | "
            + f"Days left: {m.days_to_resolution()} | Resolved: {m.resolved}"
        )

    # Run filtering
    print("\n" + "-" * 60)
    tradeable = filter_tradeable_markets(markets)

    # Show results
    print(f"\n✅ Tradeable markets ({len(tradeable)}):")
    for m in tradeable:
        print(f"  • {m.question[:60]}...")

    # Show statistics
    print("\n" + "-" * 60)
    stats = get_filtering_stats(markets)
    print("📈 Filtering statistics:")
    print(f"  Total markets:      {stats['total']}")
    print(f"  Tradeable:          {stats['tradeable']}")
    print(f"  Resolved:           {stats['resolved']}")
    print(f"  Low volume:         {stats['low_volume']}")
    print(f"  Low liquidity:      {stats['low_liquidity']}")
    print(f"  Too soon to expire: {stats['too_soon']}")

    # Verify results
    print("\n" + "=" * 60)
    expected_tradeable = 2
    if len(tradeable) == expected_tradeable:
        print(
            f"✅ TEST PASSED: {len(tradeable)} tradeable markets (expected {expected_tradeable})"
        )
        return True
    else:
        print(
            f"❌ TEST FAILED: {len(tradeable)} tradeable markets (expected {expected_tradeable})"
        )
        return False


if __name__ == "__main__":
    import sys

    success = test_filtering()
    sys.exit(0 if success else 1)
