"""
Test brokers/paper.py - Paper Broker Implementation
"""

import sys
import os
from datetime import datetime, timezone
from brokers.paper import PaperBroker
from brokers.base import Order, Execution

# ============================================================
# TESTS
# ============================================================


def test_paper_broker_instantiation():
    """Test that PaperBroker can be instantiated"""
    print("\n" + "=" * 60)
    print("TEST: Paper Broker Instantiation")
    print("=" * 60)

    broker = PaperBroker()
    assert broker is not None
    print("✅ PASS: PaperBroker instantiated")


def test_execute_order_yes_side():
    """Test order execution with YES side (1% positive slippage)"""
    print("\n" + "=" * 60)
    print("TEST: Execute Order - YES Side")
    print("=" * 60)

    broker = PaperBroker()

    # Create order
    order = Order(
        market_id="btc-100k",
        side="YES",
        size=100.0,  # $100 USD
        order_type="MARKET",
        limit_price=0.50,  # Reference price
        client_order_id="test-order-1",
    )

    # Execute
    execution = broker.execute_order(order)

    # Verify execution
    assert execution.status == "FILLED"
    assert execution.market_id == "btc-100k"
    assert execution.side == "YES"

    # Verify 1% slippage: fill_price = 0.50 * 1.01 = 0.505
    expected_fill_price = 0.50 * 1.01
    assert abs(execution.price - expected_fill_price) < 0.0001
    print(f"  Fill price: {execution.price} (expected {expected_fill_price})")

    # Verify shares calculation: 100 / 0.505 ≈ 198.02
    expected_shares = 100.0 / expected_fill_price
    assert abs(execution.size - expected_shares) < 0.01
    print(f"  Shares: {execution.size:.2f} (expected {expected_shares:.2f})")

    # Verify other fields
    assert execution.fees == 0.0
    assert execution.broker_order_id == "test-order-1"
    assert "slippage" in execution.message.lower()

    print("✅ PASS: YES order executed with correct slippage")


def test_execute_order_no_side():
    """Test order execution with NO side (1% negative slippage)"""
    print("\n" + "=" * 60)
    print("TEST: Execute Order - NO Side")
    print("=" * 60)

    broker = PaperBroker()

    # Create order
    order = Order(
        market_id="btc-100k",
        side="NO",
        size=100.0,  # $100 USD
        limit_price=0.50,  # Reference price
    )

    # Execute
    execution = broker.execute_order(order)

    # Verify 1% slippage: fill_price = 0.50 * 0.99 = 0.495
    expected_fill_price = 0.50 * 0.99
    assert abs(execution.price - expected_fill_price) < 0.0001
    print(f"  Fill price: {execution.price} (expected {expected_fill_price})")

    # Verify shares calculation: 100 / 0.495 ≈ 202.02
    expected_shares = 100.0 / expected_fill_price
    assert abs(execution.size - expected_shares) < 0.01
    print(f"  Shares: {execution.size:.2f} (expected {expected_shares:.2f})")

    print("✅ PASS: NO order executed with correct slippage")


def test_execute_order_price_clamping():
    """Test that fill prices are clamped to [0.01, 0.99]"""
    print("\n" + "=" * 60)
    print("TEST: Price Clamping")
    print("=" * 60)

    broker = PaperBroker()

    # Test upper bound: 0.99 * 1.01 = 0.9999 → should clamp to 0.99
    order_high = Order(
        market_id="test-high",
        side="YES",
        size=100.0,
        limit_price=0.99,
    )
    execution_high = broker.execute_order(order_high)
    assert execution_high.price <= 0.99
    print(f"  High price clamped: {execution_high.price} <= 0.99")

    # Test lower bound: 0.01 * 0.99 = 0.0099 → should clamp to 0.01
    order_low = Order(
        market_id="test-low",
        side="NO",
        size=100.0,
        limit_price=0.01,
    )
    execution_low = broker.execute_order(order_low)
    assert execution_low.price >= 0.01
    print(f"  Low price clamped: {execution_low.price} >= 0.01")

    print("✅ PASS: Prices clamped correctly")


def test_execute_order_without_limit_price():
    """Test that order without limit_price raises error"""
    print("\n" + "=" * 60)
    print("TEST: Order Without Limit Price")
    print("=" * 60)

    broker = PaperBroker()

    # Create order without limit_price
    order = Order(
        market_id="btc-100k",
        side="YES",
        size=100.0,
    )

    try:
        execution = broker.execute_order(order)
        print("❌ FAIL: Should have raised ValueError")
        sys.exit(1)
    except ValueError as e:
        print(f"  Got expected error: {e}")
        print("✅ PASS: ValueError raised for missing limit_price")


def test_cancel_order_always_succeeds():
    """Test that cancel_order always returns True"""
    print("\n" + "=" * 60)
    print("TEST: Cancel Order (No-op)")
    print("=" * 60)

    broker = PaperBroker()

    # Cancel should always succeed (no-op)
    result = broker.cancel_order("any-order-id")
    assert result is True
    print("✅ PASS: cancel_order returns True")


def test_get_position_without_db():
    """Test get_position when DB is unavailable"""
    print("\n" + "=" * 60)
    print("TEST: Get Position Without DB")
    print("=" * 60)

    broker = PaperBroker()

    # Should return None gracefully
    position = broker.get_position("btc-100k")
    assert position is None
    print("✅ PASS: get_position returns None when DB unavailable")


def test_execution_has_uuid():
    """Test that execution order_id is a valid UUID"""
    print("\n" + "=" * 60)
    print("TEST: Execution UUID")
    print("=" * 60)

    broker = PaperBroker()

    order = Order(
        market_id="btc-100k",
        side="YES",
        size=100.0,
        limit_price=0.50,
    )

    execution = broker.execute_order(order)

    # Verify order_id is a valid UUID string
    import uuid

    try:
        uuid.UUID(execution.order_id)
        print(f"  Order ID: {execution.order_id}")
        print("✅ PASS: order_id is valid UUID")
    except ValueError:
        print(f"❌ FAIL: order_id '{execution.order_id}' is not a valid UUID")
        sys.exit(1)


def test_execution_timestamp():
    """Test that execution has recent timestamp"""
    print("\n" + "=" * 60)
    print("TEST: Execution Timestamp")
    print("=" * 60)

    broker = PaperBroker()

    before = datetime.now(timezone.utc)

    order = Order(
        market_id="btc-100k",
        side="YES",
        size=100.0,
        limit_price=0.50,
    )

    execution = broker.execute_order(order)

    after = datetime.now(timezone.utc)

    # Verify timestamp is between before and after
    assert before <= execution.timestamp <= after
    print(f"  Timestamp: {execution.timestamp}")
    print("✅ PASS: timestamp is recent")


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PAPER BROKER TEST SUITE")
    print("=" * 60)

    try:
        test_paper_broker_instantiation()
        test_execute_order_yes_side()
        test_execute_order_no_side()
        test_execute_order_price_clamping()
        test_execute_order_without_limit_price()
        test_cancel_order_always_succeeds()
        test_get_position_without_db()
        test_execution_has_uuid()
        test_execution_timestamp()

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print()

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
