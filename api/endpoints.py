"""
BASED MONEY - Status API Endpoint

FastAPI endpoint for querying system status, portfolio, and trading activity.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import os

# Initialize FastAPI app
app = FastAPI(
    title="BASED MONEY API",
    description="Trading system status and portfolio monitoring API",
    version="1.0.0",
)

# Add CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_portfolio_data() -> Dict[str, Any]:
    """
    Fetch current portfolio state from database.
    
    Returns:
        Dictionary with portfolio data or None if unavailable
    """
    try:
        from database.db import get_portfolio
        portfolio = get_portfolio()
        
        if portfolio:
            return {
                "cash": float(portfolio.cash),
                "total_value": float(portfolio.total_value),
                "deployed_pct": float(portfolio.deployed_pct),
                "daily_pnl": float(portfolio.daily_pnl),
                "all_time_pnl": float(portfolio.all_time_pnl),
                "open_positions": len([p for p in portfolio.positions if p.status == "open"]),
            }
    except Exception as e:
        print(f"⚠️  Error fetching portfolio: {e}")
    
    # Fallback values if DB unavailable
    return {
        "cash": 0.0,
        "total_value": 0.0,
        "deployed_pct": 0.0,
        "daily_pnl": 0.0,
        "all_time_pnl": 0.0,
        "open_positions": 0,
        "note": "Database unavailable - showing default values",
    }


def get_active_theses_count() -> int:
    """
    Count active theses in database.
    
    Returns:
        Number of active theses
    """
    try:
        from database.db import get_theses
        theses = get_theses(filters={"status": "active"})
        return len(theses)
    except Exception as e:
        print(f"⚠️  Error counting theses: {e}")
        return 0


def get_recent_trades(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch recent trades from database.
    
    Args:
        limit: Number of trades to fetch
        
    Returns:
        List of trade dictionaries
    """
    try:
        from database.db import get_positions
        positions = get_positions()
        
        # Sort by created_at descending
        positions.sort(key=lambda p: p.created_at or datetime.min, reverse=True)
        
        # Take last N
        recent = positions[:limit]
        
        return [
            {
                "id": str(pos.id),
                "market_id": pos.market_id,
                "side": pos.side,
                "shares": float(pos.shares),
                "entry_price": float(pos.entry_price),
                "current_price": float(pos.current_price),
                "pnl": float(pos.pnl),
                "pnl_pct": float(pos.pnl_percentage()) if pos.shares > 0 else 0.0,
                "status": pos.status,
                "created_at": pos.created_at.isoformat() if pos.created_at else None,
            }
            for pos in recent
        ]
    except Exception as e:
        print(f"⚠️  Error fetching trades: {e}")
        return []


def get_system_status() -> str:
    """
    Determine if system is running or stalled.
    
    Checks last event timestamp - if < 5 minutes ago, system is running.
    
    Returns:
        "running" or "stalled"
    """
    try:
        from database.db import supabase
        
        # Query most recent event
        response = supabase.table("event_log").select("timestamp").order(
            "timestamp", desc=True
        ).limit(1).execute()
        
        if response.data and len(response.data) > 0:
            last_event = response.data[0]
            last_timestamp = datetime.fromisoformat(last_event["timestamp"].replace("Z", "+00:00"))
            
            # Check if within last 5 minutes
            now = datetime.now(timezone.utc)
            delta = now - last_timestamp
            
            if delta.total_seconds() < 300:  # 5 minutes
                return "running"
            else:
                return "stalled"
        else:
            # No events yet
            return "unknown"
            
    except Exception as e:
        print(f"⚠️  Error checking system status: {e}")
        return "unknown"


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "BASED MONEY API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "status": "/api/based-money/status",
            "docs": "/docs",
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/based-money/status")
async def get_status():
    """
    Get complete system status including portfolio, theses, and recent trades.
    
    Returns:
        JSON object with:
        - portfolio: Current portfolio state
        - active_theses_count: Number of active trading theses
        - recent_trades: Last 5 trades
        - system_status: "running", "stalled", or "unknown"
        - timestamp: Current server time
    """
    try:
        # Gather all status data
        portfolio = get_portfolio_data()
        active_theses_count = get_active_theses_count()
        recent_trades = get_recent_trades(limit=5)
        system_status = get_system_status()
        
        # Build response
        response = {
            "portfolio": portfolio,
            "active_theses_count": active_theses_count,
            "recent_trades": recent_trades,
            "system_status": system_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching status: {str(e)}"
        )


@app.get("/api/based-money/portfolio")
async def get_portfolio():
    """
    Get current portfolio state.
    
    Returns:
        Portfolio data including cash, total value, deployed %, and P&L
    """
    try:
        portfolio = get_portfolio_data()
        return portfolio
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching portfolio: {str(e)}"
        )


@app.get("/api/based-money/theses")
async def get_theses():
    """
    Get active trading theses.
    
    Returns:
        List of active theses with conviction, edge, and proposed actions
    """
    try:
        from database.db import get_theses as db_get_theses
        
        theses = db_get_theses(filters={"status": "active"})
        
        return {
            "count": len(theses),
            "theses": [
                {
                    "id": str(t.id),
                    "agent_id": t.agent_id,
                    "market_id": t.market_id,
                    "thesis_text": t.thesis_text[:100] + "..." if len(t.thesis_text) > 100 else t.thesis_text,
                    "edge": float(t.edge),
                    "conviction": float(t.conviction),
                    "fair_value": float(t.fair_value),
                    "current_odds": float(t.current_odds),
                    "proposed_action": t.proposed_action,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
                for t in theses
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching theses: {str(e)}"
        )


@app.get("/api/based-money/positions")
async def get_positions_endpoint():
    """
    Get all open positions.
    
    Returns:
        List of open positions with P&L
    """
    try:
        from database.db import get_positions
        
        positions = get_positions(filters={"status": "open"})
        
        return {
            "count": len(positions),
            "positions": [
                {
                    "id": str(p.id),
                    "market_id": p.market_id,
                    "side": p.side,
                    "shares": float(p.shares),
                    "entry_price": float(p.entry_price),
                    "current_price": float(p.current_price),
                    "pnl": float(p.pnl),
                    "pnl_pct": float(p.pnl_percentage()),
                    "status": p.status,
                    "opened_at": p.opened_at.isoformat() if p.opened_at else None,
                }
                for p in positions
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching positions: {str(e)}"
        )


# ============================================================
# STARTUP / SHUTDOWN
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Log API startup"""
    print("\n" + "=" * 60)
    print("BASED MONEY API - Starting")
    print("=" * 60)
    print(f"Trading Mode: {os.getenv('TRADING_MODE', 'unknown')}")
    print(f"Endpoints:")
    print(f"  • GET  /")
    print(f"  • GET  /health")
    print(f"  • GET  /api/based-money/status")
    print(f"  • GET  /api/based-money/portfolio")
    print(f"  • GET  /api/based-money/theses")
    print(f"  • GET  /api/based-money/positions")
    print(f"  • DOCS /docs")
    print("=" * 60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Log API shutdown"""
    print("\n✓ BASED MONEY API - Stopped\n")


# ============================================================
# RUN SERVER (if executed directly)
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.endpoints:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
