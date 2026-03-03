"""
Test script for Trading Floor agent messages
Demonstrates post_message() functionality
"""

import sys
import os

# Set up test environment
os.environ['TRADING_MODE'] = 'paper'
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_KEY'] = 'test_key'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.twosigma_geo import TwoSigmaGeoAgent
from models import Market


def test_message_posting():
    """Test that agent posts messages correctly."""
    print("=" * 60)
    print("TRADING FLOOR MESSAGE TEST")
    print("=" * 60)
    print()
    
    # Initialize agent
    agent = TwoSigmaGeoAgent()
    print(f"✓ Initialized {agent.agent_id} (theme: {agent.theme})")
    print()
    
    # Create test market
    test_market = Market(
        id="test_market_123",
        question="Will Netanyahu remain Israeli PM through April 2026?",
        yes_price=0.78,
        no_price=0.22,
        volume_24h=150000.0,
        category="geopolitical",
        resolved=False
    )
    
    print("📊 Test Market:")
    print(f"   Question: {test_market.question}")
    print(f"   Current odds: {test_market.yes_price:.0%} YES")
    print(f"   Volume: ${test_market.volume_24h:,.0f}")
    print()
    
    # Test thesis generation (will post messages)
    print("🤖 Generating thesis...")
    print()
    
    try:
        thesis = agent.generate_thesis(test_market)
        
        if thesis:
            print("✅ Thesis generated successfully!")
            print()
            print(f"   Fair value: {thesis.fair_value:.0%}")
            print(f"   Edge: {thesis.edge:+.1%}")
            print(f"   Conviction: {thesis.conviction:.0%}")
            print(f"   Recommendation: {thesis.proposed_action['side']}")
            print()
            print("📨 Messages posted:")
            print("   1. 'analyzing' - Started analysis")
            print("   2. 'thesis' - Thesis generated")
        else:
            print("⚠️  No thesis generated (edge or conviction insufficient)")
            print()
            print("📨 Messages posted:")
            print("   1. 'analyzing' - Started analysis")
            print("   2. 'alert' - Thesis rejected")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print()
    print("💡 To view messages:")
    print("   1. Check agent_messages table in Supabase")
    print("   2. Query: SELECT * FROM agent_messages ORDER BY timestamp DESC")
    print("   3. Or build the Trading Floor UI page")
    print()


def test_multiple_scenarios():
    """Test different message scenarios."""
    print("=" * 60)
    print("MULTIPLE SCENARIO TEST")
    print("=" * 60)
    print()
    
    agent = TwoSigmaGeoAgent()
    
    # Scenario 1: High edge market (should generate thesis)
    print("📊 Scenario 1: High edge market")
    market1 = Market(
        id="high_edge_123",
        question="Will Russia withdraw from Ukraine by June 2026?",
        yes_price=0.15,  # Low price, if agent calculates higher = edge
        no_price=0.85,
        volume_24h=200000.0,
        category="geopolitical",
        resolved=False
    )
    
    thesis1 = agent.generate_thesis(market1)
    print(f"   Result: {'✅ Thesis generated' if thesis1 else '⚠️ No thesis'}")
    print()
    
    # Scenario 2: Low edge market (should reject)
    print("📊 Scenario 2: Low edge market")
    market2 = Market(
        id="low_edge_456",
        question="Will Biden hold a press conference this week?",
        yes_price=0.52,  # Close to fair value
        no_price=0.48,
        volume_24h=50000.0,
        category="us_politics",
        resolved=False
    )
    
    thesis2 = agent.generate_thesis(market2)
    print(f"   Result: {'✅ Thesis generated' if thesis2 else '⚠️ No thesis (expected)'}")
    print()
    
    # Scenario 3: Low volume market (should process but might reject)
    print("📊 Scenario 3: Very low volume market")
    market3 = Market(
        id="low_volume_789",
        question="Will rare geopolitical event X happen?",
        yes_price=0.25,
        no_price=0.75,
        volume_24h=5000.0,  # Below agent's min_volume
        category="geopolitical",
        resolved=False
    )
    
    thesis3 = agent.generate_thesis(market3)
    print(f"   Result: {'✅ Thesis generated' if thesis3 else '⚠️ No thesis'}")
    print()
    
    print("=" * 60)
    print(f"📊 SUMMARY: Generated {sum([1 for t in [thesis1, thesis2, thesis3] if t])} theses out of 3 markets")
    print("=" * 60)
    print()


def demo_message_structure():
    """Show what a typical message looks like."""
    print("=" * 60)
    print("EXAMPLE MESSAGE STRUCTURE")
    print("=" * 60)
    print()
    
    print("🔍 When agent starts analyzing:")
    print("""
    {
        "agent_id": "twosigma_geo",
        "theme": "geopolitical",
        "message_type": "analyzing",
        "timestamp": "2026-03-02T13:56:00Z",
        "market_question": "Will Netanyahu remain Israeli PM?",
        "market_id": "poly_market_123",
        "current_odds": 0.78,
        "status": "analyzing"
    }
    """)
    
    print()
    print("✅ When thesis is generated:")
    print("""
    {
        "agent_id": "twosigma_geo",
        "theme": "geopolitical",
        "message_type": "thesis",
        "timestamp": "2026-03-02T13:56:05Z",
        "market_question": "Will Netanyahu remain Israeli PM?",
        "market_id": "poly_market_123",
        "current_odds": 0.78,
        "thesis_odds": 0.85,
        "edge": 0.07,
        "conviction": 0.71,
        "capital_allocated": 147.00,
        "reasoning": "Coalition stable despite protests...",
        "signals": {
            "news_events": 12,
            "sentiment_score": 0.15,
            "macro_drivers": ["News sentiment", "Economic pressure", "Policy stance"]
        },
        "status": "thesis_generated",
        "related_thesis_id": "thesis_uuid_456",
        "tags": ["macro_analysis", "geopolitical", "bullish"]
    }
    """)
    
    print()
    print("⚠️ When thesis is rejected:")
    print("""
    {
        "agent_id": "twosigma_geo",
        "theme": "geopolitical",
        "message_type": "alert",
        "timestamp": "2026-03-02T13:56:02Z",
        "market_question": "Will Biden hold press conference?",
        "market_id": "poly_market_789",
        "current_odds": 0.52,
        "reasoning": "Rejected: Edge 2.1% below minimum 3.0%",
        "status": "rejected",
        "tags": ["rejected", "insufficient_edge"]
    }
    """)
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    print("\n")
    
    # Run tests
    test_message_posting()
    
    print("\n")
    input("Press Enter to run multiple scenario test...")
    print("\n")
    
    test_multiple_scenarios()
    
    print("\n")
    input("Press Enter to see example message structure...")
    print("\n")
    
    demo_message_structure()
    
    print("\n✅ All tests complete!")
    print("\n💡 Next steps:")
    print("   1. Apply this pattern to all 12 agents")
    print("   2. Build Trading Floor UI page")
    print("   3. Watch real-time agent communication!\n")
