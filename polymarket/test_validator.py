"""
Test backtesting/validator.py module
"""

import sys
import importlib.util
from dataclasses import dataclass

# Import validator directly
spec = importlib.util.spec_from_file_location("validator", "backtesting/validator.py")
validator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator_module)

validate_strategy = validator_module.validate_strategy
ValidationResult = validator_module.ValidationResult
VALIDATION_THRESHOLDS = validator_module.VALIDATION_THRESHOLDS
is_strategy_approved = validator_module.is_strategy_approved
get_validation_summary = validator_module.get_validation_summary


# Mock PerformanceReport
@dataclass
class PerformanceReport:
    total_return: float
    win_rate: float
    sharpe_ratio: float
    max_drawdown: float
    avg_edge_captured: float
    trade_count: int
    avg_hold_time: float
    summary: str


def test_passing_strategy():
    """Test a strategy that passes all thresholds"""

    print("\n" + "=" * 60)
    print("TEST 1: Passing Strategy")
    print("=" * 60)

    # Create excellent metrics
    report = PerformanceReport(
        total_return=25.0,
        win_rate=65.0,
        sharpe_ratio=1.5,
        max_drawdown=15.0,
        avg_edge_captured=0.85,
        trade_count=50,
        avg_hold_time=7.0,
        summary="Good strategy",
    )

    result = validate_strategy(report)

    print(f"\nResult: {result.message}")
    print(f"Approved: {result.approved}")
    print(f"Failures: {result.failures}")
    print(f"Recommendations: {result.recommendations}")

    assert result.approved == True, "Should be approved"
    assert len(result.failures) == 0, "Should have no failures"
    print("\n✅ PASSED: Good strategy validated")


def test_failing_win_rate():
    """Test a strategy with low win rate"""

    print("\n" + "=" * 60)
    print("TEST 2: Low Win Rate")
    print("=" * 60)

    report = PerformanceReport(
        total_return=10.0,
        win_rate=45.0,  # Below 52%
        sharpe_ratio=1.2,
        max_drawdown=20.0,
        avg_edge_captured=0.70,
        trade_count=30,
        avg_hold_time=8.0,
        summary="Low win rate",
    )

    result = validate_strategy(report)

    print(f"\nResult: {result.message}")
    print(f"Approved: {result.approved}")
    print(f"Failures: {result.failures}")
    print(f"Recommendations: {result.recommendations}")

    assert result.approved == False, "Should be rejected"
    assert any("Win rate" in f for f in result.failures), "Should flag win rate"
    assert any(
        "signal quality" in r.lower() for r in result.recommendations
    ), "Should recommend signal improvement"
    print("\n✅ PASSED: Low win rate correctly flagged")


def test_failing_sharpe():
    """Test a strategy with low Sharpe ratio"""

    print("\n" + "=" * 60)
    print("TEST 3: Low Sharpe Ratio")
    print("=" * 60)

    report = PerformanceReport(
        total_return=15.0,
        win_rate=60.0,
        sharpe_ratio=0.3,  # Below 0.5
        max_drawdown=25.0,
        avg_edge_captured=0.75,
        trade_count=40,
        avg_hold_time=6.0,
        summary="Low Sharpe",
    )

    result = validate_strategy(report)

    print(f"\nResult: {result.message}")
    print(f"Approved: {result.approved}")
    print(f"Failures: {result.failures}")
    print(f"Recommendations: {result.recommendations}")

    assert result.approved == False, "Should be rejected"
    assert any("Sharpe" in f for f in result.failures), "Should flag Sharpe ratio"
    assert any(
        "position sizes" in r.lower() for r in result.recommendations
    ), "Should recommend smaller positions"
    print("\n✅ PASSED: Low Sharpe correctly flagged")


def test_failing_drawdown():
    """Test a strategy with excessive drawdown"""

    print("\n" + "=" * 60)
    print("TEST 4: Excessive Drawdown")
    print("=" * 60)

    report = PerformanceReport(
        total_return=20.0,
        win_rate=58.0,
        sharpe_ratio=0.8,
        max_drawdown=45.0,  # Above 40%
        avg_edge_captured=0.80,
        trade_count=35,
        avg_hold_time=9.0,
        summary="High drawdown",
    )

    result = validate_strategy(report)

    print(f"\nResult: {result.message}")
    print(f"Approved: {result.approved}")
    print(f"Failures: {result.failures}")
    print(f"Recommendations: {result.recommendations}")

    assert result.approved == False, "Should be rejected"
    assert any("drawdown" in f.lower() for f in result.failures), "Should flag drawdown"
    assert any(
        "stop loss" in r.lower() for r in result.recommendations
    ), "Should recommend risk controls"
    print("\n✅ PASSED: High drawdown correctly flagged")


def test_failing_trade_count():
    """Test a strategy with insufficient trades"""

    print("\n" + "=" * 60)
    print("TEST 5: Insufficient Trades")
    print("=" * 60)

    report = PerformanceReport(
        total_return=18.0,
        win_rate=70.0,
        sharpe_ratio=1.8,
        max_drawdown=12.0,
        avg_edge_captured=0.90,
        trade_count=15,  # Below 20
        avg_hold_time=10.0,
        summary="Too few trades",
    )

    result = validate_strategy(report)

    print(f"\nResult: {result.message}")
    print(f"Approved: {result.approved}")
    print(f"Failures: {result.failures}")
    print(f"Recommendations: {result.recommendations}")

    assert result.approved == False, "Should be rejected"
    assert any("Trade count" in f for f in result.failures), "Should flag trade count"
    assert any(
        "market coverage" in r.lower() for r in result.recommendations
    ), "Should recommend more markets"
    print("\n✅ PASSED: Low trade count correctly flagged")


def test_failing_return():
    """Test a losing strategy"""

    print("\n" + "=" * 60)
    print("TEST 6: Negative Return")
    print("=" * 60)

    report = PerformanceReport(
        total_return=-10.0,  # Losing money
        win_rate=45.0,
        sharpe_ratio=-0.5,
        max_drawdown=30.0,
        avg_edge_captured=0.50,
        trade_count=25,
        avg_hold_time=7.0,
        summary="Losing strategy",
    )

    result = validate_strategy(report)

    print(f"\nResult: {result.message}")
    print(f"Approved: {result.approved}")
    print(f"Failures: {result.failures}")
    print(f"Recommendations: {result.recommendations}")

    assert result.approved == False, "Should be rejected"
    assert any(
        "return" in f.lower() for f in result.failures
    ), "Should flag negative return"
    assert any(
        "revision" in r.lower() for r in result.recommendations
    ), "Should recommend strategy revision"
    print("\n✅ PASSED: Losing strategy correctly flagged")


def test_multiple_failures():
    """Test a strategy that fails multiple checks"""

    print("\n" + "=" * 60)
    print("TEST 7: Multiple Failures")
    print("=" * 60)

    report = PerformanceReport(
        total_return=-5.0,
        win_rate=40.0,
        sharpe_ratio=0.2,
        max_drawdown=50.0,
        avg_edge_captured=0.30,
        trade_count=10,
        avg_hold_time=5.0,
        summary="Bad strategy",
    )

    result = validate_strategy(report)

    print(f"\nResult: {result.message}")
    print(f"Approved: {result.approved}")
    print(f"Failures ({len(result.failures)}):")
    for failure in result.failures:
        print(f"  - {failure}")
    print(f"Recommendations ({len(result.recommendations)}):")
    for rec in result.recommendations:
        print(f"  - {rec}")

    assert result.approved == False, "Should be rejected"
    assert (
        len(result.failures) == 5
    ), f"Should have 5 failures, got {len(result.failures)}"
    assert (
        len(result.recommendations) == 5
    ), f"Should have 5 recommendations, got {len(result.recommendations)}"
    print("\n✅ PASSED: Multiple failures correctly identified")


def test_custom_thresholds():
    """Test with custom validation thresholds"""

    print("\n" + "=" * 60)
    print("TEST 8: Custom Thresholds")
    print("=" * 60)

    # Stricter thresholds
    strict_thresholds = {
        "min_win_rate": 60.0,
        "min_sharpe": 1.0,
        "max_drawdown_allowed": 20.0,
        "min_trades": 50,
        "min_return": 10.0,
    }

    # This would pass default thresholds
    report = PerformanceReport(
        total_return=8.0,
        win_rate=55.0,
        sharpe_ratio=0.8,
        max_drawdown=25.0,
        avg_edge_captured=0.70,
        trade_count=30,
        avg_hold_time=7.0,
        summary="Moderate strategy",
    )

    # Should pass default
    result_default = validate_strategy(report)
    print(f"\nWith default thresholds: {result_default.approved}")

    # Should fail strict
    result_strict = validate_strategy(report, strict_thresholds)
    print(f"With strict thresholds: {result_strict.approved}")
    print(f"Failures: {len(result_strict.failures)}")

    assert result_default.approved == True, "Should pass default thresholds"
    assert result_strict.approved == False, "Should fail strict thresholds"
    print("\n✅ PASSED: Custom thresholds work correctly")


def test_convenience_functions():
    """Test helper functions"""

    print("\n" + "=" * 60)
    print("TEST 9: Convenience Functions")
    print("=" * 60)

    good_report = PerformanceReport(
        total_return=30.0,
        win_rate=70.0,
        sharpe_ratio=2.0,
        max_drawdown=10.0,
        avg_edge_captured=0.95,
        trade_count=60,
        avg_hold_time=8.0,
        summary="Excellent strategy",
    )

    # Test is_strategy_approved
    approved = is_strategy_approved(good_report)
    print(f"\nis_strategy_approved(): {approved}")
    assert approved == True, "Should return True"

    # Test get_validation_summary
    summary = get_validation_summary(good_report)
    print(f"\nValidation Summary:")
    print(summary)

    assert "✅ APPROVED" in summary, "Should show approval"
    print("\n✅ PASSED: Convenience functions work")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("STRATEGY VALIDATOR TEST SUITE")
    print("=" * 60)

    try:
        test_passing_strategy()
        test_failing_win_rate()
        test_failing_sharpe()
        test_failing_drawdown()
        test_failing_trade_count()
        test_failing_return()
        test_multiple_failures()
        test_custom_thresholds()
        test_convenience_functions()

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print()

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
