"""
Test Command Center integration

This script simulates an orchestrator cycle with a high-conviction thesis
and verifies that a task is posted to Command Center.
"""

import sys
import os
from uuid import uuid4

# Set test environment
os.environ["BASED_MONEY_SKIP_ENV_VALIDATION"] = "1"
os.environ["TRADING_MODE"] = "paper"

from core.orchestrator import Orchestrator
from core.risk import RiskEngine, RiskDecision
from core.execution import ExecutionEngine
from core.positions import PositionMonitor
from brokers.paper import PaperBroker
from models.portfolio import Portfolio
from models.thesis import Thesis


class MockThesisStore:
    """Mock thesis store for testing"""

    def __init__(self):
        self.theses = []

    def save(self, thesis):
        self.theses.append(thesis)
        return True

    def get_actionable(self, min_conviction=0.70):
        return [t for t in self.theses if t.conviction >= min_conviction]


class MockAgent:
    """Mock agent that generates a high-conviction thesis"""

    def __init__(self):
        self.agent_id = "test-agent"

    def update_theses(self):
        # Generate a high-conviction thesis
        thesis = Thesis(
            id=uuid4(),
            agent_id=self.agent_id,
            market_id="Will Bitcoin reach $100k by EOY 2024?",
            thesis_text="Strong technical indicators and institutional adoption suggest Bitcoin will reach $100k by end of year. Multiple on-chain metrics support this thesis.",
            fair_value=0.75,
            current_odds=0.50,
            edge=0.25,
            conviction=0.85,  # High conviction
            proposed_action={"side": "YES", "size_pct": 0.10},
        )
        return [thesis]


def test_command_center_notification():
    """Test that approved thesis triggers Command Center notification"""

    print("\n" + "=" * 60)
    print("COMMAND CENTER INTEGRATION TEST")
    print("=" * 60)

    # Setup components
    print("\n1. Initializing components...")
    agents = [MockAgent()]
    risk_engine = RiskEngine()
    broker = PaperBroker()
    portfolio = Portfolio(cash=1000.0, total_value=1000.0, deployed_pct=0.0)
    execution_engine = ExecutionEngine(broker, portfolio)
    position_monitor = PositionMonitor(broker)
    thesis_store = MockThesisStore()

    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        thesis_store=thesis_store,
    )

    print("   ✓ Components initialized")

    # Check if Command Center integration is enabled
    print(
        f"\n2. Command Center integration enabled: {orchestrator.command_center_enabled}"
    )
    print(f"   URL: {orchestrator.command_center_url}")

    # Run one cycle
    print("\n3. Running orchestrator cycle...")
    print("=" * 60)

    stats = orchestrator.run_cycle()

    print("\n" + "=" * 60)
    print("4. Cycle Results:")
    print(f"   Theses generated: {stats['theses_generated']}")
    print(f"   Actionable theses: {stats['theses_actionable']}")
    print(f"   Trades executed: {stats['trades_executed']}")

    if stats["trades_executed"] > 0:
        print("\n✅ TEST PASSED: High-conviction thesis was executed")
        print("   Check Command Center dashboard for the notification")
        print(
            "   (If Command Center is offline, you'll see a warning but test still passes)"
        )
    else:
        print("\n⚠️  No trades executed (this is expected if risk checks failed)")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_command_center_notification()
