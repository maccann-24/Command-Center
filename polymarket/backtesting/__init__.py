"""
BASED MONEY - Backtesting Module
Historical data collection and simulation
"""

from .data_loader import fetch_historical_markets, get_loaded_count
from .engine import BacktestEngine, BacktestResults, Trade, run_simple_backtest
from .metrics import calculate_metrics, PerformanceReport
from .validator import (
    validate_strategy,
    ValidationResult,
    VALIDATION_THRESHOLDS,
    is_strategy_approved,
    get_validation_summary,
)

__all__ = [
    "fetch_historical_markets",
    "get_loaded_count",
    "BacktestEngine",
    "BacktestResults",
    "Trade",
    "run_simple_backtest",
    "calculate_metrics",
    "PerformanceReport",
    "validate_strategy",
    "ValidationResult",
    "VALIDATION_THRESHOLDS",
    "is_strategy_approved",
    "get_validation_summary",
]
