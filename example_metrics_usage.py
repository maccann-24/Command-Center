"""
Example: Using the Performance Metrics Module

This demonstrates how to use calculate_metrics() with backtest results.
"""

import sys
from datetime import date, timedelta
from dataclasses import dataclass, field
from typing import List, Tuple

# Direct import of metrics (avoids dependency issues)
import importlib.util
spec = importlib.util.spec_from_file_location('metrics', 'backtesting/metrics.py')
metrics_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics_module)

calculate_metrics = metrics_module.calculate_metrics
PerformanceReport = metrics_module.PerformanceReport


# Mock data structures (in real usage, these come from backtesting/engine.py)
@dataclass
class Trade:
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
    start_date: date
    end_date: date
    initial_capital: float
    agent_id: str
    final_capital: float
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[Tuple[date, float]] = field(default_factory=list)


def example_winning_strategy():
    """Example: A winning trading strategy"""
    
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Winning Strategy (High Conviction, Good Edge)")
    print("=" * 70)
    
    results = BacktestResults(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 31),
        initial_capital=1000.0,
        agent_id="GeopoliticalAgent",
        final_capital=1450.0,
    )
    
    # Strong trades with high conviction
    results.trades = [
        Trade(
            date=date(2024, 1, 10),
            market_id="market1",
            market_question="Will Russia-Ukraine peace talks begin by Feb 2024?",
            side="NO",
            shares=200.0,
            entry_price=0.35,
            exit_price=1.0,  # Correct!
            pnl=130.0,
            pnl_pct=185.7,
            conviction=0.90,
            thesis_id="thesis1",
        ),
        Trade(
            date=date(2024, 2, 1),
            market_id="market2",
            market_question="Will China announce stimulus by March?",
            side="YES",
            shares=150.0,
            entry_price=0.45,
            exit_price=1.0,  # Correct!
            pnl=82.5,
            pnl_pct=122.2,
            conviction=0.85,
            thesis_id="thesis2",
        ),
        Trade(
            date=date(2024, 2, 20),
            market_id="market3",
            market_question="Will oil prices exceed $100 by March?",
            side="YES",
            shares=180.0,
            entry_price=0.40,
            exit_price=1.0,  # Correct!
            pnl=108.0,
            pnl_pct=150.0,
            conviction=0.82,
            thesis_id="thesis3",
        ),
        Trade(
            date=date(2024, 3, 15),
            market_id="market4",
            market_question="Will NATO expand by April?",
            side="NO",
            shares=100.0,
            entry_price=0.30,
            exit_price=1.0,  # Correct!
            pnl=70.0,
            pnl_pct=233.3,
            conviction=0.95,
            thesis_id="thesis4",
        ),
    ]
    
    # Smooth equity curve (steady growth)
    results.equity_curve = [
        (date(2024, 1, 1), 1000.0),
        (date(2024, 1, 10), 1130.0),
        (date(2024, 2, 1), 1212.5),
        (date(2024, 2, 20), 1320.5),
        (date(2024, 3, 15), 1450.0),
    ]
    
    # Calculate metrics
    report = calculate_metrics(results)
    
    print(report.summary)
    
    print("\nINSIGHTS:")
    print(f"  → {report.win_rate:.0f}% win rate with high conviction trades")
    print(f"  → Sharpe ratio of {report.sharpe_ratio:.2f} shows excellent risk-adjusted returns")
    print(f"  → Max drawdown of {report.max_drawdown:.1f}% indicates low risk")
    print(f"  → Edge captured: {report.avg_edge_captured:.0f}% (outperforming expectations)")


def example_volatile_strategy():
    """Example: High returns but volatile (big wins, big losses)"""
    
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Volatile Strategy (High Risk, High Reward)")
    print("=" * 70)
    
    results = BacktestResults(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 31),
        initial_capital=1000.0,
        agent_id="AggressiveTrader",
        final_capital=1400.0,
    )
    
    # Mix of huge wins and big losses
    results.trades = [
        Trade(
            date=date(2024, 1, 5),
            market_id="m1",
            market_question="Moonshot bet #1",
            side="YES",
            shares=500.0,
            entry_price=0.10,
            exit_price=1.0,
            pnl=450.0,
            pnl_pct=900.0,  # 10x!
            conviction=0.60,
            thesis_id="t1",
        ),
        Trade(
            date=date(2024, 1, 20),
            market_id="m2",
            market_question="High risk bet",
            side="YES",
            shares=300.0,
            entry_price=0.70,
            exit_price=0.0,
            pnl=-210.0,
            pnl_pct=-100.0,
            conviction=0.75,
            thesis_id="t2",
        ),
        Trade(
            date=date(2024, 2, 10),
            market_id="m3",
            market_question="Another moonshot",
            side="YES",
            shares=400.0,
            entry_price=0.15,
            exit_price=1.0,
            pnl=340.0,
            pnl_pct=566.7,
            conviction=0.65,
            thesis_id="t3",
        ),
        Trade(
            date=date(2024, 3, 1),
            market_id="m4",
            market_question="Big loss",
            side="NO",
            shares=200.0,
            entry_price=0.60,
            exit_price=0.0,
            pnl=-120.0,
            pnl_pct=-100.0,
            conviction=0.70,
            thesis_id="t4",
        ),
    ]
    
    # Volatile equity curve
    results.equity_curve = [
        (date(2024, 1, 1), 1000.0),
        (date(2024, 1, 5), 1450.0),   # Big win
        (date(2024, 1, 20), 1240.0),  # Big loss
        (date(2024, 2, 10), 1580.0),  # Big win
        (date(2024, 3, 1), 1400.0),   # Loss
    ]
    
    report = calculate_metrics(results)
    
    print(report.summary)
    
    print("\nINSIGHTS:")
    print(f"  → Only {report.win_rate:.0f}% win rate (inconsistent)")
    print(f"  → Sharpe ratio of {report.sharpe_ratio:.2f} reflects high volatility")
    drawdown_pct = ((1580.0 - 1240.0) / 1580.0) * 100
    print(f"  → Max drawdown shows wild swings in equity")
    print(f"  → High returns but HIGH RISK profile")


def example_losing_strategy():
    """Example: A losing strategy"""
    
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Losing Strategy (Poor Edge Detection)")
    print("=" * 70)
    
    results = BacktestResults(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 2, 28),
        initial_capital=1000.0,
        agent_id="BadAgent",
        final_capital=700.0,
    )
    
    # Mostly losing trades
    results.trades = [
        Trade(
            date=date(2024, 1, 10),
            market_id="m1",
            market_question="Bad call #1",
            side="YES",
            shares=200.0,
            entry_price=0.60,
            exit_price=0.0,
            pnl=-120.0,
            pnl_pct=-100.0,
            conviction=0.80,
            thesis_id="t1",
        ),
        Trade(
            date=date(2024, 1, 20),
            market_id="m2",
            market_question="Bad call #2",
            side="NO",
            shares=150.0,
            entry_price=0.50,
            exit_price=0.0,
            pnl=-75.0,
            pnl_pct=-100.0,
            conviction=0.75,
            thesis_id="t2",
        ),
        Trade(
            date=date(2024, 2, 1),
            market_id="m3",
            market_question="Small win",
            side="YES",
            shares=100.0,
            entry_price=0.40,
            exit_price=1.0,
            pnl=60.0,
            pnl_pct=150.0,
            conviction=0.85,
            thesis_id="t3",
        ),
        Trade(
            date=date(2024, 2, 15),
            market_id="m4",
            market_question="Another loss",
            side="YES",
            shares=180.0,
            entry_price=0.70,
            exit_price=0.0,
            pnl=-126.0,
            pnl_pct=-100.0,
            conviction=0.78,
            thesis_id="t4",
        ),
    ]
    
    # Declining equity curve
    results.equity_curve = [
        (date(2024, 1, 1), 1000.0),
        (date(2024, 1, 10), 880.0),
        (date(2024, 1, 20), 805.0),
        (date(2024, 2, 1), 865.0),
        (date(2024, 2, 15), 700.0),
    ]
    
    report = calculate_metrics(results)
    
    print(report.summary)
    
    print("\nINSIGHTS:")
    print(f"  ⚠️  Only {report.win_rate:.0f}% win rate - need better edge detection")
    print(f"  ⚠️  Negative Sharpe ratio indicates poor risk management")
    print(f"  ⚠️  {report.max_drawdown:.1f}% max drawdown - too much risk")
    print(f"  ⚠️  Strategy needs major revision")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PERFORMANCE METRICS USAGE EXAMPLES")
    print("=" * 70)
    
    # Run examples
    example_winning_strategy()
    example_volatile_strategy()
    example_losing_strategy()
    
    print("\n" + "=" * 70)
    print("END OF EXAMPLES")
    print("=" * 70)
    print("\nUse these patterns to analyze your own backtest results!")
    print()
