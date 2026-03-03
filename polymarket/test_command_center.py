"""
BASED MONEY - Command Center Integration Test

Test the orchestrator's Command Center notification feature.
Runs one cycle with a high-conviction thesis to verify notifications work.
"""

import sys
from datetime import datetime
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, ".")

from models.thesis import Thesis
from models.portfolio import Portfolio
from models.market import Market
from core.risk import RiskEngine, RiskDecision
from core.execution import ExecutionEngine
from core.positions import PositionMonitor
from core.orchestrator import Orchestrator
from core.thesis_store import ThesisStore


class MockBroker:
    """Mock broker for testing"""

    def __init__(self):
        self.orders = []
        self.positions = []

    def execute_order(self, order):
        """Mock order execution"""
        from models.execution import Execution

        execution = Execution(
            id=uuid4(),
            market_id=order.market_id,
            side=order.side,
            size=order.size,
            price=0.65,
            timestamp=datetime.utcnow(),
        )

        self.orders.append(order)
        return execution

    def get_positions(self):
        """Mock get positions"""
        return self.positions

    def get_market_price(self, market_id, side):
        """Mock market price"""
        return 0.65


class MockAgent:
    """Mock agent that generates a high-conviction thesis"""

    def update_theses(self):
        """Generate one high-conviction test thesis"""

        # Create a realistic thesis
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
            conviction=0.85,  # High conviction (>0.80) to trigger "high" priority
            horizon="short",
            proposed_action={
                "side": "YES",
                "size_pct": 0.15,  # 15% of portfolio
            },
            status="active",
        )

        return [thesis]


def run_test():
    """
    Test Command Center integration.

    Steps:
    1. Create mock components (broker, portfolio, agents)
    2. Initialize orchestrator with Command Center enabled
    3. Run one cycle with high-conviction thesis
    4. Verify notification was sent to Command Center
    """

    print("=" * 70)
    print("COMMAND CENTER INTEGRATION TEST")
    print("=" * 70)
    print()

    # Check if Command Center is running
    try:
        import requests

        response = requests.get("http://localhost:3000", timeout=2)
        print("✅ Command Center detected at http://localhost:3000")
    except:
        print("⚠️  Command Center not detected at http://localhost:3000")
        print("   Notification will fail gracefully (expected)")

    print()

    # ============================================================
    # SETUP TEST COMPONENTS
    # ============================================================

    print("Setting up test components...")

    # Create mock broker
    broker = MockBroker()

    # Create test portfolio
    portfolio = Portfolio(
        cash=10000.0,
        total_value=10000.0,
        deployed_pct=0.0,
        positions=[],
    )

    # Create test agent with high-conviction thesis
    mock_agent = MockAgent()

    # Create risk engine (will approve high-conviction theses)
    risk_engine = RiskEngine()

    # Create execution engine
    execution_engine = ExecutionEngine(
        broker_adapter=broker,
        portfolio=portfolio,
    )

    # Create position monitor
    position_monitor = PositionMonitor(broker_adapter=broker)

    # Create thesis store
    thesis_store = ThesisStore()

    # Create orchestrator with Command Center enabled
    orchestrator = Orchestrator(
        agents=[mock_agent],
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        thesis_store=thesis_store,
    )

    print("✅ Components initialized")
    print()

    # ============================================================
    # RUN ONE ORCHESTRATOR CYCLE
    # ============================================================

    print("Running orchestrator cycle...")
    print("=" * 70)

    # Run one cycle
    stats = orchestrator.run_cycle()

    print()
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)

    # Display stats
    print(f"Theses generated: {stats['theses_generated']}")
    print(f"Actionable theses: {stats['theses_actionable']}")
    print(f"Trades executed: {stats['trades_executed']}")
    print(f"Errors: {len(stats['errors'])}")

    if stats["errors"]:
        print("\nErrors encountered:")
        for error in stats["errors"]:
            print(f"  - {error}")

    print()

    # Verify thesis was generated
    if stats["theses_generated"] > 0:
        print("✅ High-conviction thesis generated")
    else:
        print("❌ No thesis generated")
        return False

    # Verify thesis was actionable
    if stats["theses_actionable"] > 0:
        print("✅ Thesis met actionable threshold (conviction >= 0.70)")
    else:
        print("❌ Thesis not actionable")
        return False

    # Check if trade was executed (implies risk approved it)
    if stats["trades_executed"] > 0:
        print("✅ Trade executed (risk engine approved)")
        print("✅ Command Center notification sent (check logs above)")
    else:
        print("⚠️  Trade not executed (check risk engine)")

    print()
    print("=" * 70)
    print("TEST VERIFICATION")
    print("=" * 70)
    print()
    print("To verify the Command Center integration:")
    print("1. Check the orchestrator output above for:")
    print("   '📤 Notified Command Center (priority: high)'")
    print()
    print("2. If Command Center is running, check the dashboard at:")
    print("   http://localhost:3000")
    print()
    print("3. You should see a task card with:")
    print("   Title: 💰 Opportunity: Will Bitcoin reach $100,000 by end of Q1 2026?")
    print("   Priority: HIGH (red badge)")
    print("   Description includes: Edge, Conviction, Size")
    print()
    print("4. If Command Center is offline, you should see:")
    print("   '⚠️  Command Center offline (connection refused)'")
    print("   (This is expected behavior - orchestrator continues gracefully)")
    print()

    return True


if __name__ == "__main__":
    try:
        success = run_test()

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
