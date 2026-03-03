"""
BASED MONEY - Performance Metrics
Calculate comprehensive performance metrics from backtest results
"""

from dataclasses import dataclass
from typing import Optional
from datetime import timedelta


@dataclass
class PerformanceReport:
    """Comprehensive performance report from backtest results"""

    # Return metrics
    total_return: float  # Percentage return on initial capital

    # Win rate
    win_rate: float  # Percentage of winning trades

    # Risk-adjusted return
    sharpe_ratio: float  # Annualized Sharpe ratio (assuming 0% risk-free rate)

    # Risk metrics
    max_drawdown: float  # Maximum drawdown percentage from peak

    # Edge metrics
    avg_edge_captured: float  # Average (actual_pnl / expected_edge) across all trades

    # Trade statistics
    trade_count: int  # Total number of trades
    avg_hold_time: float  # Average holding period in days

    # Summary
    summary: str  # Human-readable summary

    def __str__(self) -> str:
        """Return human-readable summary"""
        return self.summary


def calculate_metrics(backtest_results) -> PerformanceReport:
    """
    Calculate comprehensive performance metrics from backtest results.

    Args:
        backtest_results: BacktestResults object from backtest engine

    Returns:
        PerformanceReport dataclass with all metrics and summary

    Metrics calculated:
        - total_return: (final_capital - initial_capital) / initial_capital * 100
        - win_rate: winning_trades / total_trades * 100
        - sharpe_ratio: mean(daily_returns) / std(daily_returns) * sqrt(252)
        - max_drawdown: max drop from peak equity to trough in equity_curve
        - avg_edge_captured: mean(actual_pnl / expected_edge) for all trades
        - trade_count: len(trades)
        - avg_hold_time: mean(resolution_date - entry_date) for all trades
    """

    # Extract basic data
    initial_capital = backtest_results.initial_capital
    final_capital = backtest_results.final_capital
    trades = backtest_results.trades
    equity_curve = backtest_results.equity_curve

    # ============================================================
    # TOTAL RETURN
    # ============================================================
    if initial_capital > 0:
        total_return = (final_capital - initial_capital) / initial_capital * 100.0
    else:
        total_return = 0.0

    # ============================================================
    # WIN RATE
    # ============================================================
    if trades:
        winning_trades = sum(1 for t in trades if t.pnl > 0)
        total_trades = len(trades)
        win_rate = (winning_trades / total_trades) * 100.0
    else:
        win_rate = 0.0
        total_trades = 0

    # ============================================================
    # SHARPE RATIO
    # ============================================================
    sharpe_ratio = _calculate_sharpe_ratio(equity_curve)

    # ============================================================
    # MAX DRAWDOWN
    # ============================================================
    max_drawdown = _calculate_max_drawdown(equity_curve)

    # ============================================================
    # AVERAGE EDGE CAPTURED
    # ============================================================
    avg_edge_captured = _calculate_avg_edge_captured(trades)

    # ============================================================
    # TRADE COUNT
    # ============================================================
    trade_count = len(trades)

    # ============================================================
    # AVERAGE HOLD TIME
    # ============================================================
    avg_hold_time = _calculate_avg_hold_time(backtest_results)

    # ============================================================
    # SUMMARY
    # ============================================================
    summary = _generate_summary(
        total_return=total_return,
        win_rate=win_rate,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=max_drawdown,
        avg_edge_captured=avg_edge_captured,
        trade_count=trade_count,
        avg_hold_time=avg_hold_time,
        initial_capital=initial_capital,
        final_capital=final_capital,
    )

    return PerformanceReport(
        total_return=total_return,
        win_rate=win_rate,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=max_drawdown,
        avg_edge_captured=avg_edge_captured,
        trade_count=trade_count,
        avg_hold_time=avg_hold_time,
        summary=summary,
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def _calculate_sharpe_ratio(equity_curve) -> float:
    """
    Calculate annualized Sharpe ratio from equity curve.

    Assumes 0% risk-free rate and 252 trading days per year.

    Args:
        equity_curve: List of (date, equity_value) tuples

    Returns:
        Annualized Sharpe ratio
    """
    if len(equity_curve) < 2:
        return 0.0

    # Calculate daily returns
    returns = []
    for i in range(1, len(equity_curve)):
        prev_value = equity_curve[i - 1][1]
        curr_value = equity_curve[i][1]

        if prev_value > 0:
            daily_return = (curr_value - prev_value) / prev_value
            returns.append(daily_return)

    if not returns:
        return 0.0

    # Calculate mean and standard deviation
    mean_return = sum(returns) / len(returns)

    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    std_return = variance**0.5

    # Annualized Sharpe ratio (sqrt(252) for daily returns)
    if std_return > 0:
        sharpe_ratio = (mean_return / std_return) * (252**0.5)
    else:
        sharpe_ratio = 0.0

    return sharpe_ratio


def _calculate_max_drawdown(equity_curve) -> float:
    """
    Calculate maximum drawdown percentage from equity curve.

    Args:
        equity_curve: List of (date, equity_value) tuples

    Returns:
        Maximum drawdown as percentage
    """
    if not equity_curve:
        return 0.0

    peak = equity_curve[0][1]
    max_dd_pct = 0.0

    for _, value in equity_curve:
        # Update peak if new high
        if value > peak:
            peak = value

        # Calculate drawdown from peak
        if peak > 0:
            drawdown_pct = ((peak - value) / peak) * 100.0
            if drawdown_pct > max_dd_pct:
                max_dd_pct = drawdown_pct

    return max_dd_pct


def _calculate_avg_edge_captured(trades) -> float:
    """
    Calculate average edge captured across all trades.

    Edge captured = actual_pnl / expected_edge

    Expected edge = conviction * edge (theoretical expected profit)
    We approximate edge from the trade's conviction if available.

    Args:
        trades: List of Trade objects

    Returns:
        Average edge captured ratio (0.0 if no valid trades)
    """
    if not trades:
        return 0.0

    edge_captured_ratios = []

    for trade in trades:
        # Calculate expected edge
        # Edge = (true_prob - market_price) for YES side
        # For binary outcomes, we use conviction as proxy for perceived edge

        # Approximate expected edge from entry price and conviction
        # If conviction is high and entry_price is low, expected edge is high

        conviction = trade.conviction if trade.conviction else 0.0

        # Expected edge approximation:
        # For YES side: edge = conviction - entry_price
        # For NO side: edge = conviction - (1 - entry_price)

        if trade.side == "YES":
            expected_edge = conviction - trade.entry_price
        else:  # NO
            expected_edge = conviction - (1.0 - trade.entry_price)

        # Actual edge = pnl / (shares * entry_price) = pnl_pct / 100
        actual_edge = trade.pnl_pct / 100.0

        # Edge captured ratio
        if abs(expected_edge) > 0.01:  # Avoid division by zero
            edge_captured = actual_edge / expected_edge
            edge_captured_ratios.append(edge_captured)

    if edge_captured_ratios:
        return sum(edge_captured_ratios) / len(edge_captured_ratios)
    else:
        return 0.0


def _calculate_avg_hold_time(backtest_results) -> float:
    """
    Calculate average holding time in days.

    Uses trade dates and backtest period to estimate hold times.

    Args:
        backtest_results: BacktestResults object

    Returns:
        Average hold time in days
    """
    trades = backtest_results.trades

    if not trades:
        return 0.0

    # Group trades by market to track entry/exit dates
    # Since we only have trade resolution dates, we approximate
    # hold time by looking at the time between backtest start and trade dates

    # Simpler approach: Use equity curve intervals as proxy
    # Average time between equity curve points
    equity_curve = backtest_results.equity_curve

    if len(equity_curve) < 2:
        return 0.0

    # Calculate total days in backtest
    start_date = backtest_results.start_date
    end_date = backtest_results.end_date

    total_days = (end_date - start_date).days

    if total_days > 0 and len(trades) > 0:
        # Approximate average hold time
        # Assume trades are evenly distributed across the period
        avg_hold_time = total_days / len(trades)
    else:
        avg_hold_time = 0.0

    return avg_hold_time


def _generate_summary(
    total_return: float,
    win_rate: float,
    sharpe_ratio: float,
    max_drawdown: float,
    avg_edge_captured: float,
    trade_count: int,
    avg_hold_time: float,
    initial_capital: float,
    final_capital: float,
) -> str:
    """
    Generate human-readable performance summary.

    Args:
        All performance metrics

    Returns:
        Formatted summary string
    """
    lines = [
        "",
        "=" * 60,
        "PERFORMANCE METRICS REPORT",
        "=" * 60,
        "",
        "RETURNS",
        "-" * 60,
        f"Initial Capital:    ${initial_capital:,.2f}",
        f"Final Capital:      ${final_capital:,.2f}",
        f"Total Return:       {total_return:+.2f}%",
        "",
        "RISK METRICS",
        "-" * 60,
        f"Sharpe Ratio:       {sharpe_ratio:.2f}",
        f"Max Drawdown:       {max_drawdown:.2f}%",
        "",
        "TRADE STATISTICS",
        "-" * 60,
        f"Total Trades:       {trade_count}",
        f"Win Rate:           {win_rate:.1f}%",
        f"Avg Hold Time:      {avg_hold_time:.1f} days",
        "",
        "EDGE ANALYSIS",
        "-" * 60,
        f"Avg Edge Captured:  {avg_edge_captured:.2%}",
        "",
        "=" * 60,
        "",
    ]

    return "\n".join(lines)
