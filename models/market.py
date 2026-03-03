"""
BASED MONEY - Market Model
Represents a Polymarket prediction market
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Market:
    """
    Represents a Polymarket prediction market.
    
    Contains current pricing, volume, and metadata for a tradeable market.
    """
    
    # Unique market identifier (from Polymarket API)
    id: str = ""
    
    # Market question text
    question: str = ""
    
    # Category: 'geopolitical', 'crypto', 'sports', etc.
    category: str = ""
    
    # Current YES token price (0.0 to 1.0)
    yes_price: float = 0.0
    
    # Current NO token price (0.0 to 1.0)
    no_price: float = 0.0
    
    # 24-hour trading volume (USD)
    volume_24h: float = 0.0
    
    # When the market resolves
    resolution_date: Optional[datetime] = None
    
    # Whether market has resolved
    resolved: bool = False
    
    # Additional fields for filtering
    liquidity_score: float = 0.0  # 0.0 to 1.0, calculated from order book depth
    
    # Timestamps
    created_at: Optional[datetime] = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate market fields"""
        if not 0.0 <= self.yes_price <= 1.0:
            raise ValueError(f"yes_price must be between 0.0 and 1.0, got {self.yes_price}")
        
        if not 0.0 <= self.no_price <= 1.0:
            raise ValueError(f"no_price must be between 0.0 and 1.0, got {self.no_price}")
        
        if self.volume_24h < 0:
            raise ValueError(f"volume_24h cannot be negative, got {self.volume_24h}")
    
    def days_to_resolution(self) -> Optional[int]:
        """Calculate days until market resolves"""
        if not self.resolution_date:
            return None
        
        # Use timezone-aware datetime to avoid mixing naive/aware
        from datetime import timezone
        now = datetime.now(timezone.utc)
        
        # If resolution_date is naive, make it UTC
        if self.resolution_date.tzinfo is None:
            resolution_date = self.resolution_date.replace(tzinfo=timezone.utc)
        else:
            resolution_date = self.resolution_date
        
        delta = resolution_date - now
        return max(0, delta.days)
    
    def is_tradeable(self, min_volume: float = 50000.0, min_days: int = 2) -> bool:
        """
        Check if market meets minimum tradeability criteria.
        
        Args:
            min_volume: Minimum 24h volume in USD
            min_days: Minimum days until resolution
        
        Returns:
            True if market is tradeable
        """
        if self.resolved:
            return False
        
        if self.volume_24h < min_volume:
            return False
        
        days_left = self.days_to_resolution()
        if days_left is not None and days_left < min_days:
            return False
        
        return True
    
    def to_dict(self) -> dict:
        """Convert market to dictionary for database storage"""
        return {
            "id": self.id,
            "question": self.question,
            "category": self.category,
            "yes_price": float(self.yes_price),
            "no_price": float(self.no_price),
            "volume_24h": float(self.volume_24h),
            "resolution_date": self.resolution_date.isoformat() if self.resolution_date else None,
            "resolved": self.resolved,
            "liquidity_score": float(self.liquidity_score),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Market":
        """Create Market instance from dictionary"""
        # Convert ISO timestamp strings to datetime
        if "resolution_date" in data and isinstance(data["resolution_date"], str):
            data["resolution_date"] = datetime.fromisoformat(data["resolution_date"])
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        
        return cls(**data)
    
    def __repr__(self) -> str:
        """Human-readable representation"""
        return (
            f"Market(id={self.id[:20]}..., question='{self.question[:50]}...', "
            f"yes={self.yes_price:.2f}, volume=${self.volume_24h:,.0f})"
        )
