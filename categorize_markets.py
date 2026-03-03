#!/usr/bin/env python3
"""
Categorize Markets

Apply categorization logic to all markets in database.
Updates category and theme fields.
"""

import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, '.')

from database.db import get_supabase_client
from ingestion.polymarket import categorize_from_question


# Theme mapping
CATEGORY_TO_THEME = {
    "politics": "politics",
    "geopolitics": "geopolitics", 
    "crypto": "crypto",
    "weather": "weather",
    "sports": None,  # No sports theme
    "tech": None,
    "unknown": None
}


def categorize_all_markets():
    """
    Fetch all markets from database and update their categories/themes.
    """
    
    print("="*80)
    print("📋 CATEGORIZING MARKETS")
    print("="*80)
    print()
    
    supabase = get_supabase_client()
    
    # Fetch all markets
    print("Step 1: Fetching all markets from database...")
    result = supabase.table('markets').select('*').execute()
    markets = result.data
    
    if not markets:
        print("❌ No markets found in database")
        return
    
    print(f"✅ Found {len(markets)} markets")
    print()
    
    # Categorize each market
    print("Step 2: Categorizing markets...")
    
    updated_count = 0
    category_stats = {}
    theme_stats = {}
    
    for market in markets:
        question = market.get('question', '')
        market_id = market.get('id')
        
        # Get category from question
        category = categorize_from_question(question)
        
        # Map category to theme
        theme = CATEGORY_TO_THEME.get(category)
        
        # Update stats
        category_stats[category] = category_stats.get(category, 0) + 1
        if theme:
            theme_stats[theme] = theme_stats.get(theme, 0) + 1
        
        # Update market in database
        try:
            update_data = {
                'category': category
            }
            
            supabase.table('markets').update(update_data).eq('id', market_id).execute()
            updated_count += 1
            
        except Exception as e:
            print(f"⚠️ Error updating market {market_id}: {e}")
            continue
    
    print(f"✅ Updated {updated_count} markets")
    print()
    
    # Summary
    print("="*80)
    print("📊 CATEGORIZATION SUMMARY")
    print("="*80)
    print()
    
    print("Categories:")
    for cat, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")
    
    print()
    print("Themes:")
    for theme, count in sorted(theme_stats.items(), key=lambda x: x[1], reverse=True):
        theme_name = theme if theme else "(none)"
        print(f"  {theme_name}: {count}")
    
    print()
    print("="*80)
    print("✅ CATEGORIZATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    categorize_all_markets()
