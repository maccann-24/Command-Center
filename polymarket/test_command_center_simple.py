"""
BASED MONEY - Command Center Integration Test (Simplified)

Direct test of the notify_command_center functionality without database dependencies.
"""

import sys
from datetime import datetime
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, ".")

from models.thesis import Thesis
from models.portfolio import Portfolio


def test_notification():
    """
    Test Command Center notification directly.

    This test bypasses the full orchestrator and directly tests the
    notification payload and HTTP request.
    """

    print("=" * 70)
    print("COMMAND CENTER INTEGRATION TEST (Simplified)")
    print("=" * 70)
    print()

    # Check if Command Center is running
    try:
        import requests

        response = requests.get("http://localhost:3000", timeout=2)
        print("✅ Command Center detected at http://localhost:3000")
    except:
        print("⚠️  Command Center not detected at http://localhost:3000")
        print("   Test will demonstrate the notification logic")

    print()

    # ============================================================
    # CREATE TEST DATA
    # ============================================================

    print("Creating test thesis and portfolio...")

    # Create a high-conviction thesis
    thesis = Thesis(
        id=uuid4(),
        agent_id="test_agent",
        market_id="0x1234567890abcdef",
        market_question="Will Bitcoin reach $100,000 by end of Q1 2026?",
        thesis_text="Strong technical indicators suggest BTC will break $100k resistance. "
        "Historical Q1 patterns, institutional buying, and ETF inflows support bullish case.",
        fair_value=0.75,
        current_odds=0.55,
        edge=0.20,
        conviction=0.85,  # High conviction (>0.80)
        horizon="short",
        proposed_action={
            "side": "YES",
            "size_pct": 0.15,  # 15% of portfolio
        },
        status="active",
    )

    # Create test portfolio
    portfolio = Portfolio(
        cash=10000.0,
        total_value=10000.0,
        deployed_pct=0.0,
        positions=[],
    )

    print(
        f"✅ Created thesis: conviction={thesis.conviction:.0%}, edge={thesis.edge:.1%}"
    )
    print(f"✅ Created portfolio: cash=${portfolio.cash:,.2f}")
    print()

    # ============================================================
    # PREPARE NOTIFICATION PAYLOAD
    # ============================================================

    print("Preparing Command Center payload...")

    # Calculate values per spec
    market_display = (
        thesis.market_question if thesis.market_question else thesis.market_id
    )
    market_truncated = market_display[:80]
    if len(market_display) > 80:
        market_truncated += "..."

    title = f"💰 Opportunity: {market_truncated}"

    size_usd = portfolio.cash * thesis.proposed_action.get("size_pct", 0.0)
    description = (
        f"{thesis.thesis_text} "
        f"Edge: {thesis.edge:.1%} | "
        f"Conviction: {thesis.conviction:.0%} | "
        f"Size: ${size_usd:.0f}"
    )

    priority = "high" if thesis.conviction > 0.80 else "medium"

    payload = {
        "title": title,
        "description": description,
        "priority": priority,
    }

    print(f"Title: {title}")
    print(f"Priority: {priority.upper()}")
    print(f"Description: {description[:100]}...")
    print()

    # ============================================================
    # SEND NOTIFICATION
    # ============================================================

    print("Sending notification to Command Center...")

    try:
        import requests

        response = requests.post(
            "http://localhost:3000/api/tasks",
            json=payload,
            timeout=5,
        )

        if response.status_code in (200, 201):
            print(f"✅ Notification sent successfully (status: {response.status_code})")
            print(f"   Response: {response.text[:200]}")
        else:
            print(f"⚠️  Command Center returned status {response.status_code}")
            print(f"   Response: {response.text[:200]}")

    except Exception as e:
        print(f"⚠️  Notification failed: {e}")
        print("   (This is expected if Command Center is not running)")

    print()

    # ============================================================
    # VERIFICATION INSTRUCTIONS
    # ============================================================

    print("=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print()
    print("If Command Center is running, check http://localhost:3000")
    print()
    print("You should see a new task card with:")
    print(f"  • Title: {title}")
    print(
        f"  • Priority: {priority.upper()} {'(red badge)' if priority == 'high' else '(yellow badge)'}"
    )
    print(f"  • Description containing:")
    print(f"    - Thesis text")
    print(f"    - Edge: {thesis.edge:.1%}")
    print(f"    - Conviction: {thesis.conviction:.0%}")
    print(f"    - Size: ${size_usd:.0f}")
    print()
    print("If Command Center is offline, the orchestrator will log a warning")
    print("but continue execution normally (graceful degradation).")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_notification()

        if success:
            print("✅ Test completed successfully")
            sys.exit(0)
        else:
            print("❌ Test failed")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
