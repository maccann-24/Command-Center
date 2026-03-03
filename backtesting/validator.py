"""
BASED MONEY - Strategy Validator
Validation gate to ensure strategies meet minimum quality thresholds before deployment
"""

from dataclasses import dataclass
from typing import List, Optional


# ============================================================
# VALIDATION THRESHOLDS
# ============================================================

VALIDATION_THRESHOLDS = {
    'min_win_rate': 52.0,           # Must beat coin flip (50%)
    'min_sharpe': 0.5,              # Decent risk-adjusted return
    'max_drawdown_allowed': 40.0,   # Maximum survivable drawdown
    'min_trades': 20,               # Statistically meaningful sample size
    'min_return': 0.0,              # Must be profitable overall
}


# ============================================================
# VALIDATION RESULT
# ============================================================

@dataclass
class ValidationResult:
    """Result of strategy validation"""
    approved: bool
    message: str
    metrics: object  # PerformanceReport
    failures: List[str] = None
    recommendations: List[str] = None
    
    def __str__(self) -> str:
        """Human-readable validation result"""
        return self.message


# ============================================================
# VALIDATION FUNCTION
# ============================================================

def validate_strategy(performance_report, thresholds: dict = None) -> ValidationResult:
    """
    Validate a trading strategy against quality thresholds.
    
    Args:
        performance_report: PerformanceReport from calculate_metrics()
        thresholds: Optional custom thresholds (uses VALIDATION_THRESHOLDS if None)
    
    Returns:
        ValidationResult with approval status, message, and recommendations
    
    Validation Checks:
        - Win rate > 52% (must beat coin flip)
        - Sharpe ratio > 0.5 (decent risk-adjusted returns)
        - Max drawdown < 40% (survivable)
        - Trade count >= 20 (statistically meaningful)
        - Total return > 0% (profitable)
    """
    
    # Use default thresholds if none provided
    if thresholds is None:
        thresholds = VALIDATION_THRESHOLDS
    
    # Extract metrics from report
    win_rate = performance_report.win_rate
    sharpe_ratio = performance_report.sharpe_ratio
    max_drawdown = performance_report.max_drawdown
    trade_count = performance_report.trade_count
    total_return = performance_report.total_return
    
    # Collect failures
    failures = []
    
    # Check each threshold
    if win_rate < thresholds['min_win_rate']:
        failures.append(f"Win rate {win_rate:.1f}% < {thresholds['min_win_rate']:.1f}%")
    
    if sharpe_ratio < thresholds['min_sharpe']:
        failures.append(f"Sharpe ratio {sharpe_ratio:.2f} < {thresholds['min_sharpe']:.2f}")
    
    if max_drawdown > thresholds['max_drawdown_allowed']:
        failures.append(f"Max drawdown {max_drawdown:.1f}% > {thresholds['max_drawdown_allowed']:.1f}%")
    
    if trade_count < thresholds['min_trades']:
        failures.append(f"Trade count {trade_count} < {thresholds['min_trades']}")
    
    if total_return < thresholds['min_return']:
        failures.append(f"Total return {total_return:.2f}% < {thresholds['min_return']:.2f}%")
    
    # Generate recommendations based on failures
    recommendations = _generate_recommendations(
        win_rate=win_rate,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=max_drawdown,
        trade_count=trade_count,
        total_return=total_return,
        thresholds=thresholds,
    )
    
    # Determine approval and message
    if not failures:
        # APPROVED
        message = (
            f"✅ Strategy validated! "
            f"Win rate: {win_rate:.1f}%, "
            f"Sharpe: {sharpe_ratio:.2f}, "
            f"Max DD: {max_drawdown:.1f}%, "
            f"Trades: {trade_count}, "
            f"Return: {total_return:+.1f}%"
        )
        
        return ValidationResult(
            approved=True,
            message=message,
            metrics=performance_report,
            failures=[],
            recommendations=[],
        )
    
    else:
        # FAILED
        failure_summary = "; ".join(failures)
        recommendation_summary = "; ".join(recommendations) if recommendations else "Review strategy logic"
        
        message = (
            f"❌ FAILED validation: {failure_summary}. "
            f"Recommendations: {recommendation_summary}"
        )
        
        return ValidationResult(
            approved=False,
            message=message,
            metrics=performance_report,
            failures=failures,
            recommendations=recommendations,
        )


# ============================================================
# RECOMMENDATION LOGIC
# ============================================================

def _generate_recommendations(
    win_rate: float,
    sharpe_ratio: float,
    max_drawdown: float,
    trade_count: int,
    total_return: float,
    thresholds: dict,
) -> List[str]:
    """
    Generate actionable recommendations based on which thresholds failed.
    
    Args:
        All performance metrics and thresholds
    
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # Win rate too low
    if win_rate < thresholds['min_win_rate']:
        recommendations.append("Improve signal quality (better edge detection)")
    
    # Sharpe ratio too low
    if sharpe_ratio < thresholds['min_sharpe']:
        recommendations.append("Reduce position sizes (lower volatility)")
    
    # Drawdown too high
    if max_drawdown > thresholds['max_drawdown_allowed']:
        recommendations.append("Add stop losses or reduce position concentration")
    
    # Not enough trades
    if trade_count < thresholds['min_trades']:
        recommendations.append("Expand market coverage (more opportunities)")
    
    # Negative returns
    if total_return < thresholds['min_return']:
        recommendations.append("Fundamental strategy revision needed")
    
    return recommendations


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def is_strategy_approved(performance_report, thresholds: dict = None) -> bool:
    """
    Quick check if strategy passes validation.
    
    Args:
        performance_report: PerformanceReport from calculate_metrics()
        thresholds: Optional custom thresholds
    
    Returns:
        True if strategy is approved, False otherwise
    """
    result = validate_strategy(performance_report, thresholds)
    return result.approved


def get_validation_summary(performance_report, thresholds: dict = None) -> str:
    """
    Get human-readable validation summary.
    
    Args:
        performance_report: PerformanceReport from calculate_metrics()
        thresholds: Optional custom thresholds
    
    Returns:
        Formatted validation summary string
    """
    result = validate_strategy(performance_report, thresholds)
    
    lines = [
        "",
        "=" * 60,
        "STRATEGY VALIDATION",
        "=" * 60,
        "",
        f"Status: {'✅ APPROVED' if result.approved else '❌ FAILED'}",
        "",
    ]
    
    if result.approved:
        lines.extend([
            "PASSED ALL THRESHOLDS",
            "-" * 60,
            f"Win Rate:      {performance_report.win_rate:.1f}% (≥{thresholds['min_win_rate'] if thresholds else VALIDATION_THRESHOLDS['min_win_rate']:.1f}%)",
            f"Sharpe Ratio:  {performance_report.sharpe_ratio:.2f} (≥{thresholds['min_sharpe'] if thresholds else VALIDATION_THRESHOLDS['min_sharpe']:.2f})",
            f"Max Drawdown:  {performance_report.max_drawdown:.1f}% (≤{thresholds['max_drawdown_allowed'] if thresholds else VALIDATION_THRESHOLDS['max_drawdown_allowed']:.1f}%)",
            f"Trade Count:   {performance_report.trade_count} (≥{thresholds['min_trades'] if thresholds else VALIDATION_THRESHOLDS['min_trades']})",
            f"Total Return:  {performance_report.total_return:+.1f}% (≥{thresholds['min_return'] if thresholds else VALIDATION_THRESHOLDS['min_return']:.1f}%)",
            "",
            "✅ Strategy meets all minimum requirements for deployment.",
        ])
    else:
        lines.extend([
            "FAILED CHECKS",
            "-" * 60,
        ])
        
        for failure in result.failures:
            lines.append(f"  ❌ {failure}")
        
        lines.extend([
            "",
            "RECOMMENDATIONS",
            "-" * 60,
        ])
        
        for i, rec in enumerate(result.recommendations, 1):
            lines.append(f"  {i}. {rec}")
        
        lines.append("")
        lines.append("⚠️  Strategy requires improvement before deployment.")
    
    lines.extend([
        "",
        "=" * 60,
        "",
    ])
    
    return "\n".join(lines)
