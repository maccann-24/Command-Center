"""
Simple test for backtesting/metrics.py
Direct import without package dependencies
"""

import sys
import importlib.util
from datetime import date
from dataclasses import dataclass, field
from typing import List, Tuple

# Import metrics.py directly
spec = importlib.util.spec_from_file_location('metrics', 'backtesting/metrics.py')
metrics_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics_module)

# Get exports
PerformanceReport = metrics_module.PerformanceReport
calculate_metrics = metrics_module.calculate_metrics


# Minimal dataclasses for testing
@dataclass
class Trade:
    """Represents a single backtested trade"""
    date: date
    market_id: str
    market_question: str
    side: str
    shares: float
    entry_price: float
    exit_price: float
    pnl: float
    pnl_pct: float
    conviction: float
    thesis_id: str


@dataclass
class BacktestResults:
    """Minimal BacktestResults for testing"""
    start_date: date
    end_date: date
    initial_capital: float
    agent_id: str
    final_capital: float
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[Tuple[date, float]] = field(default_factory=list)


print("\n" + "=" * 60)
print("METRICS MODULE TEST")
print("=" * 60)

# Create test data
results = BacktestResults(
    start_date=date(2024, 1, 1),
    end_date=date(2024, 3, 31),
    initial_capital=1000.0,
    agent_id="TestAgent",
    final_capital=1150.0,
)

# Add trades
results.trades = [
    Trade(
        date=date(2024, 1, 15),
        market_id="m1",
        market_question="Will X?",
        side="YES",
        shares=100.0,
        entry_price=0.40,
        exit_price=1.0,
        pnl=60.0,
        pnl_pct=150.0,
        conviction=0.85,
        thesis_id="t1",
    ),
    Trade(
        date=date(2024, 2, 1),
        market_id="m2",
        market_question="Will Y?",
        side="NO",
        shares=200.0,
        entry_price=0.30,
        exit_price=1.0,
        pnl=140.0,
        pnl_pct=233.3,
        conviction=0.90,
        thesis_id="t2",
    ),
    Trade(
        date=date(2024, 2, 15),
        market_id="m3",
        market_question="Will Z?",
        side="YES",
        shares=150.0,
        entry_price=0.60,
        exit_price=0.0,
        pnl=-90.0,
        pnl_pct=-100.0,
        conviction=0.75,
        thesis_id="t3",
    ),
    Trade(
        date=date(2024, 3, 1),
        market_id="m4",
        market_question="Will W?",
        side="YES",
        shares=80.0,
        entry_price=0.50,
        exit_price=1.0,
        pnl=40.0,
        pnl_pct=100.0,
        conviction=0.80,
        thesis_id="t4",
    ),
]

# Add equity curve
results.equity_curve = [
    (date(2024, 1, 1), 1000.0),
    (date(2024, 1, 15), 1060.0),
    (date(2024, 2, 1), 1200.0),
    (date(2024, 2, 15), 1110.0),  # Drawdown from 1200 to 1110
    (date(2024, 3, 1), 1150.0),
    (date(2024, 3, 31), 1150.0),
]

print("\nCalculating metrics...")
report = calculate_metrics(results)

print("\nRESULTS:")
print(f"  Total Return: {report.total_return:.2f}%")
print(f"  Win Rate: {report.win_rate:.1f}%")
print(f"  Sharpe Ratio: {report.sharpe_ratio:.2f}")
print(f"  Max Drawdown: {report.max_drawdown:.2f}%")
print(f"  Avg Edge Captured: {report.avg_edge_captured:.2%}")
print(f"  Trade Count: {report.trade_count}")
print(f"  Avg Hold Time: {report.avg_hold_time:.1f} days")

print("\nVERIFICATION:")
assert abs(report.total_return - 15.0) < 0.01, f"Expected 15%, got {report.total_return}%"
print("  ✓ Total return: 15%")

assert abs(report.win_rate - 75.0) < 0.1, f"Expected 75%, got {report.win_rate}%"
print("  ✓ Win rate: 75% (3 wins / 4 trades)")

assert report.trade_count == 4, f"Expected 4 trades, got {report.trade_count}"
print("  ✓ Trade count: 4")

expected_dd = ((1200.0 - 1110.0) / 1200.0) * 100.0
assert abs(report.max_drawdown - expected_dd) < 0.1, f"Expected {expected_dd:.2f}%, got {report.max_drawdown:.2f}%"
print(f"  ✓ Max drawdown: {report.max_drawdown:.2f}% (from $1200 to $1110)")

assert report.sharpe_ratio != 0.0, "Sharpe ratio should be non-zero"
print(f"  ✓ Sharpe ratio calculated: {report.sharpe_ratio:.2f}")

assert report.avg_hold_time > 0, "Avg hold time should be positive"
print(f"  ✓ Avg hold time: {report.avg_hold_time:.1f} days")

print("\nFULL SUMMARY:")
print(report.summary)

print("=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
print()
