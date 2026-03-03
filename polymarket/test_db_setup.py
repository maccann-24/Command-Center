#!/usr/bin/env python3
"""
Quick validation that database module is properly structured
"""

import sys

print("Testing database module imports...")

try:
    # Test config loads
    print("  → Loading config...")
    import config

    print(f"    ✓ TRADING_MODE: {config.TRADING_MODE}")
    print(f"    ✓ RISK_PARAMS: {config.RISK_PARAMS}")

    # Test models load
    print("  → Loading models...")
    from models import Thesis, Market, Position, NewsEvent, Portfolio

    print("    ✓ All models imported")

    # Test database module structure
    print("  → Loading database module...")
    from database import (
        save_thesis,
        get_theses,
        save_market,
        get_markets,
        save_position,
        record_event,
        save_news_event,
        get_historical_markets,
    )

    print("    ✓ All 8 required functions available")

    # Verify function signatures
    print("  → Verifying function signatures...")
    import inspect

    funcs = {
        "save_thesis": save_thesis,
        "get_theses": get_theses,
        "save_market": save_market,
        "get_markets": get_markets,
        "save_position": save_position,
        "record_event": record_event,
        "save_news_event": save_news_event,
        "get_historical_markets": get_historical_markets,
    }

    for name, func in funcs.items():
        sig = inspect.signature(func)
        print(f"    ✓ {name}{sig}")

    print("\n✅ All structure tests PASSED")
    print("\n💡 To test actual database connection:")
    print("   1. Set up Supabase project")
    print("   2. Run schema.sql in Supabase SQL editor")
    print("   3. Update .env with real SUPABASE_URL and SUPABASE_KEY")
    print("   4. Run: python database/db.py")

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print("\n💡 Install dependencies: pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
