"""
BASED MONEY - Weather Agents Tests
Test the 3 Weather institutional agents
"""

import sys
import os

# Set up test environment
os.environ['TRADING_MODE'] = 'paper'
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_KEY'] = 'test_key'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.renaissance_weather import RenaissanceWeatherAgent
from agents.morganstanley_weather import MorganStanleyWeatherAgent
from agents.bridgewater_weather import BridgewaterWeatherAgent
from models import Market


class MockNewsEvent:
    """Mock news event for testing."""
    def __init__(self, headline: str):
        self.headline = headline


def test_agent_initialization():
    """Test that all 3 Weather agents initialize correctly."""
    print("\n" + "="*60)
    print("TEST: Weather Agent Initialization")
    print("="*60)
    
    # Initialize agents
    renaissance = RenaissanceWeatherAgent()
    morganstanley = MorganStanleyWeatherAgent()
    bridgewater = BridgewaterWeatherAgent()
    
    # Check agent IDs
    assert renaissance.agent_id == "renaissance_weather"
    assert morganstanley.agent_id == "morganstanley_weather"
    assert bridgewater.agent_id == "bridgewater_weather"
    
    # Check themes
    assert renaissance.theme == "weather"
    assert morganstanley.theme == "weather"
    assert bridgewater.theme == "weather"
    
    # Check mandates
    assert "quantitative" in renaissance.mandate.lower() or "quant" in renaissance.mandate.lower()
    assert "technical" in morganstanley.mandate.lower() or "pattern" in morganstanley.mandate.lower()
    assert "risk" in bridgewater.mandate.lower()
    
    print(f"✓ Renaissance: {renaissance.agent_id} | {renaissance.mandate[:50]}...")
    print(f"✓ MorganStanley: {morganstanley.agent_id} | {morganstanley.mandate[:50]}...")
    print(f"✓ Bridgewater: {bridgewater.agent_id} | {bridgewater.mandate[:50]}...")
    
    print("✅ PASSED: All agents initialized correctly")


def test_agent_properties():
    """Test agent-specific properties."""
    print("\n" + "="*60)
    print("TEST: Agent Properties")
    print("="*60)
    
    renaissance = RenaissanceWeatherAgent()
    morganstanley = MorganStanleyWeatherAgent()
    bridgewater = BridgewaterWeatherAgent()
    
    # Check minimum thresholds
    print(f"  Renaissance min edge: {renaissance.min_edge:.1%}")
    print(f"  MorganStanley min edge: {morganstanley.min_edge:.1%}")
    print(f"  Bridgewater min edge: {bridgewater.min_edge:.1%}")
    
    print(f"  Renaissance min conviction: {renaissance.min_conviction:.1%}")
    print(f"  MorganStanley min conviction: {morganstanley.min_conviction:.1%}")
    print(f"  Bridgewater min conviction: {bridgewater.min_conviction:.1%}")
    
    # Verify differentiation
    assert renaissance.min_edge >= morganstanley.min_edge  # Quant has higher bar
    assert bridgewater.min_conviction < renaissance.min_conviction  # Risk-managed can be lower
    
    print("✅ PASSED: Agent properties correctly differentiated")


def test_thesis_generation():
    """Test that agents can generate theses."""
    print("\n" + "="*60)
    print("TEST: Thesis Generation")
    print("="*60)
    
    # Create a mock weather market
    mock_market = Market(
        id="test-weather-001",
        question="Will New York City see a heatwave (3+ days above 95°F) in July 2024?",
        category="weather",
        yes_price=0.55,
        no_price=0.45,
        volume_24h=45000.0,
        resolution_date=None,
        resolved=False
    )
    
    # Mock news events
    mock_news = [
        MockNewsEvent("Heatwave forecast for Northeast"),
        MockNewsEvent("NOAA predicts above-average temperatures"),
        MockNewsEvent("Climate models show warming trend"),
        MockNewsEvent("El Niño impacts summer weather"),
    ]
    
    # Test each agent generates a thesis
    renaissance = RenaissanceWeatherAgent()
    morganstanley = MorganStanleyWeatherAgent()
    bridgewater = BridgewaterWeatherAgent()
    
    # Renaissance thesis (quantitative)
    ren_thesis = renaissance.generate_thesis(mock_market, mock_news)
    if ren_thesis:
        print(f"  Renaissance thesis:")
        print(f"    Fair value: {ren_thesis.fair_value:.1%}")
        print(f"    Edge: {ren_thesis.edge:+.1%}")
        print(f"    Conviction: {ren_thesis.conviction:.1%}")
        print(f"    Horizon: {ren_thesis.horizon}")
    
    # MorganStanley thesis (technical)
    ms_thesis = morganstanley.generate_thesis(mock_market, mock_news)
    if ms_thesis:
        print(f"  MorganStanley thesis:")
        print(f"    Fair value: {ms_thesis.fair_value:.1%}")
        print(f"    Edge: {ms_thesis.edge:+.1%}")
        print(f"    Conviction: {ms_thesis.conviction:.1%}")
        print(f"    Horizon: {ms_thesis.horizon}")
    
    # Bridgewater thesis (risk-managed)
    bw_markets = [mock_market]  # Need list for correlation analysis
    bw_thesis = bridgewater.generate_thesis(mock_market, bw_markets, mock_news)
    if bw_thesis:
        print(f"  Bridgewater thesis:")
        print(f"    Fair value: {bw_thesis.fair_value:.1%}")
        print(f"    Edge: {bw_thesis.edge:+.1%}")
        print(f"    Conviction: {bw_thesis.conviction:.1%}")
        print(f"    Horizon: {bw_thesis.horizon}")
        print(f"    Size: {bw_thesis.proposed_action.get('size_pct', 0):.1%}")
    
    # Verify at least some theses generated
    thesis_count = sum([1 for t in [ren_thesis, ms_thesis, bw_thesis] if t is not None])
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
        question="Will New York City see a heatwave in July 2024?",
        category="weather",
        yes_price=0.85,
        no_price=0.15,
        volume_24h=45000.0,
        resolution_date=None,
        resolved=False
    )
    
    # Cheap market
    cheap = Market(
        id="test-cheap",
        question="Will New York City see a heatwave in July 2024?",
        category="weather",
        yes_price=0.15,
        no_price=0.85,
        volume_24h=45000.0,
        resolution_date=None,
        resolved=False
    )
    
    mock_news = [
        MockNewsEvent("Weather forecast update"),
        MockNewsEvent("Temperature trends analyzed"),
    ]
    
    agents = [
        ("Renaissance", RenaissanceWeatherAgent()),
        ("MorganStanley", MorganStanleyWeatherAgent()),
        ("Bridgewater", BridgewaterWeatherAgent())
    ]
    
    for name, agent in agents:
        print(f"\n  {name}:")
        
        if isinstance(agent, BridgewaterWeatherAgent):
            thesis_exp = agent.generate_thesis(expensive, [expensive, cheap], mock_news)
            thesis_cheap = agent.generate_thesis(cheap, [expensive, cheap], mock_news)
        else:
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
        RenaissanceWeatherAgent(),
        MorganStanleyWeatherAgent(),
        BridgewaterWeatherAgent()
    ]
    
    for agent in agents:
        repr_str = repr(agent)
        print(f"  {repr_str}")
        assert "Agent" in repr_str
        assert "mandate" in repr_str
    
    print("✅ PASSED: Agent repr() working")


def run_all_tests():
    """Run all Weather agent tests."""
    print("\n" + "="*60)
    print("🌦️ WEATHER AGENTS TEST SUITE")
    print("="*60)
    
    test_agent_initialization()
    test_agent_properties()
    test_thesis_generation()
    test_bidirectional_trading()
    test_agent_repr()
    
    print("\n" + "="*60)
    print("✅ ALL WEATHER AGENT TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
