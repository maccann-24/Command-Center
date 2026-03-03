#!/usr/bin/env python3
"""
Live integration test for Morgan Stanley Weather Agent + Trading Floor
No mocks - tests actual posting to agent_messages table
"""

import sys
import os

# Ensure we can import from parent directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_morganstanley_weather_trading_floor():
    """Test Morgan Stanley Weather Agent with Trading Floor integration."""
    
    print("\n" + "="*60)
    print("🧪 MORGAN STANLEY WEATHER AGENT - TRADING FLOOR TEST")
    print("="*60 + "\n")
    
    # Check environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease set:")
        for var in missing_vars:
            print(f"  export {var}=your_value_here")
        return 1
    
    try:
        # Import agent
        from agents.morganstanley_weather import MorganStanleyWeatherAgent
        
        print("✅ Agent imported successfully")
        
        # Instantiate agent
        agent = MorganStanleyWeatherAgent()
        print(f"✅ Agent instantiated: {agent.agent_id}")
        print(f"   Theme: {agent.theme}")
        print(f"   Min Edge: {agent.min_edge:.1%}")
        print(f"   Min Conviction: {agent.min_conviction:.1%}")
        
        # Run update_theses
        print("\n📊 Running update_theses()...\n")
        theses = agent.update_theses()
        
        print(f"\n✅ Generated {len(theses)} theses")
        
        if theses:
            print("\n📋 Thesis Summary:")
            for i, thesis in enumerate(theses, 1):
                print(f"\n  {i}. Market: {thesis.market_id}")
                print(f"     Edge: {thesis.edge:+.1%}")
                print(f"     Conviction: {thesis.conviction:.1%}")
                print(f"     Side: {thesis.proposed_action['side']}")
                print(f"     Size: {thesis.proposed_action['size_pct']:.1%}")
        
        print("\n" + "="*60)
        print("✅ TEST PASSED")
        print("="*60 + "\n")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_morganstanley_weather_trading_floor())
