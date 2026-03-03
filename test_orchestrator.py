"""
Test core/orchestrator.py - Trading Orchestrator
"""

import sys
import os

# Set minimal env for tests
os.environ["BASED_MONEY_SKIP_ENV_VALIDATION"] = "1"
os.environ["TRADING_MODE"] = "paper"

from uuid import uuid4
from datetime import datetime, timezone

from core.orchestrator import Orchestrator
from core.risk import RiskEngine
from core.execution import ExecutionEngine
from core.positions import PositionMonitor
from brokers.base import Order, Execution
from models.portfolio import Portfolio, Position
from models.thesis import Thesis


# ============================================================
# IN-MEMORY THESIS STORE (for testing without DB)
# ============================================================

class InMemoryThesisStore:
    """In-memory thesis store for testing"""
    
    def __init__(self):
        self.theses = []
    
    def save(self, thesis: Thesis) -> bool:
        """Save thesis to memory"""
        self.theses.append(thesis)
        return True
    
    def get_actionable(self, min_conviction: float = 0.70):
        """Get actionable theses from memory"""
        return [
            t for t in self.theses
            if t.conviction >= min_conviction and t.status == "active"
        ]
    
    def get_by_market(self, market_id: str):
        """Get theses for a market"""
        return [t for t in self.theses if t.market_id == market_id and t.status == "active"]


# ============================================================
# MOCK COMPONENTS
# ============================================================

class MockAgent:
    """Mock agent that generates test theses"""
    
    def __init__(self, name: str, generate_theses: bool = True):
        self.name = name
        self.generate_theses = generate_theses
        self.call_count = 0
    
    def update_theses(self):
        """Generate mock theses"""
        self.call_count += 1
        
        if not self.generate_theses:
            return []
        
        # Generate one thesis
        thesis = Thesis(
            id=uuid4(),
            agent_id=self.name,
            market_id=f"market-{self.name}-{self.call_count}",
            thesis_text=f"Test thesis from {self.name}",
            fair_value=0.75,
            current_odds=0.50,
            edge=0.25,
            conviction=0.85,
            proposed_action={"side": "YES", "size_pct": 0.05},
        )
        
        return [thesis]


class MockBroker:
    """Mock broker for testing"""
    
    def __init__(self):
        self.executed_orders = []
    
    def execute_order(self, order: Order) -> Execution:
        self.executed_orders.append(order)
        
        fill_price = order.limit_price * 1.01 if order.side == "YES" else order.limit_price * 0.99
        shares = order.size / fill_price
        
        return Execution(
            order_id=str(uuid4()),
            market_id=order.market_id,
            side=order.side,
            size=shares,
            price=fill_price,
            timestamp=datetime.now(timezone.utc),
            status="FILLED",
        )
    
    def get_position(self, market_id: str):
        return None
    
    def cancel_order(self, order_id: str) -> bool:
        return True


# ============================================================
# TESTS
# ============================================================

def test_orchestrator_instantiation():
    """Test that Orchestrator can be instantiated"""
    print("\n" + "=" * 60)
    print("TEST: Orchestrator Instantiation")
    print("=" * 60)
    
    # Setup components
    agents = [MockAgent("agent1")]
    risk_engine = RiskEngine()
    broker = MockBroker()
    portfolio = Portfolio(cash=1000.0, total_value=1000.0)
    execution_engine = ExecutionEngine(broker, portfolio)
    position_monitor = PositionMonitor(broker)
    thesis_store = InMemoryThesisStore()
    
    # Create orchestrator
    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        thesis_store=thesis_store,
    )
    
    assert orchestrator.agents == agents
    assert orchestrator.risk_engine is risk_engine
    assert orchestrator.execution_engine is execution_engine
    assert orchestrator.position_monitor is position_monitor
    assert orchestrator.thesis_store is thesis_store
    assert orchestrator.cycle_count == 0
    
    print("✅ PASS: Orchestrator instantiated")


def test_run_cycle_basic():
    """Test basic cycle execution"""
    print("\n" + "=" * 60)
    print("TEST: Run Cycle (Basic)")
    print("=" * 60)
    
    # Setup
    agents = [MockAgent("agent1")]
    risk_engine = RiskEngine()
    broker = MockBroker()
    portfolio = Portfolio(cash=1000.0, total_value=1000.0, deployed_pct=0.0)
    execution_engine = ExecutionEngine(broker, portfolio)
    position_monitor = PositionMonitor(broker)
    thesis_store = InMemoryThesisStore()
    
    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        thesis_store=thesis_store,
    )
    
    # Run one cycle
    stats = orchestrator.run_cycle()
    
    # Verify stats
    assert stats["cycle"] == 1
    assert orchestrator.cycle_count == 1
    assert stats["theses_generated"] >= 1, "Should generate at least 1 thesis"
    
    print(f"  Cycle: {stats['cycle']}")
    print(f"  Theses generated: {stats['theses_generated']}")
    print(f"  Actionable theses: {stats['theses_actionable']}")
    print(f"  Trades executed: {stats['trades_executed']}")
    
    print("✅ PASS: Basic cycle executed")


def test_run_cycle_with_execution():
    """Test cycle with thesis execution"""
    print("\n" + "=" * 60)
    print("TEST: Run Cycle (With Execution)")
    print("=" * 60)
    
    # Setup
    agents = [MockAgent("agent1", generate_theses=True)]
    risk_engine = RiskEngine()
    broker = MockBroker()
    portfolio = Portfolio(cash=1000.0, total_value=1000.0, deployed_pct=0.0)
    execution_engine = ExecutionEngine(broker, portfolio)
    position_monitor = PositionMonitor(broker)
    thesis_store = InMemoryThesisStore()
    
    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        thesis_store=thesis_store,
    )
    
    # Run one cycle
    stats = orchestrator.run_cycle()
    
    # Verify execution happened
    assert stats["theses_generated"] >= 1, "Should generate thesis"
    assert stats["theses_actionable"] >= 1, "Should have actionable thesis (conviction=0.85)"
    assert stats["trades_executed"] >= 1, "Should execute approved trade"
    
    # Verify broker executed order
    assert len(broker.executed_orders) >= 1, "Broker should have executed order"
    
    # Verify portfolio updated
    assert portfolio.cash < 1000.0, "Cash should decrease after trade"
    assert len(portfolio.positions) >= 1, "Position should be created"
    
    print(f"  Theses generated: {stats['theses_generated']}")
    print(f"  Actionable theses: {stats['theses_actionable']}")
    print(f"  Trades executed: {stats['trades_executed']}")
    print(f"  Portfolio cash: ${portfolio.cash:.2f}")
    print(f"  Positions: {len(portfolio.positions)}")
    
    print("✅ PASS: Cycle with execution successful")


def test_run_cycle_no_actionable():
    """Test cycle when no actionable theses"""
    print("\n" + "=" * 60)
    print("TEST: Run Cycle (No Actionable)")
    print("=" * 60)
    
    # Setup with agent that doesn't generate theses
    agents = [MockAgent("agent1", generate_theses=False)]
    risk_engine = RiskEngine()
    broker = MockBroker()
    portfolio = Portfolio(cash=1000.0, total_value=1000.0)
    execution_engine = ExecutionEngine(broker, portfolio)
    position_monitor = PositionMonitor(broker)
    thesis_store = InMemoryThesisStore()
    
    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        thesis_store=thesis_store,
    )
    
    # Run one cycle
    stats = orchestrator.run_cycle()
    
    # Verify no execution
    assert stats["theses_generated"] == 0, "Should not generate theses"
    assert stats["theses_actionable"] == 0, "Should have no actionable theses"
    assert stats["trades_executed"] == 0, "Should not execute trades"
    
    print(f"  Theses generated: {stats['theses_generated']}")
    print(f"  Trades executed: {stats['trades_executed']}")
    
    print("✅ PASS: Cycle with no actionable theses handled correctly")


def test_run_cycle_multiple_agents():
    """Test cycle with multiple agents"""
    print("\n" + "=" * 60)
    print("TEST: Run Cycle (Multiple Agents)")
    print("=" * 60)
    
    # Setup with 3 agents
    agents = [
        MockAgent("geo-agent"),
        MockAgent("signals-agent"),
        MockAgent("copy-agent"),
    ]
    risk_engine = RiskEngine()
    broker = MockBroker()
    portfolio = Portfolio(cash=1000.0, total_value=1000.0, deployed_pct=0.0)
    execution_engine = ExecutionEngine(broker, portfolio)
    position_monitor = PositionMonitor(broker)
    thesis_store = InMemoryThesisStore()
    
    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        thesis_store=thesis_store,
    )
    
    # Run one cycle
    stats = orchestrator.run_cycle()
    
    # Verify all agents called
    for agent in agents:
        assert agent.call_count == 1, f"{agent.name} should be called once"
    
    # Should generate 3 theses (one per agent)
    assert stats["theses_generated"] >= 3, f"Should generate 3+ theses, got {stats['theses_generated']}"
    
    print(f"  Agents: {len(agents)}")
    print(f"  Theses generated: {stats['theses_generated']}")
    print(f"  Trades executed: {stats['trades_executed']}")
    
    print("✅ PASS: Multiple agents handled correctly")


def test_run_cycle_counter():
    """Test cycle counter increments"""
    print("\n" + "=" * 60)
    print("TEST: Cycle Counter")
    print("=" * 60)
    
    # Setup
    agents = []
    risk_engine = RiskEngine()
    broker = MockBroker()
    portfolio = Portfolio(cash=1000.0, total_value=1000.0)
    execution_engine = ExecutionEngine(broker, portfolio)
    position_monitor = PositionMonitor(broker)
    thesis_store = InMemoryThesisStore()
    
    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        thesis_store=thesis_store,
    )
    
    # Run 5 cycles
    for i in range(1, 6):
        stats = orchestrator.run_cycle()
        assert stats["cycle"] == i, f"Cycle should be {i}"
        assert orchestrator.cycle_count == i, f"Counter should be {i}"
    
    print(f"  Completed {orchestrator.cycle_count} cycles")
    print("✅ PASS: Cycle counter increments correctly")


def test_error_handling():
    """Test that errors don't crash the cycle"""
    print("\n" + "=" * 60)
    print("TEST: Error Handling")
    print("=" * 60)
    
    # Create agent that raises error
    class ErrorAgent:
        def update_theses(self):
            raise RuntimeError("Simulated agent error")
    
    # Setup
    agents = [ErrorAgent()]
    risk_engine = RiskEngine()
    broker = MockBroker()
    portfolio = Portfolio(cash=1000.0, total_value=1000.0)
    execution_engine = ExecutionEngine(broker, portfolio)
    position_monitor = PositionMonitor(broker)
    thesis_store = InMemoryThesisStore()
    
    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        thesis_store=thesis_store,
    )
    
    # Run cycle (should not crash)
    stats = orchestrator.run_cycle()
    
    # Verify error captured
    assert stats["cycle"] == 1, "Cycle should complete"
    assert len(stats["errors"]) > 0, "Should capture error"
    assert "ErrorAgent" in str(stats["errors"]) or "agent error" in str(stats["errors"]).lower(), \
        "Error message should mention agent error"
    
    print(f"  Errors captured: {len(stats['errors'])}")
    print(f"  Cycle completed: {stats['cycle']}")
    
    print("✅ PASS: Error handling works correctly")


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ORCHESTRATOR TEST SUITE")
    print("=" * 60)
    
    try:
        test_orchestrator_instantiation()
        test_run_cycle_basic()
        test_run_cycle_with_execution()
        test_run_cycle_no_actionable()
        test_run_cycle_multiple_agents()
        test_run_cycle_counter()
        test_error_handling()
        
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
