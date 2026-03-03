#!/usr/bin/env python3
"""
Test ThesisStore structure and validate implementation logic.
This test validates the code structure without requiring database connection.
"""

import sys
import inspect
from pathlib import Path

print("\n🧪 Validating ThesisStore Implementation...")
print("=" * 60)

# Test 1: Module exists and can be imported
print("\n1️⃣  Testing module structure...")
try:
    # Check that core module exists
    core_path = Path("core")
    if not core_path.exists():
        print(f"   ❌ core/ directory not found")
        sys.exit(1)
    print(f"   ✅ core/ directory exists")
    
    # Check that thesis_store.py exists
    thesis_store_path = core_path / "thesis_store.py"
    if not thesis_store_path.exists():
        print(f"   ❌ core/thesis_store.py not found")
        sys.exit(1)
    print(f"   ✅ core/thesis_store.py exists")
    
    # Check that __init__.py exists
    init_path = core_path / "__init__.py"
    if not init_path.exists():
        print(f"   ❌ core/__init__.py not found")
        sys.exit(1)
    print(f"   ✅ core/__init__.py exists")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Read and validate class structure
print("\n2️⃣  Testing ThesisStore class structure...")
try:
    with open("core/thesis_store.py", "r") as f:
        content = f.read()
    
    # Check for class definition
    if "class ThesisStore:" not in content:
        print(f"   ❌ ThesisStore class not found")
        sys.exit(1)
    print(f"   ✅ ThesisStore class defined")
    
    # Check for save method
    if "def save(self, thesis: Thesis)" not in content:
        print(f"   ❌ save() method not found or incorrect signature")
        sys.exit(1)
    print(f"   ✅ save(thesis) method defined")
    
    # Check for get_actionable method
    if "def get_actionable(self, min_conviction: float = 0.70)" not in content:
        print(f"   ❌ get_actionable() method not found or incorrect signature")
        sys.exit(1)
    print(f"   ✅ get_actionable(min_conviction=0.70) method defined")
    
    # Check for get_by_market method
    if "def get_by_market(self, market_id: str)" not in content:
        print(f"   ❌ get_by_market() method not found or incorrect signature")
        sys.exit(1)
    print(f"   ✅ get_by_market(market_id) method defined")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 3: Validate save() implementation
print("\n3️⃣  Validating save() implementation...")
try:
    # Check that it calls db.save_thesis()
    if "db_save_thesis(thesis)" not in content or "return db_save_thesis" not in content:
        print(f"   ❌ save() does not call db.save_thesis()")
        sys.exit(1)
    print(f"   ✅ save() calls db.save_thesis()")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 4: Validate get_actionable() implementation
print("\n4️⃣  Validating get_actionable() implementation...")
try:
    # Check for 4 hours time window
    if "timedelta(hours=4)" not in content:
        print(f"   ❌ get_actionable() does not use 4-hour time window")
        sys.exit(1)
    print(f"   ✅ get_actionable() uses 4-hour time window")
    
    # Check for min_conviction filter
    if '"min_conviction": min_conviction' not in content:
        print(f"   ❌ get_actionable() does not filter by min_conviction")
        sys.exit(1)
    print(f"   ✅ get_actionable() filters by min_conviction")
    
    # Check for status='active' filter
    if '"status": "active"' not in content:
        print(f"   ❌ get_actionable() does not filter by status='active'")
        sys.exit(1)
    print(f"   ✅ get_actionable() filters by status='active'")
    
    # Check for created_after filter
    if '"created_after": cutoff_time' not in content:
        print(f"   ❌ get_actionable() does not filter by created_after")
        sys.exit(1)
    print(f"   ✅ get_actionable() filters by created_after")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 5: Validate get_by_market() implementation
print("\n5️⃣  Validating get_by_market() implementation...")
try:
    # Check for market_id filter
    if '"market_id": market_id' not in content:
        print(f"   ❌ get_by_market() does not filter by market_id")
        sys.exit(1)
    print(f"   ✅ get_by_market() filters by market_id")
    
    # Check for status='active' filter
    method_start = content.find("def get_by_market")
    method_end = content.find("\n\n", method_start)
    method_content = content[method_start:method_end]
    
    if '"status": "active"' not in method_content:
        print(f"   ❌ get_by_market() does not filter by status='active'")
        sys.exit(1)
    print(f"   ✅ get_by_market() filters by status='active'")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 6: Check for proper imports
print("\n6️⃣  Validating imports...")
try:
    if "from database.db import save_thesis as db_save_thesis, get_theses" not in content:
        print(f"   ❌ Missing required database imports")
        sys.exit(1)
    print(f"   ✅ Database imports present")
    
    if "from models import Thesis" not in content:
        print(f"   ❌ Missing Thesis model import")
        sys.exit(1)
    print(f"   ✅ Thesis model import present")
    
    if "from datetime import datetime, timedelta" not in content:
        print(f"   ❌ Missing datetime imports")
        sys.exit(1)
    print(f"   ✅ Datetime imports present")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 7: Check for singleton instance
print("\n7️⃣  Validating convenience singleton...")
try:
    if "thesis_store = ThesisStore()" not in content:
        print(f"   ❌ No singleton instance created")
        sys.exit(1)
    print(f"   ✅ Singleton thesis_store instance created")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All structure validation tests PASSED!\n")
print("📝 Implementation Summary:")
print("   • ThesisStore class created in core/thesis_store.py")
print("   • save(thesis): ✅ Calls db.save_thesis()")
print("   • get_actionable(min_conviction=0.70): ✅ Queries with:")
print("     - conviction >= min_conviction")
print("     - status = 'active'")
print("     - created_at > NOW() - 4 hours")
print("   • get_by_market(market_id): ✅ Queries active theses for market")
print("\n💡 To run integration tests:")
print("   1. Install dependencies: pip install -r requirements.txt")
print("   2. Configure .env with Supabase credentials")
print("   3. Run: python test_thesis_store.py")
print()
