#!/usr/bin/env python3
"""
Fetch real Polymarket data and save to database.

Usage:
  python3 fetch_polymarket_markets.py [--limit 100] [--clear-existing]
"""

import argparse
import sys

from ingestion.polymarket import fetch_markets
from database import save_market
from database.db import get_supabase_client


def clear_existing_markets():
    """Clear all existing markets from the database."""
    print("🗑️  Clearing existing markets...")
    sb = get_supabase_client()
    
    try:
        result = sb.table("markets").delete().neq("id", "").execute()
        print(f"✅ Cleared existing markets")
    except Exception as e:
        print(f"⚠️  Error clearing markets: {e}")


def main():
    parser = argparse.ArgumentParser(description="Fetch Polymarket markets and save to database")
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Number of markets to fetch from API before filtering (default: 500)"
    )
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Clear existing markets before fetching new ones"
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Filter by specific category (optional)"
    )
    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="Don't filter to agent themes (keep all categories including sports/pop-culture)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("POLYMARKET MARKET FETCHER")
    print("=" * 60)
    print()
    
    # Clear existing if requested
    if args.clear_existing:
        clear_existing_markets()
        print()
    
    # Fetch markets from Polymarket API
    print(f"📡 Fetching up to {args.limit} markets from Polymarket...")
    markets = fetch_markets(limit=args.limit, active_only=True)
    
    if not markets:
        print("❌ No markets fetched. Check your internet connection or API availability.")
        return 1
    
    print(f"✅ Fetched {len(markets)} markets")
    print()
    
    # Filter by category if requested
    if args.category:
        markets = [m for m in markets if m.category.lower() == args.category.lower()]
        print(f"📊 Filtered to {len(markets)} markets in category '{args.category}'")
        print()
    elif not args.no_filter:
        # Default: Only keep markets in the 4 agent themes
        target_categories = {'politics', 'geopolitics', 'crypto', 'weather'}
        original_count = len(markets)
        markets = [m for m in markets if m.category in target_categories]
        print(f"📊 Filtered to {len(markets)}/{original_count} markets in agent themes:")
        print(f"   (politics, geopolitics, crypto, weather)")
        print()
    else:
        print(f"📊 Keeping all {len(markets)} markets (no filter applied)")
        print()
    
    # Save to database
    print("💾 Saving markets to database...")
    saved_count = 0
    category_counts = {}
    
    for market in markets:
        try:
            success = save_market(market)
            if success:
                saved_count += 1
                category_counts[market.category] = category_counts.get(market.category, 0) + 1
        except Exception as e:
            print(f"⚠️  Error saving market {market.id}: {e}")
    
    print(f"✅ Saved {saved_count}/{len(markets)} markets to database")
    print()
    
    # Show category breakdown
    print("📊 Markets by category:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {category}: {count} markets")
    
    print()
    print("=" * 60)
    print("✅ COMPLETE")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Check the markets in Supabase")
    print("  2. Run agent tests to see them analyze real markets:")
    print("     python3 test_goldman_politics_trading_floor.py")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
