#!/usr/bin/env python3
"""
Refresh Markets from Polymarket CLOB API

Fetches ALL markets using the correct CLOB API endpoint.
Run twice daily at 8am and 6pm for thesis generation.
"""

import sys
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, '.')

from database.db import get_supabase_client


def categorize_market(question):
    """Categorize market from question text"""
    q_lower = question.lower()
    
    # Weather/Climate (check for actual weather terms, not just any temperature mention)
    if any(kw in q_lower for kw in ['°c', '°f', 'celsius', 'fahrenheit', 'climate', 'heat increase', 'global warming', 'global temperature', 'weather forecast']):
        return 'weather'
    # Temperature markets (specific pattern)
    if 'temperature' in q_lower and any(city in q_lower for city in ['london', 'new york', 'tokyo', 'paris', 'sydney', 'buenos aires', 'wellington']):
        return 'weather'
    
    # Politics
    if any(kw in q_lower for kw in ['trump', 'biden', 'harris', 'election', 'congress', 'senate', 'president', 'governor', 'republican', 'democrat']):
        return 'politics'
    
    # Crypto
    if any(kw in q_lower for kw in ['bitcoin', 'ethereum', 'crypto', 'btc', 'eth', 'solana', 'blockchain', 'defi', 'nft', 'dogecoin', 'cardano']):
        return 'crypto'
    
    # Geopolitics
    if any(kw in q_lower for kw in ['russia', 'ukraine', 'china', 'taiwan', 'iran', 'israel', 'war', 'nato', 'invasion', 'ceasefire']):
        return 'geopolitics'
    
    return 'unknown'


def fetch_all_markets():
    """Fetch all markets from CLOB API with pagination"""
    clob_url = "https://clob.polymarket.com/markets"
    
    all_markets = []
    next_cursor = None
    
    print("Fetching markets from CLOB API (correct endpoint)...")
    
    for page in range(20):  # Max 20 pages (1000 markets each = 20k total)
        params = {}
        if next_cursor:
            params['next_cursor'] = next_cursor
            
        try:
            response = requests.get(clob_url, params=params, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ API returned status {response.status_code}")
                break
                
            data = response.json()
            markets = data.get('data', [])
            all_markets.extend(markets)
            
            print(f"  Page {page+1}: +{len(markets)} markets (total: {len(all_markets)})")
            
            next_cursor = data.get('next_cursor')
            if not next_cursor or len(markets) == 0:
                break
        except Exception as e:
            print(f"⚠️ Error fetching page {page+1}: {e}")
            break
    
    return all_markets


def refresh_markets():
    """
    Refresh markets from Polymarket using CLOB API.
    
    1. Fetch ALL markets from CLOB API
    2. Filter for active/near-term markets
    3. Categorize each market
    4. Clear old markets from database
    5. Insert new markets
    """
    
    print("="*80)
    print("📊 REFRESHING MARKETS FROM POLYMARKET (CLOB API)")
    print("="*80)
    print()
    
    # Fetch all markets
    all_markets = fetch_all_markets()
    
    if not all_markets:
        print("❌ No markets fetched")
        return
    
    print(f"\n✅ Fetched {len(all_markets)} total markets from CLOB API")
    print()
    
    # Filter for active markets
    now = datetime.now(timezone.utc)
    cutoff_date = now + timedelta(days=30)
    
    active_markets = []
    for m in all_markets:
        # Skip closed markets
        if m.get('closed', False):
            continue
            
        # Check end date if available
        end_date_str = m.get('endDate')
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                if end_date > cutoff_date:
                    continue  # Too far in future
            except:
                pass
        
        active_markets.append(m)
    
    print(f"Active markets (≤30 days): {len(active_markets)}")
    print()
    
    # Categorize markets
    print("Categorizing markets...")
    category_stats = {}
    
    for market in active_markets:
        question = market.get('question', '')
        category = categorize_market(question)
        market['category'] = category
        category_stats[category] = category_stats.get(category, 0) + 1
    
    print()
    print("Category breakdown:")
    for cat, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")
    print()
    
    # Show samples from each category
    for cat in ['weather', 'crypto', 'politics', 'geopolitics']:
        samples = [m for m in active_markets if m.get('category') == cat][:3]
        if samples:
            print(f"{cat.upper()} samples:")
            for s in samples:
                print(f"  - {s.get('question')[:70]}")
            print()
    
    # Connect to database
    supabase = get_supabase_client()
    
    # Clear old markets
    print("Clearing old markets from database...")
    try:
        supabase.table('markets').delete().neq('id', '').execute()
        print("✅ Cleared old markets")
    except Exception as e:
        print(f"⚠️ Error clearing: {e}")
    
    print()
    
    # Insert new markets
    print("Inserting markets into database...")
    
    inserted_count = 0
    failed_count = 0
    
    for market in active_markets:
        try:
            # Extract prices from outcomePrices array
            outcome_prices = market.get('outcomePrices', [])
            yes_price = float(outcome_prices[0]) if len(outcome_prices) > 0 else 0.0
            no_price = float(outcome_prices[1]) if len(outcome_prices) > 1 else 0.0
            
            market_data = {
                'id': market.get('id') or market.get('condition_id'),
                'question': market.get('question'),
                'category': market.get('category', 'unknown'),
                'yes_price': yes_price,
                'no_price': no_price,
                'volume_24h': float(market.get('volume24hr', 0)),
                'resolution_date': market.get('endDate'),
                'resolved': market.get('closed', False),
                'liquidity_score': 0.0,
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            }
            
            supabase.table('markets').upsert(market_data).execute()
            inserted_count += 1
            
        except Exception as e:
            failed_count += 1
            if failed_count <= 5:  # Only show first 5 errors
                print(f"⚠️ Error inserting market: {e}")
            continue
    
    print(f"✅ Inserted {inserted_count} markets")
    if failed_count > 0:
        print(f"⚠️ Failed: {failed_count}")
    
    print()
    print("="*80)
    print("📈 REFRESH COMPLETE")
    print("="*80)
    print(f"  Total fetched: {len(all_markets)}")
    print(f"  Active (≤30 days): {len(active_markets)}")
    print(f"  Inserted: {inserted_count}")
    print()
    print("Category breakdown:")
    for cat, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")
    print("="*80)


if __name__ == "__main__":
    refresh_markets()
