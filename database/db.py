"""
BASED MONEY - Database Layer
Supabase client and core database functions
"""

import sys
from typing import List, Dict, Optional, Any
from datetime import datetime, date
try:
    from supabase import create_client, Client  # type: ignore
except Exception:  # pragma: no cover
    create_client = None
    Client = Any  # type: ignore

# Import config (will validate env vars)
try:
    from config import SUPABASE_URL, SUPABASE_KEY
except ImportError:
    # Handle case where we're running from different directory
    sys.path.insert(0, '..')
    from config import SUPABASE_URL, SUPABASE_KEY

from models import Thesis, Market, Position, NewsEvent


# ============================================================
# SUPABASE CLIENT
# ============================================================

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client (singleton pattern)."""
    global _supabase_client

    if create_client is None:
        raise RuntimeError(
            "Supabase dependency not installed. Install requirements.txt to use database features."
        )

    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

    return _supabase_client


class _SupabaseProxy:
    """Lazy proxy so modules can import database.db without having Supabase installed/configured."""

    def __getattr__(self, item: str):
        return getattr(get_supabase_client(), item)


# Convenience reference (lazy)
supabase = _SupabaseProxy()


# ============================================================
# THESIS FUNCTIONS
# ============================================================

def save_thesis(thesis: Thesis) -> bool:
    """
    Save a thesis to the database.
    
    Args:
        thesis: Thesis object to save
    
    Returns:
        True if successful, False otherwise
    """
    try:
        data = thesis.to_dict()
        
        # Upsert (insert or update)
        result = supabase.table("theses").upsert(data).execute()
        
        # Log event
        record_event(
            event_type="thesis_created",
            agent_id=thesis.agent_id,
            market_id=thesis.market_id,
            thesis_id=thesis.id,
            details={
                "edge": float(thesis.edge),
                "conviction": float(thesis.conviction),
                "thesis_text": thesis.thesis_text[:100],
            },
            severity="info"
        )
        
        return True
    
    except Exception as e:
        print(f"❌ Error saving thesis: {e}")
        record_event(
            event_type="database_error",
            details={"error": str(e), "function": "save_thesis"},
            severity="error"
        )
        return False


def get_theses(filters: Optional[Dict[str, Any]] = None) -> List[Thesis]:
    """
    Retrieve theses from database with optional filters.
    
    Args:
        filters: Dictionary of filter conditions
            - agent_id: Filter by agent
            - market_id: Filter by market
            - status: Filter by status ('active', 'executed', etc.)
            - min_conviction: Minimum conviction level
            - created_after: Only theses created after this datetime
    
    Returns:
        List of Thesis objects
    """
    try:
        query = supabase.table("theses").select("*")
        
        # Apply filters
        if filters:
            if "agent_id" in filters:
                query = query.eq("agent_id", filters["agent_id"])
            
            if "market_id" in filters:
                query = query.eq("market_id", filters["market_id"])
            
            if "status" in filters:
                query = query.eq("status", filters["status"])
            
            if "min_conviction" in filters:
                query = query.gte("conviction", filters["min_conviction"])
            
            if "created_after" in filters:
                iso_time = filters["created_after"].isoformat()
                query = query.gt("created_at", iso_time)
        
        # Order by conviction (highest first)
        query = query.order("conviction", desc=True)
        
        result = query.execute()
        
        # Convert to Thesis objects
        theses = [Thesis.from_dict(row) for row in result.data]
        
        return theses
    
    except Exception as e:
        print(f"❌ Error fetching theses: {e}")
        record_event(
            event_type="database_error",
            details={"error": str(e), "function": "get_theses"},
            severity="error"
        )
        return []


# ============================================================
# MARKET FUNCTIONS
# ============================================================

def save_market(market: Market) -> bool:
    """
    Save a market to the database.
    
    Args:
        market: Market object to save
    
    Returns:
        True if successful
    """
    try:
        data = market.to_dict()
        
        # Upsert (update if exists, insert if new)
        result = supabase.table("markets").upsert(data).execute()
        
        return True
    
    except Exception as e:
        print(f"❌ Error saving market: {e}")
        record_event(
            event_type="database_error",
            details={"error": str(e), "function": "save_market"},
            severity="error"
        )
        return False


def get_markets(filters: Optional[Dict[str, Any]] = None) -> List[Market]:
    """
    Retrieve markets from database with optional filters.
    
    Args:
        filters: Dictionary of filter conditions
            - category: Filter by category
            - min_volume: Minimum 24h volume
            - resolved: Filter by resolution status
            - tradeable: Only tradeable markets (volume + days checks)
    
    Returns:
        List of Market objects
    """
    try:
        query = supabase.table("markets").select("*")
        
        # Apply filters
        if filters:
            if "category" in filters:
                query = query.eq("category", filters["category"])
            
            if "min_volume" in filters:
                query = query.gte("volume_24h", filters["min_volume"])
            
            if "resolved" in filters:
                query = query.eq("resolved", filters["resolved"])
        
        # Order by volume (highest first)
        query = query.order("volume_24h", desc=True)
        
        result = query.execute()
        
        # Convert to Market objects
        markets = [Market.from_dict(row) for row in result.data]
        
        # Apply tradeable filter if requested
        if filters and filters.get("tradeable"):
            from config import MARKET_FILTERS
            markets = [
                m for m in markets
                if m.is_tradeable(
                    min_volume=MARKET_FILTERS["min_volume_24h"],
                    min_days=MARKET_FILTERS["min_days_to_resolution"]
                )
            ]
        
        return markets
    
    except Exception as e:
        print(f"❌ Error fetching markets: {e}")
        record_event(
            event_type="database_error",
            details={"error": str(e), "function": "get_markets"},
            severity="error"
        )
        return []


# ============================================================
# POSITION FUNCTIONS
# ============================================================

def save_position(position: Position) -> bool:
    """
    Save a position to the database.
    
    Args:
        position: Position object to save
    
    Returns:
        True if successful
    """
    try:
        data = position.to_dict()
        
        # Upsert
        result = supabase.table("positions").upsert(data).execute()
        
        # Log event
        record_event(
            event_type="position_created" if position.status == "open" else "position_updated",
            market_id=position.market_id,
            thesis_id=position.thesis_id,
            position_id=position.id,
            details={
                "side": position.side,
                "shares": float(position.shares),
                "entry_price": float(position.entry_price),
                "pnl": float(position.pnl),
                "status": position.status,
            },
            severity="info"
        )
        
        return True
    
    except Exception as e:
        print(f"❌ Error saving position: {e}")
        record_event(
            event_type="database_error",
            details={"error": str(e), "function": "save_position"},
            severity="error"
        )
        return False


def get_positions(filters: Optional[Dict[str, Any]] = None) -> List[Position]:
    """
    Retrieve positions from database with optional filters.
    
    Args:
        filters: Dictionary of filter conditions
            - status: Filter by status ('open', 'closed', etc.)
            - market_id: Filter by market
    
    Returns:
        List of Position objects
    """
    try:
        query = supabase.table("positions").select("*")
        
        # Apply filters
        if filters:
            if "status" in filters:
                query = query.eq("status", filters["status"])
            
            if "market_id" in filters:
                query = query.eq("market_id", filters["market_id"])
        
        # Order by opened_at (most recent first)
        query = query.order("opened_at", desc=True)
        
        result = query.execute()
        
        # Convert to Position objects
        positions = [Position.from_dict(row) for row in result.data]
        
        return positions
    
    except Exception as e:
        print(f"❌ Error fetching positions: {e}")
        return []


# ============================================================
# NEWS EVENT FUNCTIONS
# ============================================================

def save_news_event(news_event: NewsEvent) -> bool:
    """
    Save a news event to the database.
    
    Args:
        news_event: NewsEvent object to save
    
    Returns:
        True if successful
    """
    try:
        data = news_event.to_dict()
        
        # Insert (news events are append-only)
        result = supabase.table("news_events").insert(data).execute()
        
        return True
    
    except Exception as e:
        print(f"❌ Error saving news event: {e}")
        record_event(
            event_type="database_error",
            details={"error": str(e), "function": "save_news_event"},
            severity="error"
        )
        return False


def get_news_events(filters: Optional[Dict[str, Any]] = None) -> List[NewsEvent]:
    """
    Retrieve news events from database with optional filters.
    
    Args:
        filters: Dictionary of filter conditions
            - source: Filter by source
            - after_timestamp: Only events after this datetime
            - hours_back: Only events in last N hours
    
    Returns:
        List of NewsEvent objects
    """
    try:
        query = supabase.table("news_events").select("*")
        
        # Apply filters
        if filters:
            if "source" in filters:
                query = query.eq("source", filters["source"])
            
            if "after_timestamp" in filters:
                iso_time = filters["after_timestamp"].isoformat()
                query = query.gt("timestamp", iso_time)
            
            if "hours_back" in filters:
                from datetime import timedelta
                cutoff = datetime.utcnow() - timedelta(hours=filters["hours_back"])
                query = query.gt("timestamp", cutoff.isoformat())
        
        # Order by timestamp (most recent first)
        query = query.order("timestamp", desc=True)
        
        result = query.execute()
        
        # Convert to NewsEvent objects
        events = [NewsEvent.from_dict(row) for row in result.data]
        
        return events
    
    except Exception as e:
        print(f"❌ Error fetching news events: {e}")
        return []


# ============================================================
# HISTORICAL MARKETS FUNCTIONS
# ============================================================

def get_historical_markets(start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """
    Retrieve historical (resolved) markets for backtesting.
    
    Args:
        start_date: Start of date range (resolution_date)
        end_date: End of date range (resolution_date)
    
    Returns:
        List of historical market dictionaries
    """
    try:
        query = supabase.table("historical_markets").select("*")
        
        # Filter by resolution date range
        query = query.gte("resolution_date", start_date.isoformat())
        query = query.lte("resolution_date", end_date.isoformat())
        
        # Order by resolution date
        query = query.order("resolution_date", desc=False)
        
        result = query.execute()
        
        return result.data
    
    except Exception as e:
        print(f"❌ Error fetching historical markets: {e}")
        record_event(
            event_type="database_error",
            details={"error": str(e), "function": "get_historical_markets"},
            severity="error"
        )
        return []


# ============================================================
# EVENT LOG FUNCTIONS
# ============================================================

def record_event(
    event_type: str,
    agent_id: Optional[str] = None,
    market_id: Optional[str] = None,
    thesis_id: Optional[Any] = None,
    position_id: Optional[Any] = None,
    details: Optional[Dict[str, Any]] = None,
    severity: str = "info"
) -> bool:
    """
    Record an event to the append-only event log.
    
    Args:
        event_type: Type of event (e.g., 'thesis_created', 'trade_executed')
        agent_id: Agent identifier (optional)
        market_id: Market identifier (optional)
        thesis_id: Thesis UUID (optional)
        position_id: Position UUID (optional)
        details: Additional event details as JSON (optional)
        severity: 'info', 'warning', 'error', or 'critical'
    
    Returns:
        True if successful
    """
    try:
        # Convert UUIDs to strings
        thesis_id_str = str(thesis_id) if thesis_id else None
        position_id_str = str(position_id) if position_id else None
        
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "agent_id": agent_id,
            "market_id": market_id,
            "thesis_id": thesis_id_str,
            "position_id": position_id_str,
            "details": details or {},
            "severity": severity,
            "created_at": datetime.utcnow().isoformat(),  # For append-only constraint
        }
        
        # Insert into event log
        result = supabase.table("event_log").insert(data).execute()
        
        return True
    
    except Exception as e:
        # Don't recursively call record_event on error (infinite loop risk)
        print(f"❌ Error recording event: {e}")
        return False


# ============================================================
# PORTFOLIO FUNCTIONS
# ============================================================

def get_portfolio() -> Dict[str, Any]:
    """
    Get current portfolio state (single row table).
    
    Returns:
        Portfolio dictionary
    """
    try:
        result = supabase.table("portfolio").select("*").eq("id", 1).execute()
        
        if result.data:
            return result.data[0]
        else:
            # Return default portfolio if not found
            return {
                "id": 1,
                "cash": 1000.0,
                "total_value": 1000.0,
                "deployed_pct": 0.0,
                "daily_pnl": 0.0,
                "all_time_pnl": 0.0,
            }
    
    except Exception as e:
        print(f"❌ Error fetching portfolio: {e}")
        return {}


def update_portfolio(portfolio_data: Dict[str, Any]) -> bool:
    """
    Update portfolio state.
    
    Args:
        portfolio_data: Dictionary with portfolio fields
    
    Returns:
        True if successful
    """
    try:
        # Ensure id=1 (single row table)
        portfolio_data["id"] = 1
        portfolio_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Upsert
        result = supabase.table("portfolio").upsert(portfolio_data).execute()
        
        return True
    
    except Exception as e:
        print(f"❌ Error updating portfolio: {e}")
        record_event(
            event_type="database_error",
            details={"error": str(e), "function": "update_portfolio"},
            severity="error"
        )
        return False


# ============================================================
# CONNECTION TEST
# ============================================================

def test_connection() -> bool:
    """
    Test database connection by inserting, fetching, and deleting a test market.
    Verifies event logging works.
    
    Returns:
        True if all tests pass
    """
    print("\n🧪 Testing database connection...")
    
    try:
        # Create test market
        test_market = Market(
            id="test_market_123",
            question="Will this test pass?",
            category="test",
            yes_price=0.50,
            no_price=0.50,
            volume_24h=1000.0,
            resolved=False
        )
        
        # 1. Insert test market
        print("   1. Inserting test market...")
        success = save_market(test_market)
        if not success:
            print("   ❌ Failed to insert test market")
            return False
        print("   ✅ Test market inserted")
        
        # 2. Fetch it back
        print("   2. Fetching test market...")
        markets = get_markets(filters={"category": "test"})
        if not markets or markets[0].id != "test_market_123":
            print("   ❌ Failed to fetch test market")
            return False
        print(f"   ✅ Test market fetched: {markets[0].question}")
        
        # 3. Log a test event
        print("   3. Logging test event...")
        record_event(
            event_type="test_event",
            market_id="test_market_123",
            details={"test": "connection_test"},
            severity="info"
        )
        print("   ✅ Test event logged")
        
        # 4. Delete test market
        print("   4. Deleting test market...")
        result = supabase.table("markets").delete().eq("id", "test_market_123").execute()
        print("   ✅ Test market deleted")
        
        # 5. Verify event log entry exists
        print("   5. Verifying event log...")
        result = supabase.table("event_log").select("*").eq("event_type", "test_event").execute()
        if not result.data:
            print("   ❌ Event not found in log")
            return False
        print(f"   ✅ Event verified in log (id: {result.data[0]['id']})")
        
        print("\n✅ Database connection test PASSED\n")
        return True
    
    except Exception as e:
        print(f"\n❌ Database connection test FAILED: {e}\n")
        return False


# ============================================================
# MAIN (for testing)
# ============================================================

if __name__ == "__main__":
    # Run connection test
    test_connection()
