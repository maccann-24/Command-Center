#!/usr/bin/env python3
"""
Apply agent_messages table migration to Supabase.
Run: python apply_agent_messages_migration.py
"""

import os
import sys
from supabase import create_client

# Load Supabase credentials
SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set")
    sys.exit(1)

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Read migration SQL
migration_file = "migrations/create_agent_messages_table.sql"
print(f"📄 Reading migration: {migration_file}")

with open(migration_file, "r") as f:
    sql = f.read()

print(f"📊 Executing migration...")
print(f"{'='*70}")

try:
    # Execute the SQL
    result = supabase.rpc("exec_sql", {"sql": sql}).execute()
    
    print("✅ Migration executed successfully!")
    print(f"{'='*70}")
    print()
    print("🎉 agent_messages table created!")
    print()
    print("Next steps:")
    print("1. Run test_trading_floor_post.py to verify message posting works")
    print("2. Run test_geo_trading_floor.py to test full agent integration")
    print("3. Check Trading Floor at http://localhost:3000/trading/floor")
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
    print()
    print("Note: If exec_sql RPC doesn't exist, you'll need to run the SQL manually:")
    print("1. Go to Supabase Dashboard → SQL Editor")
    print("2. Copy the contents of migrations/create_agent_messages_table.sql")
    print("3. Paste and run the SQL")
    print()
    print("Or use the Supabase CLI:")
    print(f"  supabase db push")
    sys.exit(1)
