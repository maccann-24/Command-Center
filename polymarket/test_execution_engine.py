"""
Test core/execution.py - Execution Engine
"""

import sys
import os

# Set minimal env for tests
os.environ["BASED_MONEY_SKIP_ENV_VALIDATION"] = "1"
os.environ["TRADING_MODE"] = "paper"

# Suppress config validation errors during import
import io

_original_stdout = sys.stdout
_original_stderr = sys.stderr
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

try:
    from uuid import uuid4
    from datetime import datetime, timezone

    from core.execution import ExecutionEngine, SecurityError, ExecutionError
    from core.risk import RiskEngine, RiskDecision
    from brokers.paper import PaperBroker
    from brokers.base import Order, Execution
    from models.portfolio import Portfolio, Position
    from models.thesis import Thesis
finally:
    sys.stdout = _original_stdout
    sys.stderr = _original_stderr


# ============================================================
# MOCK BROKER (for testing rejection cases)
# ============================================================


class MockBroker:
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
# TESTS
# ============================================================


def test_execution_engine_instantiation():
    """Test that ExecutionEngine can be instantiated"""
    print("\n" + "=" * 60)
    print("TEST: Execution Engine Instantiation")
    print("=" * 60)

    broker = MockBroker()
    portfolio = Portfolio(cash=1000.0, total_value=1000.0)

    engine = ExecutionEngine(broker_adapter=broker, portfolio=portfolio)

    assert engine.broker is broker
    assert engine.portfolio is portfolio
    assert engine.risk_engine is not None

    print("✅ PASS: ExecutionEngine instantiated")


def test_execute_with_rejected_risk_decision():
    """Test that executing a rejected trade raises SecurityError"""
    print("\n" + "=" * 60)
    print("TEST: Execute Rejected Trade")
    print("=" * 60)

    broker = MockBroker()
    portfolio = Portfolio(cash=1000.0, total_value=1000.0)
    engine = ExecutionEngine(broker_adapter=broker, portfolio=portfolio)

    # Create rejected risk decision
    risk_decision = RiskDecision(
        approved=False,
        reason="Conviction too low",
        risk_notes=["conviction=0.5 < min=0.7"],
    )

    # Create thesis
    thesis = Thesis(
        market_id="btc-100k",
        thesis_text="Test thesis",
        fair_value=0.65,
        current_odds=0.50,
        edge=0.15,
        conviction=0.50,
        proposed_action={"side": "YES", "size_pct": 0.10},
    )

    # Should raise SecurityError
    try:
        execution = engine.execute(risk_decision, thesis)
        print("❌ FAIL: Should have raised SecurityError")
        sys.exit(1)
    except SecurityError as e:
        print(f"  Got expected SecurityError: {e}")
        print("✅ PASS: SecurityError raised for rejected trade")


def test_execute_successful():
    """Test successful execution flow"""
    print("\n" + "=" * 60)
    print("TEST: Successful Execution")
    print("=" * 60)

    broker = MockBroker()
    portfolio = Portfolio(cash=1000.0, total_value=1000.0, deployed_pct=0.0)
    engine = ExecutionEngine(broker_adapter=broker, portfolio=portfolio)

    # Create approved risk decision
    risk_decision = RiskDecision(
        approved=True,
        reason="All checks passed",
        risk_notes=[],
        recommended_size=10.0,
    )

    # Create thesis
    thesis = Thesis(
        market_id="btc-100k",
        thesis_text="Bitcoin will reach $100k",
        fair_value=0.75,
        current_odds=0.50,
        edge=0.25,
        conviction=0.85,
        proposed_action={"side": "YES", "size_pct": 0.10},  # 10% of portfolio
    )

    # Execute
    initial_cash = portfolio.cash
    execution = engine.execute(risk_decision, thesis)

    # Verify execution
    assert execution.status == "FILLED"
    assert execution.market_id == "btc-100k"
    assert execution.side == "YES"

    print(f"  Execution: {execution.size:.2f} shares @ ${execution.price:.4f}")

    # Verify portfolio updated
    assert portfolio.cash < initial_cash, "Cash should decrease"
    print(f"  Cash: ${initial_cash:.2f} → ${portfolio.cash:.2f}")

    # Verify position added
    assert len(portfolio.positions) == 1
    position = portfolio.positions[0]
    assert position.market_id == "btc-100k"
    assert position.side == "YES"
    assert position.status == "open"
    print(f"  Position: {position.shares:.2f} shares @ ${position.entry_price:.4f}")

    # Verify deployed_pct updated
    assert portfolio.deployed_pct > 0.0
    print(f"  Deployed: {portfolio.deployed_pct:.2f}%")

    print("✅ PASS: Execution successful, portfolio updated")


def test_execute_with_broker_failure():
    """Test that broker rejection is handled"""
    print("\n" + "=" * 60)
    print("TEST: Broker Rejection")
    print("=" * 60)

    broker = MockBroker(should_fail=True)  # Force rejection
    portfolio = Portfolio(cash=1000.0, total_value=1000.0)
    engine = ExecutionEngine(broker_adapter=broker, portfolio=portfolio)

    # Create approved risk decision
    risk_decision = RiskDecision(
        approved=True,
        reason="All checks passed",
        risk_notes=[],
    )

    # Create thesis
    thesis = Thesis(
        market_id="btc-100k",
        thesis_text="Test",
        fair_value=0.75,
        current_odds=0.50,
        edge=0.25,
        conviction=0.85,
        proposed_action={"side": "YES", "size_pct": 0.10},
    )

    # Should raise ExecutionError
    try:
        execution = engine.execute(risk_decision, thesis)
        print("❌ FAIL: Should have raised ExecutionError")
        sys.exit(1)
    except ExecutionError as e:
        print(f"  Got expected ExecutionError: {e}")
        print("✅ PASS: ExecutionError raised for rejected order")


def test_double_check_risk():
    """Test that risk is re-evaluated before execution"""
    print("\n" + "=" * 60)
    print("TEST: Double-Check Risk Evaluation")
    print("=" * 60)

    broker = MockBroker()
    portfolio = Portfolio(cash=1000.0, total_value=1000.0, deployed_pct=0.0)
    engine = ExecutionEngine(broker_adapter=broker, portfolio=portfolio)

    # Create approved risk decision
    risk_decision = RiskDecision(
        approved=True,
        reason="All checks passed",
        risk_notes=[],
    )

    # Create thesis with low conviction (should fail double-check)
    thesis = Thesis(
        market_id="btc-100k",
        thesis_text="Test",
        fair_value=0.75,
        current_odds=0.50,
        edge=0.25,
        conviction=0.50,  # Below min_conviction threshold
        proposed_action={"side": "YES", "size_pct": 0.10},
    )

    # Should raise SecurityError during double-check
    try:
        execution = engine.execute(risk_decision, thesis)
        print("❌ FAIL: Should have raised SecurityError on double-check")
        sys.exit(1)
    except SecurityError as e:
        assert "no longer valid" in str(e).lower()
        print(f"  Got expected SecurityError: {e}")
        print("✅ PASS: Double-check caught invalid state")


def test_order_creation():
    """Test that order is created correctly from thesis"""
    print("\n" + "=" * 60)
    print("TEST: Order Creation")
    print("=" * 60)

    broker = MockBroker()
    portfolio = Portfolio(cash=1000.0, total_value=1000.0)
    engine = ExecutionEngine(broker_adapter=broker, portfolio=portfolio)

    # Create approved risk decision
    risk_decision = RiskDecision(
        approved=True,
        reason="All checks passed",
        risk_notes=[],
    )

    # Create thesis
    thesis = Thesis(
        market_id="btc-100k",
        thesis_text="Test",
        fair_value=0.75,
        current_odds=0.50,
        edge=0.25,
        conviction=0.85,
        proposed_action={"side": "NO", "size_pct": 0.15},  # 15% NO
    )

    # Execute
    execution = engine.execute(risk_decision, thesis)

    # Verify order was created correctly
    assert len(broker.executed_orders) == 1
    order = broker.executed_orders[0]

    assert order.market_id == "btc-100k"
    assert order.side == "NO"
    assert order.size == 1000.0 * 0.15  # 15% of $1000 = $150
    assert order.limit_price == 0.50  # thesis.current_odds
    assert "thesis" in order.client_order_id.lower()

    print(f"  Order: {order.side} {order.size} @ ${order.limit_price}")
    print("✅ PASS: Order created correctly from thesis")


def test_position_links_to_thesis():
    """Test that position is linked to thesis"""
    print("\n" + "=" * 60)
    print("TEST: Position Links to Thesis")
    print("=" * 60)

    broker = MockBroker()
    portfolio = Portfolio(cash=1000.0, total_value=1000.0)
    engine = ExecutionEngine(broker_adapter=broker, portfolio=portfolio)

    risk_decision = RiskDecision(approved=True, reason="OK", risk_notes=[])

    thesis = Thesis(
        market_id="btc-100k",
        thesis_text="Test",
        fair_value=0.75,
        current_odds=0.50,
        edge=0.25,
        conviction=0.85,
        proposed_action={"side": "YES", "size_pct": 0.10},
    )

    # Execute
    execution = engine.execute(risk_decision, thesis)

    # Verify position links to thesis
    position = portfolio.positions[0]
    assert position.thesis_id == thesis.id

    print(f"  Position thesis_id: {position.thesis_id}")
    print(f"  Thesis id: {thesis.id}")
    print("✅ PASS: Position linked to thesis")


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("EXECUTION ENGINE TEST SUITE")
    print("=" * 60)

    try:
        test_execution_engine_instantiation()
        test_execute_with_rejected_risk_decision()
        test_execute_successful()
        test_execute_with_broker_failure()
        test_double_check_risk()
        test_order_creation()
        test_position_links_to_thesis()

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print()

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
