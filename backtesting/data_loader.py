"""
BASED MONEY - Historical Data Loader
Fetch and store resolved markets for backtesting
"""

import sys
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

# Import modules
sys.path.insert(0, '..')

from database.db import supabase, record_event


# Polymarket API endpoints
POLYMARKET_API_BASE = "https://gamma-api.polymarket.com"
MARKETS_ENDPOINT = f"{POLYMARKET_API_BASE}/markets"

# Target categories for diverse dataset
TARGET_CATEGORIES = ["geopolitical", "crypto", "sports"]


def fetch_historical_markets(
    days_back: int = 90,
    target_count: int = 200,
    categories: Optional[List[str]] = None
) -> int:
    """
    Fetch resolved markets from Polymarket API and store in historical_markets table.
    
    Fetches markets that:
    - Are closed/resolved
    - Resolved within the last {days_back} days
    - Fall into target categories (geopolitical, crypto, sports)
    
    Args:
        days_back: Number of days to look back for resolved markets (default: 90)
        target_count: Target number of markets to collect (default: 200)
        categories: List of categories to include (default: ["geopolitical", "crypto", "sports"])
    
    Returns:
        Count of markets successfully loaded
    """
    if categories is None:
        categories = TARGET_CATEGORIES
    
    print("\n" + "=" * 60)
    print("HISTORICAL MARKET DATA COLLECTION")
    print("=" * 60)
    print(f"📅 Target: Markets resolved in last {days_back} days")
    print(f"🎯 Goal: {target_count}+ markets")
    print(f"📂 Categories: {', '.join(categories)}")
    print()
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    print(f"⏰ Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M UTC')}\n")
    
    # Track results
    markets_loaded = 0
    markets_processed = 0
    markets_skipped = 0
    
    try:
        # Fetch resolved markets from API
        # Try multiple batches to reach target count
        batch_size = 500
        max_batches = 5  # Up to 2500 markets total
        
        for batch_num in range(max_batches):
            offset = batch_num * batch_size
            
            print(f"📡 Fetching batch {batch_num + 1} (offset={offset}, limit={batch_size})...")
            
            # Build query parameters
            params = {
                "closed": "true",  # Only resolved markets
                "limit": batch_size,
                "offset": offset,
            }
            
            # Make API request
            try:
                response = requests.get(
                    MARKETS_ENDPOINT,
                    params=params,
                    timeout=15,
                    headers={"User-Agent": "BasedMoney/1.0"}
                )
                
                if response.status_code != 200:
                    print(f"⚠️  API returned status {response.status_code}, stopping batch fetch")
                    break
                
                # Parse response
                data = response.json()
                
                # Handle different response structures
                if isinstance(data, dict) and "data" in data:
                    markets_data = data["data"]
                elif isinstance(data, list):
                    markets_data = data
                else:
                    print(f"⚠️  Unexpected response structure: {type(data)}")
                    break
                
                if not markets_data:
                    print("   No more markets returned, stopping batch fetch")
                    break
                
                print(f"   Retrieved {len(markets_data)} markets from API")
                
                # Process each market
                batch_loaded = 0
                for market_data in markets_data:
                    markets_processed += 1
                    
                    # Parse and filter market
                    historical_market = parse_historical_market(
                        market_data,
                        cutoff_date=cutoff_date,
                        target_categories=categories
                    )
                    
                    if historical_market:
                        # Save to database
                        success = save_historical_market(historical_market)
                        if success:
                            markets_loaded += 1
                            batch_loaded += 1
                    else:
                        markets_skipped += 1
                
                print(f"   ✅ Saved {batch_loaded} markets from this batch")
                print(f"   📊 Total loaded so far: {markets_loaded}")
                print()
                
                # Check if we've reached target
                if markets_loaded >= target_count:
                    print(f"🎯 Target reached! ({markets_loaded} >= {target_count})")
                    break
                
                # If batch returned fewer than batch_size, we've hit the end
                if len(markets_data) < batch_size:
                    print("   Reached end of available markets")
                    break
            
            except requests.exceptions.RequestException as e:
                print(f"❌ API request failed: {e}")
                break
        
        # Summary
        print("\n" + "=" * 60)
        print("COLLECTION SUMMARY")
        print("=" * 60)
        print(f"📊 Markets processed: {markets_processed}")
        print(f"✅ Markets loaded: {markets_loaded}")
        print(f"⏭️  Markets skipped: {markets_skipped}")
        
        # Check if we met minimum threshold
        if markets_loaded < 100:
            warning_msg = f"⚠️  WARNING: Only {markets_loaded} markets loaded (target: {target_count}, minimum: 100)"
            print(warning_msg)
            record_event(
                event_type="data_collection_warning",
                details={
                    "markets_loaded": markets_loaded,
                    "target": target_count,
                    "days_back": days_back,
                },
                severity="warning"
            )
        elif markets_loaded < target_count:
            print(f"⚠️  Below target: {markets_loaded}/{target_count} markets")
        else:
            print(f"✅ Target met: {markets_loaded}/{target_count} markets")
        
        # Log success event
        record_event(
            event_type="historical_data_collected",
            details={
                "markets_loaded": markets_loaded,
                "markets_processed": markets_processed,
                "days_back": days_back,
                "categories": categories,
            },
            severity="info"
        )
        
        print("=" * 60)
        print()
        
        return markets_loaded
    
    except Exception as e:
        error_msg = f"Failed to fetch historical markets: {str(e)}"
        print(f"❌ {error_msg}")
        record_event(
            event_type="data_collection_error",
            details={"error": error_msg, "type": type(e).__name__},
            severity="error"
        )
        return markets_loaded


def parse_historical_market(
    data: Dict[str, Any],
    cutoff_date: datetime,
    target_categories: List[str]
) -> Optional[Dict[str, Any]]:
    """
    Parse a resolved market from API response and filter.
    
    Args:
        data: Raw market data from API
        cutoff_date: Only include markets resolved after this date
        target_categories: Only include markets in these categories
    
    Returns:
        Dictionary ready for database insert, or None if filtered out
    """
    try:
        # Extract basic fields
        market_id = data.get("id") or data.get("market_id") or data.get("condition_id")
        question = data.get("question") or data.get("title") or ""
        category = (data.get("category") or data.get("tag") or "unknown").lower()
        
        # Validate required fields
        if not market_id or not question:
            return None
        
        # Filter by category
        if category not in target_categories:
            return None
        
        # Extract resolution data
        closed = bool(data.get("closed") or data.get("resolved") or False)
        if not closed:
            # Skip unresolved markets
            return None
        
        # Extract resolved_at timestamp
        resolved_at = None
        resolved_at_str = (
            data.get("resolved_at") or 
            data.get("closedAt") or 
            data.get("closed_at") or
            data.get("end_date_iso")
        )
        
        if resolved_at_str:
            try:
                resolved_at = datetime.fromisoformat(resolved_at_str.replace("Z", "+00:00"))
            except:
                try:
                    resolved_at = datetime.fromtimestamp(float(resolved_at_str))
                except:
                    # If we can't parse resolved_at, skip this market
                    return None
        
        if not resolved_at:
            return None
        
        # Filter by resolution date (must be after cutoff)
        if resolved_at < cutoff_date:
            return None
        
        # Extract resolution value (1.0 for YES, 0.0 for NO)
        resolution_value = None
        
        # Try different fields for resolution outcome
        outcome = (
            data.get("outcome") or 
            data.get("resolution") or 
            data.get("resolved_outcome")
        )
        
        if outcome:
            outcome_str = str(outcome).upper()
            if "YES" in outcome_str or outcome_str == "1" or outcome_str == "1.0":
                resolution_value = Decimal("1.0")
            elif "NO" in outcome_str or outcome_str == "0" or outcome_str == "0.0":
                resolution_value = Decimal("0.0")
        
        # Alternative: check if outcomes array has prices near 1.0 or 0.0
        if resolution_value is None and "outcomes" in data:
            outcomes = data["outcomes"]
            if isinstance(outcomes, list):
                for out in outcomes:
                    price = float(out.get("price", 0.0))
                    name = out.get("name", "").upper()
                    
                    # If YES price is very close to 1.0, it resolved YES
                    if "YES" in name and price > 0.95:
                        resolution_value = Decimal("1.0")
                        break
                    # If NO price is very close to 1.0, it resolved NO
                    elif "NO" in name and price > 0.95:
                        resolution_value = Decimal("0.0")
                        break
        
        if resolution_value is None:
            # Can't determine resolution value, skip
            return None
        
        # Extract prices at decision time
        yes_price = Decimal("0.0")
        no_price = Decimal("0.0")
        
        if "outcomes" in data and isinstance(data["outcomes"], list):
            for outcome in data["outcomes"]:
                outcome_name = outcome.get("name", "").upper()
                price = Decimal(str(outcome.get("price", 0.0)))
                
                if "YES" in outcome_name:
                    yes_price = price
                elif "NO" in outcome_name:
                    no_price = price
        elif "yes_price" in data:
            yes_price = Decimal(str(data.get("yes_price", 0.0)))
            no_price = Decimal(str(data.get("no_price", 0.0)))
        
        # Calculate complement if one is missing
        if yes_price > 0 and no_price == 0:
            no_price = Decimal("1.0") - yes_price
        elif no_price > 0 and yes_price == 0:
            yes_price = Decimal("1.0") - no_price
        
        # Extract volume
        volume_24h = Decimal(str(data.get("volume") or data.get("volume24hr") or 0.0))
        
        # Extract resolution_date (when market was scheduled to close)
        resolution_date = resolved_at  # Default to resolved_at
        end_date_str = data.get("end_date_iso") or data.get("endDate")
        if end_date_str:
            try:
                resolution_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            except:
                pass
        
        # Build historical market record
        historical_market = {
            "id": str(market_id),
            "question": question,
            "category": category,
            "yes_price": yes_price,
            "no_price": no_price,
            "volume_24h": volume_24h,
            "resolution_date": resolution_date.isoformat(),
            "resolution_value": resolution_value,
            "resolved_at": resolved_at.isoformat(),
        }
        
        return historical_market
    
    except Exception as e:
        # Silently skip markets with parse errors
        return None


def save_historical_market(market: Dict[str, Any]) -> bool:
    """
    Save a historical market to the database.
    
    Args:
        market: Historical market dictionary
    
    Returns:
        True if successful
    """
    try:
        # Upsert (update if exists, insert if new)
        result = supabase.table("historical_markets").upsert(market).execute()
        return True
    
    except Exception as e:
        # Log error but don't crash
        print(f"   ⚠️  Failed to save market {market.get('id')}: {e}")
        return False


def get_loaded_count() -> int:
    """
    Get count of markets currently in historical_markets table.
    
    Returns:
        Count of historical markets
    """
    try:
        result = supabase.table("historical_markets").select("id", count="exact").execute()
        return result.count or 0
    except Exception as e:
        print(f"❌ Error getting historical market count: {e}")
        return 0


# ============================================================
# MAIN (for testing)
# ============================================================

if __name__ == "__main__":
    print("\n🚀 Starting historical data collection...\n")
    
    # Check current count
    current_count = get_loaded_count()
    print(f"📊 Current historical markets in database: {current_count}\n")
    
    # Fetch historical markets
    loaded_count = fetch_historical_markets(
        days_back=90,
        target_count=200,
        categories=["geopolitical", "crypto", "sports"]
    )
    
    # Final count
    final_count = get_loaded_count()
    print(f"\n📊 Final historical markets in database: {final_count}")
    print(f"   ({loaded_count} newly loaded in this run)\n")
