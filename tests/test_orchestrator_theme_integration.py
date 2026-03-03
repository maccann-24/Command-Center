"""
BASED MONEY - Orchestrator Theme Integration Tests
Test theme-based portfolio management in the orchestrator
"""

import sys
import os

# Set up test environment
os.environ['TRADING_MODE'] = 'paper'
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_KEY'] = 'test_key'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator import Orchestrator
from core.theme_portfolio import ThemeManager
from core.risk import RiskEngine
from core.execution import ExecutionEngine
from core.positions import PositionMonitor
from brokers.paper import PaperBroker
from models.portfolio import Portfolio


class MockAgent:
    """Mock agent for testing."""
    def __init__(self, agent_id: str, theme: str):
        self.agent_id = agent_id
        self.theme = theme
        self.theses = []
    
    def update_theses(self):
        return self.theses


def test_orchestrator_initialization_with_themes():
    """Test that orchestrator initializes with ThemeManager."""
    print("\n" + "="*60)
    print("TEST: Orchestrator Theme Manager Initialization")
    print("="*60)
    
    # Create mock agents
    agents = [
        MockAgent('twosigma_geo', 'geopolitical'),
        MockAgent('goldman_geo', 'geopolitical'),
        MockAgent('renaissance_politics', 'us_politics'),
    ]
    
    # Create theme manager
    theme_manager = ThemeManager(total_capital=10000.0)
    
    # Register agents to themes
    theme_manager.add_agent_to_theme('geopolitical', 'twosigma_geo')
    theme_manager.add_agent_to_theme('geopolitical', 'goldman_geo')
    theme_manager.add_agent_to_theme('us_politics', 'renaissance_politics')
    
    # Create orchestrator
    portfolio = Portfolio(cash=10000.0)
    broker = PaperBroker()
    risk_engine = RiskEngine()
    execution_engine = ExecutionEngine(broker, portfolio)
    position_monitor = PositionMonitor(broker)
    
    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        theme_manager=theme_manager,
    )
    
    # Verify orchestrator has theme_manager
    assert orchestrator.theme_manager is not None
    assert orchestrator.theme_manager.total_capital == 10000.0
    assert len(orchestrator.theme_manager.themes) == 4
    
    # Verify agent map built correctly
    assert len(orchestrator.agent_map) == 3
    assert 'twosigma_geo' in orchestrator.agent_map
    assert orchestrator.agent_map['twosigma_geo']['theme'] == 'geopolitical'
    
    print("✅ PASSED: Orchestrator initialized with ThemeManager")
    print(f"   - Theme manager created with 4 themes")
    print(f"   - 3 agents registered")
    print(f"   - Agent map built correctly")
    

def test_weekly_reallocation_method():
    """Test that weekly_reallocation_check method exists and can be called."""
    print("\n" + "="*60)
    print("TEST: Weekly Reallocation Method")
    print("="*60)
    
    agents = [MockAgent('test_agent', 'geopolitical')]
    theme_manager = ThemeManager(total_capital=10000.0)
    
    portfolio = Portfolio(cash=10000.0)
    broker = PaperBroker()
    risk_engine = RiskEngine()
    execution_engine = ExecutionEngine(broker, portfolio)
    position_monitor = PositionMonitor(broker)
    
    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        theme_manager=theme_manager,
    )
    
    # Verify method exists
    assert hasattr(orchestrator, 'weekly_reallocation_check')
    assert callable(orchestrator.weekly_reallocation_check)
    
    # Call method (should not raise exception)
    try:
        orchestrator.weekly_reallocation_check()
        success = True
    except Exception as e:
        print(f"⚠️ Method call failed: {e}")
        success = False
    
    assert success, "weekly_reallocation_check should not raise exception"
    
    print("✅ PASSED: weekly_reallocation_check method works")


def test_monthly_theme_review_method():
    """Test that monthly_theme_review method exists and can be called."""
    print("\n" + "="*60)
    print("TEST: Monthly Theme Review Method")
    print("="*60)
    
    agents = [MockAgent('test_agent', 'geopolitical')]
    theme_manager = ThemeManager(total_capital=10000.0)
    
    portfolio = Portfolio(cash=10000.0)
    broker = PaperBroker()
    risk_engine = RiskEngine()
    execution_engine = ExecutionEngine(broker, portfolio)
    position_monitor = PositionMonitor(broker)
    
    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        theme_manager=theme_manager,
    )
    
    # Verify method exists
    assert hasattr(orchestrator, 'monthly_theme_review')
    assert callable(orchestrator.monthly_theme_review)
    
    # Call method (should not raise exception)
    try:
        orchestrator.monthly_theme_review()
        success = True
    except Exception as e:
        print(f"⚠️ Method call failed: {e}")
        success = False
    
    assert success, "monthly_theme_review should not raise exception"
    
    print("✅ PASSED: monthly_theme_review method works")


def test_generate_ic_memo_method():
    """Test that generate_ic_memo method exists."""
    print("\n" + "="*60)
    print("TEST: Generate IC Memo Method")
    print("="*60)
    
    agents = [MockAgent('test_agent', 'geopolitical')]
    theme_manager = ThemeManager(total_capital=10000.0)
    
    portfolio = Portfolio(cash=10000.0)
    broker = PaperBroker()
    risk_engine = RiskEngine()
    execution_engine = ExecutionEngine(broker, portfolio)
    position_monitor = PositionMonitor(broker)
    
    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        theme_manager=theme_manager,
    )
    
    # Verify method exists
    assert hasattr(orchestrator, 'generate_ic_memo')
    assert callable(orchestrator.generate_ic_memo)
    
    print("✅ PASSED: generate_ic_memo method exists")


def test_agent_metadata_tagging():
    """Test that agent metadata is correctly extracted and tagged."""
    print("\n" + "="*60)
    print("TEST: Agent Metadata Tagging")
    print("="*60)
    
    agents = [
        MockAgent('twosigma_geo', 'geopolitical'),
        MockAgent('renaissance_politics', 'us_politics'),
        MockAgent('citadel_crypto', 'crypto'),
    ]
    
    theme_manager = ThemeManager(total_capital=10000.0)
    
    portfolio = Portfolio(cash=10000.0)
    broker = PaperBroker()
    risk_engine = RiskEngine()
    execution_engine = ExecutionEngine(broker, portfolio)
    position_monitor = PositionMonitor(broker)
    
    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        theme_manager=theme_manager,
    )
    
    # Verify agent_map has correct metadata
    assert len(orchestrator.agent_map) == 3
    
    # Check each agent
    assert orchestrator.agent_map['twosigma_geo']['agent_id'] == 'twosigma_geo'
    assert orchestrator.agent_map['twosigma_geo']['theme'] == 'geopolitical'
    
    assert orchestrator.agent_map['renaissance_politics']['agent_id'] == 'renaissance_politics'
    assert orchestrator.agent_map['renaissance_politics']['theme'] == 'us_politics'
    
    assert orchestrator.agent_map['citadel_crypto']['agent_id'] == 'citadel_crypto'
    assert orchestrator.agent_map['citadel_crypto']['theme'] == 'crypto'
    
    print("✅ PASSED: Agent metadata correctly tagged")
    print(f"   - 3 agents with correct agent_id and theme")


def test_track_closed_position_method():
    """Test that track_closed_position method exists."""
    print("\n" + "="*60)
    print("TEST: Track Closed Position Method")
    print("="*60)
    
    agents = [MockAgent('test_agent', 'geopolitical')]
    theme_manager = ThemeManager(total_capital=10000.0)
    
    portfolio = Portfolio(cash=10000.0)
    broker = PaperBroker()
    risk_engine = RiskEngine()
    execution_engine = ExecutionEngine(broker, portfolio)
    position_monitor = PositionMonitor(broker)
    
    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
        theme_manager=theme_manager,
    )
    
    # Verify method exists
    assert hasattr(orchestrator, 'track_closed_position')
    assert callable(orchestrator.track_closed_position)
    
    print("✅ PASSED: track_closed_position method exists")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("ORCHESTRATOR THEME INTEGRATION TESTS")
    print("="*60)
    
    # Run all tests
    test_orchestrator_initialization_with_themes()
    test_weekly_reallocation_method()
    test_monthly_theme_review_method()
    test_generate_ic_memo_method()
    test_agent_metadata_tagging()
    test_track_closed_position_method()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✅")
    print("="*60)
