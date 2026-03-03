"""
BASED MONEY - Risk Engine Tests
Test suite for core/risk.py with 5 critical test cases
"""

import sys
import os
import importlib.util

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import pytest

    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

from dataclasses import dataclass

# Import risk module directly to avoid dependency chain
spec = importlib.util.spec_from_file_location(
    "risk", os.path.join(os.path.dirname(__file__), "..", "core", "risk.py")
)
risk_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(risk_module)

RiskEngine = risk_module.RiskEngine
RiskDecision = risk_module.RiskDecision
RISK_PARAMS = risk_module.RISK_PARAMS


# ============================================================
# MOCK OBJECTS
# ============================================================


@dataclass
class MockPortfolio:
    """Mock Portfolio for testing"""

    cash: float
    deployed_pct: float


@dataclass
class MockThesis:
    """Mock Thesis for testing"""

    proposed_action: dict
    conviction: float
    edge: float


# ============================================================
# TEST CASES
# ============================================================


def test_approved():
    """Test case 1: All checks pass - should be approved"""

    # Setup: Portfolio with 40% deployed
    portfolio = MockPortfolio(
        cash=1000.0, deployed_pct=40.0  # 40% deployed, 60% available
    )

    # Setup: Thesis with good parameters
    thesis = MockThesis(
        proposed_action={"size_pct": 15.0},  # 15% position size
        conviction=0.85,  # High conviction
        edge=0.12,  # Good edge (12%)
    )

    # Evaluate
    risk_engine = RiskEngine()
    decision = risk_engine.evaluate(thesis, portfolio)

    # Verify: Should be approved
    assert decision.approved == True, f"Expected approved=True, got {decision.approved}"
    assert (
        decision.recommended_size == 15.0
    ), f"Expected size 15.0, got {decision.recommended_size}"
    assert (
        "All checks passed" in decision.reason
    ), f"Unexpected reason: {decision.reason}"

    # Verify: Spec requires a single success note
    assert decision.risk_notes == [
        "All checks passed"
    ], f"Unexpected risk_notes: {decision.risk_notes}"

    print("✅ test_approved: PASSED")


def test_position_too_large():
    """Test case 2: Position size exceeds limit - should be rejected"""

    # Setup: Portfolio with 40% deployed
    portfolio = MockPortfolio(cash=1000.0, deployed_pct=40.0)

    # Setup: Thesis with oversized position
    thesis = MockThesis(
        proposed_action={"size_pct": 25.0},  # 25% position (exceeds 20% limit)
        conviction=0.85,
        edge=0.15,
    )

    # Evaluate
    risk_engine = RiskEngine()
    decision = risk_engine.evaluate(thesis, portfolio)

    # Verify: Should be rejected
    assert (
        decision.approved == False
    ), f"Expected approved=False, got {decision.approved}"
    assert (
        "Position size" in decision.reason
    ), f"Expected 'Position size' in reason, got: {decision.reason}"
    assert (
        decision.recommended_size == 0.0
    ), f"Expected recommended_size=0.0, got {decision.recommended_size}"

    # Verify: Position size check failed
    position_check_failed = any(
        "Position size" in note and "✗" in note for note in decision.risk_notes
    )
    assert position_check_failed, "Position size check should have failed"

    print("✅ test_position_too_large: PASSED")


def test_portfolio_over_deployed():
    """Test case 3: Total deployed exceeds limit - should be rejected"""

    # Setup: Portfolio with 50% already deployed
    portfolio = MockPortfolio(cash=1000.0, deployed_pct=50.0)  # 50% deployed

    # Setup: Thesis with 15% position (total would be 65% > 60% limit)
    thesis = MockThesis(
        proposed_action={"size_pct": 15.0}, conviction=0.80, edge=0.10  # 15% position
    )

    # Evaluate
    risk_engine = RiskEngine()
    decision = risk_engine.evaluate(thesis, portfolio)

    # Verify: Should be rejected
    assert (
        decision.approved == False
    ), f"Expected approved=False, got {decision.approved}"
    assert (
        "deployed" in decision.reason.lower()
    ), f"Expected 'deployed' in reason, got: {decision.reason}"
    assert (
        decision.recommended_size == 0.0
    ), f"Expected recommended_size=0.0, got {decision.recommended_size}"

    # Verify: Total deployed check failed
    deployed_check_failed = any(
        "deployed" in note.lower() and "✗" in note for note in decision.risk_notes
    )
    assert deployed_check_failed, "Total deployed check should have failed"

    print("✅ test_portfolio_over_deployed: PASSED")


def test_low_conviction():
    """Test case 4: Conviction below minimum - should be rejected"""

    # Setup: Portfolio with 40% deployed
    portfolio = MockPortfolio(cash=1000.0, deployed_pct=40.0)

    # Setup: Thesis with low conviction
    thesis = MockThesis(
        proposed_action={"size_pct": 10.0},  # 10% position
        conviction=0.65,  # 65% conviction (below 70% threshold)
        edge=0.12,
    )

    # Evaluate
    risk_engine = RiskEngine()
    decision = risk_engine.evaluate(thesis, portfolio)

    # Verify: Should be rejected
    assert (
        decision.approved == False
    ), f"Expected approved=False, got {decision.approved}"
    assert (
        "Conviction" in decision.reason
    ), f"Expected 'Conviction' in reason, got: {decision.reason}"
    assert (
        decision.recommended_size == 0.0
    ), f"Expected recommended_size=0.0, got {decision.recommended_size}"

    # Verify: Conviction check failed
    conviction_check_failed = any(
        "Conviction" in note and "✗" in note for note in decision.risk_notes
    )
    assert conviction_check_failed, "Conviction check should have failed"

    print("✅ test_low_conviction: PASSED")


def test_insufficient_edge():
    """Test case 5: Edge below minimum - should be rejected"""

    # Setup: Portfolio with 40% deployed
    portfolio = MockPortfolio(cash=1000.0, deployed_pct=40.0)

    # Setup: Thesis with insufficient edge
    thesis = MockThesis(
        proposed_action={"size_pct": 10.0},  # 10% position
        conviction=0.85,
        edge=0.03,  # 3% edge (below 5% threshold)
    )

    # Evaluate
    risk_engine = RiskEngine()
    decision = risk_engine.evaluate(thesis, portfolio)

    # Verify: Should be rejected
    assert (
        decision.approved == False
    ), f"Expected approved=False, got {decision.approved}"
    assert (
        "Edge" in decision.reason
    ), f"Expected 'Edge' in reason, got: {decision.reason}"
    assert (
        decision.recommended_size == 0.0
    ), f"Expected recommended_size=0.0, got {decision.recommended_size}"

    # Verify: Edge check failed
    edge_check_failed = any(
        "Edge" in note and "✗" in note for note in decision.risk_notes
    )
    assert edge_check_failed, "Edge check should have failed"

    print("✅ test_insufficient_edge: PASSED")


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    """Run tests manually without pytest"""
    print("\n" + "=" * 60)
    print("RISK ENGINE TEST SUITE (5 Required Tests)")
    print("=" * 60)

    try:
        test_approved()
        test_position_too_large()
        test_portfolio_over_deployed()
        test_low_conviction()
        test_insufficient_edge()

        print("\n" + "=" * 60)
        print("🎉 ALL 5 TESTS PASSED!")
        print("=" * 60)
        print()

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
