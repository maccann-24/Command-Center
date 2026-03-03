#!/usr/bin/env python3
"""
Live integration test for ALL remaining agents + Trading Floor
Tests: goldman_geo, bridgewater_geo, morganstanley_crypto, renaissance_crypto, citadel_crypto
"""

import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_all_agents():
    """Test all 5 remaining agents with Trading Floor integration."""
    
    print("\n" + "="*70)
    print("🧪 TRADING FLOOR INTEGRATION - ALL REMAINING AGENTS")
    print("="*70 + "\n")
    
    # Check environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease set:")
        for var in missing_vars:
            print(f"  export {var}=your_value_here")
        return 1
    
    agents_to_test = [
        ('goldman_geo', 'GoldmanGeoAgent', 'agents.goldman_geo'),
        ('bridgewater_geo', 'BridgewaterGeoAgent', 'agents.bridgewater_geo'),
        ('morganstanley_crypto', 'MorganStanleyCryptoAgent', 'agents.morganstanley_crypto'),
        ('renaissance_crypto', 'RenaissanceCryptoAgent', 'agents.renaissance_crypto'),
        ('citadel_crypto', 'CitadelCryptoAgent', 'agents.citadel_crypto'),
    ]
    
    total_theses = 0
    passed_agents = 0
    
    for agent_id, class_name, module_path in agents_to_test:
        print(f"\n{'─'*70}")
        print(f"🔍 Testing: {agent_id}")
        print(f"{'─'*70}\n")
        
        try:
            # Dynamic import
            module = __import__(module_path, fromlist=[class_name])
            AgentClass = getattr(module, class_name)
            
            print(f"✅ Agent imported: {class_name}")
            
            # Instantiate
            agent = AgentClass()
            print(f"✅ Agent instantiated: {agent.agent_id}")
            print(f"   Theme: {agent.theme}")
            print(f"   Min Edge: {agent.min_edge:.1%}")
            print(f"   Min Conviction: {agent.min_conviction:.1%}")
            
            # Run update_theses
            print(f"\n📊 Running update_theses()...\n")
            theses = agent.update_theses()
            
            print(f"\n✅ Generated {len(theses)} theses for {agent_id}")
            total_theses += len(theses)
            passed_agents += 1
            
            if theses:
                print(f"\n📋 Thesis Summary:")
                for i, thesis in enumerate(theses[:3], 1):  # Show first 3
                    print(f"  {i}. Edge: {thesis.edge:+.1%} | Conv: {thesis.conviction:.1%} | Side: {thesis.proposed_action['side']}")
                if len(theses) > 3:
                    print(f"  ... and {len(theses) - 3} more")
            
        except Exception as e:
            print(f"\n❌ FAILED for {agent_id}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*70}")
    print(f"✅ Passed: {passed_agents}/5 agents")
    print(f"💡 Total theses generated: {total_theses}")
    print(f"🎯 Target: 3-4 theses per agent")
    print(f"\n🌐 View Trading Floor: http://localhost:3000/trading/floor")
    print(f"{'='*70}\n")
    
    return 0 if passed_agents == 5 else 1

if __name__ == "__main__":
    sys.exit(test_all_agents())
