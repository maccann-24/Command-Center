#!/usr/bin/env python3
"""
Automatically create agent_messages table using Supabase REST API.
"""

import os
import sys
import requests

# Load Supabase credentials
SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set")
    sys.exit(1)

# Read migration SQL
migration_file = "migrations/create_agent_messages_table.sql"
print(f"📄 Reading migration: {migration_file}")

with open(migration_file, "r") as f:
    sql = f.read()

print(f"🚀 Creating agent_messages table...")
print(f"{'='*70}")

# Execute SQL via Supabase REST API
url = f"{SUPABASE_URL}/rest/v1/rpc/query"
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Try using PostgREST's query endpoint
# Note: This may not work if the RPC function doesn't exist
# In that case, we'll use psycopg2 directly
try:
    from supabase import create_client
    import psycopg2
    
    # Get connection string from Supabase
    # We'll need to construct it or use psycopg2
    
    # Alternative: Use psycopg2 directly if connection string is available
    conn_string = os.environ.get("DATABASE_URL")
    
    if conn_string:
        print("Using direct PostgreSQL connection...")
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Table created successfully via PostgreSQL!")
    else:
        # Fallback: Create table using Supabase client (insert approach)
        print("No DATABASE_URL found, using Supabase REST API approach...")
        
        # Since we can't execute arbitrary SQL via Supabase client,
        # let's use curl to hit the Database API
        import subprocess
        
        # Save SQL to temp file
        with open("/tmp/migration.sql", "w") as f:
            f.write(sql)
        
        # Use psql if available
        result = subprocess.run(
            ["which", "psql"],
            capture_output=True
        )
        
        if result.returncode == 0:
            print("Found psql, constructing connection string...")
            
            # Parse connection details from SUPABASE_URL
            # Format: https://PROJECT_REF.supabase.co
            project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
            
            # Prompt for database password or use service role key
            print(f"\n⚠️  Need database connection to execute migration.")
            print(f"Project: {project_ref}")
            print(f"\nOption 1: Get connection string from Supabase Dashboard:")
            print(f"  Settings → Database → Connection String (Postgres)")
            print(f"\nOption 2: Set DATABASE_URL environment variable")
            print(f"\nFor now, creating table via API insert (limited functionality)...\n")
            
            # Fallback: Create a dummy row to trigger table creation
            # This won't work, we need actual SQL execution
            print("❌ Cannot create table automatically without DATABASE_URL or psql access")
            print("\n📋 Manual steps required:")
            print("1. Go to Supabase Dashboard → SQL Editor")
            print("2. Run this SQL:")
            print(f"\n{sql}\n")
            sys.exit(1)
        else:
            print("❌ psql not found and no DATABASE_URL provided")
            print("\n📋 Manual steps required:")
            print("1. Go to Supabase Dashboard → SQL Editor")  
            print("2. Run: migrations/create_agent_messages_table.sql")
            sys.exit(1)

except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Install: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print(f"{'='*70}")
print()
print("🎉 agent_messages table ready!")
print()
print("Next: Run tests")
print("  python3 test_trading_floor_post.py")
