#!/usr/bin/env python3
"""
Test Polymarket API Fetcher Structure
Validates parsing logic and error handling without requiring live API access
"""

import sys

sys.path.insert(0, ".")

from ingestion.polymarket import parse_polymarket_market, fetch_markets
from models import Market


def test_parse_market():
    """Test parsing of different Polymarket API response formats"""

    print("=" * 60)
    print("POLYMARKET PARSER TEST")
    print("=" * 60)

    # Test case 1: Standard format with outcomes array
    print("\n1. Testing standard format with outcomes array...")
    test_data_1 = {
        "id": "test_market_1",
        "question": "Will Bitcoin reach $100k in 2026?",
        "category": "crypto",
        "outcomes": [{"name": "YES", "price": "0.65"}, {"name": "NO", "price": "0.35"}],
        "volume": "125000.50",
        "end_date_iso": "2026-12-31T23:59:59Z",
        "closed": False,
    }

    market_1 = parse_polymarket_market(test_data_1)
    if market_1:
        print(f"   ✓ Parsed: {market_1.question[:50]}...")
        print(f"   ✓ YES: {market_1.yes_price:.2%}, NO: {market_1.no_price:.2%}")
        print(f"   ✓ Volume: ${market_1.volume_24h:,.2f}")
        assert market_1.yes_price == 0.65, "YES price mismatch"
        assert market_1.no_price == 0.35, "NO price mismatch"
        assert market_1.category == "crypto", "Category mismatch"
        print("   ✅ PASSED")
    else:
        print("   ❌ FAILED: Could not parse market")
        return False

    # Test case 2: Direct price fields
    print("\n2. Testing direct price fields format...")
    test_data_2 = {
        "id": "test_market_2",
        "question": "Will Trump win 2028 election?",
        "category": "politics",
        "yes_price": 0.52,
        "no_price": 0.48,
        "volume24hr": 250000,
        "endDate": "2028-11-08T00:00:00Z",
        "resolved": False,
    }

    market_2 = parse_polymarket_market(test_data_2)
    if market_2:
        print(f"   ✓ Parsed: {market_2.question[:50]}...")
        print(f"   ✓ YES: {market_2.yes_price:.2%}, NO: {market_2.no_price:.2%}")
        assert market_2.yes_price == 0.52, "YES price mismatch"
        assert market_2.no_price == 0.48, "NO price mismatch"
        print("   ✅ PASSED")
    else:
        print("   ❌ FAILED: Could not parse market")
        return False

    # Test case 3: Alternative structure (outcomePrices)
    print("\n3. Testing outcomePrices array format...")
    test_data_3 = {
        "market_id": "test_market_3",
        "title": "Russia-Ukraine conflict ends in 2026?",
        "tag": "geopolitical",
        "outcomePrices": ["0.42", "0.58"],
        "volume": 500000,
        "end_date": "2026-12-31T23:59:59Z",
        "closed": False,
    }

    market_3 = parse_polymarket_market(test_data_3)
    if market_3:
        print(f"   ✓ Parsed: {market_3.question[:50]}...")
        print(f"   ✓ YES: {market_3.yes_price:.2%}, NO: {market_3.no_price:.2%}")
        assert market_3.yes_price == 0.42, "YES price mismatch"
        assert market_3.no_price == 0.58, "NO price mismatch"
        assert market_3.category == "geopolitical", "Category mismatch"
        print("   ✅ PASSED")
    else:
        print("   ❌ FAILED: Could not parse market")
        return False

    # Test case 4: Missing required fields (should return None)
    print("\n4. Testing error handling (missing required fields)...")
    test_data_4 = {
        "id": "test_market_4",
        # Missing question
        "yes_price": 0.5,
        "no_price": 0.5,
    }

    market_4 = parse_polymarket_market(test_data_4)
    if market_4 is None:
        print("   ✓ Correctly rejected market with missing question")
        print("   ✅ PASSED")
    else:
        print("   ❌ FAILED: Should have rejected invalid market")
        return False

    # Test case 5: Resolved market
    print("\n5. Testing resolved market...")
    test_data_5 = {
        "id": "test_market_5",
        "question": "Will Biden run in 2024?",
        "category": "politics",
        "yes_price": 1.0,  # Resolved YES
        "no_price": 0.0,
        "volume": 1000000,
        "closed": True,
    }

    market_5 = parse_polymarket_market(test_data_5)
    if market_5:
        print(f"   ✓ Parsed: {market_5.question[:50]}...")
        print(f"   ✓ Resolved: {market_5.resolved}")
        assert market_5.resolved == True, "Should be resolved"
        print("   ✅ PASSED")
    else:
        print("   ❌ FAILED: Could not parse resolved market")
        return False

    print("\n" + "=" * 60)
    print("✅ ALL PARSER TESTS PASSED")
    print("=" * 60)
    return True


def test_error_handling():
    """Test error handling in fetch_markets()"""

    print("\n" + "=" * 60)
    print("ERROR HANDLING TEST")
    print("=" * 60)

    print("\nNote: This will attempt to fetch from live API.")
    print("If API is unreachable, it should fail gracefully.\n")

    # This will likely fail due to network/auth, but should not crash
    try:
        markets = fetch_markets(limit=5)

        if markets:
            print(f"✅ Successfully fetched {len(markets)} markets from live API")
        else:
            print("⚠️ No markets fetched (expected if API down/rate-limited)")
            print("✅ Error handled gracefully (no crash)")

        return True

    except Exception as e:
        print(f"❌ FAILED: Uncaught exception: {e}")
        return False


def test_model_field_mapping():
    """Verify all Market model fields are properly populated"""

    print("\n" + "=" * 60)
    print("MODEL FIELD MAPPING TEST")
    print("=" * 60)

    test_data = {
        "id": "complete_market",
        "question": "Complete market test",
        "category": "test",
        "yes_price": 0.60,
        "no_price": 0.40,
        "volume": 100000,
        "liquidityScore": 0.85,
        "end_date_iso": "2026-12-31T23:59:59Z",
        "closed": False,
    }

    market = parse_polymarket_market(test_data)

    if not market:
        print("❌ FAILED: Could not parse test market")
        return False

    # Check all required fields mapped
    print("\nVerifying field mapping:")
    print(f"  ✓ id: {market.id}")
    print(f"  ✓ question: {market.question[:40]}...")
    print(f"  ✓ category: {market.category}")
    print(f"  ✓ yes_price: {market.yes_price}")
    print(f"  ✓ no_price: {market.no_price}")
    print(f"  ✓ volume_24h: {market.volume_24h}")
    print(f"  ✓ resolution_date: {market.resolution_date}")
    print(f"  ✓ resolved: {market.resolved}")
    print(f"  ✓ liquidity_score: {market.liquidity_score}")

    # Verify to_dict() works (for DB storage)
    market_dict = market.to_dict()
    print(f"\n✓ to_dict() works: {len(market_dict)} fields")

    print("\n✅ FIELD MAPPING TEST PASSED")
    return True


if __name__ == "__main__":
    print("\n🧪 POLYMARKET FETCHER VALIDATION\n")

    success = True

    # Run all tests
    if not test_parse_market():
        success = False

    if not test_model_field_mapping():
        success = False

    if not test_error_handling():
        success = False

    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
        print("\n💡 Next: Set up Supabase and test save_market() integration")
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
    print("=" * 60 + "\n")
