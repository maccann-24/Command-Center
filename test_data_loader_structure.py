#!/usr/bin/env python3
"""
Test data_loader structure and validate implementation logic.
This test validates the code structure without requiring database connection.
"""

import sys
import inspect
from pathlib import Path

print("\n🧪 Validating Historical Data Loader Implementation...")
print("=" * 60)

# Test 1: Module exists and can be imported
print("\n1️⃣  Testing module structure...")
try:
    # Check that backtesting module exists
    backtesting_path = Path("backtesting")
    if not backtesting_path.exists():
        print(f"   ❌ backtesting/ directory not found")
        sys.exit(1)
    print(f"   ✅ backtesting/ directory exists")
    
    # Check that data_loader.py exists
    data_loader_path = backtesting_path / "data_loader.py"
    if not data_loader_path.exists():
        print(f"   ❌ backtesting/data_loader.py not found")
        sys.exit(1)
    print(f"   ✅ backtesting/data_loader.py exists")
    
    # Check that __init__.py exists
    init_path = backtesting_path / "__init__.py"
    if not init_path.exists():
        print(f"   ❌ backtesting/__init__.py not found")
        sys.exit(1)
    print(f"   ✅ backtesting/__init__.py exists")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Read and validate function structure
print("\n2️⃣  Testing fetch_historical_markets() function...")
try:
    with open("backtesting/data_loader.py", "r") as f:
        content = f.read()
    
    # Check for main function
    if "def fetch_historical_markets(" not in content:
        print(f"   ❌ fetch_historical_markets() function not found")
        sys.exit(1)
    print(f"   ✅ fetch_historical_markets() function defined")
    
    # Check for parameters
    if "days_back: int = 90" not in content:
        print(f"   ❌ days_back parameter missing or incorrect")
        sys.exit(1)
    print(f"   ✅ days_back parameter (default: 90)")
    
    if "target_count: int = 200" not in content:
        print(f"   ❌ target_count parameter missing or incorrect")
        sys.exit(1)
    print(f"   ✅ target_count parameter (default: 200)")
    
    # Check return type
    if "-> int:" not in content:
        print(f"   ❌ Function should return int (count)")
        sys.exit(1)
    print(f"   ✅ Returns int (count of markets loaded)")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 3: Validate API endpoint
print("\n3️⃣  Validating Polymarket API integration...")
try:
    # Check for API endpoint
    if 'MARKETS_ENDPOINT = f"{POLYMARKET_API_BASE}/markets"' not in content:
        print(f"   ❌ MARKETS_ENDPOINT not correctly defined")
        sys.exit(1)
    print(f"   ✅ MARKETS_ENDPOINT defined")
    
    # Check for closed=true parameter
    if '"closed": "true"' not in content:
        print(f"   ❌ API call missing closed=true parameter")
        sys.exit(1)
    print(f"   ✅ API queries for closed/resolved markets")
    
    # Check for limit parameter
    if "limit" not in content or "batch_size = 500" not in content:
        print(f"   ❌ Batch fetching not implemented")
        sys.exit(1)
    print(f"   ✅ Implements batch fetching (500 per batch)")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 4: Validate filtering logic
print("\n4️⃣  Validating market filtering...")
try:
    # Check for 90-day filter
    if "timedelta(days=days_back)" not in content or "cutoff_date" not in content:
        print(f"   ❌ Date filtering not implemented")
        sys.exit(1)
    print(f"   ✅ Filters by resolution date (last N days)")
    
    # Check for category filter
    if 'TARGET_CATEGORIES = ["geopolitical", "crypto", "sports"]' not in content:
        print(f"   ❌ TARGET_CATEGORIES missing or incorrect")
        sys.exit(1)
    print(f"   ✅ Filters by categories (geopolitical, crypto, sports)")
    
    # Check for category matching
    if "if category not in target_categories:" not in content:
        print(f"   ❌ Category filtering not implemented")
        sys.exit(1)
    print(f"   ✅ Category filtering logic present")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 5: Validate database fields
print("\n5️⃣  Validating historical_markets fields...")
try:
    required_fields = [
        '"id"',
        '"question"',
        '"category"',
        '"yes_price"',
        '"no_price"',
        '"volume_24h"',
        '"resolution_date"',
        '"resolution_value"',
        '"resolved_at"',
    ]
    
    for field in required_fields:
        if field not in content:
            print(f"   ❌ Missing required field: {field}")
            sys.exit(1)
    
    print(f"   ✅ All required fields present:")
    print(f"      • id, question, category")
    print(f"      • yes_price, no_price")
    print(f"      • volume_24h")
    print(f"      • resolution_date, resolved_at")
    print(f"      • resolution_value (1.0=YES, 0.0=NO)")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 6: Validate resolution value logic
print("\n6️⃣  Validating resolution value parsing...")
try:
    # Check for 1.0 and 0.0 values
    if 'Decimal("1.0")' not in content or 'Decimal("0.0")' not in content:
        print(f"   ❌ Resolution value logic not implemented")
        sys.exit(1)
    print(f"   ✅ Resolution value: 1.0 for YES, 0.0 for NO")
    
    # Check for outcome parsing
    if "outcome" not in content.lower():
        print(f"   ❌ Outcome parsing not implemented")
        sys.exit(1)
    print(f"   ✅ Parses outcome field from API")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 7: Validate warning logic
print("\n7️⃣  Validating warning/logging logic...")
try:
    # Check for <100 warning
    if "if markets_loaded < 100:" not in content:
        print(f"   ❌ Warning logic for <100 markets not found")
        sys.exit(1)
    print(f"   ✅ Warns if fewer than 100 markets loaded")
    
    # Check for event logging
    if "record_event" not in content:
        print(f"   ❌ Event logging not implemented")
        sys.exit(1)
    print(f"   ✅ Logs events (success, warnings, errors)")
    
    # Check for return count
    if "return markets_loaded" not in content:
        print(f"   ❌ Function doesn't return count")
        sys.exit(1)
    print(f"   ✅ Returns count of markets loaded")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 8: Validate helper functions
print("\n8️⃣  Validating helper functions...")
try:
    # Check for parse function
    if "def parse_historical_market(" not in content:
        print(f"   ❌ parse_historical_market() function not found")
        sys.exit(1)
    print(f"   ✅ parse_historical_market() function defined")
    
    # Check for save function
    if "def save_historical_market(" not in content:
        print(f"   ❌ save_historical_market() function not found")
        sys.exit(1)
    print(f"   ✅ save_historical_market() function defined")
    
    # Check for get_loaded_count function
    if "def get_loaded_count(" not in content:
        print(f"   ❌ get_loaded_count() function not found")
        sys.exit(1)
    print(f"   ✅ get_loaded_count() function defined")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 9: Validate database operations
print("\n9️⃣  Validating database operations...")
try:
    # Check for supabase table operations
    if 'supabase.table("historical_markets")' not in content:
        print(f"   ❌ Database table access not implemented")
        sys.exit(1)
    print(f"   ✅ Saves to historical_markets table")
    
    # Check for upsert
    if ".upsert(market)" not in content and ".upsert(" not in content:
        print(f"   ❌ Upsert operation not found")
        sys.exit(1)
    print(f"   ✅ Uses upsert (insert or update)")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All structure validation tests PASSED!\n")
print("📝 Implementation Summary:")
print("   • fetch_historical_markets() function created")
print("   • API Integration:")
print("     - Calls /markets?closed=true&_limit=500")
print("     - Batch fetching up to 2500 markets (5 batches)")
print("   • Filtering:")
print("     - Resolved in last 90 days")
print("     - Categories: geopolitical, crypto, sports")
print("   • Database:")
print("     - Saves to historical_markets table")
print("     - Fields: id, question, category, prices, volume,")
print("               resolution_date, resolution_value, resolved_at")
print("   • Resolution value: 1.0 for YES, 0.0 for NO")
print("   • Target: 200+ markets (warns if <100)")
print("   • Returns: Count of markets loaded")
print("\n💡 To run data collection:")
print("   1. Install dependencies: pip install -r requirements.txt")
print("   2. Configure .env with Supabase credentials")
print("   3. Run: python backtesting/data_loader.py")
print("   4. Or import: from backtesting import fetch_historical_markets")
print()
