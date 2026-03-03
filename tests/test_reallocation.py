"""
BASED MONEY - Reallocation Logic Tests
Test weekly and monthly reallocation algorithms
"""

import sys
import os

# Set up test environment
os.environ['TRADING_MODE'] = 'paper'
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_KEY'] = 'test_key'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.theme_portfolio import ThemeManager, ThemePortfolio
from reallocation_config.reallocation_rules import (
    get_agent_allocation_pct,
    get_theme_capital_adjustment,
    should_pause_theme,
    MIN_THEME_CAPITAL,
    MIN_AGENT_CAPITAL,
    MAX_THEME_CAPITAL_PCT
)


def test_get_agent_allocation_pct():
    """Test agent allocation percentage calculation."""
    print("\n" + "="*60)
    print("TEST: Agent Allocation Percentage")
    print("="*60)
    
    # Test high performer
    pct = get_agent_allocation_pct(win_rate=0.70, profit_pct=15.0)
    assert pct >= 35.0  # Should get >=35% allocation (returns as 35.0, not 0.35)
    print(f"✓ High performer (70% WR, +15% profit): {pct:.1f}% allocation")
    
    # Test medium performer
    pct = get_agent_allocation_pct(win_rate=0.55, profit_pct=5.0)
    assert 30.0 <= pct <= 40.0  # Should get 30-40% allocation
    print(f"✓ Medium performer (55% WR, +5% profit): {pct:.1f}% allocation")
    
    # Test poor performer
    pct = get_agent_allocation_pct(win_rate=0.35, profit_pct=-10.0)
    assert pct <= 30.0  # Should get <=30% allocation
    print(f"✓ Poor performer (35% WR, -10% profit): {pct:.1f}% allocation")
    
    print("✅ PASSED: Agent allocation calculation working")


def test_get_theme_capital_adjustment():
    """Test theme capital adjustment multiplier."""
    print("\n" + "="*60)
    print("TEST: Theme Capital Adjustment")
    print("="*60)
    
    # Test winning theme
    adj = get_theme_capital_adjustment(profit_pct=10.0, win_rate=0.65, consecutive_losing_weeks=0)
    assert adj > 1.0  # Should increase capital
    print(f"✓ Winning theme (65% WR, +10% profit): {adj:.2f}x multiplier")
    
    # Test stable theme
    adj = get_theme_capital_adjustment(profit_pct=2.0, win_rate=0.52, consecutive_losing_weeks=0)
    assert adj >= 0.95 and adj <= 1.05  # Should stay roughly same
    print(f"✓ Stable theme (52% WR, +2% profit): {adj:.2f}x multiplier")
    
    # Test losing theme
    adj = get_theme_capital_adjustment(profit_pct=-8.0, win_rate=0.42, consecutive_losing_weeks=1)
    assert adj < 1.0  # Should decrease capital
    print(f"✓ Losing theme (42% WR, -8% profit, 1 losing week): {adj:.2f}x multiplier")
    
    # Test probation theme
    adj = get_theme_capital_adjustment(profit_pct=-12.0, win_rate=0.35, consecutive_losing_weeks=2)
    assert adj < 0.90  # Should decrease more significantly
    print(f"✓ Probation theme (35% WR, -12% profit, 2 losing weeks): {adj:.2f}x multiplier")
    
    print("✅ PASSED: Theme capital adjustment working")


def test_should_pause_theme():
    """Test theme pause logic."""
    print("\n" + "="*60)
    print("TEST: Theme Pause Logic")
    print("="*60)
    
    # Test normal performance
    should_pause = should_pause_theme(consecutive_losing_months=0)
    assert not should_pause
    print("✓ 0 losing months: Don't pause")
    
    # Test 1 losing month
    should_pause = should_pause_theme(consecutive_losing_months=1)
    assert not should_pause
    print("✓ 1 losing month: Don't pause")
    
    # Test 2 losing months
    should_pause = should_pause_theme(consecutive_losing_months=2)
    # Should pause at 2 months (based on rule: consecutive_losing_months >= 2)
    assert should_pause
    print(f"✓ 2 losing months: {'Pause' if should_pause else 'Do not pause'} (correct)")
    
    # Test 3+ losing months
    should_pause = should_pause_theme(consecutive_losing_months=3)
    assert should_pause  # Should definitely pause
    print("✓ 3+ losing months: Pause (correct)")
    
    print("✅ PASSED: Theme pause logic working")


def test_min_capital_constraints():
    """Test minimum capital constraints."""
    print("\n" + "="*60)
    print("TEST: Minimum Capital Constraints")
    print("="*60)
    
    print(f"✓ MIN_THEME_CAPITAL: ${MIN_THEME_CAPITAL:,.2f}")
    print(f"✓ MIN_AGENT_CAPITAL: ${MIN_AGENT_CAPITAL:,.2f}")
    print(f"✓ MAX_THEME_CAPITAL_PCT: {MAX_THEME_CAPITAL_PCT}%")
    
    # Verify constraints are reasonable
    assert MIN_THEME_CAPITAL > 0
    assert MIN_AGENT_CAPITAL > 0
    assert MIN_AGENT_CAPITAL < MIN_THEME_CAPITAL
    assert MAX_THEME_CAPITAL_PCT > 0 and MAX_THEME_CAPITAL_PCT <= 100
    
    print("✅ PASSED: Capital constraints are properly defined")


def test_theme_reallocate_capital():
    """Test ThemePortfolio.reallocate_capital method."""
    print("\n" + "="*60)
    print("TEST: Theme Capital Reallocation")
    print("="*60)
    
    # Create a theme portfolio
    theme = ThemePortfolio("test_theme", initial_capital=2500.0)
    
    # Add some agents
    theme.add_agent("agent_1")
    theme.add_agent("agent_2")
    theme.add_agent("agent_3")
    
    # Reallocate (with no performance data, should use equal distribution)
    allocations = theme.reallocate_capital()
    
    # Verify allocations
    assert isinstance(allocations, dict)
    assert len(allocations) == 3
    assert all(val > 0 for val in allocations.values())
    
    # Verify total allocation equals current capital (approximately)
    total_allocated = sum(allocations.values())
    assert abs(total_allocated - theme.current_capital) < 10  # Within $10
    
    print("✅ PASSED: Theme reallocation working")
    for agent_id, capital in allocations.items():
        print(f"   {agent_id}: ${capital:,.2f}")


def test_theme_manager_weekly_reallocation():
    """Test ThemeManager.weekly_reallocation method."""
    print("\n" + "="*60)
    print("TEST: ThemeManager Weekly Reallocation")
    print("="*60)
    
    # Create theme manager
    theme_manager = ThemeManager(total_capital=10000.0)
    
    # Verify method exists
    assert hasattr(theme_manager, 'weekly_reallocation')
    assert callable(theme_manager.weekly_reallocation)
    
    print("✅ PASSED: ThemeManager has weekly_reallocation method")


def test_theme_manager_monthly_rotation():
    """Test ThemeManager.monthly_theme_rotation method."""
    print("\n" + "="*60)
    print("TEST: ThemeManager Monthly Theme Rotation")
    print("="*60)
    
    # Create theme manager
    theme_manager = ThemeManager(total_capital=10000.0)
    
    # Verify method exists
    assert hasattr(theme_manager, 'monthly_theme_rotation')
    assert callable(theme_manager.monthly_theme_rotation)
    
    print("✅ PASSED: ThemeManager has monthly_theme_rotation method")


def test_theme_manager_get_theme_leaderboard():
    """Test ThemeManager.get_theme_leaderboard method."""
    print("\n" + "="*60)
    print("TEST: ThemeManager Theme Leaderboard")
    print("="*60)
    
    # Create theme manager
    theme_manager = ThemeManager(total_capital=10000.0)
    
    # Get leaderboard
    leaderboard = theme_manager.get_theme_leaderboard(period='7d')
    
    # Verify structure
    assert isinstance(leaderboard, list)
    assert len(leaderboard) == 4  # 4 themes
    
    # Verify each entry has required fields
    for entry in leaderboard:
        assert 'theme' in entry
        assert 'current_capital' in entry
        assert 'status' in entry
        assert 'win_rate' in entry
        assert 'total_pnl' in entry
    
    # Verify sorted by profit_pct
    if len(leaderboard) > 1:
        assert leaderboard[0]['profit_pct'] >= leaderboard[-1]['profit_pct']
    
    print("✅ PASSED: Theme leaderboard working")
    for i, entry in enumerate(leaderboard, 1):
        print(f"   #{i} {entry['theme']}: ${entry['current_capital']:,.2f} ({entry['status']})")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("REALLOCATION LOGIC TESTS")
    print("="*60)
    
    # Run all tests
    test_get_agent_allocation_pct()
    test_get_theme_capital_adjustment()
    test_should_pause_theme()
    test_min_capital_constraints()
    test_theme_reallocate_capital()
    test_theme_manager_weekly_reallocation()
    test_theme_manager_monthly_rotation()
    test_theme_manager_get_theme_leaderboard()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✅")
    print("="*60)
