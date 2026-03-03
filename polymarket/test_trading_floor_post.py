#!/usr/bin/env python3
"""
Simple test to post a message to Trading Floor.
"""

import sys
import os

sys.path.insert(0, os.getcwd())

from database.trading_floor import post_analyzing_message, post_thesis_message

print("="*70)
print("TESTING TRADING FLOOR - DIRECT MESSAGE POST")
print("="*70)
print()

# Test 1: Post analyzing message
print("1. Posting 'analyzing' message...")
result1 = post_analyzing_message(
    agent_id="test-geo-agent",
    theme="geopolitics",
    content="Testing Trading Floor integration - analyzing geopolitical markets..."
)
print(f"   Result: {'✅ Success' if result1 else '❌ Failed'}")
print()

# Test 2: Post thesis message
print("2. Posting 'thesis' message...")
result2 = post_thesis_message(
    agent_id="test-geo-agent",
    theme="geopolitics",
    thesis_text="Market underpriced based on recent diplomatic developments",
    market_question="Will Russia and Ukraine sign peace agreement by March 15?",
    current_odds=0.35,
    fair_value=0.65,
    edge=0.30,
    conviction=0.72,
    reasoning="Multiple diplomatic channels confirm backroom negotiations accelerating. Key European leaders scheduled to meet in Warsaw this weekend.",
    capital_allocated=250
)
print(f"   Result: {'✅ Success' if result2 else '❌ Failed'}")
print()

print("="*70)
print("VERIFICATION")
print("="*70)
print("Check Trading Floor at: http://localhost:3000/trading/floor")
print("You should see 2 messages from 'test-geo-agent':")
print("  1. Analyzing message (gray border)")
print("  2. Thesis message (blue border) with all metadata fields")
print("="*70)
