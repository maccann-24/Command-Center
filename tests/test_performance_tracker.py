"""
BASED MONEY - Performance Tracker Tests
Test the PerformanceTracker class for agent/theme performance tracking
"""

import sys
import os

# Set up test environment
os.environ['TRADING_MODE'] = 'paper'
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_KEY'] = 'test_key'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.performance_tracker import PerformanceTracker
from datetime import datetime, timedelta


def test_performance_tracker_initialization():
    """Test that PerformanceTracker initializes correctly."""
    print("\n" + "="*60)
    print("TEST: PerformanceTracker Initialization")
    print("="*60)
    
    tracker = PerformanceTracker()
    
    assert tracker.db is not None
    
    print("✅ PASSED: PerformanceTracker initialized")


def test_track_trade_structure():
    """Test that track_trade method has correct structure."""
    print("\n" + "="*60)
    print("TEST: track_trade Method Structure")
    print("="*60)
    
    tracker = PerformanceTracker()
    
    # Verify method exists
    assert hasattr(tracker, 'track_trade')
    assert callable(tracker.track_trade)
    
    # Verify method signature (should accept agent_id, theme, thesis_id, trade_result, pnl)
    import inspect
    sig = inspect.signature(tracker.track_trade)
    params = list(sig.parameters.keys())
    
    assert 'agent_id' in params
    assert 'theme' in params
    assert 'thesis_id' in params
    assert 'trade_result' in params
    assert 'pnl' in params
    
    print("✅ PASSED: track_trade method has correct structure")
    print(f"   Parameters: {params}")


def test_get_agent_stats_structure():
    """Test that get_agent_stats returns correct structure."""
    print("\n" + "="*60)
    print("TEST: get_agent_stats Method Structure")
    print("="*60)
    
    tracker = PerformanceTracker()
    
    # Call with non-existent agent (should return default stats)
    stats = tracker.get_agent_stats("test_agent_123", period='7d')
    
    # Verify structure
    assert isinstance(stats, dict)
    assert 'win_rate' in stats
    assert 'total_pnl' in stats
    assert 'sharpe' in stats
    assert 'trades_count' in stats
    assert 'profit_pct' in stats
    
    # Verify types
    assert isinstance(stats['win_rate'], (int, float))
    assert isinstance(stats['total_pnl'], (int, float))
    assert isinstance(stats['sharpe'], (int, float))
    assert isinstance(stats['trades_count'], int)
    assert isinstance(stats['profit_pct'], (int, float))
    
    print("✅ PASSED: get_agent_stats returns correct structure")
    print(f"   Stats: {stats}")


def test_get_theme_stats_structure():
    """Test that get_theme_stats returns correct structure."""
    print("\n" + "="*60)
    print("TEST: get_theme_stats Method Structure")
    print("="*60)
    
    tracker = PerformanceTracker()
    
    # Call with non-existent theme (should return default stats)
    stats = tracker.get_theme_stats("test_theme", period='7d')
    
    # Verify structure
    assert isinstance(stats, dict)
    assert 'win_rate' in stats
    assert 'total_pnl' in stats
    assert 'trades_count' in stats
    assert 'profit_pct' in stats
    assert 'agent_count' in stats
    
    # Verify types
    assert isinstance(stats['win_rate'], (int, float))
    assert isinstance(stats['total_pnl'], (int, float))
    assert isinstance(stats['trades_count'], int)
    assert isinstance(stats['profit_pct'], (int, float))
    assert isinstance(stats['agent_count'], int)
    
    print("✅ PASSED: get_theme_stats returns correct structure")
    print(f"   Stats: {stats}")


def test_get_leaderboard_structure():
    """Test that get_leaderboard returns correct structure."""
    print("\n" + "="*60)
    print("TEST: get_leaderboard Method Structure")
    print("="*60)
    
    tracker = PerformanceTracker()
    
    # Get leaderboard (may be empty)
    leaderboard = tracker.get_leaderboard(period='7d')
    
    # Verify structure
    assert isinstance(leaderboard, list)
    
    # If there are entries, verify structure
    if leaderboard:
        entry = leaderboard[0]
        assert isinstance(entry, dict)
        assert 'agent_id' in entry
        assert 'theme' in entry
        assert 'win_rate' in entry
        assert 'total_pnl' in entry
        assert 'trades_count' in entry
    
    print("✅ PASSED: get_leaderboard returns correct structure")
    print(f"   Entries: {len(leaderboard)}")


def test_trigger_weekly_reallocation_structure():
    """Test that trigger_weekly_reallocation returns correct structure."""
    print("\n" + "="*60)
    print("TEST: trigger_weekly_reallocation Method Structure")
    print("="*60)
    
    tracker = PerformanceTracker()
    
    # Trigger reallocation (should return dict with winners/losers/probation)
    result = tracker.trigger_weekly_reallocation()
    
    # Verify structure
    assert isinstance(result, dict)
    assert 'winners' in result
    assert 'losers' in result
    assert 'probation' in result
    
    assert isinstance(result['winners'], list)
    assert isinstance(result['losers'], list)
    assert isinstance(result['probation'], list)
    
    print("✅ PASSED: trigger_weekly_reallocation returns correct structure")
    print(f"   Winners: {result['winners']}")
    print(f"   Losers: {result['losers']}")
    print(f"   Probation: {result['probation']}")


def test_performance_calculation_logic():
    """Test performance calculation logic with mock data."""
    print("\n" + "="*60)
    print("TEST: Performance Calculation Logic")
    print("="*60)
    
    tracker = PerformanceTracker()
    
    # Test with empty data (should return defaults)
    stats = tracker.get_agent_stats("nonexistent_agent", period='7d')
    
    assert stats['win_rate'] == 0.0
    assert stats['total_pnl'] == 0.0
    assert stats['trades_count'] == 0
    
    print("✅ PASSED: Performance calculation handles empty data correctly")
    print(f"   Empty stats: {stats}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PERFORMANCE TRACKER TESTS")
    print("="*60)
    
    # Run all tests
    test_performance_tracker_initialization()
    test_track_trade_structure()
    test_get_agent_stats_structure()
    test_get_theme_stats_structure()
    test_get_leaderboard_structure()
    test_trigger_weekly_reallocation_structure()
    test_performance_calculation_logic()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✅")
    print("="*60)
