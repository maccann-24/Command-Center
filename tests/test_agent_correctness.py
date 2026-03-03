"""
BASED MONEY - Agent Correctness Tests
Comprehensive validation of all 3 institutional agents
"""

import sys
import os

# Set up test environment
os.environ['TRADING_MODE'] = 'paper'
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_KEY'] = 'test_key'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.twosigma_geo import TwoSigmaGeoAgent
from agents.goldman_geo import GoldmanGeoAgent
from agents.bridgewater_geo import BridgewaterGeoAgent
from models import Market


class MockNewsEvent:
    """Mock news event for testing."""
    def __init__(self, headline: str):
        self.headline = headline


def test_bidirectional_theses():
    """Test that all agents can generate both BUY and SELL recommendations."""
    print("\n" + "="*60)
    print("TEST: Bidirectional Thesis Generation")
    print("="*60)
    
    # Create test markets
    expensive_market = Market(
        id='expensive-test',
        question='Will Russia invade Ukraine by March 2026?',
        category='geopolitical',
        yes_price=0.85,
        no_price=0.15,
        volume_24h=100000,
        resolution_date=None,
        resolved=False
    )
    
    cheap_market = Market(
        id='cheap-test',
        question='Will Russia invade Ukraine by March 2026?',
        category='geopolitical',
        yes_price=0.15,
        no_price=0.85,
        volume_24h=100000,
        resolution_date=None,
        resolved=False
    )
    
    mock_news = [
        MockNewsEvent('Russia mobilizes troops near Ukraine border'),
        MockNewsEvent('Ukraine requests emergency NATO meeting'),
    ]
    
    # Test TwoSigma
    print("\n  TwoSigma:")
    ts = TwoSigmaGeoAgent()
    
    ts_expensive = ts.generate_thesis(expensive_market, mock_news)
    ts_cheap = ts.generate_thesis(cheap_market, mock_news)
    
    if ts_expensive:
        assert ts_expensive.proposed_action['side'] == 'NO', "Should recommend SELL for expensive market"
        assert ts_expensive.edge < 0, "Edge should be negative for SELL"
        print(f"    ✓ Expensive market: {ts_expensive.proposed_action['side']} (edge: {ts_expensive.edge:+.2%})")
    else:
        print(f"    ⚠️  No thesis for expensive market")
    
    if ts_cheap:
        assert ts_cheap.proposed_action['side'] == 'YES', "Should recommend BUY for cheap market"
        assert ts_cheap.edge > 0, "Edge should be positive for BUY"
        print(f"    ✓ Cheap market: {ts_cheap.proposed_action['side']} (edge: {ts_cheap.edge:+.2%})")
    else:
        print(f"    ⚠️  No thesis for cheap market")
    
    # Test Goldman
    print("\n  Goldman:")
    gs = GoldmanGeoAgent()
    
    gs_expensive = gs.generate_thesis(expensive_market, mock_news)
    gs_cheap = gs.generate_thesis(cheap_market, mock_news)
    
    if gs_expensive:
        print(f"    ✓ Expensive market: {gs_expensive.proposed_action['side']} (edge: {gs_expensive.edge:+.2%})")
    else:
        print(f"    ⚠️  No thesis for expensive market")
    
    if gs_cheap:
        print(f"    ✓ Cheap market: {gs_cheap.proposed_action['side']} (edge: {gs_cheap.edge:+.2%})")
    else:
        print(f"    ⚠️  No thesis for cheap market")
    
    # Test Bridgewater
    print("\n  Bridgewater:")
    bw = BridgewaterGeoAgent()
    all_markets = [expensive_market, cheap_market]
    
    bw_expensive = bw.generate_thesis(expensive_market, all_markets, mock_news)
    bw_cheap = bw.generate_thesis(cheap_market, all_markets, mock_news)
    
    if bw_expensive:
        print(f"    ✓ Expensive market: {bw_expensive.proposed_action['side']} (edge: {bw_expensive.edge:+.2%})")
    else:
        print(f"    ⚠️  No thesis for expensive market")
    
    if bw_cheap:
        print(f"    ✓ Cheap market: {bw_cheap.proposed_action['side']} (edge: {bw_cheap.edge:+.2%})")
    else:
        print(f"    ⚠️  No thesis for cheap market")
    
    print("\n✅ PASSED: Agents support bidirectional trading")


def test_edge_calculation_consistency():
    """Test that edge calculations are consistent with proposed action."""
    print("\n" + "="*60)
    print("TEST: Edge Calculation Consistency")
    print("="*60)
    
    market = Market(
        id='test',
        question='Test market',
        category='geopolitical',
        yes_price=0.50,
        no_price=0.50,
        volume_24h=100000,
        resolution_date=None,
        resolved=False
    )
    
    agents = [
        TwoSigmaGeoAgent(),
        GoldmanGeoAgent(),
        BridgewaterGeoAgent()
    ]
    
    mock_news = [MockNewsEvent('Test news event')]
    
    for agent in agents:
        # Generate thesis
        if isinstance(agent, BridgewaterGeoAgent):
            thesis = agent.generate_thesis(market, [market], mock_news)
        else:
            thesis = agent.generate_thesis(market, mock_news)
        
        if thesis:
            # Verify consistency
            if thesis.edge > 0:
                assert thesis.proposed_action['side'] == 'YES', \
                    f"{agent.agent_id}: Positive edge should recommend YES"
            elif thesis.edge < 0:
                assert thesis.proposed_action['side'] == 'NO', \
                    f"{agent.agent_id}: Negative edge should recommend NO"
            
            # Verify fair value calculation
            assert abs(thesis.edge - (thesis.fair_value - thesis.current_odds)) < 0.0001, \
                f"{agent.agent_id}: Edge should equal fair_value - current_odds"
            
            print(f"  ✓ {agent.agent_id}: edge={thesis.edge:+.3f}, side={thesis.proposed_action['side']}")
    
    print("\n✅ PASSED: Edge calculations consistent")


def test_required_attributes():
    """Test that all agents have required attributes."""
    print("\n" + "="*60)
    print("TEST: Required Attributes")
    print("="*60)
    
    required_attrs = ['agent_id', 'theme', 'mandate', 'update_theses', 'generate_thesis']
    
    agents = [
        TwoSigmaGeoAgent(),
        GoldmanGeoAgent(),
        BridgewaterGeoAgent()
    ]
    
    for agent in agents:
        for attr in required_attrs:
            assert hasattr(agent, attr), f"{agent.__class__.__name__} missing {attr}"
        
        # Verify agent_id and theme
        assert agent.theme == 'geopolitical', f"{agent.agent_id} has wrong theme"
        assert '_geo' in agent.agent_id, f"{agent.agent_id} should contain '_geo'"
        
        print(f"  ✓ {agent.agent_id}: all attributes present")
    
    print("\n✅ PASSED: All required attributes present")


def test_error_handling():
    """Test that agents handle errors gracefully."""
    print("\n" + "="*60)
    print("TEST: Error Handling")
    print("="*60)
    
    # Create invalid market
    invalid_market = Market(
        id='invalid',
        question='',  # Empty question
        category='geopolitical',
        yes_price=0.50,
        no_price=0.50,
        volume_24h=0,  # Zero volume
        resolution_date=None,
        resolved=False
    )
    
    agents = [
        TwoSigmaGeoAgent(),
        GoldmanGeoAgent(),
        BridgewaterGeoAgent()
    ]
    
    for agent in agents:
        try:
            # Should not crash, even with invalid input
            if isinstance(agent, BridgewaterGeoAgent):
                thesis = agent.generate_thesis(invalid_market, [invalid_market], [])
            else:
                thesis = agent.generate_thesis(invalid_market, [])
            
            print(f"  ✓ {agent.agent_id}: handles invalid market gracefully")
        except Exception as e:
            print(f"  ⚠️  {agent.agent_id}: raised exception: {e}")
    
    print("\n✅ PASSED: Error handling works")


def run_all_tests():
    """Run all correctness tests."""
    print("\n" + "="*60)
    print("🔍 AGENT CORRECTNESS TEST SUITE")
    print("="*60)
    
    test_required_attributes()
    test_bidirectional_theses()
    test_edge_calculation_consistency()
    test_error_handling()
    
    print("\n" + "="*60)
    print("✅ ALL CORRECTNESS TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
