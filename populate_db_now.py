#!/usr/bin/env python3
import requests
import sys
from datetime import datetime, timezone
from dotenv import dotenv_values
import os

# Load env
env = dotenv_values('.env')
os.environ.update(env)

sys.path.insert(0, '.')
from database.db import get_supabase_client

print("Fetching from CLOB API...")
url = "https://clob.polymarket.com/markets"
all_markets = []

for page in range(10):
    r = requests.get(url, params={'next_cursor': all_markets[-1].get('id') if all_markets else None} if all_markets else {}, timeout=10)
    data = r.json().get('data', [])
    if not data:
        break
    all_markets.extend(data)
    print(f"Page {page+1}: {len(all_markets)} total")

print(f"\n{len(all_markets)} markets fetched\n")

def cat(q):
    ql = q.lower()
    if any(k in ql for k in ['°c', '°f', 'celsius', 'fahrenheit']) or ('temperature' in ql and any(c in ql for c in ['london', 'new york', 'buenos aires'])):
        return 'weather'
    if 'bitcoin' in ql or 'ethereum' in ql or 'crypto' in ql:
        return 'crypto'
    if 'trump' in ql or 'biden' in ql or 'election' in ql:
        return 'politics'
    if 'russia' in ql or 'ukraine' in ql or 'china' in ql:
        return 'geopolitics'
    return 'unknown'

print("Inserting to DB...")
supabase = get_supabase_client()
supabase.table('markets').delete().neq('id', '').execute()

for i, m in enumerate(all_markets):
    if m.get('closed'):
        continue
    try:
        prices = m.get('outcomePrices', [])
        supabase.table('markets').upsert({
            'id': m['id'],
            'question': m['question'],
            'category': cat(m['question']),
            'yes_price': float(prices[0]) if prices else 0.0,
            'no_price': float(prices[1]) if len(prices) > 1 else 0.0,
            'volume_24h': float(m.get('volume24hr', 0)),
            'resolution_date': m.get('endDate'),
            'resolved': False,
            'liquidity_score': 0.0,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }).execute()
        if (i+1) % 100 == 0:
            print(f"  {i+1}...")
    except Exception as e:
        pass

print("Done")
