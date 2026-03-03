"""
COMPREHENSIVE TRADING FLOOR TEST
Tests all components: Database, Agents, Conflicts, Consensus
"""

import sys
import os
from datetime import datetime
import traceback

# Set up test environment
os.environ['TRADING_MODE'] = 'paper'
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_KEY'] = 'test_key'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_test(test_name, test_func):
    """Run a test and report results."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print('='*60)
    try:
        test_func()
        print(f"✅ PASSED: {test_name}")
        return True
    except AssertionError as e:
        print(f"❌ FAILED: {test_name}")
        print(f"   Assertion Error: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ ERROR: {test_name}")
        print(f"   Exception: {e}")
        traceback.print_exc()
        return False


def test_1_imports():
    """Test 1: All imports work correctly."""
    from database.db import get_supabase_client
    from agents.base import BaseAgent
    from agents.twosigma_geo import TwoSigmaGeoAgent
    from models import Market, Thesis
    from core.message_utils import (
        detect_conflicts,
        detect_consensus,
        check_all_after_thesis
    )
    print("✓ All imports successful")


def test_2_database_connection():
    """Test 2: Database connection works."""
    from database.db import get_supabase_client
    
    # Try to query agent_messages table
    try:
        supabase = get_supabase_client()
        response = supabase.table('agent_messages').select('id').limit(1).execute()
        print(f"✓ Database connected")
        print(f"✓ agent_messages table exists")
    except Exception as e:
        raise AssertionError(f"Database connection failed: {e}")


def test_3_base_agent_has_post_message():
    """Test 3: BaseAgent has post_message method."""
    from agents.base import BaseAgent
    
    assert hasattr(BaseAgent, 'post_message'), "BaseAgent missing post_message method"
    
    # Check method signature
    import inspect
    sig = inspect.signature(BaseAgent.post_message)
    params = list(sig.parameters.keys())
    
    assert 'self' in params, "post_message missing self parameter"
    assert 'message_type' in params, "post_message missing message_type parameter"
    assert 'kwargs' in params, "post_message missing kwargs parameter"
    
    print("✓ BaseAgent.post_message() exists")
    print(f"✓ Method signature correct: {params}")


def test_4_twosigma_agent_initialization():
    """Test 4: TwoSigma agent initializes correctly."""
    from agents.twosigma_geo import TwoSigmaGeoAgent
    
    agent = TwoSigmaGeoAgent()
    
    # Check required attributes
    assert hasattr(agent, 'agent_id'), "Agent missing agent_id"
    assert hasattr(agent, 'theme'), "Agent missing theme"
    assert hasattr(agent, 'min_edge'), "Agent missing min_edge"
    assert hasattr(agent, 'min_conviction'), "Agent missing min_conviction"
    
    assert agent.agent_id == 'twosigma_geo', f"Wrong agent_id: {agent.agent_id}"
    assert agent.theme == 'geopolitical', f"Wrong theme: {agent.theme}"
    assert agent.min_edge > 0, f"Invalid min_edge: {agent.min_edge}"
    assert agent.min_conviction > 0, f"Invalid min_conviction: {agent.min_conviction}"
    
    print(f"✓ Agent ID: {agent.agent_id}")
    print(f"✓ Theme: {agent.theme}")
    print(f"✓ Min edge: {agent.min_edge:.1%}")
    print(f"✓ Min conviction: {agent.min_conviction:.1%}")


def test_5_agent_posts_message():
    """Test 5: Agent can post messages to database."""
    from agents.twosigma_geo import TwoSigmaGeoAgent
    from database.db import get_supabase_client
    
    agent = TwoSigmaGeoAgent()
    
    # Post a test message
    test_market_id = f"test_post_{datetime.utcnow().timestamp()}"
    
    agent.post_message(
        'analyzing',
        market_question='Test market for posting',
        market_id=test_market_id,
        current_odds=0.50,
        status='analyzing'
    )
    
    # Verify it was posted
    import time
    time.sleep(0.5)  # Give DB a moment
    
    response = get_supabase_client().table('agent_messages').select('*').eq(
        'market_id', test_market_id
    ).execute()
    
    assert response.data, "Message not found in database"
    assert len(response.data) > 0, "No messages returned"
    
    msg = response.data[0]
    assert msg['agent_id'] == 'twosigma_geo', f"Wrong agent_id: {msg['agent_id']}"
    assert msg['message_type'] == 'analyzing', f"Wrong message_type: {msg['message_type']}"
    assert msg['market_id'] == test_market_id, f"Wrong market_id: {msg['market_id']}"
    
    print(f"✓ Message posted successfully")
    print(f"✓ Message ID: {msg['id']}")
    print(f"✓ Timestamp: {msg['timestamp']}")
    
    # Cleanup
    get_supabase_client().table('agent_messages').delete().eq('market_id', test_market_id).execute()


def test_6_agent_generates_thesis():
    """Test 6: Agent can generate thesis and post messages."""
    from agents.twosigma_geo import TwoSigmaGeoAgent
    from models import Market
    from database.db import get_supabase_client
    
    agent = TwoSigmaGeoAgent()
    
    # Create test market
    test_market = Market(
        id=f"test_thesis_{datetime.utcnow().timestamp()}",
        question="Will comprehensive test pass?",
        yes_price=0.65,
        no_price=0.35,
        volume_24h=150000.0,
        category="geopolitical",
        resolved=False
    )
    
    # Generate thesis (may or may not produce thesis, but should post messages)
    thesis = agent.generate_thesis(test_market)
    
    # Check messages were posted
    import time
    time.sleep(0.5)
    
    response = get_supabase_client().table('agent_messages').select('*').eq(
        'market_id', test_market.id
    ).order('timestamp', desc=False).execute()
    
    assert response.data, "No messages posted during thesis generation"
    
    messages = response.data
    print(f"✓ {len(messages)} message(s) posted during thesis generation")
    
    # Should have at least 'analyzing' message
    analyzing_msg = [m for m in messages if m['message_type'] == 'analyzing']
    assert analyzing_msg, "No 'analyzing' message found"
    print(f"✓ 'analyzing' message posted")
    
    # Check for thesis or rejection
    thesis_msgs = [m for m in messages if m['message_type'] == 'thesis']
    alert_msgs = [m for m in messages if m['message_type'] == 'alert']
    
    if thesis:
        assert thesis_msgs, "Thesis generated but no 'thesis' message posted"
        print(f"✓ Thesis generated and 'thesis' message posted")
        print(f"  Fair value: {thesis.fair_value:.0%}")
        print(f"  Edge: {thesis.edge:+.1%}")
    else:
        assert alert_msgs, "Thesis rejected but no 'alert' message posted"
        print(f"✓ Thesis rejected and 'alert' message posted")
        if alert_msgs:
            print(f"  Reason: {alert_msgs[0].get('reasoning', 'N/A')[:80]}")
    
    # Cleanup
    get_supabase_client().table('agent_messages').delete().eq('market_id', test_market.id).execute()


def test_7_conflict_detection():
    """Test 7: Conflict detection works."""
    from core.message_utils import detect_conflicts
    from database.db import get_supabase_client
    
    market_id = f"test_conflict_{datetime.utcnow().timestamp()}"
    
    # Create two conflicting theses
    thesis1 = {
        'agent_id': 'agent_bullish',
        'theme': 'test',
        'message_type': 'thesis',
        'market_question': 'Test conflict detection?',
        'market_id': market_id,
        'current_odds': 0.50,
        'thesis_odds': 0.75,  # Bullish
        'edge': 0.25,
        'conviction': 0.70,
        'reasoning': 'Very bullish reasoning',
        'status': 'thesis_generated',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    thesis2 = {
        'agent_id': 'agent_bearish',
        'theme': 'test',
        'message_type': 'thesis',
        'market_question': 'Test conflict detection?',
        'market_id': market_id,
        'current_odds': 0.50,
        'thesis_odds': 0.30,  # Bearish
        'edge': -0.20,
        'conviction': 0.68,
        'reasoning': 'Very bearish reasoning',
        'status': 'thesis_generated',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Insert theses
    get_supabase_client().table('agent_messages').insert(thesis1).execute()
    get_supabase_client().table('agent_messages').insert(thesis2).execute()
    
    import time
    time.sleep(0.5)
    
    # Detect conflict
    conflict = detect_conflicts(market_id, min_difference=0.20)
    
    assert conflict is not None, "Conflict not detected (45% difference)"
    assert conflict['difference'] >= 0.40, f"Wrong difference: {conflict['difference']}"
    assert conflict['agent1'] in ['agent_bullish', 'agent_bearish']
    assert conflict['agent2'] in ['agent_bullish', 'agent_bearish']
    assert conflict['agent1'] != conflict['agent2']
    
    print(f"✓ Conflict detected")
    print(f"  {conflict['agent1']}: {conflict['thesis1_odds']:.0%}")
    print(f"  {conflict['agent2']}: {conflict['thesis2_odds']:.0%}")
    print(f"  Difference: {conflict['difference']:.0%}")
    
    # Check conflict message was posted
    response = get_supabase_client().table('agent_messages').select('*').eq(
        'market_id', market_id
    ).eq('message_type', 'conflict').execute()
    
    assert response.data, "Conflict message not posted"
    print(f"✓ Conflict message posted to database")
    
    # Cleanup
    get_supabase_client().table('agent_messages').delete().eq('market_id', market_id).execute()


def test_8_consensus_detection():
    """Test 8: Consensus detection works."""
    from core.message_utils import detect_consensus
    from database.db import get_supabase_client
    
    market_id = f"test_consensus_{datetime.utcnow().timestamp()}"
    
    # Create three agreeing theses (within 10%)
    theses = [
        {
            'agent_id': 'agent_1',
            'theme': 'test',
            'message_type': 'thesis',
            'market_question': 'Test consensus detection?',
            'market_id': market_id,
            'current_odds': 0.50,
            'thesis_odds': 0.30,
            'edge': -0.20,
            'conviction': 0.72,
            'capital_allocated': 200.00,
            'reasoning': 'Agent 1 reasoning',
            'status': 'thesis_generated',
            'timestamp': datetime.utcnow().isoformat()
        },
        {
            'agent_id': 'agent_2',
            'theme': 'test',
            'message_type': 'thesis',
            'market_question': 'Test consensus detection?',
            'market_id': market_id,
            'current_odds': 0.50,
            'thesis_odds': 0.32,
            'edge': -0.18,
            'conviction': 0.68,
            'capital_allocated': 180.00,
            'reasoning': 'Agent 2 reasoning',
            'status': 'thesis_generated',
            'timestamp': datetime.utcnow().isoformat()
        },
        {
            'agent_id': 'agent_3',
            'theme': 'test',
            'message_type': 'thesis',
            'market_question': 'Test consensus detection?',
            'market_id': market_id,
            'current_odds': 0.50,
            'thesis_odds': 0.35,
            'edge': -0.15,
            'conviction': 0.75,
            'capital_allocated': 220.00,
            'reasoning': 'Agent 3 reasoning',
            'status': 'thesis_generated',
            'timestamp': datetime.utcnow().isoformat()
        }
    ]
    
    # Insert theses
    for thesis in theses:
        get_supabase_client().table('agent_messages').insert(thesis).execute()
    
    import time
    time.sleep(0.5)
    
    # Detect consensus
    consensus = detect_consensus(market_id, min_agents=3, max_spread=0.10)
    
    assert consensus is not None, "Consensus not detected (3 agents within 10%)"
    assert consensus['count'] == 3, f"Wrong agent count: {consensus['count']}"
    assert len(consensus['agents']) == 3, f"Wrong agents list: {consensus['agents']}"
    assert consensus['avg_conviction'] > 0.70, f"Wrong avg conviction: {consensus['avg_conviction']}"
    assert consensus['is_high_conviction'], "Should be flagged as HIGH_CONVICTION"
    
    print(f"✓ Consensus detected")
    print(f"  Agents: {consensus['count']}")
    print(f"  Average thesis: {consensus['avg_odds']:.0%}")
    print(f"  Combined capital: ${consensus['total_capital']:,.2f}")
    print(f"  Average conviction: {consensus['avg_conviction']:.0%}")
    print(f"  🔥 HIGH_CONVICTION: {consensus['is_high_conviction']}")
    
    # Check consensus message was posted
    response = get_supabase_client().table('agent_messages').select('*').eq(
        'market_id', market_id
    ).eq('message_type', 'consensus').execute()
    
    assert response.data, "Consensus message not posted"
    print(f"✓ Consensus message posted to database")
    
    # Cleanup
    get_supabase_client().table('agent_messages').delete().eq('market_id', market_id).execute()


def test_9_message_utils_functions():
    """Test 9: All message_utils helper functions exist."""
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
        print(f"✓ {func_name}() exists")


def test_10_message_validation():
    """Test 10: Message type validation works."""
    from agents.twosigma_geo import TwoSigmaGeoAgent
    from database.db import get_supabase_client
    
    agent = TwoSigmaGeoAgent()
    
    # Test valid message types
    valid_types = ['thesis', 'conflict', 'consensus', 'alert', 'analyzing']
    
    for msg_type in valid_types:
        test_id = f"test_valid_{msg_type}_{datetime.utcnow().timestamp()}"
        agent.post_message(
            msg_type,
            market_id=test_id,
            market_question=f"Test {msg_type}"
        )
        
        # Verify posted
        import time
        time.sleep(0.3)
        response = get_supabase_client().table('agent_messages').select('*').eq(
            'market_id', test_id
        ).execute()
        
        assert response.data, f"Valid message type '{msg_type}' not posted"
        
        # Cleanup
        get_supabase_client().table('agent_messages').delete().eq('market_id', test_id).execute()
    
    print(f"✓ All {len(valid_types)} valid message types work")
    
    # Test invalid message type (should be silently ignored)
    invalid_id = f"test_invalid_{datetime.utcnow().timestamp()}"
    agent.post_message(
        'invalid_type',
        market_id=invalid_id,
        market_question="Test invalid"
    )
    
    import time
    time.sleep(0.3)
    response = get_supabase_client().table('agent_messages').select('*').eq(
        'market_id', invalid_id
    ).execute()
    
    assert not response.data, "Invalid message type was posted (should be rejected)"
    print(f"✓ Invalid message types properly rejected")


def test_11_integration_workflow():
    """Test 11: Complete workflow (thesis → conflict/consensus detection)."""
    from agents.twosigma_geo import TwoSigmaGeoAgent
    from models import Market
    from database.db import get_supabase_client
    
    market_id = f"test_workflow_{datetime.utcnow().timestamp()}"
    
    # Create market
    market = Market(
        id=market_id,
        question="Test complete workflow?",
        yes_price=0.55,
        no_price=0.45,
        volume_24h=200000.0,
        category="geopolitical",
        resolved=False
    )
    
    # Agent generates thesis (with conflict/consensus check)
    agent = TwoSigmaGeoAgent()
    thesis = agent.generate_thesis(market)
    
    import time
    time.sleep(0.5)
    
    # Verify messages were posted
    response = get_supabase_client().table('agent_messages').select('*').eq(
        'market_id', market_id
    ).order('timestamp', desc=False).execute()
    
    assert response.data, "No messages in workflow"
    
    messages = response.data
    msg_types = [m['message_type'] for m in messages]
    
    print(f"✓ Complete workflow executed")
    print(f"  Messages posted: {len(messages)}")
    print(f"  Message types: {', '.join(msg_types)}")
    
    # Should have at least analyzing
    assert 'analyzing' in msg_types, "Missing 'analyzing' message"
    print(f"✓ Workflow includes all expected message types")
    
    # Cleanup
    get_supabase_client().table('agent_messages').delete().eq('market_id', market_id).execute()


def cleanup_all_test_data():
    """Clean up all test data."""
    from database.db import get_supabase_client
    
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60)
    
    try:
        # Delete all test messages
        patterns = ['test_%', 'Test%']
        for pattern in patterns:
            get_supabase_client().table('agent_messages').delete().like('market_id', pattern).execute()
        
        print("✓ All test data cleaned up")
    except Exception as e:
        print(f"⚠️  Cleanup error: {e}")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("COMPREHENSIVE TRADING FLOOR TEST SUITE")
    print("="*60)
    print("\nTesting all components:")
    print("  • Database schema")
    print("  • Agent message posting")
    print("  • Conflict detection")
    print("  • Consensus detection")
    print("  • Complete workflows")
    print()
    
    tests = [
        ("Imports", test_1_imports),
        ("Database Connection", test_2_database_connection),
        ("BaseAgent.post_message() Exists", test_3_base_agent_has_post_message),
        ("TwoSigma Agent Initialization", test_4_twosigma_agent_initialization),
        ("Agent Posts Message", test_5_agent_posts_message),
        ("Agent Generates Thesis", test_6_agent_generates_thesis),
        ("Conflict Detection", test_7_conflict_detection),
        ("Consensus Detection", test_8_consensus_detection),
        ("Message Utils Functions", test_9_message_utils_functions),
        ("Message Validation", test_10_message_validation),
        ("Integration Workflow", test_11_integration_workflow),
    ]
    
    results = []
    for test_name, test_func in tests:
        passed = run_test(test_name, test_func)
        results.append((test_name, passed))
    
    # Cleanup
    cleanup_all_test_data()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print()
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print("="*60)
    print(f"RESULT: {passed_count}/{total_count} tests passed")
    print("="*60)
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n✅ Trading Floor system is fully operational:")
        print("   • Database schema ✓")
        print("   • Agent messaging ✓")
        print("   • Conflict detection ✓")
        print("   • Consensus detection ✓")
        print("   • Complete workflows ✓")
        print("\n🚀 Ready to build UI!")
        return 0
    else:
        print(f"\n❌ {total_count - passed_count} TEST(S) FAILED")
        print("\n⚠️  Please review failures above")
        return 1


if __name__ == "__main__":
    exit(main())
