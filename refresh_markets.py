#!/usr/bin/env python3
"""
Refresh Markets from Polymarket

Fetches markets resolving within the next 30 days.
Run twice daily at 8am and 6pm for thesis generation.
"""

import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, '.')
sys.path.insert(0, 'polymarket')

from database.db import get_supabase_client
from polymarket.ingestion.polymarket import fetch_markets


def refresh_markets():
    """
    Refresh markets from Polymarket.
    
    1. Fetch fresh markets from Polymarket API
    2. Filter for markets resolving within 30 days
    3. Clear old markets from database
    4. Insert new markets
    """
    
    print("="*80)
    print("📊 REFRESHING MARKETS FROM POLYMARKET")
    print("="*80)
    print()
    
    # Calculate 30-day cutoff
    from datetime import timezone
    now = datetime.now(timezone.utc)
    cutoff_date = now + timedelta(days=30)
    
    print(f"Current time: {now.isoformat()}")
    print(f"Cutoff date: {cutoff_date.isoformat()}")
    print(f"Fetching markets resolving before {cutoff_date.strftime('%Y-%m-%d')}")
    print()
    
    # Fetch markets from Polymarket
    print("Step 1: Fetching markets from Polymarket API...")
    all_markets = fetch_markets(limit=500, active_only=True)
    
    if not all_markets:
        print("❌ No markets fetched from Polymarket")
        return
    
    print(f"✅ Fetched {len(all_markets)} markets from Polymarket")
    print()
    
    # Filter for markets within 30 days
    print("Step 2: Filtering for markets resolving within 30 days...")
    near_term_markets = []
    
    for market in all_markets:
        if market.resolution_date:
            # Check if resolution date is within 30 days
            if market.resolution_date <= cutoff_date:
                near_term_markets.append(market)
        else:
            # No resolution date - include if not resolved
            if not market.resolved:
                near_term_markets.append(market)
    
    print(f"✅ Filtered to {len(near_term_markets)} markets resolving within 30 days")
    
    if not near_term_markets:
        print("⚠️ No near-term markets found")
        return
    
    print()
    
    # Show sample
    print("Sample markets:")
    for i, market in enumerate(near_term_markets[:5], 1):
        res_date = market.resolution_date.strftime('%Y-%m-%d') if market.resolution_date else 'Unknown'
        print(f"  {i}. {market.question[:70]}")
        print(f"     Resolves: {res_date} | Category: {market.category}")
    print()
    
    # Connect to database
    supabase = get_supabase_client()
    
    # Step 3: Clear old markets
    print("Step 3: Clearing old markets from database...")
    try:
        # Delete all existing markets
        delete_result = supabase.table('markets').delete().neq('id', '').execute()
        print(f"✅ Cleared old markets")
    except Exception as e:
        print(f"⚠️ Error clearing old markets: {e}")
        print("   Continuing with insert...")
    
    print()
    
    # Step 4: Insert new markets
    print("Step 4: Inserting new markets...")
    
    inserted_count = 0
    failed_count = 0
    
    for market in near_term_markets:
        try:
            # Prepare market data
            market_data = {
                'id': market.id,
                'question': market.question,
                'category': market.category,
                'yes_price': market.yes_price,
                'no_price': market.no_price,
                'volume_24h': market.volume_24h,
                'resolution_date': market.resolution_date.isoformat() if market.resolution_date else None,
                'resolved': market.resolved,
                'liquidity_score': market.liquidity_score,
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            }
            
            # Upsert to database
            result = supabase.table('markets').upsert(market_data).execute()
            inserted_count += 1
            
        except Exception as e:
            print(f"⚠️ Error inserting market {market.id}: {e}")
            failed_count += 1
            continue
    
    print(f"✅ Inserted {inserted_count} markets")
    if failed_count > 0:
        print(f"⚠️ Failed to insert {failed_count} markets")
    
    print()
    
    # Summary
    print("="*80)
    print("📈 MARKET REFRESH SUMMARY")
    print("="*80)
    print(f"  Fetched from API: {len(all_markets)}")
    print(f"  Filtered (≤30 days): {len(near_term_markets)}")
    print(f"  Inserted to DB: {inserted_count}")
    print(f"  Failed: {failed_count}")
    print()
    print(f"  Cutoff date: {cutoff_date.strftime('%Y-%m-%d')}")
    print(f"  Next refresh: 8am or 6pm (scheduled via cron)")
    print()
    
    # Show category breakdown
    print("Category breakdown:")
    categories = {}
    for market in near_term_markets:
        cat = market.category
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")
    
    print()
    print("="*80)
    print("✅ REFRESH COMPLETE")
    print("="*80)


if __name__ == "__main__":
    refresh_markets()
