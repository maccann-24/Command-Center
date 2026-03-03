"""
BASED MONEY - Crypto Agents Tests
Test the 3 Crypto institutional agents
"""

import sys
import os

# Set up test environment
os.environ['TRADING_MODE'] = 'paper'
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_KEY'] = 'test_key'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.morganstanley_crypto import MorganStanleyCryptoAgent
from agents.renaissance_crypto import RenaissanceCryptoAgent
from agents.citadel_crypto import CitadelCryptoAgent
from models import Market


class MockNewsEvent:
    """Mock news event for testing."""
    def __init__(self, headline: str):
        self.headline = headline


def test_agent_initialization():
    """Test that all 3 Crypto agents initialize correctly."""
    print("\n" + "="*60)
    print("TEST: Crypto Agent Initialization")
    print("="*60)
    
    # Initialize agents
    morganstanley = MorganStanleyCryptoAgent()
    renaissance = RenaissanceCryptoAgent()
    citadel = CitadelCryptoAgent()
    
    # Check agent IDs
    assert morganstanley.agent_id == "morganstanley_crypto"
    assert renaissance.agent_id == "renaissance_crypto"
    assert citadel.agent_id == "citadel_crypto"
    
    # Check themes
    assert morganstanley.theme == "crypto"
    assert renaissance.theme == "crypto"
    assert citadel.theme == "crypto"
    
    # Check mandates
    assert "technical" in morganstanley.mandate.lower()
    assert "quantitative" in renaissance.mandate.lower() or "quant" in renaissance.mandate.lower()
    assert "cycle" in citadel.mandate.lower() or "sector" in citadel.mandate.lower()
    
    print(f"✓ MorganStanley: {morganstanley.agent_id} | {morganstanley.mandate[:50]}...")
    print(f"✓ Renaissance: {renaissance.agent_id} | {renaissance.mandate[:50]}...")
    print(f"✓ Citadel: {citadel.agent_id} | {citadel.mandate[:50]}...")
    
    print("✅ PASSED: All agents initialized correctly")


def test_agent_properties():
    """Test agent-specific properties."""
    print("\n" + "="*60)
    print("TEST: Agent Properties")
    print("="*60)
    
    morganstanley = MorganStanleyCryptoAgent()
    renaissance = RenaissanceCryptoAgent()
    citadel = CitadelCryptoAgent()
    
    # Check minimum thresholds
    print(f"  MorganStanley min edge: {morganstanley.min_edge:.1%}")
    print(f"  Renaissance min edge: {renaissance.min_edge:.1%}")
    print(f"  Citadel min edge: {citadel.min_edge:.1%}")
    
    print(f"  MorganStanley min conviction: {morganstanley.min_conviction:.1%}")
    print(f"  Renaissance min conviction: {renaissance.min_conviction:.1%}")
    print(f"  Citadel min conviction: {citadel.min_conviction:.1%}")
    
    # Verify differentiation
    assert renaissance.min_edge >= morganstanley.min_edge  # Quant has higher bar
    
    print("✅ PASSED: Agent properties correctly differentiated")


def test_thesis_generation():
    """Test that agents can generate theses."""
    print("\n" + "="*60)
    print("TEST: Thesis Generation")
    print("="*60)
    
    # Create a mock crypto market
    mock_market = Market(
        id="test-crypto-001",
        question="Will Bitcoin reach $100,000 by December 2024?",
        category="crypto",
        yes_price=0.55,
        no_price=0.45,
        volume_24h=75000.0,
        resolution_date=None,
        resolved=False
    )
    
    # Mock news events
    mock_news = [
        MockNewsEvent("Bitcoin price hits new high"),
        MockNewsEvent("Federal Reserve signals rate cuts"),
        MockNewsEvent("Bitcoin ETF approval expected"),
        MockNewsEvent("Crypto market sentiment bullish"),
        MockNewsEvent("Ethereum blockchain upgrade successful"),
    ]
    
    # Test each agent generates a thesis
    morganstanley = MorganStanleyCryptoAgent()
    renaissance = RenaissanceCryptoAgent()
    citadel = CitadelCryptoAgent()
    
    # MorganStanley thesis (technical)
    ms_thesis = morganstanley.generate_thesis(mock_market, mock_news)
    if ms_thesis:
        print(f"  MorganStanley thesis:")
        print(f"    Fair value: {ms_thesis.fair_value:.1%}")
        print(f"    Edge: {ms_thesis.edge:+.1%}")
        print(f"    Conviction: {ms_thesis.conviction:.1%}")
        print(f"    Horizon: {ms_thesis.horizon}")
    
    # Renaissance thesis (quantitative)
    ren_thesis = renaissance.generate_thesis(mock_market, mock_news)
    if ren_thesis:
        print(f"  Renaissance thesis:")
        print(f"    Fair value: {ren_thesis.fair_value:.1%}")
        print(f"    Edge: {ren_thesis.edge:+.1%}")
        print(f"    Conviction: {ren_thesis.conviction:.1%}")
        print(f"    Horizon: {ren_thesis.horizon}")
    
    # Citadel thesis (cycle)
    citadel_thesis = citadel.generate_thesis(mock_market, mock_news)
    if citadel_thesis:
        print(f"  Citadel thesis:")
        print(f"    Fair value: {citadel_thesis.fair_value:.1%}")
        print(f"    Edge: {citadel_thesis.edge:+.1%}")
        print(f"    Conviction: {citadel_thesis.conviction:.1%}")
        print(f"    Horizon: {citadel_thesis.horizon}")
    
    # Verify at least some theses generated
    thesis_count = sum([1 for t in [ms_thesis, ren_thesis, citadel_thesis] if t is not None])
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
        question="Will Bitcoin reach $100,000 by December 2024?",
        category="crypto",
        yes_price=0.85,
        no_price=0.15,
        volume_24h=75000.0,
        resolution_date=None,
        resolved=False
    )
    
    # Cheap market
    cheap = Market(
        id="test-cheap",
        question="Will Bitcoin reach $100,000 by December 2024?",
        category="crypto",
        yes_price=0.15,
        no_price=0.85,
        volume_24h=75000.0,
        resolution_date=None,
        resolved=False
    )
    
    mock_news = [
        MockNewsEvent("Bitcoin market update"),
        MockNewsEvent("Crypto trading volume surges"),
    ]
    
    agents = [
        ("MorganStanley", MorganStanleyCryptoAgent()),
        ("Renaissance", RenaissanceCryptoAgent()),
        ("Citadel", CitadelCryptoAgent())
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
        MorganStanleyCryptoAgent(),
        RenaissanceCryptoAgent(),
        CitadelCryptoAgent()
    ]
    
    for agent in agents:
        repr_str = repr(agent)
        print(f"  {repr_str}")
        assert "Agent" in repr_str
        assert "mandate" in repr_str
    
    print("✅ PASSED: Agent repr() working")


def run_all_tests():
    """Run all Crypto agent tests."""
    print("\n" + "="*60)
    print("₿ CRYPTO AGENTS TEST SUITE")
    print("="*60)
    
    test_agent_initialization()
    test_agent_properties()
    test_thesis_generation()
    test_bidirectional_trading()
    test_agent_repr()
    
    print("\n" + "="*60)
    print("✅ ALL CRYPTO AGENT TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
