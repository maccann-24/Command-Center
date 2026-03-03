#!/usr/bin/env python3
"""
Fetch Weather Markets from Polymarket CLOB API
The gamma API doesn't return all markets - use CLOB API instead
"""

import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from database.db import get_supabase_client

def fetch_all_markets_from_clob():
    """Fetch all markets from CLOB API with pagination"""
    clob_url = "https://clob.polymarket.com/markets"
    
    all_markets = []
    next_cursor = None
    
    print("Fetching all markets from CLOB API...")
    
    for page in range(100):  # Max 100 pages
        params = {}
        if next_cursor:
            params['next_cursor'] = next_cursor
            
        response = requests.get(clob_url, params=params, timeout=10)
        if response.status_code != 200:
            break
            
        data = response.json()
        markets = data.get('data', [])
        all_markets.extend(markets)
        
        print(f"  Page {page+1}: {len(markets)} markets (total: {len(all_markets)})")
        
        next_cursor = data.get('next_cursor')
        if not next_cursor:
            break
    
    return all_markets


def categorize_market(question):
    """Categorize market from question text"""
    q_lower = question.lower()
    
    # Weather/Climate
    if any(kw in q_lower for kw in ['temperature', '°', 'degrees', 'celsius', 'fahrenheit', 'climate', 'heat increase']):
        return 'weather'
    
    # Politics
    if any(kw in q_lower for kw in ['trump', 'biden', 'election', 'congress', 'president', 'governor']):
        return 'politics'
    
    # Crypto
    if any(kw in q_lower for kw in ['bitcoin', 'ethereum', 'crypto', 'btc', 'eth']):
        return 'crypto'
    
    # Geopolitics
    if any(kw in q_lower for kw in ['russia', 'ukraine', 'china', 'taiwan', 'war', 'nato']):
        return 'geopolitics'
    
    return 'unknown'


def main():
    print("="*80)
    print("FETCHING WEATHER MARKETS FROM POLYMARKET")
    print("="*80)
    print()
    
    # Fetch all markets
    all_markets = fetch_all_markets_from_clob()
    print(f"\nTotal markets fetched: {len(all_markets)}")
    
    # Filter for weather
    weather_keywords = ['temperature', '°', 'degrees', 'celsius', 'fahrenheit', 'climate', 'heat increase']
    
    weather_markets = []
    for m in all_markets:
        question = m.get('question', '')
        if any(kw in question for kw in weather_keywords):
            weather_markets.append(m)
    
    print(f"Weather markets found: {len(weather_markets)}")
    print()
    
    if not weather_markets:
        print("❌ No weather markets found")
        return
    
    # Show samples
    print("Sample weather markets:")
    for m in weather_markets[:10]:
        print(f"  - {m.get('question')}")
    print()
    
    # Insert into database
    supabase = get_supabase_client()
    
    print("Inserting weather markets into database...")
    inserted = 0
    
    for market in weather_markets:
        try:
            market_data = {
                'id': market.get('id') or market.get('condition_id'),
                'question': market.get('question'),
                'category': 'weather',
                'yes_price': float(market.get('outcomePrices', [0, 0])[0]) if market.get('outcomePrices') else 0.0,
                'no_price': float(market.get('outcomePrices', [0, 0])[1]) if market.get('outcomePrices') else 0.0,
                'volume_24h': float(market.get('volume24hr', 0)),
                'resolution_date': market.get('endDate'),
                'resolved': market.get('closed', False),
                'liquidity_score': 0.0,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            supabase.table('markets').upsert(market_data).execute()
            inserted += 1
            
        except Exception as e:
            print(f"⚠️ Error inserting market: {e}")
            continue
    
    print(f"✅ Inserted {inserted} weather markets")
    print()
    print("="*80)
    print("COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
