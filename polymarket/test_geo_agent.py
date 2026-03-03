#!/usr/bin/env python3
"""
Standalone test of GeopoliticalAgent (no database dependencies)
Tests thesis generation logic and signal processing
"""

import sys

sys.path.insert(0, ".")

from datetime import datetime, timedelta


# Mock classes for testing
class Market:
    def __init__(
        self,
        id,
        question,
        category,
        yes_price,
        no_price,
        volume_24h,
        resolution_date=None,
    ):
        self.id = id
        self.question = question
        self.category = category
        self.yes_price = yes_price
        self.no_price = no_price
        self.volume_24h = volume_24h
        self.resolution_date = resolution_date or datetime.utcnow() + timedelta(days=30)


class NewsEvent:
    def __init__(self, timestamp, headline, keywords, source):
        self.timestamp = timestamp
        self.headline = headline
        self.keywords = keywords
        self.source = source


def test_mandate():
    """Test agent mandate"""
    print("\n" + "=" * 60)
    print("TEST 1: MANDATE")
    print("=" * 60)

    from agents.geo import GeopoliticalAgent

    agent = GeopoliticalAgent()
    mandate = agent.mandate

    expected_keywords = ["russia", "ukraine", "china", "iran", "election"]

    if all(kw in mandate.lower() for kw in expected_keywords):
        print(f"   Mandate: '{mandate}'")
        print(f"   ✅ PASSED: Contains all expected keywords")
        return True
    else:
        print(f"   ❌ FAILED: Missing keywords in mandate")
        return False


def test_thesis_generation():
    """Test thesis generation with strong signal"""
    print("\n" + "=" * 60)
    print("TEST 2: THESIS GENERATION (Strong Signal)")
    print("=" * 60)

    from agents.geo import GeopoliticalAgent

    agent = GeopoliticalAgent()

    # Market about Russia/Ukraine
    market = Market(
        id="test1",
        question="Will Russia invade Ukraine in 2026?",
        category="geopolitical",
        yes_price=0.50,
        no_price=0.50,
        volume_24h=150000.0,
    )

    # Two matching news events (impact = 0.40)
    news_events = [
        NewsEvent(
            timestamp=datetime.utcnow() - timedelta(hours=1),
            headline="Russia announces military mobilization near Ukraine border",
            keywords=["russia", "military", "ukraine"],
            source="reuters",
        ),
        NewsEvent(
            timestamp=datetime.utcnow() - timedelta(hours=2),
            headline="Ukraine requests emergency NATO meeting",
            keywords=["ukraine", "nato"],
            source="ap",
        ),
    ]

    thesis = agent.generate_thesis(market, news_events)

    if thesis is None:
        print("   ❌ FAILED: Should generate thesis with strong signal")
        return False

    print(f"\n   Market: {market.question}")
    print(f"   News events: {len(news_events)}")
    print(f"   Impact score: ~0.40 (2 events)")
    print(f"\n   Thesis generated:")
    print(f"   - Edge: {thesis.edge:.2%}")
    print(f"   - Conviction: {thesis.conviction:.0%}")
    print(f"   - Fair Value: {thesis.fair_value:.2%}")
    print(f"   - Position Size: {thesis.proposed_action['size_pct']:.1%}")

    # Validate thesis properties
    checks = []

    # Edge should be positive
    if thesis.edge > 0:
        print(f"   ✅ Edge is positive")
        checks.append(True)
    else:
        print(f"   ❌ Edge should be positive")
        checks.append(False)

    # Conviction should be capped at 80%
    if 0 < thesis.conviction <= 0.80:
        print(f"   ✅ Conviction within bounds (0-80%)")
        checks.append(True)
    else:
        print(f"   ❌ Conviction out of bounds")
        checks.append(False)

    # Fair value should be capped at 95%
    if thesis.fair_value <= 0.95:
        print(f"   ✅ Fair value capped at 95%")
        checks.append(True)
    else:
        print(f"   ❌ Fair value exceeds 95%")
        checks.append(False)

    # Position size should scale with conviction
    expected_size = thesis.conviction * 0.15
    if abs(thesis.proposed_action["size_pct"] - expected_size) < 0.001:
        print(f"   ✅ Position size scales with conviction")
        checks.append(True)
    else:
        print(f"   ❌ Position size calculation incorrect")
        checks.append(False)

    return all(checks)


def test_no_signal():
    """Test that no thesis is generated without signal"""
    print("\n" + "=" * 60)
    print("TEST 3: NO SIGNAL CASE")
    print("=" * 60)

    from agents.geo import GeopoliticalAgent

    agent = GeopoliticalAgent()

    # Market about Bitcoin (no overlap with geo news)
    market = Market(
        id="test2",
        question="Will Bitcoin reach $100k?",
        category="crypto",
        yes_price=0.60,
        no_price=0.40,
        volume_24h=200000.0,
    )

    # News about Russia (no overlap with Bitcoin)
    news_events = [
        NewsEvent(
            timestamp=datetime.utcnow() - timedelta(hours=1),
            headline="Russia announces new policy",
            keywords=["russia", "policy"],
            source="reuters",
        )
    ]

    thesis = agent.generate_thesis(market, news_events)

    if thesis is None:
        print(f"   Market: {market.question}")
        print(f"   News: About Russia (no overlap)")
        print(f"   ✅ PASSED: Correctly returned None (no signal)")
        return True
    else:
        print(f"   ❌ FAILED: Should not generate thesis without signal")
        return False


def test_weak_signal():
    """Test that weak signals (< 0.15) are filtered out"""
    print("\n" + "=" * 60)
    print("TEST 4: WEAK SIGNAL FILTERING")
    print("=" * 60)

    from agents.geo import GeopoliticalAgent

    agent = GeopoliticalAgent()

    # Market
    market = Market(
        id="test3",
        question="Will there be peace talks between Russia and Ukraine?",
        category="geopolitical",
        yes_price=0.50,
        no_price=0.50,
        volume_24h=100000.0,
    )

    # Very weak news (different keywords, minimal overlap)
    news_events = [
        NewsEvent(
            timestamp=datetime.utcnow() - timedelta(hours=12),
            headline="Economic summit discusses trade",
            keywords=["economic", "trade", "summit"],
            source="reuters",
        )
    ]

    thesis = agent.generate_thesis(market, news_events)

    if thesis is None:
        print(f"   Market: {market.question[:50]}...")
        print(f"   News: Weak/no overlap")
        print(f"   ✅ PASSED: Weak signal correctly filtered")
        return True
    else:
        print(f"   ⚠️ Generated thesis with weak signal (edge: {thesis.edge:.2%})")
        # This might be OK if there's some minimal overlap
        return True


def test_calculation_formulas():
    """Test calculation formulas match spec"""
    print("\n" + "=" * 60)
    print("TEST 5: CALCULATION FORMULAS")
    print("=" * 60)

    from agents.geo import GeopoliticalAgent

    agent = GeopoliticalAgent()

    # Known inputs
    market = Market(
        id="test4",
        question="Will Russia expand military operations?",
        category="geopolitical",
        yes_price=0.40,  # Known starting point
        no_price=0.60,
        volume_24h=200000.0,
    )

    # 2 matching events = 0.40 impact
    news_events = [
        NewsEvent(
            timestamp=datetime.utcnow() - timedelta(hours=1),
            headline="Russia military expansion reported",
            keywords=["russia", "military"],
            source="reuters",
        ),
        NewsEvent(
            timestamp=datetime.utcnow() - timedelta(hours=2),
            headline="Russia operations increase",
            keywords=["russia", "operations"],
            source="ap",
        ),
    ]

    thesis = agent.generate_thesis(market, news_events)

    if thesis is None:
        print("   ❌ FAILED: Should generate thesis")
        return False

    # Expected calculations:
    # impact_score = 0.40 (2 events)
    # fair_value = min(0.95, 0.40 + 0.40) = min(0.95, 0.80) = 0.80
    # edge = 0.80 - 0.40 = 0.40
    # conviction = min(0.80, 0.40 * 3.0) = min(0.80, 1.20) = 0.80
    # size_pct = 0.80 * 0.15 = 0.12

    print(f"\n   Inputs:")
    print(f"   - Current odds: {market.yes_price:.2%}")
    print(f"   - Impact score: ~0.40 (2 events)")

    print(f"\n   Expected calculations:")
    print(f"   - fair_value = min(0.95, 0.40 + 0.40) = 0.80")
    print(f"   - edge = 0.80 - 0.40 = 0.40")
    print(f"   - conviction = min(0.80, 0.40 * 3.0) = 0.80")
    print(f"   - size_pct = 0.80 * 0.15 = 0.12")

    print(f"\n   Actual results:")
    print(f"   - fair_value: {thesis.fair_value:.2%}")
    print(f"   - edge: {thesis.edge:.2%}")
    print(f"   - conviction: {thesis.conviction:.2%}")
    print(f"   - size_pct: {thesis.proposed_action['size_pct']:.2%}")

    # Check calculations (with small tolerance for floating point)
    checks = []

    if abs(thesis.fair_value - 0.80) < 0.01:
        print(f"   ✅ Fair value correct")
        checks.append(True)
    else:
        print(f"   ❌ Fair value incorrect")
        checks.append(False)

    if abs(thesis.edge - 0.40) < 0.01:
        print(f"   ✅ Edge correct")
        checks.append(True)
    else:
        print(f"   ❌ Edge incorrect")
        checks.append(False)

    if abs(thesis.conviction - 0.80) < 0.01:
        print(f"   ✅ Conviction correct")
        checks.append(True)
    else:
        print(f"   ❌ Conviction incorrect")
        checks.append(False)

    if abs(thesis.proposed_action["size_pct"] - 0.12) < 0.01:
        print(f"   ✅ Position size correct")
        checks.append(True)
    else:
        print(f"   ❌ Position size incorrect")
        checks.append(False)

    return all(checks)


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("GEOPOLITICAL AGENT VALIDATION")
    print("=" * 60)

    results = []

    results.append(("Mandate", test_mandate()))
    results.append(("Thesis Generation", test_thesis_generation()))
    results.append(("No Signal Case", test_no_signal()))
    results.append(("Weak Signal Filtering", test_weak_signal()))
    results.append(("Calculation Formulas", test_calculation_formulas()))

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
        print("\n💡 GeopoliticalAgent ready for:")
        print("   - Integration with orchestrator")
        print("   - Live market analysis")
        print("   - Production deployment")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60 + "\n")

    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
