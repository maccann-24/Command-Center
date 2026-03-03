#!/usr/bin/env python3
"""
Test BaseAgent abstract class
Validates abstract methods and interface
"""

import sys
sys.path.insert(0, '.')

from typing import List
from agents.base import BaseAgent
from models import Thesis, Market
from datetime import datetime, timedelta


class TestAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing"""
    
    @property
    def mandate(self) -> str:
        return "Test markets for validation"
    
    def update_theses(self) -> List[Thesis]:
        """Test implementation"""
        # Create a sample thesis
        thesis = Thesis(
            agent_id="test_agent",
            market_id="test_market_1",
            thesis_text="Test thesis",
            fair_value=0.60,
            current_odds=0.50,
            edge=0.10,
            conviction=0.75,
            horizon="medium",
            proposed_action={"side": "YES", "size_pct": 0.15}
        )
        
        self._theses_cache = [thesis]
        return [thesis]
    
    def generate_thesis(self, market: Market) -> Thesis:
        """Test implementation"""
        return Thesis(
            agent_id="test_agent",
            market_id=market.id,
            thesis_text=f"Generated thesis for {market.question}",
            fair_value=0.55,
            current_odds=0.50,
            edge=0.05,
            conviction=0.70,
            horizon="short",
            proposed_action={"side": "YES", "size_pct": 0.10}
        )


def test_abstract_enforcement():
    """Test that BaseAgent cannot be instantiated directly"""
    print("\n" + "=" * 60)
    print("ABSTRACT CLASS ENFORCEMENT TEST")
    print("=" * 60)
    
    try:
        # This should fail - can't instantiate abstract class
        agent = BaseAgent()
        print("❌ FAILED: BaseAgent should not be instantiable")
        return False
    except TypeError as e:
        if "abstract" in str(e).lower():
            print("✅ PASSED: BaseAgent correctly prevents instantiation")
            print(f"   Error: {str(e)[:80]}...")
            return True
        else:
            print(f"❌ FAILED: Wrong error type: {e}")
            return False


def test_concrete_implementation():
    """Test that concrete implementation works"""
    print("\n" + "=" * 60)
    print("CONCRETE IMPLEMENTATION TEST")
    print("=" * 60)
    
    try:
        # Create concrete agent
        agent = TestAgent()
        
        # Test mandate property
        print(f"\n1. Testing mandate property...")
        mandate = agent.mandate
        if isinstance(mandate, str) and len(mandate) > 0:
            print(f"   ✅ mandate: '{mandate}'")
        else:
            print(f"   ❌ Invalid mandate: {mandate}")
            return False
        
        # Test update_theses()
        print(f"\n2. Testing update_theses()...")
        theses = agent.update_theses()
        if isinstance(theses, list) and len(theses) > 0:
            print(f"   ✅ Generated {len(theses)} thesis/theses")
            thesis = theses[0]
            print(f"   ✅ Thesis: {thesis.thesis_text}")
            print(f"   ✅ Edge: {thesis.edge:.2%}, Conviction: {thesis.conviction:.0%}")
        else:
            print(f"   ❌ Invalid theses: {theses}")
            return False
        
        # Test generate_thesis()
        print(f"\n3. Testing generate_thesis()...")
        test_market = Market(
            id="test_market_2",
            question="Will Bitcoin reach $100k?",
            category="crypto",
            yes_price=0.55,
            no_price=0.45,
            volume_24h=100000.0,
            resolution_date=datetime.utcnow() + timedelta(days=30)
        )
        
        thesis = agent.generate_thesis(test_market)
        if isinstance(thesis, Thesis):
            print(f"   ✅ Generated thesis for market")
            print(f"   ✅ Market: {test_market.question[:50]}...")
            print(f"   ✅ Edge: {thesis.edge:.2%}")
        else:
            print(f"   ❌ Invalid thesis: {thesis}")
            return False
        
        # Test cache
        print(f"\n4. Testing thesis cache...")
        cached = agent.get_cached_theses()
        if len(cached) == 1:
            print(f"   ✅ Cache works: {len(cached)} thesis cached")
        else:
            print(f"   ❌ Cache issue: expected 1, got {len(cached)}")
            return False
        
        # Test cache clear
        agent.clear_cache()
        cached = agent.get_cached_theses()
        if len(cached) == 0:
            print(f"   ✅ Cache clear works")
        else:
            print(f"   ❌ Cache clear failed: {len(cached)} remaining")
            return False
        
        # Test __repr__
        print(f"\n5. Testing __repr__...")
        repr_str = repr(agent)
        if "TestAgent" in repr_str and "mandate" in repr_str:
            print(f"   ✅ __repr__: {repr_str}")
        else:
            print(f"   ❌ Invalid __repr__: {repr_str}")
            return False
        
        print("\n✅ ALL CONCRETE IMPLEMENTATION TESTS PASSED")
        return True
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_required_methods():
    """Test that all required abstract methods are defined"""
    print("\n" + "=" * 60)
    print("REQUIRED METHODS TEST")
    print("=" * 60)
    
    required_methods = ['update_theses', 'generate_thesis']
    required_properties = ['mandate']
    
    print("\nChecking abstract methods:")
    for method in required_methods:
        if hasattr(BaseAgent, method):
            print(f"   ✅ {method}() defined")
        else:
            print(f"   ❌ {method}() missing")
            return False
    
    print("\nChecking abstract properties:")
    for prop in required_properties:
        if hasattr(BaseAgent, prop):
            print(f"   ✅ {prop} defined")
        else:
            print(f"   ❌ {prop} missing")
            return False
    
    print("\n✅ ALL REQUIRED METHODS PRESENT")
    return True


def test_type_hints():
    """Test that methods have correct type hints"""
    print("\n" + "=" * 60)
    print("TYPE HINTS TEST")
    print("=" * 60)
    
    import inspect
    
    # Check update_theses return type
    print("\n1. Checking update_theses() signature...")
    sig = inspect.signature(BaseAgent.update_theses)
    if sig.return_annotation != inspect.Signature.empty:
        print(f"   ✅ Return type: {sig.return_annotation}")
    else:
        print(f"   ⚠️  No return type hint")
    
    # Check generate_thesis signature
    print("\n2. Checking generate_thesis() signature...")
    sig = inspect.signature(BaseAgent.generate_thesis)
    if sig.return_annotation != inspect.Signature.empty:
        print(f"   ✅ Return type: {sig.return_annotation}")
    else:
        print(f"   ⚠️  No return type hint")
    
    params = list(sig.parameters.values())
    if len(params) > 1:  # Skip self
        param = params[1]
        if param.annotation != inspect.Parameter.empty:
            print(f"   ✅ Parameter 'market' type: {param.annotation}")
        else:
            print(f"   ⚠️  No parameter type hint")
    
    print("\n✅ TYPE HINTS TEST COMPLETE")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("BASE AGENT VALIDATION")
    print("=" * 60)
    
    success = True
    
    # Test 1: Required methods
    if not test_required_methods():
        success = False
    
    # Test 2: Abstract enforcement
    if not test_abstract_enforcement():
        success = False
    
    # Test 3: Concrete implementation
    if not test_concrete_implementation():
        success = False
    
    # Test 4: Type hints
    if not test_type_hints():
        success = False
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
        print("\n💡 BaseAgent interface ready for:")
        print("   - GeopoliticalAgent (Task 10)")
        print("   - CopyTradingAgent (Task 11)")
        print("   - Future agents...")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60 + "\n")
    
    return success


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
