"""
Test ThesisStore implementation
"""

import sys
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, '.')

from core.thesis_store import ThesisStore
from models import Thesis


def test_thesis_store():
    """
    Test ThesisStore methods:
    1. save(thesis)
    2. get_actionable(min_conviction)
    3. get_by_market(market_id)
    """
    
    print("\n🧪 Testing ThesisStore...")
    print("=" * 60)
    
    # Initialize store
    store = ThesisStore()
    
    # Create test thesis with conviction=0.75
    test_market_id = f"test_market_{uuid4().hex[:8]}"
    test_thesis = Thesis(
        id=uuid4(),
        agent_id="test_agent",
        market_id=test_market_id,
        edge=Decimal("0.15"),
        conviction=Decimal("0.75"),
        thesis_text="Test thesis for ThesisStore validation",
        reasoning="Testing the save and retrieval methods",
        signals=["test_signal"],
        target_side="yes",
        status="active",
        created_at=datetime.utcnow()
    )
    
    # Test 1: Save thesis
    print("\n1️⃣  Testing save()...")
    success = store.save(test_thesis)
    if success:
        print(f"   ✅ Thesis saved successfully (id: {test_thesis.id})")
    else:
        print(f"   ❌ Failed to save thesis")
        return False
    
    # Test 2: Get actionable with min_conviction=0.70 (should return the thesis)
    print("\n2️⃣  Testing get_actionable(0.70)...")
    actionable_theses = store.get_actionable(min_conviction=0.70)
    
    # Check if our test thesis is in the results
    found = any(t.id == test_thesis.id for t in actionable_theses)
    
    if found:
        print(f"   ✅ Found test thesis in actionable results")
        print(f"   📊 Returned {len(actionable_theses)} actionable thesis/theses")
        for t in actionable_theses:
            if t.id == test_thesis.id:
                print(f"   📝 Test thesis: conviction={t.conviction}, status={t.status}")
    else:
        print(f"   ❌ Test thesis NOT found in actionable results")
        print(f"   📊 Returned {len(actionable_theses)} other thesis/theses")
        return False
    
    # Test 3: Get actionable with min_conviction=0.80 (should return empty or exclude our thesis)
    print("\n3️⃣  Testing get_actionable(0.80)...")
    high_conviction_theses = store.get_actionable(min_conviction=0.80)
    
    # Check that our test thesis is NOT in these results
    found_in_high = any(t.id == test_thesis.id for t in high_conviction_theses)
    
    if not found_in_high:
        print(f"   ✅ Test thesis correctly excluded (conviction 0.75 < 0.80)")
        print(f"   📊 Returned {len(high_conviction_theses)} high-conviction thesis/theses")
    else:
        print(f"   ❌ Test thesis should NOT be in high-conviction results")
        return False
    
    # Test 4: Get by market
    print("\n4️⃣  Testing get_by_market()...")
    market_theses = store.get_by_market(test_market_id)
    
    found_by_market = any(t.id == test_thesis.id for t in market_theses)
    
    if found_by_market:
        print(f"   ✅ Found test thesis by market_id")
        print(f"   📊 Returned {len(market_theses)} thesis/theses for this market")
    else:
        print(f"   ❌ Test thesis NOT found by market_id")
        return False
    
    # Cleanup: Delete test thesis
    print("\n🧹 Cleaning up...")
    try:
        from database.db import supabase
        supabase.table("theses").delete().eq("id", str(test_thesis.id)).execute()
        print(f"   ✅ Test thesis deleted")
    except Exception as e:
        print(f"   ⚠️  Cleanup warning: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All ThesisStore tests PASSED!\n")
    
    return True


if __name__ == "__main__":
    try:
        success = test_thesis_store()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
