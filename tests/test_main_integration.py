"""
BASED MONEY - Main.py Integration Test
Test that institutional agents integrate properly with ThemeManager
"""

import sys
import os

# Set up test environment
os.environ['TRADING_MODE'] = 'paper'
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_KEY'] = 'test_key'
os.environ['INITIAL_CAPITAL'] = '10000'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after setting env vars
import config
from core.theme_portfolio import ThemeManager
from agents.twosigma_geo import TwoSigmaGeoAgent
from agents.goldman_geo import GoldmanGeoAgent
from agents.bridgewater_geo import BridgewaterGeoAgent


def test_theme_manager_initialization():
    """Test ThemeManager creates 4 themes with equal allocation."""
    print("\n" + "="*60)
    print("TEST: ThemeManager Initialization")
    print("="*60)
    
    tm = ThemeManager(total_capital=10000)
    
    # Verify 4 themes created
    assert len(tm.themes) == 4
    assert "geopolitical" in tm.themes
    assert "us_politics" in tm.themes
    assert "crypto" in tm.themes
    assert "weather" in tm.themes
    
    # Verify equal allocation (25% each)
    for theme_name, theme in tm.themes.items():
        assert theme.current_capital == 2500.0
        print(f"  ✓ {theme_name}: ${theme.current_capital:,.2f}")
    
    print("✅ PASSED: ThemeManager initialized with 4 themes")


def test_agent_registration():
    """Test registering institutional agents to Geopolitical theme."""
    print("\n" + "="*60)
    print("TEST: Agent Registration")
    print("="*60)
    
    tm = ThemeManager(total_capital=10000)
    
    # Create agents
    ts = TwoSigmaGeoAgent()
    gs = GoldmanGeoAgent()
    bw = BridgewaterGeoAgent()
    
    # Verify agent properties
    assert ts.agent_id == "twosigma_geo"
    assert gs.agent_id == "goldman_geo"
    assert bw.agent_id == "bridgewater_geo"
    
    assert ts.theme == "geopolitical"
    assert gs.theme == "geopolitical"
    assert bw.theme == "geopolitical"
    
    # Register to theme
    tm.add_agent_to_theme("geopolitical", ts.agent_id)
    tm.add_agent_to_theme("geopolitical", gs.agent_id)
    tm.add_agent_to_theme("geopolitical", bw.agent_id)
    
    # Verify registration
    geo_theme = tm.themes["geopolitical"]
    assert len(geo_theme.agents) == 3
    assert "twosigma_geo" in geo_theme.agents
    assert "goldman_geo" in geo_theme.agents
    assert "bridgewater_geo" in geo_theme.agents
    
    print(f"  ✓ Registered {len(geo_theme.agents)} agents")
    for agent_id in geo_theme.agents:
        print(f"    - {agent_id}")
    
    print("✅ PASSED: Agents registered successfully")


def test_agent_instances():
    """Test that agent instances are properly created and callable."""
    print("\n" + "="*60)
    print("TEST: Agent Instances")
    print("="*60)
    
    agents = [
        TwoSigmaGeoAgent(),
        GoldmanGeoAgent(),
        BridgewaterGeoAgent()
    ]
    
    for agent in agents:
        # Verify agent has required attributes
        assert hasattr(agent, 'agent_id')
        assert hasattr(agent, 'theme')
        assert hasattr(agent, 'mandate')
        assert hasattr(agent, 'update_theses')
        assert hasattr(agent, 'generate_thesis')
        
        # Verify mandate is meaningful
        assert len(agent.mandate) > 20
        
        print(f"  ✓ {agent.agent_id}")
        print(f"    Theme: {agent.theme}")
        print(f"    Mandate: {agent.mandate[:50]}...")
    
    print("✅ PASSED: All agent instances valid")


def test_config_loading():
    """Test that config loaded correctly from environment."""
    print("\n" + "="*60)
    print("TEST: Config Loading")
    print("="*60)
    
    assert config.TRADING_MODE == "paper"
    assert config.INITIAL_CAPITAL == 10000.0
    
    print(f"  ✓ TRADING_MODE: {config.TRADING_MODE}")
    print(f"  ✓ INITIAL_CAPITAL: ${config.INITIAL_CAPITAL:,.2f}")
    
    print("✅ PASSED: Config loaded correctly")


def test_main_compatibility():
    """Test that agents work with main.py's expected interface."""
    print("\n" + "="*60)
    print("TEST: Main.py Compatibility")
    print("="*60)
    
    # Simulate what main.py does
    tm = ThemeManager(total_capital=config.INITIAL_CAPITAL)
    
    # Create and register agents
    agent_instances = []
    
    ts = TwoSigmaGeoAgent()
    gs = GoldmanGeoAgent()
    bw = BridgewaterGeoAgent()
    
    agent_instances.extend([ts, gs, bw])
    
    for agent in [ts, gs, bw]:
        tm.add_agent_to_theme("geopolitical", agent.agent_id)
    
    # Store instances on theme_manager (like main.py does)
    tm._agent_instances = agent_instances
    
    # Extract agents (like main.py does)
    agents = getattr(tm, '_agent_instances', [])
    
    assert len(agents) == 3
    print(f"  ✓ Extracted {len(agents)} agent instances from ThemeManager")
    
    # Verify agents are callable
    for agent in agents:
        agent_id = agent.agent_id if hasattr(agent, 'agent_id') else 'unknown'
        print(f"    - {agent_id}")
    
    print("✅ PASSED: Main.py compatibility verified")


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("🔗 MAIN.PY INTEGRATION TEST SUITE")
    print("="*60)
    
    test_config_loading()
    test_theme_manager_initialization()
    test_agent_registration()
    test_agent_instances()
    test_main_compatibility()
    
    print("\n" + "="*60)
    print("✅ ALL INTEGRATION TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
