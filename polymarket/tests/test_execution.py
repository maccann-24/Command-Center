"""
Test core/execution.py - Execution Engine Integration Tests
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set minimal env for tests
os.environ["BASED_MONEY_SKIP_ENV_VALIDATION"] = "1"
os.environ["TRADING_MODE"] = "paper"

from uuid import uuid4
from datetime import datetime, timezone

from core.execution import ExecutionEngine, SecurityError, ExecutionError
from core.risk import RiskEngine, RiskDecision
from brokers.base import BrokerAdapter, Order, Execution
from models.portfolio import Portfolio, Position
from models.thesis import Thesis

# ============================================================
# MOCK BROKER
# ============================================================


class MockBroker(BrokerAdapter):
    """Mock broker for testing"""

    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.executed_orders = []

    def execute_order(self, order: Order) -> Execution:
        """Mock execution"""
        self.executed_orders.append(order)

        if self.should_fail:
            return Execution(
                order_id=str(uuid4()),
                market_id=order.market_id,
                side=order.side,
                size=0.0,
                price=0.0,
                timestamp=datetime.now(timezone.utc),
                status="REJECTED",
                message="Mock rejection",
            )

        # Simulate successful fill
        fill_price = (
            order.limit_price * 1.01
            if order.side == "YES"
            else order.limit_price * 0.99
        )
        shares = order.size / fill_price

        return Execution(
            order_id=str(uuid4()),
            market_id=order.market_id,
            side=order.side,
            size=shares,
            price=fill_price,
            timestamp=datetime.now(timezone.utc),
            status="FILLED",
            broker_order_id=order.client_order_id,
        )

    def get_position(self, market_id: str):
        return None

    def cancel_order(self, order_id: str) -> bool:
        return True


# ============================================================
# TEST 1: Approved Execution
# ============================================================


def test_approved_execution():
    """
    Test successful execution flow:
    - Approved risk decision
    - Position created
    - Portfolio cash decreased
    - Event logged (best effort)
    """
    print("\n" + "=" * 60)
    print("TEST 1: Approved Execution")
    print("=" * 60)

    # Setup
    broker = MockBroker()
    portfolio = Portfolio(
        cash=1000.0,
        total_value=1000.0,
        deployed_pct=0.0,
        positions=[],
    )

    engine = ExecutionEngine(broker_adapter=broker, portfolio=portfolio)

    # Create approved risk decision
    risk_decision = RiskDecision(
        approved=True,
        reason="All checks passed",
        risk_notes=["Position size: 10.0%", "Conviction: 0.85"],
        recommended_size=10.0,
    )

    # Create thesis
    thesis = Thesis(
        id=uuid4(),
        agent_id="test-agent",
        market_id="btc-100k",
        thesis_text="Bitcoin will reach $100k by EOY 2024",
        fair_value=0.75,
        current_odds=0.50,
        edge=0.25,
        conviction=0.85,
        proposed_action={"side": "YES", "size_pct": 0.10},  # 10% of portfolio
    )

    # Record initial state
    initial_cash = portfolio.cash
    initial_positions = len(portfolio.positions)

    # Execute
    execution = engine.execute(risk_decision, thesis)

    # ============================================================
    # VERIFY EXECUTION
    # ============================================================
    assert execution is not None, "Execution should return"
    assert execution.status == "FILLED", f"Expected FILLED, got {execution.status}"
    assert execution.market_id == "btc-100k", "Market ID mismatch"
    assert execution.side == "YES", "Side mismatch"
    assert execution.size > 0, "Shares should be positive"

    print(f"  ✓ Execution: {execution.size:.2f} shares @ ${execution.price:.4f}")

    # ============================================================
    # VERIFY POSITION CREATED
    # ============================================================
    assert len(portfolio.positions) == initial_positions + 1, "Position not added"

    position = portfolio.positions[0]
    assert position.market_id == "btc-100k", "Position market ID mismatch"
    assert position.side == "YES", "Position side mismatch"
    assert position.shares == execution.size, "Position shares mismatch"
    assert position.entry_price == execution.price, "Position entry price mismatch"
    assert (
        position.status == "open"
    ), f"Position status should be 'open', got {position.status}"
    assert position.thesis_id == thesis.id, "Position not linked to thesis"

    print(
        f"  ✓ Position created: {position.shares:.2f} shares @ ${position.entry_price:.4f}"
    )

    # ============================================================
    # VERIFY PORTFOLIO CASH DECREASED
    # ============================================================
    expected_cost = execution.size * execution.price
    expected_cash = initial_cash - expected_cost

    assert portfolio.cash < initial_cash, "Cash should decrease"
    assert (
        abs(portfolio.cash - expected_cash) < 0.01
    ), f"Cash mismatch: expected ${expected_cash:.2f}, got ${portfolio.cash:.2f}"

    print(
        f"  ✓ Cash: ${initial_cash:.2f} → ${portfolio.cash:.2f} (cost: ${expected_cost:.2f})"
    )

    # ============================================================
    # VERIFY DEPLOYED PERCENTAGE UPDATED
    # ============================================================
    assert portfolio.deployed_pct > 0, "Deployed percentage should increase"

    # Expected deployed: (position value / total value) * 100
    position_value = position.shares * position.current_price
    expected_deployed = (position_value / portfolio.total_value) * 100.0

    assert (
        abs(portfolio.deployed_pct - expected_deployed) < 1.0
    ), f"Deployed % mismatch: expected {expected_deployed:.2f}%, got {portfolio.deployed_pct:.2f}%"

    print(f"  ✓ Deployed: {portfolio.deployed_pct:.2f}%")

    # ============================================================
    # VERIFY BROKER EXECUTED ORDER
    # ============================================================
    assert len(broker.executed_orders) == 1, "Broker should have executed 1 order"

    order = broker.executed_orders[0]
    assert order.market_id == "btc-100k", "Order market ID mismatch"
    assert order.side == "YES", "Order side mismatch"
    assert (
        order.size == 100.0
    ), f"Order size should be $100 (10% of $1000), got ${order.size}"

    print(
        f"  ✓ Order executed: {order.side} ${order.size:.2f} @ ${order.limit_price:.4f}"
    )

    print("\n✅ TEST 1 PASSED: Approved execution successful\n")


# ============================================================
# TEST 2: Rejected Execution
# ============================================================


def test_rejected_execution():
    """
    Test rejected execution:
    - Rejected risk decision
    - SecurityError raised
    - No position created
    - No cash moved
    """
    print("\n" + "=" * 60)
    print("TEST 2: Rejected Execution")
    print("=" * 60)

    # Setup
    broker = MockBroker()
    portfolio = Portfolio(
        cash=1000.0,
        total_value=1000.0,
        deployed_pct=0.0,
        positions=[],
    )

    engine = ExecutionEngine(broker_adapter=broker, portfolio=portfolio)

    # Create rejected risk decision
    risk_decision = RiskDecision(
        approved=False,
        reason="Conviction too low",
        risk_notes=["Conviction: 0.50 < minimum 0.70"],
        recommended_size=0.0,
    )

    # Create thesis (with low conviction)
    thesis = Thesis(
        id=uuid4(),
        agent_id="test-agent",
        market_id="btc-100k",
        thesis_text="Test thesis",
        fair_value=0.75,
        current_odds=0.50,
        edge=0.25,
        conviction=0.50,  # Below threshold
        proposed_action={"side": "YES", "size_pct": 0.10},
    )

    # Record initial state
    initial_cash = portfolio.cash
    initial_positions = len(portfolio.positions)

    # ============================================================
    # ATTEMPT EXECUTION (should fail)
    # ============================================================
    try:
        execution = engine.execute(risk_decision, thesis)
        print("❌ FAIL: Should have raised SecurityError")
        assert False, "SecurityError not raised"

    except SecurityError as e:
        print(f"  ✓ SecurityError raised: {e}")

        # Verify error message contains reason
        assert (
            "rejected trade" in str(e).lower()
        ), "Error message should mention rejected trade"
        assert (
            "conviction too low" in str(e).lower()
        ), "Error message should contain rejection reason"

    # ============================================================
    # VERIFY NO POSITION CREATED
    # ============================================================
    assert (
        len(portfolio.positions) == initial_positions
    ), "No position should be created"
    print("  ✓ No position created")

    # ============================================================
    # VERIFY NO CASH MOVED
    # ============================================================
    assert portfolio.cash == initial_cash, "Cash should not change"
    print(f"  ✓ Cash unchanged: ${portfolio.cash:.2f}")

    # ============================================================
    # VERIFY NO ORDER EXECUTED
    # ============================================================
    assert (
        len(broker.executed_orders) == 0
    ), "Broker should not have executed any orders"
    print("  ✓ No broker execution")

    print("\n✅ TEST 2 PASSED: Rejected execution blocked correctly\n")


# ============================================================
# TEST 3: Double-Check Safety
# ============================================================


def test_double_check_safety():
    """
    Test double-check catches portfolio state changes:
    - Approved risk decision initially
    - Portfolio.deployed_pct manually changed to 0.90 (over limit)
    - Execution rejected on double-check
    - SecurityError raised with "no longer valid"
    """
    print("\n" + "=" * 60)
    print("TEST 3: Double-Check Safety")
    print("=" * 60)

    # Setup
    broker = MockBroker()
    portfolio = Portfolio(
        cash=1000.0,
        total_value=1000.0,
        deployed_pct=0.0,  # Initially 0%
        positions=[],
    )

    engine = ExecutionEngine(broker_adapter=broker, portfolio=portfolio)

    # Create approved risk decision (valid at this time)
    risk_decision = RiskDecision(
        approved=True,
        reason="All checks passed (initial evaluation)",
        risk_notes=["Deployed: 0.0% + 10.0% = 10.0% < 60.0% max"],
        recommended_size=10.0,
    )

    # Create thesis
    thesis = Thesis(
        id=uuid4(),
        agent_id="test-agent",
        market_id="btc-100k",
        thesis_text="Bitcoin will reach $100k",
        fair_value=0.75,
        current_odds=0.50,
        edge=0.25,
        conviction=0.85,
        proposed_action={"side": "YES", "size_pct": 0.10},
    )

    # ============================================================
    # SIMULATE RACE CONDITION: Portfolio state changed
    # ============================================================
    # Another trade filled while this trade was being approved
    portfolio.deployed_pct = 90.0  # Now at 90% deployed (over 60% limit)

    print(f"  Portfolio state changed: deployed_pct = {portfolio.deployed_pct:.1f}%")
    print("  (Simulates another trade filling between approval and execution)")

    # Record initial state
    initial_cash = portfolio.cash
    initial_positions = len(portfolio.positions)

    # ============================================================
    # ATTEMPT EXECUTION (should fail double-check)
    # ============================================================
    try:
        execution = engine.execute(risk_decision, thesis)
        print("❌ FAIL: Should have raised SecurityError on double-check")
        assert False, "SecurityError not raised"

    except SecurityError as e:
        print(f"  ✓ SecurityError raised: {e}")

        # Verify error message indicates double-check failure
        assert (
            "no longer valid" in str(e).lower()
        ), "Error should mention 'no longer valid' (double-check failure)"
        assert (
            "portfolio state changed" in str(e).lower() or "deployed" in str(e).lower()
        ), "Error should mention portfolio state change"

    # ============================================================
    # VERIFY NO POSITION CREATED
    # ============================================================
    assert (
        len(portfolio.positions) == initial_positions
    ), "No position should be created"
    print("  ✓ No position created")

    # ============================================================
    # VERIFY NO CASH MOVED
    # ============================================================
    assert portfolio.cash == initial_cash, "Cash should not change"
    print(f"  ✓ Cash unchanged: ${portfolio.cash:.2f}")

    # ============================================================
    # VERIFY NO ORDER EXECUTED
    # ============================================================
    assert (
        len(broker.executed_orders) == 0
    ), "Broker should not execute when double-check fails"
    print("  ✓ No broker execution")

    print("\n✅ TEST 3 PASSED: Double-check caught portfolio state change\n")


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("EXECUTION ENGINE INTEGRATION TESTS")
    print("=" * 60)

    try:
        test_approved_execution()
        test_rejected_execution()
        test_double_check_safety()

        print("=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print()

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
