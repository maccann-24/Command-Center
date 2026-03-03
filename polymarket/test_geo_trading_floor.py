#!/usr/bin/env python3
"""
Test script to run GeopoliticalAgent update_theses() and verify Trading Floor integration.

Run: python test_geo_trading_floor.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.geo import GeopoliticalAgent

def test_geo_agent_trading_floor():
    """
    Test GeopoliticalAgent with Trading Floor message posting.
    """
    print("="*70)
    print("TESTING GEOPOLITICAL AGENT - TRADING FLOOR INTEGRATION")
    print("="*70)
    print()
    
    # Create agent
    agent = GeopoliticalAgent()
    
    print("📡 Calling update_theses()...")
    print("   - Should post 'analyzing' message at start")
    print("   - Should post 'thesis' messages for each generated thesis")
    print()
    
    # Run update_theses
    theses = agent.update_theses()
    
    print()
    print("="*70)
    print("RESULTS")
    print("="*70)
    print(f"✅ Generated {len(theses)} theses")
    print()
    
    if theses:
        print("📊 Thesis Summary:")
        for i, thesis in enumerate(theses, 1):
            print(f"\n{i}. {thesis.thesis_text[:80]}...")
            print(f"   Edge: {thesis.edge:.2%}")
            print(f"   Conviction: {thesis.conviction:.0%}")
            print(f"   Fair Value: {thesis.fair_value:.2%}")
    
    print()
    print("="*70)
    print("VERIFICATION STEPS")
    print("="*70)
    print("1. Check Trading Floor at: http://localhost:3000/trading/floor")
    print("2. Verify 'analyzing' message appeared when script started")
    print("3. Verify thesis messages appeared for each generated thesis")
    print("4. Check that metadata fields are populated:")
    print("   - Market question")
    print("   - Current/Thesis/Edge")
    print("   - Conviction")
    print("   - Reasoning")
    print("   - Capital allocated")
    print("5. Verify real-time update worked (messages appeared without refresh)")
    print()
    print("If all checks pass, integrate into remaining 11 agents!")
    print("="*70)

if __name__ == "__main__":
    test_geo_agent_trading_floor()
