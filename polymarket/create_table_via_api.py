#!/usr/bin/env python3
"""
Create agent_messages table using Supabase REST API directly.
Since we can't execute arbitrary SQL, we'll create via API schema manipulation.
"""

import os
import requests
import json

# Load env
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set")
    exit(1)

print("="*70)
print("AUTO-CREATING agent_messages TABLE")
print("="*70)
print()

# Step 1: Check if table exists by trying to query it
print("1. Checking if table exists...")
url = f"{SUPABASE_URL}/rest/v1/agent_messages?limit=0"
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("   ✅ Table already exists!")
    exit(0)
elif "PGRST205" in response.text or "not found" in response.text.lower():
    print("   ⚠️ Table does not exist, creating...")
else:
    print(f"   ❌ Unexpected error: {response.text}")
    exit(1)

# Step 2: Create table using PostgREST's table creation
# Unfortunately, PostgREST doesn't support CREATE TABLE via REST API
# We need to use the Supabase Management API

print()
print("2. Attempting to create via Management API...")

# The Management API endpoint for database operations
# This requires a service role key or project API key
management_url = f"https://api.supabase.com/v1/projects/{SUPABASE_URL.split('//')[1].split('.')[0]}/database/migrations"

# Try to create a migration
migration_data = {
    "name": "create_agent_messages_table",
    "sql": open("migrations/create_agent_messages_table.sql").read()
}

# This will likely fail without proper auth, but let's try
response = requests.post(
    management_url,
    headers={
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    },
    json=migration_data
)

if response.status_code in [200, 201]:
    print("   ✅ Table created successfully!")
else:
    print(f"   ❌ Management API failed: {response.status_code}")
    print(f"   {response.text[:200]}")
    print()
    print("="*70)
    print("FALLBACK: Use SQL Editor")
    print("="*70)
    print("Since automatic creation failed, please run this SQL:")
    print()
    print(open("migrations/create_agent_messages_table.sql").read())
    print()
    print("Steps:")
    print("1. Go to: https://supabase.com/dashboard/project/anidsrakghbelumhvlls/sql/new")
    print("2. Paste the SQL above")
    print("3. Click 'Run'")
    print("4. Then run: python3 test_trading_floor_post.py")
    exit(1)
