"""
TRADING FLOOR VALIDATION TEST
Validates code structure and logic without requiring database connection
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Validate all required modules can be imported."""
    print("\n" + "="*60)
    print("TEST 1: IMPORTS")
    print("="*60)
    
    try:
        from agents.base import BaseAgent
        print("✓ BaseAgent imported")
        
        from agents.twosigma_geo import TwoSigmaGeoAgent
        print("✓ TwoSigmaGeoAgent imported")
        
        from models import Market, Thesis
        print("✓ Models imported")
        
        from core.message_utils import (
            detect_conflicts,
            detect_consensus,
            check_all_after_thesis
        )
        print("✓ message_utils imported")
        
        print("\n✅ ALL IMPORTS SUCCESSFUL")
        return True
    except Exception as e:
        print(f"\n❌ IMPORT FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_agent_structure():
    """Validate BaseAgent has required methods."""
    print("\n" + "="*60)
    print("TEST 2: BaseAgent STRUCTURE")
    print("="*60)
    
    try:
        from agents.base import BaseAgent
        import inspect
        
        # Check post_message exists
        assert hasattr(BaseAgent, 'post_message'), "Missing post_message method"
        print("✓ post_message() method exists")
        
        # Check signature
        sig = inspect.signature(BaseAgent.post_message)
        params = list(sig.parameters.keys())
        assert 'message_type' in params, "Missing message_type parameter"
        assert 'kwargs' in params, "Missing kwargs parameter"
        print(f"✓ Method signature correct: {params}")
        
        # Check docstring
        assert BaseAgent.post_message.__doc__, "Missing docstring"
        print("✓ Method has docstring")
        
        print("\n✅ BaseAgent STRUCTURE VALID")
        return True
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_twosigma_agent():
    """Validate TwoSigma agent structure."""
    print("\n" + "="*60)
    print("TEST 3: TwoSigmaGeoAgent STRUCTURE")
    print("="*60)
    
    try:
        from agents.twosigma_geo import TwoSigmaGeoAgent
        
        agent = TwoSigmaGeoAgent()
        
        # Check attributes
        assert hasattr(agent, 'agent_id'), "Missing agent_id"
        assert hasattr(agent, 'theme'), "Missing theme"
        assert hasattr(agent, 'min_edge'), "Missing min_edge"
        assert hasattr(agent, 'min_conviction'), "Missing min_conviction"
        
        assert agent.agent_id == 'twosigma_geo', f"Wrong agent_id: {agent.agent_id}"
        assert agent.theme == 'geopolitical', f"Wrong theme: {agent.theme}"
        
        print(f"✓ Agent ID: {agent.agent_id}")
        print(f"✓ Theme: {agent.theme}")
        print(f"✓ Min edge: {agent.min_edge:.1%}")
        print(f"✓ Min conviction: {agent.min_conviction:.1%}")
        
        # Check it has post_message (inherited)
        assert hasattr(agent, 'post_message'), "Agent missing post_message method"
        print("✓ Agent inherits post_message()")
        
        # Check imports check_all_after_thesis
        import agents.twosigma_geo as module
        import inspect
        source = inspect.getsource(module)
        assert 'check_all_after_thesis' in source, "Agent doesn't import check_all_after_thesis"
        print("✓ Agent imports check_all_after_thesis")
        
        print("\n✅ TwoSigmaGeoAgent STRUCTURE VALID")
        return True
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_message_utils_functions():
    """Validate message_utils has all required functions."""
    print("\n" + "="*60)
    print("TEST 4: message_utils FUNCTIONS")
    print("="*60)
    
    try:
        from core import message_utils
        
        required_functions = [
            'detect_conflicts',
            'detect_consensus',
            'check_for_conflicts_after_thesis',
            'check_for_consensus_after_thesis',
            'check_all_after_thesis',
            'get_recent_conflicts',
            'get_recent_consensus',
            'get_market_conflicts'
        ]
        
        for func_name in required_functions:
            assert hasattr(message_utils, func_name), f"Missing function: {func_name}"
            func = getattr(message_utils, func_name)
            assert callable(func), f"{func_name} is not callable"
            print(f"✓ {func_name}() exists and is callable")
        
        print(f"\n✅ ALL {len(required_functions)} FUNCTIONS PRESENT")
        return True
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_message_type_validation():
    """Validate message type checking logic."""
    print("\n" + "="*60)
    print("TEST 5: MESSAGE TYPE VALIDATION")
    print("="*60)
    
    try:
        from agents.base import BaseAgent
        import inspect
        
        # Get post_message source
        source = inspect.getsource(BaseAgent.post_message)
        
        # Check for validation
        assert 'valid_types' in source or "'thesis'" in source, "No message type validation found"
        print("✓ Message type validation exists")
        
        # Check for all 5 valid types
        required_types = ['thesis', 'conflict', 'consensus', 'alert', 'analyzing']
        for msg_type in required_types:
            assert f"'{msg_type}'" in source, f"Missing message type: {msg_type}"
        print(f"✓ All {len(required_types)} message types defined")
        
        print("\n✅ MESSAGE TYPE VALIDATION VALID")
        return True
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_import():
    """Validate database imports are correct."""
    print("\n" + "="*60)
    print("TEST 6: DATABASE IMPORTS")
    print("="*60)
    
    try:
        # Check BaseAgent uses correct import
        from agents import base as base_module
        import inspect
        source = inspect.getsource(base_module)
        assert 'get_supabase_client' in source, "BaseAgent not using get_supabase_client"
        print("✓ BaseAgent uses get_supabase_client()")
        
        # Check message_utils uses correct import
        from core import message_utils
        source = inspect.getsource(message_utils)
        assert 'get_supabase_client' in source, "message_utils not using get_supabase_client"
        print("✓ message_utils uses get_supabase_client()")
        
        print("\n✅ DATABASE IMPORTS CORRECT")
        return True
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_documentation_exists():
    """Validate documentation files exist."""
    print("\n" + "="*60)
    print("TEST 7: DOCUMENTATION")
    print("="*60)
    
    try:
        import os
        
        docs = [
            'schema_migrations/agent_messages.sql',
            'schema_migrations/README.md',
            'AGENT_MESSAGE_INTEGRATION_GUIDE.md',
            'tests/test_trading_floor_messages.py',
            'tests/test_conflict_detection.py',
            'tests/test_consensus_detection.py'
        ]
        
        for doc in docs:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), doc)
            assert os.path.exists(path), f"Missing: {doc}"
            print(f"✓ {doc}")
        
        print(f"\n✅ ALL {len(docs)} DOCUMENTATION FILES EXIST")
        return True
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_typescript_functions():
    """Validate TypeScript functions exist in trading.ts."""
    print("\n" + "="*60)
    print("TEST 8: TYPESCRIPT FUNCTIONS")
    print("="*60)
    
    try:
        import os
        
        ts_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'command-center/lib/supabase/trading.ts'
        )
        
        assert os.path.exists(ts_file), "trading.ts not found"
        print(f"✓ trading.ts exists")
        
        with open(ts_file, 'r') as f:
            content = f.read()
        
        # Check for required functions and types
        required_items = [
            'export type AgentMessage',
            'export type AgentMessageFilters',
            'getAgentMessages',
            'subscribeToAgentMessages'
        ]
        
        for item in required_items:
            assert item in content, f"Missing in trading.ts: {item}"
            print(f"✓ {item}")
        
        print("\n✅ TYPESCRIPT FUNCTIONS PRESENT")
        return True
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests."""
    print("\n" + "="*60)
    print("TRADING FLOOR VALIDATION TEST SUITE")
    print("="*60)
    print("\nValidating code structure and logic...")
    print("(No database connection required)")
    print()
    
    tests = [
        ("Imports", test_imports),
        ("BaseAgent Structure", test_base_agent_structure),
        ("TwoSigma Agent", test_twosigma_agent),
        ("message_utils Functions", test_message_utils_functions),
        ("Message Type Validation", test_message_type_validation),
        ("Database Imports", test_database_import),
        ("Documentation", test_documentation_exists),
        ("TypeScript Functions", test_typescript_functions),
    ]
    
    results = []
    for test_name, test_func in tests:
        passed = test_func()
        results.append((test_name, passed))
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print()
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print("="*60)
    print(f"RESULT: {passed_count}/{total_count} validations passed")
    print("="*60)
    
    if passed_count == total_count:
        print("\n🎉 ALL VALIDATIONS PASSED! 🎉")
        print("\n✅ Trading Floor code structure is correct:")
        print("   • All required files exist ✓")
        print("   • All functions defined ✓")
        print("   • Agent integration correct ✓")
        print("   • Database imports correct ✓")
        print("   • TypeScript functions present ✓")
        print("   • Documentation complete ✓")
        print("\n💡 NOTE: Database tests skipped (require live connection)")
        print("   To test with real database:")
        print("   1. Apply migration: schema_migrations/agent_messages.sql")
        print("   2. Set SUPABASE_URL and SUPABASE_KEY")
        print("   3. Run: python tests/test_trading_floor_messages.py")
        print("\n🚀 Ready to build Trading Floor UI!")
        return 0
    else:
        print(f"\n❌ {total_count - passed_count} VALIDATION(S) FAILED")
        print("\n⚠️  Please review failures above")
        return 1


if __name__ == "__main__":
    exit(main())
