"""
Test script for conflict detection
Demonstrates detect_conflicts() functionality
"""

import sys
import os
from datetime import datetime

# Set up test environment
os.environ['TRADING_MODE'] = 'paper'
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_KEY'] = 'test_key'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from core.message_utils import (
    detect_conflicts,
    check_for_conflicts_after_thesis,
    get_recent_conflicts,
    get_market_conflicts
)


def create_test_theses():
    """
    Create test thesis messages to simulate conflict.
    """
    print("=" * 60)
    print("CREATING TEST THESES")
    print("=" * 60)
    print()
    
    market_id = "test_conflict_market_123"
    market_question = "Will Trump win the 2024 presidential election?"
    
    # Agent 1: Bullish (65% YES)
    thesis1 = {
        'agent_id': 'renaissance_politics',
        'theme': 'us_politics',
        'message_type': 'thesis',
        'market_question': market_question,
        'market_id': market_id,
        'current_odds': 0.45,
        'thesis_odds': 0.65,  # Bullish
        'edge': 0.20,
        'conviction': 0.72,
        'capital_allocated': 250.00,
        'reasoning': "Quantitative polling model shows strong momentum in swing states. Historical patterns suggest incumbent disadvantage. Economic indicators favor challenger.",
        'status': 'thesis_generated',
        'tags': ['quant', 'us_politics', 'bullish'],
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Agent 2: Bearish (35% YES)
    thesis2 = {
        'agent_id': 'jpmorgan_politics',
        'theme': 'us_politics',
        'message_type': 'thesis',
        'market_question': market_question,
        'market_id': market_id,
        'current_odds': 0.45,
        'thesis_odds': 0.35,  # Bearish
        'edge': -0.10,
        'conviction': 0.68,
        'capital_allocated': 200.00,
        'reasoning': "Event catalyst analysis suggests negative news cycle. Fundraising data shows weakness. Key demographic trends unfavorable.",
        'status': 'thesis_generated',
        'tags': ['events', 'us_politics', 'bearish'],
        'timestamp': datetime.utcnow().isoformat()
    }
    
    print("📊 Creating thesis 1 (Renaissance Politics):")
    print(f"   Thesis: {thesis1['thesis_odds']:.0%} YES")
    print(f"   Edge: {thesis1['edge']:+.0%}")
    print()
    
    try:
        db.table('agent_messages').insert(thesis1).execute()
        print("   ✅ Posted")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("📊 Creating thesis 2 (JPMorgan Politics):")
    print(f"   Thesis: {thesis2['thesis_odds']:.0%} YES")
    print(f"   Edge: {thesis2['edge']:+.0%}")
    print()
    
    try:
        db.table('agent_messages').insert(thesis2).execute()
        print("   ✅ Posted")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("=" * 60)
    print(f"DIFFERENCE: {abs(thesis1['thesis_odds'] - thesis2['thesis_odds']):.0%}")
    print("=" * 60)
    print()
    
    return market_id


def test_detect_conflicts(market_id):
    """
    Test conflict detection.
    """
    print("=" * 60)
    print("TESTING CONFLICT DETECTION")
    print("=" * 60)
    print()
    
    print("🔍 Running detect_conflicts()...")
    print()
    
    conflict = detect_conflicts(market_id)
    
    if conflict:
        print("⚠️  CONFLICT DETECTED!")
        print()
        print(f"   Agent 1: {conflict['agent1']}")
        print(f"   Thesis:  {conflict['thesis1_odds']:.0%} YES")
        print()
        print(f"   Agent 2: {conflict['agent2']}")
        print(f"   Thesis:  {conflict['thesis2_odds']:.0%} YES")
        print()
        print(f"   Difference: {conflict['difference']:.0%}")
        print()
        print("   ✅ Conflict message posted to Trading Floor")
    else:
        print("   ℹ️  No conflicts detected")
    
    print()
    print("=" * 60)


def test_get_conflicts():
    """
    Test getting recent conflicts.
    """
    print("=" * 60)
    print("TESTING GET CONFLICTS")
    print("=" * 60)
    print()
    
    print("📊 Getting recent conflicts (last 24 hours)...")
    conflicts = get_recent_conflicts(hours=24, limit=10)
    
    print(f"   Found {len(conflicts)} conflict(s)")
    print()
    
    for i, conflict in enumerate(conflicts, 1):
        signals = conflict.get('signals', {})
        print(f"   Conflict {i}:")
        print(f"   - Market: {conflict.get('market_question', 'Unknown')[:60]}...")
        print(f"   - Agents: {signals.get('agent1', '?')} vs {signals.get('agent2', '?')}")
        print(f"   - Difference: {signals.get('difference', 0):.0%}")
        print()
    
    print("=" * 60)


def test_auto_detection():
    """
    Test automatic conflict detection after thesis posting.
    """
    print("=" * 60)
    print("TESTING AUTOMATIC DETECTION")
    print("=" * 60)
    print()
    
    market_id = "auto_detect_market_456"
    
    print("📝 This simulates what happens in agent code:")
    print()
    print("   1. Agent posts thesis message")
    print("   2. Agent calls check_for_conflicts_after_thesis()")
    print("   3. System automatically detects and posts conflicts")
    print()
    
    print("🔍 Running check_for_conflicts_after_thesis()...")
    check_for_conflicts_after_thesis(market_id)
    
    print("   ✅ Check complete")
    print()
    print("=" * 60)


def demo_conflict_message_structure():
    """
    Show what a conflict message looks like.
    """
    print("=" * 60)
    print("EXAMPLE CONFLICT MESSAGE")
    print("=" * 60)
    print()
    
    print("""
    ⚠️ CONFLICT MESSAGE STRUCTURE:
    
    {
        "agent_id": "system",
        "theme": "us_politics",
        "message_type": "conflict",
        "market_question": "Will Trump win 2024 election?",
        "market_id": "poly_market_123",
        "current_odds": 0.45,
        "reasoning": "⚠️ CONFLICT DETECTED
        
        renaissance_politics vs jpmorgan_politics
        
        RENAISSANCE_POLITICS:
        Thesis: 65% YES
        Quantitative polling model shows strong momentum...
        
        JPMORGAN_POLITICS:
        Thesis: 35% YES
        Event catalyst analysis suggests negative news cycle...
        
        DIFFERENCE: 30%
        This is a significant disagreement that requires review.",
        
        "signals": {
            "agent1": "renaissance_politics",
            "agent2": "jpmorgan_politics",
            "thesis1_odds": 0.65,
            "thesis2_odds": 0.35,
            "difference": 0.30
        },
        "status": "detected",
        "tags": ["conflict", "requires_review", "renaissance_politics_bullish", "jpmorgan_politics_bearish"]
    }
    """)
    
    print()
    print("=" * 60)


def cleanup_test_data():
    """
    Clean up test thesis messages.
    """
    print()
    print("🧹 Cleaning up test data...")
    
    try:
        # Delete test messages
        db.table('agent_messages').delete().like(
            'market_id', 'test_%'
        ).execute()
        
        db.table('agent_messages').delete().like(
            'market_id', 'auto_detect_%'
        ).execute()
        
        print("   ✅ Test data cleaned up")
    except Exception as e:
        print(f"   ⚠️  Error cleaning up: {e}")
    
    print()


if __name__ == "__main__":
    print("\n")
    
    # Test 1: Create test theses
    market_id = create_test_theses()
    
    input("Press Enter to detect conflicts...")
    print("\n")
    
    # Test 2: Detect conflicts
    test_detect_conflicts(market_id)
    
    input("Press Enter to view all conflicts...")
    print("\n")
    
    # Test 3: Get recent conflicts
    test_get_conflicts()
    
    input("Press Enter to see conflict message structure...")
    print("\n")
    
    # Test 4: Show conflict structure
    demo_conflict_message_structure()
    
    input("Press Enter to test automatic detection...")
    print("\n")
    
    # Test 5: Auto detection
    test_auto_detection()
    
    # Cleanup
    cleanup_test_data()
    
    print("\n✅ All tests complete!")
    print("\n💡 Key takeaways:")
    print("   1. Conflicts auto-detected when agents disagree by >20%")
    print("   2. System posts conflict message to Trading Floor")
    print("   3. Includes both agents' reasoning for comparison")
    print("   4. Works automatically - agents just call check_for_conflicts_after_thesis()")
    print()
