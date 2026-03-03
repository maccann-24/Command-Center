#!/usr/bin/env python3
"""
Standalone test of market filtering (no database dependencies)
"""

import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta
from models import Market


def filter_tradeable_markets(markets):
    """Local copy of filter function for testing"""
    if not markets:
        return []
    
    total_count = len(markets)
    tradeable = []
    
    MIN_VOLUME = 50000.0
    MIN_LIQUIDITY = 0.3
    MIN_DAYS_TO_RESOLUTION = 2
    
    for market in markets:
        # Not resolved
        if market.resolved:
            continue
        
        # Sufficient volume
        if market.volume_24h < MIN_VOLUME:
            continue
        
        # Liquidity score (if available)
        if market.liquidity_score > 0:
            if market.liquidity_score < MIN_LIQUIDITY:
                continue
        
        # Sufficient time to resolution
        days_left = market.days_to_resolution()
        if days_left is not None and days_left < MIN_DAYS_TO_RESOLUTION:
            continue
        
        tradeable.append(market)
    
    filtered_count = len(tradeable)
    print(f"📊 Filtered to {filtered_count} tradeable markets from {total_count} total")
    
    return tradeable


def test_basic_filtering():
    """Test basic filtering logic"""
    print("\n" + "=" * 60)
    print("BASIC FILTERING TEST")
    print("=" * 60)
    
    # Create test markets
    markets = [
        # Good market 1
        Market(
            id="good1",
            question="Will Bitcoin reach $100k?",
            category="crypto",
            yes_price=0.65,
            no_price=0.35,
            volume_24h=150000.0,
            liquidity_score=0.8,
            resolution_date=datetime.utcnow() + timedelta(days=30),
            resolved=False
        ),
        # Good market 2
        Market(
            id="good2",
            question="Will Trump win 2028?",
            category="politics",
            yes_price=0.52,
            no_price=0.48,
            volume_24h=500000.0,
            liquidity_score=0.9,
            resolution_date=datetime.utcnow() + timedelta(days=365),
            resolved=False
        ),
        # Resolved (filtered)
        Market(
            id="resolved",
            question="Resolved market",
            category="test",
            yes_price=1.0,
            no_price=0.0,
            volume_24h=1000000.0,
            resolved=True
        ),
        # Low volume (filtered)
        Market(
            id="low_vol",
            question="Low volume market",
            category="test",
            yes_price=0.5,
            no_price=0.5,
            volume_24h=1000.0,  # < 50k
            resolved=False
        ),
    ]
    
    print(f"\nInput: {len(markets)} markets")
    
    # Filter
    tradeable = filter_tradeable_markets(markets)
    
    print(f"\nOutput: {len(tradeable)} tradeable markets")
    for m in tradeable:
        print(f"  ✓ {m.question}")
    
    # Verify
    if len(tradeable) == 2:
        print("\n✅ PASSED: 2 tradeable markets")
        return True
    else:
        print(f"\n❌ FAILED: Expected 2, got {len(tradeable)}")
        return False


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "=" * 60)
    print("EDGE CASES TEST")
    print("=" * 60)
    
    # Test 1: Empty list
    print("\n1. Empty list...")
    result = filter_tradeable_markets([])
    if len(result) == 0:
        print("   ✅ PASSED")
    else:
        print("   ❌ FAILED")
        return False
    
    # Test 2: Market with no liquidity score (should skip liquidity check)
    print("\n2. Market with no liquidity score...")
    market = Market(
        id="no_liq",
        question="No liquidity score",
        category="test",
        yes_price=0.5,
        no_price=0.5,
        volume_24h=100000.0,
        liquidity_score=0.0,  # Not set
        resolution_date=datetime.utcnow() + timedelta(days=10),
        resolved=False
    )
    result = filter_tradeable_markets([market])
    if len(result) == 1:
        print("   ✅ PASSED (liquidity check skipped)")
    else:
        print("   ❌ FAILED (should pass when liquidity=0)")
        return False
    
    # Test 3: Market with no resolution date (should pass days check)
    print("\n3. Market with no resolution date...")
    market = Market(
        id="no_date",
        question="No resolution date",
        category="test",
        yes_price=0.5,
        no_price=0.5,
        volume_24h=100000.0,
        liquidity_score=0.5,
        resolution_date=None,
        resolved=False
    )
    result = filter_tradeable_markets([market])
    if len(result) == 1:
        print("   ✅ PASSED (days check skipped)")
    else:
        print("   ❌ FAILED")
        return False
    
    # Test 4: Market exactly at threshold (should pass)
    print("\n4. Market exactly at volume threshold...")
    market = Market(
        id="threshold",
        question="Exactly $50k volume",
        category="test",
        yes_price=0.5,
        no_price=0.5,
        volume_24h=50000.0,  # Exactly at threshold
        liquidity_score=0.3,  # Exactly at threshold
        resolution_date=datetime.utcnow() + timedelta(days=3),  # Safely above threshold
        resolved=False
    )
    result = filter_tradeable_markets([market])
    if len(result) == 1:
        print("   ✅ PASSED (threshold values accepted)")
    else:
        print("   ❌ FAILED (should accept threshold values)")
        print(f"      Market: vol={market.volume_24h}, liq={market.liquidity_score}, days={market.days_to_resolution()}")
        return False
    
    # Test 5: Market just below threshold (should fail)
    print("\n5. Market just below thresholds...")
    market = Market(
        id="below",
        question="Just below threshold",
        category="test",
        yes_price=0.5,
        no_price=0.5,
        volume_24h=49999.0,  # Just below
        liquidity_score=0.29,  # Just below
        resolution_date=datetime.utcnow() + timedelta(days=1),  # Just below
        resolved=False
    )
    result = filter_tradeable_markets([market])
    if len(result) == 0:
        print("   ✅ PASSED (correctly filtered)")
    else:
        print("   ❌ FAILED (should filter markets below threshold)")
        return False
    
    print("\n✅ All edge cases PASSED")
    return True


def test_filter_criteria():
    """Test each filter criterion individually"""
    print("\n" + "=" * 60)
    print("FILTER CRITERIA TEST")
    print("=" * 60)
    
    base_market = Market(
        id="base",
        question="Base market",
        category="test",
        yes_price=0.5,
        no_price=0.5,
        volume_24h=100000.0,
        liquidity_score=0.5,
        resolution_date=datetime.utcnow() + timedelta(days=10),
        resolved=False
    )
    
    # Test resolved=True
    print("\n1. Resolved market...")
    m = Market.from_dict(base_market.to_dict())
    m.resolved = True
    result = filter_tradeable_markets([m])
    if len(result) == 0:
        print("   ✅ PASSED (resolved market filtered)")
    else:
        print("   ❌ FAILED")
        return False
    
    # Test low volume
    print("\n2. Low volume market...")
    m = Market.from_dict(base_market.to_dict())
    m.volume_24h = 10000.0
    result = filter_tradeable_markets([m])
    if len(result) == 0:
        print("   ✅ PASSED (low volume filtered)")
    else:
        print("   ❌ FAILED")
        return False
    
    # Test low liquidity
    print("\n3. Low liquidity market...")
    m = Market.from_dict(base_market.to_dict())
    m.liquidity_score = 0.1
    result = filter_tradeable_markets([m])
    if len(result) == 0:
        print("   ✅ PASSED (low liquidity filtered)")
    else:
        print("   ❌ FAILED")
        return False
    
    # Test too soon
    print("\n4. Too soon to resolution...")
    m = Market.from_dict(base_market.to_dict())
    m.resolution_date = datetime.utcnow() + timedelta(hours=12)
    result = filter_tradeable_markets([m])
    if len(result) == 0:
        print("   ✅ PASSED (too soon filtered)")
    else:
        print("   ❌ FAILED")
        return False
    
    # Test all criteria pass
    print("\n5. All criteria pass...")
    m = Market.from_dict(base_market.to_dict())
    result = filter_tradeable_markets([m])
    if len(result) == 1:
        print("   ✅ PASSED (market accepted)")
    else:
        print("   ❌ FAILED")
        return False
    
    print("\n✅ All criteria tests PASSED")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MARKET FILTERING VALIDATION (Standalone)")
    print("=" * 60)
    
    success = True
    
    if not test_basic_filtering():
        success = False
    
    if not test_edge_cases():
        success = False
    
    if not test_filter_criteria():
        success = False
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
        print("\n💡 Next steps:")
        print("   1. Install dependencies if needed")
        print("   2. Test with live API: python ingestion/filters.py")
        print("   3. Integrate with fetch_markets() workflow")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60 + "\n")
    
    return success


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
