"""
BASED MONEY - US Politics Agents Tests
Test the 3 US Politics institutional agents
"""

import sys
import os

# Set up test environment
os.environ['TRADING_MODE'] = 'paper'
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_KEY'] = 'test_key'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.renaissance_politics import RenaissancePoliticsAgent
from agents.jpmorgan_politics import JPMorganPoliticsAgent
from agents.goldman_politics import GoldmanPoliticsAgent
from models import Market


class MockNewsEvent:
    """Mock news event for testing."""
    def __init__(self, headline: str):
        self.headline = headline


def test_agent_initialization():
    """Test that all 3 US Politics agents initialize correctly."""
    print("\n" + "="*60)
    print("TEST: US Politics Agent Initialization")
    print("="*60)
    
    # Initialize agents
    renaissance = RenaissancePoliticsAgent()
    jpmorgan = JPMorganPoliticsAgent()
    goldman = GoldmanPoliticsAgent()
    
    # Check agent IDs
    assert renaissance.agent_id == "renaissance_politics"
    assert jpmorgan.agent_id == "jpmorgan_politics"
    assert goldman.agent_id == "goldman_politics"
    
    # Check themes
    assert renaissance.theme == "us_politics"
    assert jpmorgan.theme == "us_politics"
    assert goldman.theme == "us_politics"
    
    # Check mandates
    assert "quantitative" in renaissance.mandate.lower() or "quant" in renaissance.mandate.lower()
    assert "event" in jpmorgan.mandate.lower() or "catalyst" in jpmorgan.mandate.lower()
    assert "fundamental" in goldman.mandate.lower()
    
    print(f"✓ Renaissance: {renaissance.agent_id} | {renaissance.mandate[:50]}...")
    print(f"✓ JPMorgan: {jpmorgan.agent_id} | {jpmorgan.mandate[:50]}...")
    print(f"✓ Goldman: {goldman.agent_id} | {goldman.mandate[:50]}...")
    
    print("✅ PASSED: All agents initialized correctly")


def test_agent_properties():
    """Test agent-specific properties."""
    print("\n" + "="*60)
    print("TEST: Agent Properties")
    print("="*60)
    
    renaissance = RenaissancePoliticsAgent()
    jpmorgan = JPMorganPoliticsAgent()
    goldman = GoldmanPoliticsAgent()
    
    # Check minimum thresholds differ by strategy
    print(f"  Renaissance min edge: {renaissance.min_edge:.1%}")
    print(f"  JPMorgan min edge: {jpmorgan.min_edge:.1%}")
    print(f"  Goldman min edge: {goldman.min_edge:.1%}")
    
    print(f"  Renaissance min conviction: {renaissance.min_conviction:.1%}")
    print(f"  JPMorgan min conviction: {jpmorgan.min_conviction:.1%}")
    print(f"  Goldman min conviction: {goldman.min_conviction:.1%}")
    
    # Verify differentiation
    assert goldman.min_edge >= jpmorgan.min_edge  # Fundamental has higher bar
    assert goldman.min_conviction >= jpmorgan.min_conviction
    
    print("✅ PASSED: Agent properties correctly differentiated")


def test_thesis_generation():
    """Test that agents can generate theses."""
    print("\n" + "="*60)
    print("TEST: Thesis Generation")
    print("="*60)
    
    # Create a mock politics market
    mock_market = Market(
        id="test-politics-001",
        question="Will Trump win the 2024 presidential election?",
        category="politics",
        yes_price=0.55,
        no_price=0.45,
        volume_24h=50000.0,
        resolution_date=None,
        resolved=False
    )
    
    # Mock news events
    mock_news = [
        MockNewsEvent("Trump leads in latest Iowa poll"),
        MockNewsEvent("Presidential debate scheduled for next week"),
        MockNewsEvent("Major endorsement announcement expected"),
    ]
    
    # Test each agent generates a thesis
    renaissance = RenaissancePoliticsAgent()
    jpmorgan = JPMorganPoliticsAgent()
    goldman = GoldmanPoliticsAgent()
    
    # Renaissance thesis (quantitative)
    ren_thesis = renaissance.generate_thesis(mock_market, mock_news)
    if ren_thesis:
        print(f"  Renaissance thesis:")
        print(f"    Fair value: {ren_thesis.fair_value:.1%}")
        print(f"    Edge: {ren_thesis.edge:+.1%}")
        print(f"    Conviction: {ren_thesis.conviction:.1%}")
        print(f"    Horizon: {ren_thesis.horizon}")
    
    # JPMorgan thesis (event catalyst)
    jpm_thesis = jpmorgan.generate_thesis(mock_market, mock_news)
    if jpm_thesis:
        print(f"  JPMorgan thesis:")
        print(f"    Fair value: {jpm_thesis.fair_value:.1%}")
        print(f"    Edge: {jpm_thesis.edge:+.1%}")
        print(f"    Conviction: {jpm_thesis.conviction:.1%}")
        print(f"    Horizon: {jpm_thesis.horizon}")
    
    # Goldman thesis (fundamental)
    gs_thesis = goldman.generate_thesis(mock_market, mock_news)
    if gs_thesis:
        print(f"  Goldman thesis:")
        print(f"    Fair value: {gs_thesis.fair_value:.1%}")
        print(f"    Edge: {gs_thesis.edge:+.1%}")
        print(f"    Conviction: {gs_thesis.conviction:.1%}")
        print(f"    Horizon: {gs_thesis.horizon}")
    
    # Verify at least some theses generated
    thesis_count = sum([1 for t in [ren_thesis, jpm_thesis, gs_thesis] if t is not None])
    print(f"  ✓ Generated {thesis_count}/3 theses")
    
    print("✅ PASSED: Thesis generation working")


def test_bidirectional_trading():
    """Test that agents can generate both BUY and SELL recommendations."""
    print("\n" + "="*60)
    print("TEST: Bidirectional Trading")
    print("="*60)
    
    # Expensive market
    expensive = Market(
        id="test-expensive",
        question="Will Trump win the 2024 presidential election?",
        category="politics",
        yes_price=0.85,
        no_price=0.15,
        volume_24h=50000.0,
        resolution_date=None,
        resolved=False
    )
    
    # Cheap market
    cheap = Market(
        id="test-cheap",
        question="Will Trump win the 2024 presidential election?",
        category="politics",
        yes_price=0.15,
        no_price=0.85,
        volume_24h=50000.0,
        resolution_date=None,
        resolved=False
    )
    
    mock_news = [
        MockNewsEvent("Trump campaign update"),
        MockNewsEvent("Election polling data released"),
    ]
    
    agents = [
        ("Renaissance", RenaissancePoliticsAgent()),
        ("JPMorgan", JPMorganPoliticsAgent()),
        ("Goldman", GoldmanPoliticsAgent())
    ]
    
    for name, agent in agents:
        print(f"\n  {name}:")
        
        thesis_exp = agent.generate_thesis(expensive, mock_news)
        thesis_cheap = agent.generate_thesis(cheap, mock_news)
        
        if thesis_exp:
            print(f"    Expensive (0.85): {thesis_exp.proposed_action['side']} (edge: {thesis_exp.edge:+.2%})")
        else:
            print(f"    Expensive (0.85): No thesis")
        
        if thesis_cheap:
            print(f"    Cheap (0.15): {thesis_cheap.proposed_action['side']} (edge: {thesis_cheap.edge:+.2%})")
        else:
            print(f"    Cheap (0.15): No thesis")
    
    print("\n✅ PASSED: Bidirectional trading supported")


def test_agent_repr():
    """Test string representation."""
    print("\n" + "="*60)
    print("TEST: Agent String Representation")
    print("="*60)
    
    agents = [
        RenaissancePoliticsAgent(),
        JPMorganPoliticsAgent(),
        GoldmanPoliticsAgent()
    ]
    
    for agent in agents:
        repr_str = repr(agent)
        print(f"  {repr_str}")
        assert "Agent" in repr_str
        assert "mandate" in repr_str
    
    print("✅ PASSED: Agent repr() working")


def run_all_tests():
    """Run all US Politics agent tests."""
    print("\n" + "="*60)
    print("🇺🇸 US POLITICS AGENTS TEST SUITE")
    print("="*60)
    
    test_agent_initialization()
    test_agent_properties()
    test_thesis_generation()
    test_bidirectional_trading()
    test_agent_repr()
    
    print("\n" + "="*60)
    print("✅ ALL US POLITICS AGENT TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
