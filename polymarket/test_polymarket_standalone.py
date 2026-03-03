#!/usr/bin/env python3
"""
Standalone test of Polymarket parser (no database dependencies)
"""

import sys

sys.path.insert(0, ".")

# Only import models, not database
from models import Market
from datetime import datetime
from typing import Dict, Any, Optional


def parse_polymarket_market(data: Dict[str, Any]) -> Optional[Market]:
    """
    Local copy of parse function for testing (without database dependency)
    """
    try:
        market_id = data.get("id") or data.get("market_id") or data.get("condition_id")
        question = data.get("question") or data.get("title") or ""
        category = data.get("category") or data.get("tag") or "unknown"

        yes_price = 0.0
        no_price = 0.0

        if "outcomes" in data and isinstance(data["outcomes"], list):
            for outcome in data["outcomes"]:
                outcome_name = outcome.get("name", "").upper()
                price = float(outcome.get("price", 0.0))

                if "YES" in outcome_name:
                    yes_price = price
                elif "NO" in outcome_name:
                    no_price = price
        elif "yes_price" in data:
            yes_price = float(data.get("yes_price", 0.0))
            no_price = float(data.get("no_price", 0.0))
        elif "outcomePrices" in data:
            prices = data["outcomePrices"]
            if isinstance(prices, list) and len(prices) >= 2:
                yes_price = float(prices[0])
                no_price = float(prices[1])

        if yes_price > 0 and no_price == 0:
            no_price = 1.0 - yes_price
        elif no_price > 0 and yes_price == 0:
            yes_price = 1.0 - no_price

        volume_24h = float(
            data.get("volume")
            or data.get("volume24hr")
            or data.get("volume_24h")
            or 0.0
        )

        resolution_date = None
        end_date_str = (
            data.get("end_date_iso") or data.get("endDate") or data.get("end_date")
        )
        if end_date_str:
            try:
                resolution_date = datetime.fromisoformat(
                    end_date_str.replace("Z", "+00:00")
                )
            except:
                try:
                    resolution_date = datetime.fromtimestamp(float(end_date_str))
                except:
                    resolution_date = None

        resolved = bool(data.get("closed") or data.get("resolved") or False)
        liquidity_score = float(
            data.get("liquidityScore") or data.get("liquidity") or 0.0
        )

        if not market_id or not question:
            return None

        market = Market(
            id=str(market_id),
            question=question,
            category=category,
            yes_price=yes_price,
            no_price=no_price,
            volume_24h=volume_24h,
            resolution_date=resolution_date,
            resolved=resolved,
            liquidity_score=liquidity_score,
        )

        return market

    except Exception as e:
        print(f"Parse error: {e}")
        return None


def run_tests():
    """Run all parser tests"""

    print("\n" + "=" * 60)
    print("POLYMARKET PARSER VALIDATION (Standalone)")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Outcomes array format
    print("\n1. Testing outcomes array format...")
    data1 = {
        "id": "test1",
        "question": "Will Bitcoin reach $100k?",
        "category": "crypto",
        "outcomes": [{"name": "YES", "price": "0.65"}, {"name": "NO", "price": "0.35"}],
        "volume": "125000",
        "end_date_iso": "2026-12-31T23:59:59Z",
        "closed": False,
    }

    m1 = parse_polymarket_market(data1)
    if m1 and m1.yes_price == 0.65 and m1.no_price == 0.35:
        print("   ✅ PASSED")
        tests_passed += 1
    else:
        print("   ❌ FAILED")
        tests_failed += 1

    # Test 2: Direct price fields
    print("\n2. Testing direct price fields...")
    data2 = {
        "id": "test2",
        "question": "Test market 2",
        "yes_price": 0.52,
        "no_price": 0.48,
        "volume24hr": 250000,
    }

    m2 = parse_polymarket_market(data2)
    if m2 and m2.yes_price == 0.52:
        print("   ✅ PASSED")
        tests_passed += 1
    else:
        print("   ❌ FAILED")
        tests_failed += 1

    # Test 3: outcomePrices array
    print("\n3. Testing outcomePrices format...")
    data3 = {
        "market_id": "test3",
        "title": "Test market 3",
        "tag": "geopolitical",
        "outcomePrices": ["0.42", "0.58"],
        "volume": 500000,
    }

    m3 = parse_polymarket_market(data3)
    if m3 and m3.yes_price == 0.42 and m3.category == "geopolitical":
        print("   ✅ PASSED")
        tests_passed += 1
    else:
        print("   ❌ FAILED")
        tests_failed += 1

    # Test 4: Missing required fields (should fail)
    print("\n4. Testing error handling...")
    data4 = {"id": "test4"}  # Missing question

    m4 = parse_polymarket_market(data4)
    if m4 is None:
        print("   ✅ PASSED (correctly rejected)")
        tests_passed += 1
    else:
        print("   ❌ FAILED (should have rejected)")
        tests_failed += 1

    # Test 5: Model to_dict()
    print("\n5. Testing Market.to_dict()...")
    if m1:
        d = m1.to_dict()
        if "id" in d and "question" in d and "yes_price" in d:
            print("   ✅ PASSED")
            tests_passed += 1
        else:
            print("   ❌ FAILED")
            tests_failed += 1
    else:
        print("   ⏭️  SKIPPED")

    # Summary
    print("\n" + "=" * 60)
    print(f"RESULTS: {tests_passed} passed, {tests_failed} failed")

    if tests_failed == 0:
        print("✅ ALL TESTS PASSED")
        print("\n💡 Next steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Test live API: python ingestion/polymarket.py")
        print("   3. Integrate with database: save fetched markets")
    else:
        print("❌ SOME TESTS FAILED")
        return False

    print("=" * 60 + "\n")
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
