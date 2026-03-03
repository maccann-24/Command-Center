"""
BASED MONEY - Institutional Agents Tests
Test the 3 geopolitical institutional agents
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


def test_agent_initialization():
    """Test that all 3 agents initialize correctly."""
    print("\n" + "="*60)
    print("TEST: Institutional Agent Initialization")
    print("="*60)
    
    # Initialize agents
    twosigma = TwoSigmaGeoAgent()
    goldman = GoldmanGeoAgent()
    bridgewater = BridgewaterGeoAgent()
    
    # Check agent IDs
    assert twosigma.agent_id == "twosigma_geo"
    assert goldman.agent_id == "goldman_geo"
    assert bridgewater.agent_id == "bridgewater_geo"
    
    # Check themes
    assert twosigma.theme == "geopolitical"
    assert goldman.theme == "geopolitical"
    assert bridgewater.theme == "geopolitical"
    
    # Check mandates
    assert "macro" in twosigma.mandate.lower()
    assert "fundamental" in goldman.mandate.lower()
    assert "risk" in bridgewater.mandate.lower()
    
    print(f"✓ TwoSigma: {twosigma.agent_id} | {twosigma.mandate[:50]}...")
    print(f"✓ Goldman: {goldman.agent_id} | {goldman.mandate[:50]}...")
    print(f"✓ Bridgewater: {bridgewater.agent_id} | {bridgewater.mandate[:50]}...")
    
    print("✅ PASSED: All agents initialized correctly")


def test_agent_properties():
    """Test agent-specific properties."""
    print("\n" + "="*60)
    print("TEST: Agent Properties")
    print("="*60)
    
    twosigma = TwoSigmaGeoAgent()
    goldman = GoldmanGeoAgent()
    bridgewater = BridgewaterGeoAgent()
    
    # Check minimum thresholds differ by strategy
    print(f"  TwoSigma min edge: {twosigma.min_edge:.1%}")
    print(f"  Goldman min edge: {goldman.min_edge:.1%}")
    print(f"  Bridgewater min edge: {bridgewater.min_edge:.1%}")
    
    assert goldman.min_edge > twosigma.min_edge  # Fundamental has higher bar
    
    print(f"  TwoSigma min conviction: {twosigma.min_conviction:.1%}")
    print(f"  Goldman min conviction: {goldman.min_conviction:.1%}")
    print(f"  Bridgewater min conviction: {bridgewater.min_conviction:.1%}")
    
    assert goldman.min_conviction > bridgewater.min_conviction  # Risk-managed can be lower
    
    print("✅ PASSED: Agent properties correctly differentiated")


def test_thesis_generation():
    """Test that agents can generate theses."""
    print("\n" + "="*60)
    print("TEST: Thesis Generation")
    print("="*60)
    
    # Create a mock market
    mock_market = Market(
        id="test-geo-market-001",
        question="Will Russia and Ukraine reach a peace agreement by June 2026?",
        category="geopolitical",
        yes_price=0.35,
        no_price=0.65,
        volume_24h=125000.0,
        resolution_date=None,
        resolved=False
    )
    
    # Test each agent generates a thesis
    twosigma = TwoSigmaGeoAgent()
    goldman = GoldmanGeoAgent()
    bridgewater = BridgewaterGeoAgent()
    
    # TwoSigma thesis (macro)
    ts_thesis = twosigma.generate_thesis(mock_market, [])
    if ts_thesis:
        print(f"  TwoSigma thesis:")
        print(f"    Fair value: {ts_thesis.fair_value:.1%}")
        print(f"    Edge: {ts_thesis.edge:.1%}")
        print(f"    Conviction: {ts_thesis.conviction:.1%}")
        print(f"    Horizon: {ts_thesis.horizon}")
    
    # Goldman thesis (fundamental)
    gs_thesis = goldman.generate_thesis(mock_market, [])
    if gs_thesis:
        print(f"  Goldman thesis:")
        print(f"    Fair value: {gs_thesis.fair_value:.1%}")
        print(f"    Edge: {gs_thesis.edge:.1%}")
        print(f"    Conviction: {gs_thesis.conviction:.1%}")
        print(f"    Horizon: {gs_thesis.horizon}")
    
    # Bridgewater thesis (risk-managed)
    bw_markets = [mock_market]  # Need list for correlation analysis
    bw_thesis = bridgewater.generate_thesis(mock_market, bw_markets, [])
    if bw_thesis:
        print(f"  Bridgewater thesis:")
        print(f"    Fair value: {bw_thesis.fair_value:.1%}")
        print(f"    Edge: {bw_thesis.edge:.1%}")
        print(f"    Conviction: {bw_thesis.conviction:.1%}")
        print(f"    Horizon: {bw_thesis.horizon}")
        print(f"    Size: {bw_thesis.proposed_action.get('size_pct', 0):.1%}")
    
    # Verify theses have different characteristics
    if ts_thesis and gs_thesis and bw_thesis:
        # Different horizons
        assert ts_thesis.horizon != gs_thesis.horizon or gs_thesis.horizon != bw_thesis.horizon
        print("  ✓ Agents produce differentiated theses")
    
    print("✅ PASSED: Thesis generation working")


def test_agent_repr():
    """Test string representation."""
    print("\n" + "="*60)
    print("TEST: Agent String Representation")
    print("="*60)
    
    agents = [
        TwoSigmaGeoAgent(),
        GoldmanGeoAgent(),
        BridgewaterGeoAgent()
    ]
    
    for agent in agents:
        repr_str = repr(agent)
        print(f"  {repr_str}")
        assert "Agent" in repr_str
        assert "mandate" in repr_str
    
    print("✅ PASSED: Agent repr() working")


def run_all_tests():
    """Run all institutional agent tests."""
    print("\n" + "="*60)
    print("🏛️ INSTITUTIONAL AGENTS TEST SUITE")
    print("="*60)
    
    test_agent_initialization()
    test_agent_properties()
    test_thesis_generation()
    test_agent_repr()
    
    print("\n" + "="*60)
    print("✅ ALL INSTITUTIONAL AGENT TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
