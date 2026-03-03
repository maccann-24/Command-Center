"""
Test backtesting/metrics.py module
"""

from datetime import date, timedelta
from backtesting.engine import BacktestResults, Trade
from backtesting.metrics import calculate_metrics, PerformanceReport


def test_metrics_basic():
    """Test basic metrics calculation"""
    
    print("\n" + "=" * 60)
    print("TEST: Basic Metrics Calculation")
    print("=" * 60)
    
    # Create mock backtest results
    start_date = date(2024, 1, 1)
    end_date = date(2024, 3, 31)
    initial_capital = 1000.0
    
    results = BacktestResults(
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        agent_id="TestAgent",
        final_capital=1150.0,
        total_pnl=150.0,
        total_pnl_pct=15.0,
    )
    
    # Add mock trades
    results.trades = [
        Trade(
            date=date(2024, 1, 15),
            market_id="market1",
            market_question="Will X happen?",
            side="YES",
            shares=100.0,
            entry_price=0.40,
            exit_price=1.0,
            pnl=60.0,
            pnl_pct=150.0,
            conviction=0.85,
            thesis_id="thesis1",
        ),
        Trade(
            date=date(2024, 2, 1),
            market_id="market2",
            market_question="Will Y happen?",
            side="NO",
            shares=200.0,
            entry_price=0.30,
            exit_price=1.0,
            pnl=140.0,
            pnl_pct=233.3,
            conviction=0.90,
            thesis_id="thesis2",
        ),
        Trade(
            date=date(2024, 2, 15),
            market_id="market3",
            market_question="Will Z happen?",
            side="YES",
            shares=150.0,
            entry_price=0.60,
            exit_price=0.0,
            pnl=-90.0,
            pnl_pct=-100.0,
            conviction=0.75,
            thesis_id="thesis3",
        ),
        Trade(
            date=date(2024, 3, 1),
            market_id="market4",
            market_question="Will W happen?",
            side="YES",
            shares=80.0,
            entry_price=0.50,
            exit_price=1.0,
            pnl=40.0,
            pnl_pct=100.0,
            conviction=0.80,
            thesis_id="thesis4",
        ),
    ]
    
    # Add equity curve
    results.equity_curve = [
        (date(2024, 1, 1), 1000.0),
        (date(2024, 1, 15), 1060.0),
        (date(2024, 2, 1), 1200.0),
        (date(2024, 2, 15), 1110.0),  # Drawdown
        (date(2024, 3, 1), 1150.0),
        (date(2024, 3, 31), 1150.0),
    ]
    
    # Calculate metrics
    print("\nCalculating metrics...")
    report = calculate_metrics(results)
    
    # Verify metrics
    print(f"\n✓ Total Return: {report.total_return:.2f}%")
    assert abs(report.total_return - 15.0) < 0.01, "Total return mismatch"
    
    print(f"✓ Win Rate: {report.win_rate:.1f}%")
    assert abs(report.win_rate - 75.0) < 0.1, "Win rate mismatch"
    
    print(f"✓ Trade Count: {report.trade_count}")
    assert report.trade_count == 4, "Trade count mismatch"
    
    print(f"✓ Sharpe Ratio: {report.sharpe_ratio:.2f}")
    assert report.sharpe_ratio != 0.0, "Sharpe ratio should be calculated"
    
    print(f"✓ Max Drawdown: {report.max_drawdown:.2f}%")
    assert report.max_drawdown > 0, "Max drawdown should be positive"
    
    print(f"✓ Avg Edge Captured: {report.avg_edge_captured:.2%}")
    # Edge captured can be any value (positive/negative)
    
    print(f"✓ Avg Hold Time: {report.avg_hold_time:.1f} days")
    assert report.avg_hold_time > 0, "Avg hold time should be positive"
    
    # Print full summary
    print(report.summary)
    
    print("\n✅ All basic metrics tests passed!")
    
    return report


def test_metrics_edge_cases():
    """Test edge cases (no trades, single trade, etc.)"""
    
    print("\n" + "=" * 60)
    print("TEST: Edge Cases")
    print("=" * 60)
    
    # Test: No trades
    print("\n1. Testing with no trades...")
    results_empty = BacktestResults(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        initial_capital=1000.0,
        agent_id="EmptyAgent",
        final_capital=1000.0,
    )
    
    report_empty = calculate_metrics(results_empty)
    print(f"   Total Return: {report_empty.total_return:.2f}%")
    print(f"   Win Rate: {report_empty.win_rate:.1f}%")
    print(f"   Trade Count: {report_empty.trade_count}")
    
    assert report_empty.total_return == 0.0, "Should have 0% return with no trades"
    assert report_empty.win_rate == 0.0, "Should have 0% win rate with no trades"
    assert report_empty.trade_count == 0, "Should have 0 trades"
    print("   ✓ No trades case handled correctly")
    
    # Test: Single winning trade
    print("\n2. Testing with single winning trade...")
    results_single = BacktestResults(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        initial_capital=1000.0,
        agent_id="SingleAgent",
        final_capital=1100.0,
    )
    
    results_single.trades = [
        Trade(
            date=date(2024, 1, 15),
            market_id="market1",
            market_question="Single trade",
            side="YES",
            shares=200.0,
            entry_price=0.50,
            exit_price=1.0,
            pnl=100.0,
            pnl_pct=100.0,
            conviction=0.90,
            thesis_id="thesis1",
        )
    ]
    
    results_single.equity_curve = [
        (date(2024, 1, 1), 1000.0),
        (date(2024, 1, 15), 1100.0),
        (date(2024, 1, 31), 1100.0),
    ]
    
    report_single = calculate_metrics(results_single)
    print(f"   Total Return: {report_single.total_return:.2f}%")
    print(f"   Win Rate: {report_single.win_rate:.1f}%")
    print(f"   Trade Count: {report_single.trade_count}")
    
    assert report_single.win_rate == 100.0, "Should have 100% win rate"
    assert report_single.trade_count == 1, "Should have 1 trade"
    print("   ✓ Single trade case handled correctly")
    
    # Test: All losing trades
    print("\n3. Testing with all losing trades...")
    results_losses = BacktestResults(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        initial_capital=1000.0,
        agent_id="LossAgent",
        final_capital=700.0,
    )
    
    results_losses.trades = [
        Trade(
            date=date(2024, 1, 10),
            market_id="market1",
            market_question="Loss 1",
            side="YES",
            shares=100.0,
            entry_price=0.50,
            exit_price=0.0,
            pnl=-50.0,
            pnl_pct=-100.0,
            conviction=0.80,
            thesis_id="thesis1",
        ),
        Trade(
            date=date(2024, 1, 20),
            market_id="market2",
            market_question="Loss 2",
            side="NO",
            shares=200.0,
            entry_price=0.40,
            exit_price=0.0,
            pnl=-80.0,
            pnl_pct=-100.0,
            conviction=0.75,
            thesis_id="thesis2",
        ),
    ]
    
    results_losses.equity_curve = [
        (date(2024, 1, 1), 1000.0),
        (date(2024, 1, 10), 950.0),
        (date(2024, 1, 20), 870.0),
        (date(2024, 1, 31), 700.0),
    ]
    
    report_losses = calculate_metrics(results_losses)
    print(f"   Total Return: {report_losses.total_return:.2f}%")
    print(f"   Win Rate: {report_losses.win_rate:.1f}%")
    print(f"   Trade Count: {report_losses.trade_count}")
    
    assert report_losses.total_return < 0, "Should have negative return"
    assert report_losses.win_rate == 0.0, "Should have 0% win rate"
    print("   ✓ All losses case handled correctly")
    
    print("\n✅ All edge case tests passed!")


def test_performance_report_output():
    """Test PerformanceReport formatting"""
    
    print("\n" + "=" * 60)
    print("TEST: Performance Report Output")
    print("=" * 60)
    
    # Create a report directly
    report = PerformanceReport(
        total_return=25.5,
        win_rate=65.0,
        sharpe_ratio=1.8,
        max_drawdown=12.3,
        avg_edge_captured=0.85,
        trade_count=20,
        avg_hold_time=7.5,
        summary="Test summary",
    )
    
    print("\nDirect report creation:")
    print(f"  Total Return: {report.total_return}%")
    print(f"  Win Rate: {report.win_rate}%")
    print(f"  Sharpe: {report.sharpe_ratio}")
    print(f"  Max DD: {report.max_drawdown}%")
    print(f"  Edge: {report.avg_edge_captured}")
    print(f"  Trades: {report.trade_count}")
    print(f"  Hold Time: {report.avg_hold_time} days")
    
    # Test __str__ method
    print(f"\nString representation:\n{report}")
    
    print("\n✅ Performance report output test passed!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BACKTESTING METRICS TEST SUITE")
    print("=" * 60)
    
    try:
        # Run tests
        test_metrics_basic()
        test_metrics_edge_cases()
        test_performance_report_output()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print()
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
