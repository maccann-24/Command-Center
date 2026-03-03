"""
Test script for consensus detection
Demonstrates detect_consensus() functionality
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
    detect_consensus,
    check_for_consensus_after_thesis,
    check_all_after_thesis,
    get_recent_consensus
)


def create_consensus_test_theses():
    """
    Create test thesis messages to simulate consensus.
    """
    print("=" * 60)
    print("CREATING CONSENSUS TEST THESES")
    print("=" * 60)
    print()
    
    market_id = "test_consensus_market_789"
    market_question = "Will Biden announce VP pick by March 15, 2026?"
    
    # 3 agents with similar opinions (within 10%)
    theses = [
        {
            'agent_id': 'renaissance_politics',
            'theme': 'us_politics',
            'message_type': 'thesis',
            'market_question': market_question,
            'market_id': market_id,
            'current_odds': 0.42,
            'thesis_odds': 0.24,  # All within ~10% range
            'edge': -0.18,
            'conviction': 0.72,
            'capital_allocated': 220.00,
            'reasoning': "Quantitative polling model shows low probability. Historical patterns suggest delayed announcement.",
            'status': 'thesis_generated',
            'tags': ['quant', 'us_politics', 'bearish'],
            'timestamp': datetime.utcnow().isoformat()
        },
        {
            'agent_id': 'jpmorgan_politics',
            'theme': 'us_politics',
            'message_type': 'thesis',
            'market_question': market_question,
            'market_id': market_id,
            'current_odds': 0.42,
            'thesis_odds': 0.26,
            'edge': -0.16,
            'conviction': 0.68,
            'capital_allocated': 200.00,
            'reasoning': "Event catalyst analysis suggests no immediate announcement. Campaign strategy favors waiting.",
            'status': 'thesis_generated',
            'tags': ['events', 'us_politics', 'bearish'],
            'timestamp': datetime.utcnow().isoformat()
        },
        {
            'agent_id': 'goldman_politics',
            'theme': 'us_politics',
            'message_type': 'thesis',
            'market_question': market_question,
            'market_id': market_id,
            'current_odds': 0.42,
            'thesis_odds': 0.28,
            'edge': -0.14,
            'conviction': 0.75,  # High conviction
            'capital_allocated': 250.00,
            'reasoning': "Fundamental political analysis indicates delayed timeline. Party dynamics require more time.",
            'status': 'thesis_generated',
            'tags': ['fundamental', 'us_politics', 'bearish'],
            'timestamp': datetime.utcnow().isoformat()
        }
    ]
    
    print("📊 Creating 3 agreeing theses:")
    print()
    
    for i, thesis in enumerate(theses, 1):
        print(f"   Thesis {i} ({thesis['agent_id']}):")
        print(f"   Thesis: {thesis['thesis_odds']:.0%} YES")
        print(f"   Edge: {thesis['edge']:+.0%}")
        print(f"   Conviction: {thesis['conviction']:.0%}")
        
        try:
            db.table('agent_messages').insert(thesis).execute()
            print("   ✅ Posted")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Calculate stats
    avg_odds = sum(t['thesis_odds'] for t in theses) / len(theses)
    total_edge = sum(t['edge'] for t in theses)
    total_capital = sum(t['capital_allocated'] for t in theses)
    avg_conviction = sum(t['conviction'] for t in theses) / len(theses)
    max_spread = max(t['thesis_odds'] for t in theses) - min(t['thesis_odds'] for t in theses)
    
    print("=" * 60)
    print("CONSENSUS STATS")
    print("=" * 60)
    print(f"   Agents: {len(theses)}")
    print(f"   Average thesis: {avg_odds:.0%} YES")
    print(f"   Spread: {max_spread:.0%} (within 10% threshold)")
    print(f"   Combined edge: {total_edge:+.0%}")
    print(f"   Combined capital: ${total_capital:,.2f}")
    print(f"   Average conviction: {avg_conviction:.0%}")
    print(f"   HIGH CONVICTION: {'✅ YES' if avg_conviction > 0.70 else '❌ NO'}")
    print("=" * 60)
    print()
    
    return market_id


def test_detect_consensus(market_id):
    """
    Test consensus detection.
    """
    print("=" * 60)
    print("TESTING CONSENSUS DETECTION")
    print("=" * 60)
    print()
    
    print("🔍 Running detect_consensus()...")
    print()
    
    consensus = detect_consensus(market_id)
    
    if consensus:
        print("🎯 CONSENSUS DETECTED!")
        print()
        print(f"   Agents ({consensus['count']}):")
        for agent in consensus['agents']:
            print(f"     • {agent}")
        print()
        print(f"   Average thesis: {consensus['avg_odds']:.0%} YES")
        print(f"   Combined edge: {consensus['total_edge']:+.1%}")
        print(f"   Combined capital: ${consensus['total_capital']:,.2f}")
        print(f"   Average conviction: {consensus['avg_conviction']:.0%}")
        print()
        if consensus['is_high_conviction']:
            print("   🔥 HIGH CONVICTION CONSENSUS!")
        print()
        print("   ✅ Consensus message posted to Trading Floor")
    else:
        print("   ℹ️  No consensus detected")
    
    print()
    print("=" * 60)


def test_get_consensus():
    """
    Test getting recent consensus.
    """
    print("=" * 60)
    print("TESTING GET CONSENSUS")
    print("=" * 60)
    print()
    
    print("📊 Getting recent consensus (last 24 hours)...")
    consensus_list = get_recent_consensus(hours=24, limit=10)
    
    print(f"   Found {len(consensus_list)} consensus play(s)")
    print()
    
    for i, consensus in enumerate(consensus_list, 1):
        signals = consensus.get('signals', {})
        print(f"   Consensus {i}:")
        print(f"   - Market: {consensus.get('market_question', 'Unknown')[:60]}...")
        print(f"   - Agents: {signals.get('count', 0)} ({', '.join(signals.get('agents', [])[:3])})")
        print(f"   - Position: {signals.get('avg_odds', 0):.0%} YES")
        print(f"   - Capital: ${signals.get('total_capital', 0):,.2f}")
        if signals.get('is_high_conviction'):
            print(f"   - 🔥 HIGH CONVICTION")
        print()
    
    print("=" * 60)


def test_check_all():
    """
    Test combined conflict and consensus detection.
    """
    print("=" * 60)
    print("TESTING check_all_after_thesis()")
    print("=" * 60)
    print()
    
    market_id = "combined_check_market_999"
    
    print("📝 This function runs BOTH checks:")
    print("   1. detect_conflicts() - looks for disagreements >20%")
    print("   2. detect_consensus() - looks for agreements within 10%")
    print()
    
    print("🔍 Running check_all_after_thesis()...")
    check_all_after_thesis(market_id)
    
    print("   ✅ Both checks complete")
    print()
    print("💡 Use this in agent code after posting thesis:")
    print("   self.post_message('thesis', ...)")
    print("   check_all_after_thesis(market.id)")
    print()
    print("=" * 60)


def demo_consensus_message_structure():
    """
    Show what a consensus message looks like.
    """
    print("=" * 60)
    print("EXAMPLE CONSENSUS MESSAGE")
    print("=" * 60)
    print()
    
    print("""
    🎯 CONSENSUS MESSAGE STRUCTURE:
    
    {
        "agent_id": "system",
        "theme": "us_politics",
        "message_type": "consensus",
        "market_question": "Will Biden announce VP pick by March 15?",
        "market_id": "poly_market_789",
        "current_odds": 0.42,
        "thesis_odds": 0.26,  // Average of all agents
        "edge": -0.48,  // Combined edge
        "conviction": 0.72,  // Average conviction
        "capital_allocated": 670.00,  // Combined capital
        "reasoning": "🎯 🔥 HIGH CONVICTION - 3 AGENTS AGREE
        
        AGENTS:
          • renaissance_politics
          • jpmorgan_politics
          • goldman_politics
        
        CONSENSUS POSITION:
        Average Thesis: 26% YES
        Current Market: 42%
        Combined Edge: -48.0%
        Average Conviction: 72%
        
        CAPITAL ALLOCATION:
        Combined: $670.00
        
        This is a multi-agent consensus play with strong agreement.
        ⚠️ HIGH CONVICTION - Average conviction 72% exceeds 70%",
        
        "signals": {
            "agents": ["renaissance_politics", "jpmorgan_politics", "goldman_politics"],
            "count": 3,
            "avg_odds": 0.26,
            "total_edge": -0.48,
            "total_capital": 670.00,
            "avg_conviction": 0.72,
            "is_high_conviction": true,
            "individual_theses": [
                {"agent": "renaissance_politics", "odds": 0.24, "conviction": 0.72},
                {"agent": "jpmorgan_politics", "odds": 0.26, "conviction": 0.68},
                {"agent": "goldman_politics", "odds": 0.28, "conviction": 0.75}
            ]
        },
        "status": "detected",
        "tags": ["consensus", "multi_agent", "high_conviction", "bearish", "renaissance_politics", "jpmorgan_politics", "goldman_politics"]
    }
    """)
    
    print()
    print("=" * 60)


def cleanup_test_data():
    """
    Clean up test consensus messages.
    """
    print()
    print("🧹 Cleaning up test data...")
    
    try:
        # Delete test messages
        db.table('agent_messages').delete().like(
            'market_id', 'test_%'
        ).execute()
        
        db.table('agent_messages').delete().like(
            'market_id', 'combined_%'
        ).execute()
        
        print("   ✅ Test data cleaned up")
    except Exception as e:
        print(f"   ⚠️  Error cleaning up: {e}")
    
    print()


if __name__ == "__main__":
    print("\n")
    
    # Test 1: Create consensus test theses
    market_id = create_consensus_test_theses()
    
    input("Press Enter to detect consensus...")
    print("\n")
    
    # Test 2: Detect consensus
    test_detect_consensus(market_id)
    
    input("Press Enter to view all consensus...")
    print("\n")
    
    # Test 3: Get recent consensus
    test_get_consensus()
    
    input("Press Enter to see consensus message structure...")
    print("\n")
    
    # Test 4: Show consensus structure
    demo_consensus_message_structure()
    
    input("Press Enter to test combined check...")
    print("\n")
    
    # Test 5: Combined check
    test_check_all()
    
    # Cleanup
    cleanup_test_data()
    
    print("\n✅ All tests complete!")
    print("\n💡 Key takeaways:")
    print("   1. Consensus detected when 3+ agents agree within 10%")
    print("   2. System posts consensus message with combined stats")
    print("   3. Flagged as HIGH_CONVICTION if avg conviction > 70%")
    print("   4. Use check_all_after_thesis() for both conflicts & consensus")
    print()
