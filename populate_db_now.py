#!/usr/bin/env python3
import requests
import sys
from datetime import datetime, timezone
from dotenv import dotenv_values
import os

env = dotenv_values('.env')
os.environ.update(env)

sys.path.insert(0, '.')
from database.db import get_supabase_client

print("Fetching from CLOB API...")
url = "https://clob.polymarket.com/markets"
all_markets = []
next_cursor = None

for page in range(10):
    params = {}
    if next_cursor:
        params['next_cursor'] = next_cursor
    
    r = requests.get(url, params=params, timeout=10)
    data = r.json()
    markets = data.get('data', [])
    if not markets:
        break
    all_markets.extend(markets)
    next_cursor = data.get('next_cursor')
    print(f"Page {page+1}: {len(all_markets)} total")
    if not next_cursor:
        break

print(f"\n{len(all_markets)} markets fetched\n")

def cat(q):
    ql = q.lower()
    if any(k in ql for k in ['°c', '°f', 'celsius', 'fahrenheit']) or ('temperature' in ql and any(c in ql for c in ['london', 'new york', 'buenos aires', 'wellington'])):
        return 'weather'
    if 'bitcoin' in ql or 'ethereum' in ql or 'crypto' in ql or 'btc' in ql or 'eth' in ql:
        return 'crypto'
    if 'trump' in ql or 'biden' in ql or 'election' in ql or 'congress' in ql:
        return 'politics'
    if 'russia' in ql or 'ukraine' in ql or 'china' in ql or 'taiwan' in ql:
        return 'geopolitics'
    return 'unknown'

cats = {}
for m in all_markets:
    c = cat(m.get('question', ''))
    cats[c] = cats.get(c, 0) + 1

print("Categories:")
for c, n in sorted(cats.items(), key=lambda x: x[1], reverse=True):
    print(f"  {c}: {n}")
print()

print("Clearing old markets...")
supabase = get_supabase_client()
supabase.table('markets').delete().neq('id', '').execute()
print("Cleared\n")

print("Inserting...")
inserted = 0
errors = 0

for i, m in enumerate(all_markets):
    if m.get('closed'):
        continue
    try:
        prices = m.get('outcomePrices', [])
        data = {
            'id': str(m.get('id')),
            'question': m.get('question', 'Unknown'),
            'category': cat(m.get('question', '')),
            'yes_price': float(prices[0]) if prices and len(prices) > 0 else 0.0,
            'no_price': float(prices[1]) if prices and len(prices) > 1 else 0.0,
            'volume_24h': float(m.get('volume24hr', 0)),
            'resolution_date': m.get('endDate'),
            'resolved': False,
            'liquidity_score': 0.0,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        supabase.table('markets').upsert(data).execute()
        inserted += 1
        if inserted % 100 == 0:
            print(f"  {inserted} inserted...")
    except Exception as e:
        errors += 1
        if errors <= 5:
            print(f"Error on market {m.get('id')}: {e}")

print(f"\n✅ Inserted {inserted} markets")
print(f"⚠️ Errors: {errors}")
