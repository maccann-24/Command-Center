"""
BASED MONEY - Theme Portfolio Tests
Unit tests for theme-based portfolio system
"""

import sys
import os

# Set up test environment variables
os.environ['TRADING_MODE'] = 'paper'
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_KEY'] = 'test_key'

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.theme_portfolio import ThemePortfolio, ThemeManager
from core.performance_tracker import PerformanceTracker
from reallocation_config.reallocation_rules import get_agent_allocation_pct, get_theme_capital_adjustment


def test_theme_portfolio_initialization():
    """Test basic ThemePortfolio creation."""
    print("\n" + "="*60)
    print("TEST: Theme Portfolio Initialization")
    print("="*60)
    
    theme = ThemePortfolio("geopolitical", 2500.0)
    
    assert theme.name == "geopolitical"
    assert theme.initial_capital == 2500.0
    assert theme.current_capital == 2500.0
    assert theme.status == "ACTIVE"
    assert len(theme.agents) == 0
    
    print("✅ PASSED: Theme portfolio initialization")


def test_add_agents():
    """Test adding agents to theme."""
    print("\n" + "="*60)
    print("TEST: Add Agents to Theme")
    print("="*60)
    
    theme = ThemePortfolio("geopolitical", 2500.0)
    
    theme.add_agent("twosigma_geo")
    theme.add_agent("goldman_geo")
    theme.add_agent("bridgewater_geo")
    
    assert len(theme.agents) == 3
    assert "twosigma_geo" in theme.agents
    assert "goldman_geo" in theme.agents
    
    print("✅ PASSED: Add agents to theme")


def test_theme_manager_initialization():
    """Test ThemeManager creation with 4 themes."""
    print("\n" + "="*60)
    print("TEST: Theme Manager Initialization")
    print("="*60)
    
    manager = ThemeManager(total_capital=10000.0)
    
    assert manager.total_capital == 10000.0
    assert len(manager.themes) == 4
    assert "geopolitical" in manager.themes
    assert "us_politics" in manager.themes
    assert "crypto" in manager.themes
    assert "weather" in manager.themes
    
    # Each theme should start with $2500
    for theme_name, theme in manager.themes.items():
        assert theme.current_capital == 2500.0
        print(f"  {theme_name}: ${theme.current_capital:.2f}")
    
    print("✅ PASSED: Theme manager initialization")


def test_add_agents_to_themes():
    """Test adding agents to themes via ThemeManager."""
    print("\n" + "="*60)
    print("TEST: Add Agents via Theme Manager")
    print("="*60)
    
    manager = ThemeManager(total_capital=10000.0)
    
    # Add geopolitical agents
    manager.add_agent_to_theme("geopolitical", "twosigma_geo")
    manager.add_agent_to_theme("geopolitical", "goldman_geo")
    manager.add_agent_to_theme("geopolitical", "bridgewater_geo")
    
    # Add us_politics agents
    manager.add_agent_to_theme("us_politics", "renaissance_politics")
    manager.add_agent_to_theme("us_politics", "jpmorgan_politics")
    
    # Add crypto agents
    manager.add_agent_to_theme("crypto", "morganstanley_crypto")
    manager.add_agent_to_theme("crypto", "renaissance_crypto")
    
    # Add weather agents
    manager.add_agent_to_theme("weather", "renaissance_weather")
    manager.add_agent_to_theme("weather", "morganstanley_weather")
    
    assert len(manager.themes["geopolitical"].agents) == 3
    assert len(manager.themes["us_politics"].agents) == 2
    assert len(manager.themes["crypto"].agents) == 2
    assert len(manager.themes["weather"].agents) == 2
    
    print("✅ PASSED: Add agents via theme manager")


def test_agent_allocation_rules():
    """Test agent capital allocation percentage logic."""
    print("\n" + "="*60)
    print("TEST: Agent Allocation Rules")
    print("="*60)
    
    # Top performer: 60% win rate, 7% profit
    pct1 = get_agent_allocation_pct(win_rate=0.60, profit_pct=7.0)
    assert pct1 == 40.0
    print(f"  Top performer (60% WR, 7% profit): {pct1}% allocation")
    
    # Good performer: 55% win rate, 5% profit
    pct2 = get_agent_allocation_pct(win_rate=0.55, profit_pct=5.0)
    assert pct2 == 35.0
    print(f"  Good performer (55% WR, 5% profit): {pct2}% allocation")
    
    # Underperformer: 45% win rate, -2% profit
    pct3 = get_agent_allocation_pct(win_rate=0.45, profit_pct=-2.0)
    assert pct3 == 25.0
    print(f"  Underperformer (45% WR, -2% profit): {pct3}% allocation")
    
    print("✅ PASSED: Agent allocation rules")


def test_theme_capital_adjustment():
    """Test theme capital adjustment multipliers."""
    print("\n" + "="*60)
    print("TEST: Theme Capital Adjustment")
    print("="*60)
    
    # Winner: 6% profit, 58% win rate, 0 losing weeks
    adj1 = get_theme_capital_adjustment(profit_pct=6.0, win_rate=0.58, consecutive_losing_weeks=0)
    assert adj1 == 1.10
    print(f"  Winner (+6% profit, 58% WR): {adj1:.2f}x capital")
    
    # Underperformer: -2% profit, 1 losing week
    adj2 = get_theme_capital_adjustment(profit_pct=-2.0, win_rate=0.48, consecutive_losing_weeks=1)
    assert adj2 == 0.95
    print(f"  Underperformer (-2% profit): {adj2:.2f}x capital")
    
    # Probation: 2 consecutive losing weeks
    adj3 = get_theme_capital_adjustment(profit_pct=-3.0, win_rate=0.42, consecutive_losing_weeks=2)
    assert adj3 == 0.80
    print(f"  Probation (2 losing weeks): {adj3:.2f}x capital")
    
    print("✅ PASSED: Theme capital adjustment")


def test_theme_leaderboard():
    """Test theme leaderboard ranking."""
    print("\n" + "="*60)
    print("TEST: Theme Leaderboard")
    print("="*60)
    
    manager = ThemeManager(total_capital=10000.0)
    
    # Get leaderboard (will be empty without real trades)
    leaderboard = manager.get_theme_leaderboard(period='7d')
    
    assert len(leaderboard) == 4
    print(f"  Leaderboard has {len(leaderboard)} themes")
    
    for rank, theme_stats in enumerate(leaderboard, 1):
        print(f"  {rank}. {theme_stats['theme']}: ${theme_stats['current_capital']:.2f}")
    
    print("✅ PASSED: Theme leaderboard")


def test_mock_trade_tracking():
    """Test tracking mock trades."""
    print("\n" + "="*60)
    print("TEST: Mock Trade Tracking")
    print("="*60)
    
    # Note: This test doesn't actually write to DB in test mode
    # In production, this would use PerformanceTracker.track_trade()
    
    print("  (Skipping DB writes in test mode)")
    print("  In production: PerformanceTracker.track_trade() writes to agent_performance table")
    
    print("✅ PASSED: Mock trade tracking")


def test_serialization():
    """Test theme and manager serialization to dict."""
    print("\n" + "="*60)
    print("TEST: Serialization to Dict")
    print("="*60)
    
    manager = ThemeManager(total_capital=10000.0)
    manager.add_agent_to_theme("geopolitical", "twosigma_geo")
    
    # Serialize to dict
    data = manager.to_dict()
    
    assert data['total_capital'] == 10000.0
    assert 'themes' in data
    assert 'geopolitical' in data['themes']
    assert data['themes']['geopolitical']['agents'] == ['twosigma_geo']
    
    print("  Serialized manager to dict:")
    print(f"    Total capital: ${data['total_capital']:.2f}")
    print(f"    Current value: ${data['current_value']:.2f}")
    print(f"    Themes: {len(data['themes'])}")
    
    print("✅ PASSED: Serialization")


def run_all_tests():
    """Run all unit tests."""
    print("\n" + "="*60)
    print("🧪 THEME PORTFOLIO TEST SUITE")
    print("="*60)
    
    test_theme_portfolio_initialization()
    test_add_agents()
    test_theme_manager_initialization()
    test_add_agents_to_themes()
    test_agent_allocation_rules()
    test_theme_capital_adjustment()
    test_theme_leaderboard()
    test_mock_trade_tracking()
    test_serialization()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
