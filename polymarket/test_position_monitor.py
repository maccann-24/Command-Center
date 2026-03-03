"""
Test core/positions.py - Position Monitor
"""

import sys
import os

# Set minimal env for tests
os.environ["BASED_MONEY_SKIP_ENV_VALIDATION"] = "1"
os.environ["TRADING_MODE"] = "paper"

from uuid import uuid4
from datetime import datetime, timezone

from core.positions import PositionMonitor
from brokers.base import Order
from models.portfolio import Position

# ============================================================
# MOCK BROKER
# ============================================================


class MockBroker:
    """Mock broker that returns preset position data"""

    def __init__(self):
        self.positions = {}  # market_id -> Position

    def set_position(self, market_id: str, position: Position):
        """Set position data for a market"""
        self.positions[market_id] = position

    def get_position(self, market_id: str):
        """Get position data for a market"""
        return self.positions.get(market_id)

    def execute_order(self, order: Order):
        pass

    def cancel_order(self, order_id: str) -> bool:
        return True


# ============================================================
# TESTS
# ============================================================


def test_position_monitor_instantiation():
    """Test that PositionMonitor can be instantiated"""
    print("\n" + "=" * 60)
    print("TEST: Position Monitor Instantiation")
    print("=" * 60)

    broker = MockBroker()
    monitor = PositionMonitor(broker_adapter=broker)

    assert monitor.broker is broker
    print("✅ PASS: PositionMonitor instantiated")


def test_update_positions_no_positions():
    """Test update_positions when no positions exist"""
    print("\n" + "=" * 60)
    print("TEST: Update Positions (No Positions)")
    print("=" * 60)

    broker = MockBroker()
    monitor = PositionMonitor(broker_adapter=broker)

    # Will return empty list when DB has no positions
    positions = monitor.update_positions()

    assert positions == []
    print("✅ PASS: Empty list returned when no positions")


def test_check_stop_losses_no_trigger():
    """Test check_stop_losses when no positions hit stop-loss"""
    print("\n" + "=" * 60)
    print("TEST: Check Stop-Losses (No Trigger)")
    print("=" * 60)

    broker = MockBroker()
    monitor = PositionMonitor(broker_adapter=broker)

    # Create position with small loss (5%)
    position = Position(
        id=uuid4(),
        market_id="btc-100k",
        side="YES",
        shares=100.0,
        entry_price=0.50,
        current_price=0.475,  # 5% loss
        pnl=-2.50,
        status="open",
    )

    # Check with 15% threshold (should not trigger)
    exit_orders = monitor.check_stop_losses([position], stop_loss_pct=15.0)

    assert len(exit_orders) == 0, "Should not trigger stop-loss for 5% loss"
    print(f"  Position loss: -5.0% (threshold: 15.0%)")
    print("✅ PASS: No stop-loss triggered for small loss")


def test_check_stop_losses_trigger():
    """Test check_stop_losses when position hits stop-loss"""
    print("\n" + "=" * 60)
    print("TEST: Check Stop-Losses (Trigger)")
    print("=" * 60)

    broker = MockBroker()
    monitor = PositionMonitor(broker_adapter=broker)

    # Create position with large loss (20%)
    position = Position(
        id=uuid4(),
        market_id="btc-100k",
        side="YES",
        shares=100.0,
        entry_price=0.50,
        current_price=0.40,  # 20% loss
        pnl=-10.0,
        status="open",
    )

    # Check with 15% threshold (should trigger)
    exit_orders = monitor.check_stop_losses([position], stop_loss_pct=15.0)

    assert len(exit_orders) == 1, "Should generate 1 exit order"

    order = exit_orders[0]
    assert order.market_id == "btc-100k"
    assert order.side == "NO", "Exit side should be opposite (YES → NO)"
    assert order.size == 100.0, "Should exit entire position"
    assert order.order_type == "MARKET"
    assert order.limit_price == 0.40, "Should use current price"
    assert "stop-loss" in order.client_order_id.lower()

    print(f"  Position loss: -20.0% (threshold: 15.0%)")
    print(f"  Exit order: {order.side} {order.size} shares @ ${order.limit_price}")
    print("✅ PASS: Stop-loss triggered and exit order generated")


def test_check_stop_losses_opposite_side():
    """Test that exit order uses opposite side"""
    print("\n" + "=" * 60)
    print("TEST: Check Stop-Losses (Opposite Side)")
    print("=" * 60)

    broker = MockBroker()
    monitor = PositionMonitor(broker_adapter=broker)

    # Test YES → NO
    position_yes = Position(
        id=uuid4(),
        market_id="market-1",
        side="YES",
        shares=100.0,
        entry_price=0.50,
        current_price=0.30,  # 40% loss
        pnl=-20.0,
        status="open",
    )

    exit_orders = monitor.check_stop_losses([position_yes], stop_loss_pct=15.0)
    assert exit_orders[0].side == "NO", "YES position should exit with NO"
    print("  ✓ YES → NO")

    # Test NO → YES
    position_no = Position(
        id=uuid4(),
        market_id="market-2",
        side="NO",
        shares=100.0,
        entry_price=0.50,
        current_price=0.30,  # 40% loss
        pnl=-20.0,
        status="open",
    )

    exit_orders = monitor.check_stop_losses([position_no], stop_loss_pct=15.0)
    assert exit_orders[0].side == "YES", "NO position should exit with YES"
    print("  ✓ NO → YES")

    print("✅ PASS: Exit orders use opposite side")


def test_check_stop_losses_multiple_positions():
    """Test check_stop_losses with multiple positions"""
    print("\n" + "=" * 60)
    print("TEST: Check Stop-Losses (Multiple Positions)")
    print("=" * 60)

    broker = MockBroker()
    monitor = PositionMonitor(broker_adapter=broker)

    positions = [
        # Position 1: Small loss (5%) - should NOT trigger
        Position(
            id=uuid4(),
            market_id="market-1",
            side="YES",
            shares=100.0,
            entry_price=0.50,
            current_price=0.475,
            pnl=-2.50,
            status="open",
        ),
        # Position 2: Large loss (25%) - SHOULD trigger
        Position(
            id=uuid4(),
            market_id="market-2",
            side="YES",
            shares=200.0,
            entry_price=0.60,
            current_price=0.45,
            pnl=-30.0,
            status="open",
        ),
        # Position 3: Profit (10%) - should NOT trigger
        Position(
            id=uuid4(),
            market_id="market-3",
            side="NO",
            shares=150.0,
            entry_price=0.40,
            current_price=0.44,
            pnl=6.0,
            status="open",
        ),
        # Position 4: Exact threshold (15%) - should NOT trigger (< not <=)
        Position(
            id=uuid4(),
            market_id="market-4",
            side="YES",
            shares=100.0,
            entry_price=0.50,
            current_price=0.425,
            pnl=-7.50,
            status="open",
        ),
        # Position 5: Large loss (20%) - SHOULD trigger
        Position(
            id=uuid4(),
            market_id="market-5",
            side="NO",
            shares=100.0,
            entry_price=0.50,
            current_price=0.40,
            pnl=-10.0,
            status="open",
        ),
    ]

    exit_orders = monitor.check_stop_losses(positions, stop_loss_pct=15.0)

    # Should generate 2 exit orders (market-2 and market-5)
    assert (
        len(exit_orders) == 2
    ), f"Should generate 2 exit orders, got {len(exit_orders)}"

    # Verify correct markets triggered
    triggered_markets = {order.market_id for order in exit_orders}
    assert "market-2" in triggered_markets, "market-2 should trigger (25% loss)"
    assert "market-5" in triggered_markets, "market-5 should trigger (20% loss)"

    print(f"  Position 1: -5.0% → No trigger")
    print(f"  Position 2: -25.0% → TRIGGER")
    print(f"  Position 3: +10.0% → No trigger")
    print(f"  Position 4: -15.0% → No trigger (at threshold)")
    print(f"  Position 5: -20.0% → TRIGGER")
    print(f"  Total exit orders: {len(exit_orders)}")

    print("✅ PASS: Multiple positions handled correctly")


def test_check_stop_losses_custom_threshold():
    """Test check_stop_losses with custom threshold"""
    print("\n" + "=" * 60)
    print("TEST: Check Stop-Losses (Custom Threshold)")
    print("=" * 60)

    broker = MockBroker()
    monitor = PositionMonitor(broker_adapter=broker)

    # Position with 12% loss
    position = Position(
        id=uuid4(),
        market_id="btc-100k",
        side="YES",
        shares=100.0,
        entry_price=0.50,
        current_price=0.44,
        pnl=-6.0,
        status="open",
    )

    # Should NOT trigger with 15% threshold
    exit_orders_15 = monitor.check_stop_losses([position], stop_loss_pct=15.0)
    assert len(exit_orders_15) == 0, "Should not trigger with 15% threshold"
    print(f"  Loss: -12.0%, Threshold: 15.0% → No trigger")

    # SHOULD trigger with 10% threshold
    exit_orders_10 = monitor.check_stop_losses([position], stop_loss_pct=10.0)
    assert len(exit_orders_10) == 1, "Should trigger with 10% threshold"
    print(f"  Loss: -12.0%, Threshold: 10.0% → TRIGGER")

    print("✅ PASS: Custom threshold works correctly")


def test_position_pnl_calculation():
    """Test that P&L calculation matches Position.pnl_percentage()"""
    print("\n" + "=" * 60)
    print("TEST: P&L Calculation Consistency")
    print("=" * 60)

    broker = MockBroker()
    monitor = PositionMonitor(broker_adapter=broker)

    # Create position and manually set P&L
    position = Position(
        id=uuid4(),
        market_id="test-market",
        side="YES",
        shares=100.0,
        entry_price=0.50,
        current_price=0.40,
        pnl=0.0,  # Will be calculated
        status="open",
    )

    # Calculate P&L using position method
    position.update_pnl()
    expected_pnl = position.pnl
    expected_pnl_pct = position.pnl_percentage()

    # Calculate P&L using monitor logic
    position_cost = position.entry_price * position.shares
    actual_pnl = (position.current_price - position.entry_price) * position.shares
    actual_pnl_pct = (actual_pnl / position_cost) * 100.0

    # Verify consistency
    assert abs(expected_pnl - actual_pnl) < 0.01, "P&L calculation mismatch"
    assert abs(expected_pnl_pct - actual_pnl_pct) < 0.01, "P&L % calculation mismatch"

    print(f"  Entry: {position.shares} shares @ ${position.entry_price}")
    print(f"  Current: ${position.current_price}")
    print(f"  P&L: ${actual_pnl:.2f} ({actual_pnl_pct:.2f}%)")

    print("✅ PASS: P&L calculations consistent")


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("POSITION MONITOR TEST SUITE")
    print("=" * 60)

    try:
        test_position_monitor_instantiation()
        test_update_positions_no_positions()
        test_check_stop_losses_no_trigger()
        test_check_stop_losses_trigger()
        test_check_stop_losses_opposite_side()
        test_check_stop_losses_multiple_positions()
        test_check_stop_losses_custom_threshold()
        test_position_pnl_calculation()

        print("\n" + "=" * 60)
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
