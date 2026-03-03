"""
BASED MONEY - Portfolio & Position Models
Represents portfolio state and trading positions
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Position:
    """
    Represents a single trading position in a market.
    
    Tracks entry, current pricing, and P&L for an open or closed position.
    """
    
    # Unique position identifier
    id: UUID = field(default_factory=uuid4)
    
    # Market this position is in
    market_id: str = ""
    
    # Side: 'YES' or 'NO'
    side: str = "YES"
    
    # Number of shares held
    shares: float = 0.0
    
    # Price paid per share at entry
    entry_price: float = 0.0
    
    # Current market price per share
    current_price: float = 0.0
    
    # Profit/loss (updated dynamically)
    pnl: float = 0.0
    
    # Position status
    status: str = "open"  # 'open', 'closed', 'stopped_out'
    
    # Reference to the thesis that created this position
    thesis_id: Optional[UUID] = None
    
    # Timestamps
    opened_at: Optional[datetime] = field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None
    created_at: Optional[datetime] = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate position fields"""
        if self.side not in ["YES", "NO"]:
            raise ValueError(f"side must be 'YES' or 'NO', got {self.side}")
        
        if self.shares < 0:
            raise ValueError(f"shares cannot be negative, got {self.shares}")
        
        if not 0.0 <= self.entry_price <= 1.0:
            raise ValueError(f"entry_price must be between 0.0 and 1.0, got {self.entry_price}")
        
        if not 0.0 <= self.current_price <= 1.0:
            raise ValueError(f"current_price must be between 0.0 and 1.0, got {self.current_price}")
    
    def update_pnl(self, current_price: Optional[float] = None) -> float:
        """
        Update position P&L based on current market price.
        
        Args:
            current_price: Optional override for current price
        
        Returns:
            Updated P&L value
        """
        if current_price is not None:
            self.current_price = current_price
        
        # Calculate P&L: (current_price - entry_price) * shares
        entry_cost = self.entry_price * self.shares
        current_value = self.current_price * self.shares
        self.pnl = current_value - entry_cost
        
        return self.pnl
    
    def pnl_percentage(self) -> float:
        """Calculate P&L as percentage of entry cost"""
        entry_cost = self.entry_price * self.shares
        if entry_cost == 0:
            return 0.0
        return (self.pnl / entry_cost) * 100.0
    
    def should_stop_loss(self, stop_loss_pct: float = 15.0) -> bool:
        """
        Check if position has hit stop loss threshold.
        
        Args:
            stop_loss_pct: Stop loss percentage (e.g., 15.0 for 15%)
        
        Returns:
            True if stop loss should trigger
        """
        return self.pnl_percentage() <= -stop_loss_pct
    
    def to_dict(self) -> dict:
        """Convert position to dictionary for database storage"""
        return {
            "id": str(self.id),
            "market_id": self.market_id,
            "side": self.side,
            "shares": float(self.shares),
            "entry_price": float(self.entry_price),
            "current_price": float(self.current_price),
            "pnl": float(self.pnl),
            "status": self.status,
            "thesis_id": str(self.thesis_id) if self.thesis_id else None,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Position":
        """Create Position instance from dictionary"""
        # Convert string UUIDs back to UUID objects
        if "id" in data and isinstance(data["id"], str):
            data["id"] = UUID(data["id"])
        if "thesis_id" in data and data["thesis_id"] and isinstance(data["thesis_id"], str):
            data["thesis_id"] = UUID(data["thesis_id"])
        
        # Convert ISO timestamp strings to datetime
        for field_name in ["opened_at", "closed_at", "created_at", "updated_at"]:
            if field_name in data and isinstance(data[field_name], str):
                data[field_name] = datetime.fromisoformat(data[field_name])
        
        return cls(**data)
    
    def __repr__(self) -> str:
        """Human-readable representation"""
        return (
            f"Position(id={str(self.id)[:8]}..., market={self.market_id[:20]}..., "
            f"side={self.side}, shares={self.shares:.2f}, pnl=${self.pnl:.2f}, "
            f"status={self.status})"
        )


@dataclass
class Portfolio:
    """
    Represents the overall portfolio state.
    
    Tracks cash, positions, total value, and deployment metrics.
    """
    
    # Available cash (USD)
    cash: float = 1000.0
    
    # List of current positions
    positions: List[Position] = field(default_factory=list)
    
    # Total portfolio value (cash + position values)
    total_value: float = 1000.0
    
    # Percentage of capital currently deployed
    deployed_pct: float = 0.0
    
    # Daily P&L
    daily_pnl: float = 0.0
    
    # All-time P&L
    all_time_pnl: float = 0.0
    
    # Timestamp of last update
    updated_at: Optional[datetime] = field(default_factory=datetime.utcnow)
    
    def recalculate(self):
        """Recalculate portfolio metrics based on current positions"""
        # Sum up position values
        position_value = sum(pos.current_price * pos.shares for pos in self.positions if pos.status == "open")
        
        # Total value = cash + position value
        self.total_value = self.cash + position_value
        
        # Deployed percentage
        if self.total_value > 0:
            self.deployed_pct = (position_value / self.total_value) * 100.0
        else:
            self.deployed_pct = 0.0
        
        # Update all-time P&L (total_value - initial capital)
        initial_capital = 1000.0  # TODO: Make this configurable
        self.all_time_pnl = self.total_value - initial_capital
        
        self.updated_at = datetime.utcnow()
    
    def get_open_positions(self) -> List[Position]:
        """Get all open positions"""
        return [pos for pos in self.positions if pos.status == "open"]
    
    def get_position_by_market(self, market_id: str) -> Optional[Position]:
        """Find an open position for a specific market"""
        for pos in self.positions:
            if pos.market_id == market_id and pos.status == "open":
                return pos
        return None
    
    def add_position(self, position: Position):
        """Add a new position to the portfolio"""
        self.positions.append(position)
        
        # Deduct cash used for entry
        entry_cost = position.entry_price * position.shares
        self.cash -= entry_cost
        
        # Recalculate metrics
        self.recalculate()
    
    def close_position(self, position: Position, exit_price: float):
        """
        Close a position and update portfolio.
        
        Args:
            position: Position to close
            exit_price: Exit price per share
        """
        # Update position
        position.current_price = exit_price
        position.update_pnl()
        position.status = "closed"
        position.closed_at = datetime.utcnow()
        
        # Add proceeds back to cash
        proceeds = exit_price * position.shares
        self.cash += proceeds
        
        # Recalculate metrics
        self.recalculate()
    
    def available_for_deployment(self, max_deployed_pct: float = 60.0) -> float:
        """
        Calculate how much cash is available for new positions.
        
        Args:
            max_deployed_pct: Maximum portfolio deployment percentage
        
        Returns:
            Amount in USD available for deployment
        """
        max_deployable = (self.total_value * max_deployed_pct) / 100.0
        currently_deployed = self.total_value * (self.deployed_pct / 100.0)
        available = max_deployable - currently_deployed
        
        # Can't deploy more than available cash
        return min(available, self.cash)
    
    def to_dict(self) -> dict:
        """Convert portfolio to dictionary"""
        return {
            "cash": float(self.cash),
            "total_value": float(self.total_value),
            "deployed_pct": float(self.deployed_pct),
            "daily_pnl": float(self.daily_pnl),
            "all_time_pnl": float(self.all_time_pnl),
            "position_count": len(self.get_open_positions()),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        """Human-readable representation"""
        return (
            f"Portfolio(cash=${self.cash:.2f}, total_value=${self.total_value:.2f}, "
            f"deployed={self.deployed_pct:.1f}%, positions={len(self.get_open_positions())}, "
            f"pnl=${self.all_time_pnl:.2f})"
        )
