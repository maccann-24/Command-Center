"""
Test core/risk.py module
"""

import sys
import importlib.util
from dataclasses import dataclass

# Import risk module directly
spec = importlib.util.spec_from_file_location('risk', 'core/risk.py')
risk_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(risk_module)

RiskEngine = risk_module.RiskEngine
RiskDecision = risk_module.RiskDecision
RISK_PARAMS = risk_module.RISK_PARAMS
check_risk = risk_module.check_risk
is_trade_safe = risk_module.is_trade_safe


# Mock objects for testing
@dataclass
class MockThesis:
    proposed_action: dict
    conviction: float
    edge: float


@dataclass
class MockPortfolio:
    deployed_pct: float


def test_all_checks_pass():
    """Test a thesis that passes all risk checks"""
    
    print("\n" + "=" * 60)
    print("TEST 1: All Checks Pass")
    print("=" * 60)
    
    thesis = MockThesis(
        proposed_action={'size_pct': 10.0},
        conviction=0.85,
        edge=0.15,
    )
    
    portfolio = MockPortfolio(deployed_pct=20.0)
    
    engine = RiskEngine()
    decision = engine.evaluate(thesis, portfolio)
    
    print(f"\nDecision: {decision}")
    print(f"Approved: {decision.approved}")
    print(f"Reason: {decision.reason}")
    print(f"Recommended Size: {decision.recommended_size}%")
    print("\nRisk Notes:")
    for note in decision.risk_notes:
        print(f"  {note}")
    
    assert decision.approved == True, "Should be approved"
    assert decision.recommended_size == 10.0, "Should recommend full size"
    assert all("✓" in note for note in decision.risk_notes), "All checks should pass"
    
    print("\n✅ PASSED: All checks passed correctly")


def test_position_size_too_large():
    """Test rejection due to excessive position size"""
    
    print("\n" + "=" * 60)
    print("TEST 2: Position Size Too Large")
    print("=" * 60)
    
    thesis = MockThesis(
        proposed_action={'size_pct': 25.0},  # Exceeds 20% limit
        conviction=0.90,
        edge=0.20,
    )
    
    portfolio = MockPortfolio(deployed_pct=10.0)
    
    engine = RiskEngine()
    decision = engine.evaluate(thesis, portfolio)
    
    print(f"\nDecision: {decision}")
    print(f"Approved: {decision.approved}")
    print(f"Reason: {decision.reason}")
    print("\nRisk Notes:")
    for note in decision.risk_notes:
        print(f"  {note}")
    
    assert decision.approved == False, "Should be rejected"
    assert "Position size" in decision.reason, "Should mention position size"
    assert decision.recommended_size == 0.0, "Should not recommend any size"
    
    print("\n✅ PASSED: Excessive position size rejected")


def test_total_deployed_too_high():
    """Test rejection due to excessive total deployment"""
    
    print("\n" + "=" * 60)
    print("TEST 3: Total Deployed Too High")
    print("=" * 60)
    
    thesis = MockThesis(
        proposed_action={'size_pct': 15.0},
        conviction=0.80,
        edge=0.12,
    )
    
    portfolio = MockPortfolio(deployed_pct=50.0)  # 50% + 15% = 65% > 60%
    
    engine = RiskEngine()
    decision = engine.evaluate(thesis, portfolio)
    
    print(f"\nDecision: {decision}")
    print(f"Approved: {decision.approved}")
    print(f"Reason: {decision.reason}")
    print("\nRisk Notes:")
    for note in decision.risk_notes:
        print(f"  {note}")
    
    assert decision.approved == False, "Should be rejected"
    assert "deployed" in decision.reason.lower(), "Should mention deployment"
    
    print("\n✅ PASSED: Excessive total deployment rejected")


def test_conviction_too_low():
    """Test rejection due to low conviction"""
    
    print("\n" + "=" * 60)
    print("TEST 4: Conviction Too Low")
    print("=" * 60)
    
    thesis = MockThesis(
        proposed_action={'size_pct': 10.0},
        conviction=0.60,  # Below 0.70 threshold
        edge=0.15,
    )
    
    portfolio = MockPortfolio(deployed_pct=20.0)
    
    engine = RiskEngine()
    decision = engine.evaluate(thesis, portfolio)
    
    print(f"\nDecision: {decision}")
    print(f"Approved: {decision.approved}")
    print(f"Reason: {decision.reason}")
    print("\nRisk Notes:")
    for note in decision.risk_notes:
        print(f"  {note}")
    
    assert decision.approved == False, "Should be rejected"
    assert "Conviction" in decision.reason, "Should mention conviction"
    
    print("\n✅ PASSED: Low conviction rejected")


def test_edge_too_small():
    """Test rejection due to insufficient edge"""
    
    print("\n" + "=" * 60)
    print("TEST 5: Edge Too Small")
    print("=" * 60)
    
    thesis = MockThesis(
        proposed_action={'size_pct': 10.0},
        conviction=0.85,
        edge=0.03,  # Below 0.05 (5%) threshold
    )
    
    portfolio = MockPortfolio(deployed_pct=20.0)
    
    engine = RiskEngine()
    decision = engine.evaluate(thesis, portfolio)
    
    print(f"\nDecision: {decision}")
    print(f"Approved: {decision.approved}")
    print(f"Reason: {decision.reason}")
    print("\nRisk Notes:")
    for note in decision.risk_notes:
        print(f"  {note}")
    
    assert decision.approved == False, "Should be rejected"
    assert "Edge" in decision.reason, "Should mention edge"
    
    print("\n✅ PASSED: Insufficient edge rejected")


def test_multiple_failures():
    """Test rejection with multiple failing checks"""
    
    print("\n" + "=" * 60)
    print("TEST 6: Multiple Failures")
    print("=" * 60)
    
    thesis = MockThesis(
        proposed_action={'size_pct': 25.0},  # Too large
        conviction=0.60,  # Too low
        edge=0.02,  # Too small
    )
    
    portfolio = MockPortfolio(deployed_pct=50.0)  # Will exceed total
    
    engine = RiskEngine()
    decision = engine.evaluate(thesis, portfolio)
    
    print(f"\nDecision: {decision}")
    print(f"Approved: {decision.approved}")
    print(f"Reason: {decision.reason}")
    print("\nRisk Notes:")
    for note in decision.risk_notes:
        print(f"  {note}")
    
    assert decision.approved == False, "Should be rejected"
    failed_count = sum(1 for note in decision.risk_notes if "✗" in note)
    print(f"\nFailed checks: {failed_count}/4")
    assert failed_count == 4, "All 4 checks should fail"
    
    print("\n✅ PASSED: Multiple failures detected")


def test_custom_risk_params():
    """Test with custom risk parameters"""
    
    print("\n" + "=" * 60)
    print("TEST 7: Custom Risk Parameters")
    print("=" * 60)
    
    # More strict parameters
    strict_params = {
        'max_position_pct': 10.0,
        'max_deployed_pct': 40.0,
        'min_conviction': 0.80,
        'min_edge': 0.10,
    }
    
    thesis = MockThesis(
        proposed_action={'size_pct': 12.0},
        conviction=0.75,
        edge=0.08,
    )
    
    portfolio = MockPortfolio(deployed_pct=20.0)
    
    # Should pass with default params
    engine_default = RiskEngine()
    decision_default = engine_default.evaluate(thesis, portfolio)
    print(f"\nDefault params: {decision_default.approved}")
    
    # Should fail with strict params
    engine_strict = RiskEngine(strict_params)
    decision_strict = engine_strict.evaluate(thesis, portfolio)
    print(f"Strict params: {decision_strict.approved}")
    print(f"Reason: {decision_strict.reason}")
    
    assert decision_default.approved == True, "Should pass default params"
    assert decision_strict.approved == False, "Should fail strict params"
    
    print("\n✅ PASSED: Custom parameters work correctly")


def test_max_position_size():
    """Test get_max_position_size calculation"""
    
    print("\n" + "=" * 60)
    print("TEST 8: Max Position Size Calculation")
    print("=" * 60)
    
    engine = RiskEngine()
    
    # Case 1: Deployment limit is constraining
    portfolio1 = MockPortfolio(deployed_pct=55.0)  # 60% - 55% = 5% available
    max_size1 = engine.get_max_position_size(portfolio1)
    print(f"\nPortfolio deployed 55%: Max position = {max_size1}%")
    assert max_size1 == 5.0, f"Should be 5%, got {max_size1}%"
    
    # Case 2: Position limit is constraining
    portfolio2 = MockPortfolio(deployed_pct=10.0)  # Plenty of room
    max_size2 = engine.get_max_position_size(portfolio2)
    print(f"Portfolio deployed 10%: Max position = {max_size2}%")
    assert max_size2 == 20.0, f"Should be 20%, got {max_size2}%"
    
    # Case 3: Fully deployed
    portfolio3 = MockPortfolio(deployed_pct=60.0)
    max_size3 = engine.get_max_position_size(portfolio3)
    print(f"Portfolio deployed 60%: Max position = {max_size3}%")
    assert max_size3 == 0.0, f"Should be 0%, got {max_size3}%"
    
    print("\n✅ PASSED: Max position size calculated correctly")


def test_suggest_position_size():
    """Test position size suggestion based on conviction and edge"""
    
    print("\n" + "=" * 60)
    print("TEST 9: Suggest Position Size")
    print("=" * 60)
    
    engine = RiskEngine()
    portfolio = MockPortfolio(deployed_pct=20.0)
    
    # High conviction, good edge
    thesis1 = MockThesis(
        proposed_action={'size_pct': 0},  # Unused
        conviction=0.90,
        edge=0.20,
    )
    
    suggested1 = engine.suggest_position_size(thesis1, portfolio)
    print(f"\nHigh conviction (0.90), good edge (20%): {suggested1:.2f}%")
    assert suggested1 > 0, "Should suggest non-zero size"
    assert suggested1 <= 20.0, "Should not exceed max position"
    
    # Lower conviction, smaller edge
    thesis2 = MockThesis(
        proposed_action={'size_pct': 0},
        conviction=0.70,
        edge=0.08,
    )
    
    suggested2 = engine.suggest_position_size(thesis2, portfolio)
    print(f"Lower conviction (0.70), small edge (8%): {suggested2:.2f}%")
    assert suggested2 < suggested1, "Should suggest smaller size"
    
    print("\n✅ PASSED: Position sizing works correctly")


def test_convenience_functions():
    """Test convenience wrapper functions"""
    
    print("\n" + "=" * 60)
    print("TEST 10: Convenience Functions")
    print("=" * 60)
    
    thesis = MockThesis(
        proposed_action={'size_pct': 15.0},
        conviction=0.80,
        edge=0.12,
    )
    
    portfolio = MockPortfolio(deployed_pct=30.0)
    
    # Test check_risk
    decision = check_risk(thesis, portfolio)
    print(f"\ncheck_risk(): {decision}")
    assert isinstance(decision, RiskDecision), "Should return RiskDecision"
    
    # Test is_trade_safe
    is_safe = is_trade_safe(thesis, portfolio)
    print(f"is_trade_safe(): {is_safe}")
    assert isinstance(is_safe, bool), "Should return bool"
    assert is_safe == decision.approved, "Should match decision.approved"
    
    print("\n✅ PASSED: Convenience functions work")


def test_update_params():
    """Test updating risk parameters"""
    
    print("\n" + "=" * 60)
    print("TEST 11: Update Parameters")
    print("=" * 60)
    
    engine = RiskEngine()
    
    print(f"\nOriginal max_position_pct: {engine.params['max_position_pct']}")
    
    # Update parameter
    engine.update_params(max_position_pct=15.0)
    
    print(f"Updated max_position_pct: {engine.params['max_position_pct']}")
    
    assert engine.params['max_position_pct'] == 15.0, "Should be updated to 15.0"
    
    # Test with updated params
    thesis = MockThesis(
        proposed_action={'size_pct': 18.0},
        conviction=0.80,
        edge=0.10,
    )
    
    portfolio = MockPortfolio(deployed_pct=20.0)
    
    decision = engine.evaluate(thesis, portfolio)
    print(f"\nThesis with 18% size against 15% limit: {decision.approved}")
    assert decision.approved == False, "Should be rejected with new limit"
    
    print("\n✅ PASSED: Parameter updates work")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RISK ENGINE TEST SUITE")
    print("=" * 60)
    
    try:
        test_all_checks_pass()
        test_position_size_too_large()
        test_total_deployed_too_high()
        test_conviction_too_low()
        test_edge_too_small()
        test_multiple_failures()
        test_custom_risk_params()
        test_max_position_size()
        test_suggest_position_size()
        test_convenience_functions()
        test_update_params()
        
        print("\n" + "=" * 60)
        print("🎉 ALL 11 TESTS PASSED!")
        print("=" * 60)
        print()
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
