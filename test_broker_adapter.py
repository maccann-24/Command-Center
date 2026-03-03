"""
Test brokers/base.py - Broker Adapter Interface
"""

import sys
from datetime import datetime
from brokers.base import BrokerAdapter, Order, Execution
from models.portfolio import Position


# ============================================================
# TESTS
# ============================================================

def test_abstract_class_cannot_instantiate():
    """Test that BrokerAdapter cannot be instantiated directly"""
    print("\n" + "=" * 60)
    print("TEST: Abstract class cannot be instantiated")
    print("=" * 60)
    
    try:
        broker = BrokerAdapter()
        print("❌ FAIL: Should not be able to instantiate abstract class")
        sys.exit(1)
    except TypeError as e:
        print(f"✅ PASS: Got expected error: {e}")


def test_concrete_implementation():
    """Test that concrete implementation can be created"""
    print("\n" + "=" * 60)
    print("TEST: Concrete implementation works")
    print("=" * 60)
    
    class MockBroker(BrokerAdapter):
        """Mock broker for testing"""
        
        def execute_order(self, order: Order) -> Execution:
            return Execution(
                order_id="exec-123",
                market_id=order.market_id,
                side=order.side,
                size=order.size,
                price=0.65,
                timestamp=datetime.utcnow(),
                status="FILLED",
                broker_order_id="broker-456",
            )
        
        def get_position(self, market_id: str):
            return None
        
        def cancel_order(self, order_id: str) -> bool:
            return True
    
    # Should be able to instantiate
    broker = MockBroker()
    print("✅ PASS: Concrete implementation created")
    
    # Test execute_order
    order = Order(market_id="btc-100k", side="YES", size=100)
    execution = broker.execute_order(order)
    
    assert execution.order_id == "exec-123"
    assert execution.market_id == "btc-100k"
    assert execution.side == "YES"
    assert execution.size == 100
    assert execution.status == "FILLED"
    print("✅ PASS: execute_order works")
    
    # Test get_position
    position = broker.get_position("btc-100k")
    assert position is None
    print("✅ PASS: get_position works")
    
    # Test cancel_order
    success = broker.cancel_order("order-123")
    assert success is True
    print("✅ PASS: cancel_order works")


def test_incomplete_implementation_fails():
    """Test that incomplete implementation fails"""
    print("\n" + "=" * 60)
    print("TEST: Incomplete implementation fails")
    print("=" * 60)
    
    try:
        class IncompleteBroker(BrokerAdapter):
            """Missing methods"""
            def execute_order(self, order: Order) -> Execution:
                pass
            # Missing get_position and cancel_order
        
        broker = IncompleteBroker()
        print("❌ FAIL: Should not be able to instantiate incomplete implementation")
        sys.exit(1)
    except TypeError as e:
        print(f"✅ PASS: Got expected error: {e}")


def test_order_dataclass():
    """Test Order dataclass"""
    print("\n" + "=" * 60)
    print("TEST: Order dataclass")
    print("=" * 60)
    
    # Market order
    order = Order(market_id="btc-100k", side="YES", size=100)
    assert order.market_id == "btc-100k"
    assert order.side == "YES"
    assert order.size == 100
    assert order.order_type == "MARKET"
    assert order.limit_price is None
    print("✅ PASS: Market order created")
    
    # Limit order
    limit_order = Order(
        market_id="btc-100k",
        side="YES",
        size=100,
        order_type="LIMIT",
        limit_price=0.65,
        client_order_id="client-123",
    )
    assert limit_order.order_type == "LIMIT"
    assert limit_order.limit_price == 0.65
    assert limit_order.client_order_id == "client-123"
    print("✅ PASS: Limit order created")


def test_execution_dataclass():
    """Test Execution dataclass"""
    print("\n" + "=" * 60)
    print("TEST: Execution dataclass")
    print("=" * 60)
    
    execution = Execution(
        order_id="exec-123",
        market_id="btc-100k",
        side="YES",
        size=100,
        price=0.65,
        timestamp=datetime.utcnow(),
        status="FILLED",
        broker_order_id="broker-456",
        fees=0.50,
        message="Order filled successfully",
    )
    
    assert execution.order_id == "exec-123"
    assert execution.market_id == "btc-100k"
    assert execution.status == "FILLED"
    assert execution.fees == 0.50
    assert execution.message == "Order filled successfully"
    print("✅ PASS: Execution dataclass created")


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BROKER ADAPTER TEST SUITE")
    print("=" * 60)
    
    try:
        test_abstract_class_cannot_instantiate()
        test_concrete_implementation()
        test_incomplete_implementation_fails()
        test_order_dataclass()
        test_execution_dataclass()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print()
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
