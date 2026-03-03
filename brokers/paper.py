"""
BASED MONEY - Paper Broker Implementation

In-memory paper trading broker for testing and backtesting.
Simulates order execution with slippage but no real money at risk.
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional
from dataclasses import asdict

from .base import BrokerAdapter, Order, Execution
from models.portfolio import Position


# ============================================================
# PAPER BROKER
# ============================================================

class PaperBroker(BrokerAdapter):
    """
    Paper trading broker implementation.
    
    Simulates order execution with 1% slippage and instant fills.
    All orders are filled immediately at simulated prices.
    Logs all executions to event_log for audit trail.
    
    Usage:
        >>> broker = PaperBroker()
        >>> order = Order(market_id="btc-100k", side="YES", size=100, limit_price=0.65)
        >>> execution = broker.execute_order(order)
        >>> print(execution.status)  # "FILLED"
    """
    
    def __init__(self):
        """Initialize paper broker."""
        self.db_available = self._check_db()
    
    def _check_db(self) -> bool:
        """Check if database is available."""
        required = ("TRADING_MODE", "SUPABASE_URL", "SUPABASE_KEY")
        return all(os.getenv(k) for k in required)
    
    def _get_db(self):
        """Get database connection (lazy)."""
        if not self.db_available:
            raise RuntimeError("Database not configured for paper broker")
        
        from database.db import supabase
        return supabase
    
    def execute_order(self, order: Order) -> Execution:
        """
        Execute order with simulated slippage.
        
        Simulates 1% slippage:
        - YES orders: fill at 1% higher than reference price
        - NO orders: fill at 1% lower than reference price
        
        Args:
            order: Order to execute (must have limit_price set as reference)
            
        Returns:
            Execution object with simulated fill details
            
        Raises:
            ValueError: If order.limit_price is None
            RuntimeError: If database logging fails (non-fatal)
        """
        # Validate order has reference price
        if order.limit_price is None:
            raise ValueError(
                f"Paper broker requires limit_price as reference for slippage simulation. "
                f"Got order: {order}"
            )
        
        # Simulate 1% slippage
        if order.side.upper() == "YES":
            fill_price = order.limit_price * 1.01
        else:
            fill_price = order.limit_price * 0.99
        
        # Clamp to valid price range [0.01, 0.99]
        fill_price = max(0.01, min(0.99, fill_price))
        
        # Calculate shares filled (size is in USD)
        shares = order.size / fill_price
        
        # Create execution
        execution = Execution(
            order_id=str(uuid.uuid4()),
            market_id=order.market_id,
            side=order.side,
            size=shares,
            price=fill_price,
            timestamp=datetime.now(timezone.utc),
            status="FILLED",
            broker_order_id=order.client_order_id,
            fees=0.0,  # No fees in paper trading
            message="Paper execution with 1% simulated slippage",
        )
        
        # Log to event_log (best effort)
        self._log_execution(order, execution)
        
        return execution
    
    def _log_execution(self, order: Order, execution: Execution) -> None:
        """
        Log execution to event_log table.
        
        Non-fatal if logging fails (paper broker continues).
        """
        if not self.db_available:
            print(f"⚠️  Paper execution not logged (DB unavailable): {execution.order_id}")
            return
        
        try:
            db = self._get_db()
            
            # Convert dataclasses to dicts
            order_dict = asdict(order)
            execution_dict = asdict(execution)
            
            # Convert datetime objects to ISO strings for JSON
            execution_dict['timestamp'] = execution_dict['timestamp'].isoformat()
            
            # Insert event log
            db.table("event_log").insert({
                "event_type": "paper_execution",
                "market_id": order.market_id,
                "details": {
                    "order": order_dict,
                    "execution": execution_dict,
                },
                "severity": "info",
            }).execute()
            
        except Exception as e:
            # Non-fatal: log to console but don't fail execution
            print(f"⚠️  Failed to log paper execution: {e}")
    
    def get_position(self, market_id: str) -> Optional[Position]:
        """
        Get current open position for a market.
        
        Queries the positions table for open positions in the specified market.
        
        Args:
            market_id: Market identifier
            
        Returns:
            Position object if open position exists, None otherwise
            
        Raises:
            RuntimeError: If database query fails
        """
        if not self.db_available:
            print(f"⚠️  Cannot fetch position (DB unavailable): {market_id}")
            return None
        
        try:
            db = self._get_db()
            
            # Query for open position
            response = db.table("positions").select("*").eq(
                "market_id", market_id
            ).eq(
                "status", "open"
            ).execute()
            
            # Return first match or None
            if response.data and len(response.data) > 0:
                pos_data = response.data[0]
                
                # Convert to Position object
                position = Position(
                    id=uuid.UUID(pos_data["id"]),
                    market_id=pos_data["market_id"],
                    side=pos_data["side"],
                    shares=float(pos_data["shares"]),
                    entry_price=float(pos_data["entry_price"]),
                    current_price=float(pos_data["current_price"]),
                    pnl=float(pos_data.get("pnl", 0.0)),
                    status=pos_data["status"],
                    thesis_id=uuid.UUID(pos_data["thesis_id"]) if pos_data.get("thesis_id") else None,
                    opened_at=datetime.fromisoformat(pos_data["opened_at"]) if pos_data.get("opened_at") else None,
                    closed_at=datetime.fromisoformat(pos_data["closed_at"]) if pos_data.get("closed_at") else None,
                    created_at=datetime.fromisoformat(pos_data["created_at"]) if pos_data.get("created_at") else None,
                    updated_at=datetime.fromisoformat(pos_data["updated_at"]) if pos_data.get("updated_at") else None,
                )
                
                return position
            
            return None
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch position for {market_id}: {e}")
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order (no-op for paper trading).
        
        In paper trading, all orders fill instantly, so there's nothing to cancel.
        Always returns True to indicate "success" (order is not pending).
        
        Args:
            order_id: Order identifier (ignored)
            
        Returns:
            True (always, since orders fill instantly)
        """
        # No-op: paper orders fill instantly, nothing to cancel
        return True
