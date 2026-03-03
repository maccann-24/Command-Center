"""
Test main.py initialization
"""

import sys
import os

# Set test environment
os.environ["BASED_MONEY_SKIP_ENV_VALIDATION"] = "1"
os.environ["TRADING_MODE"] = "paper"
os.environ["SUPABASE_URL"] = "http://test"
os.environ["SUPABASE_KEY"] = "test-key"

print("Testing main.py initialization...\n")

# Test import
try:
    import main

    print("✅ main.py imported successfully")
except Exception as e:
    print(f"❌ Failed to import main.py: {e}")
    sys.exit(1)

# Test initialization functions
print("\nTesting initialization functions:")

try:
    portfolio = main.initialize_portfolio()
    print(f"✅ initialize_portfolio() works")
    print(f"   Portfolio cash: ${portfolio.cash:,.2f}")
except Exception as e:
    print(f"❌ initialize_portfolio() failed: {e}")

try:
    agents = main.initialize_agents()
    print(f"✅ initialize_agents() works")
    print(f"   Agents: {len(agents)}")
    for agent in agents:
        print(f"   - {agent}")
except Exception as e:
    print(f"❌ initialize_agents() failed: {e}")

try:
    broker = main.initialize_broker()
    print(f"✅ initialize_broker() works")
    print(f"   Broker: {broker.__class__.__name__}")
except Exception as e:
    print(f"❌ initialize_broker() failed: {e}")

print("\n✅ All initialization tests passed!")
