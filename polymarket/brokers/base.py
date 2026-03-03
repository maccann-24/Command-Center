"""
BASED MONEY - Broker Adapter Interface

Abstract base class for broker integrations.
All broker implementations (Polymarket, paper trading, etc.) must inherit from BrokerAdapter.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from models.portfolio import Position

# ============================================================
# ORDER DATA MODEL
# ============================================================


@dataclass
class Order:
    """
    Represents an order to be executed by a broker.

    Attributes:
        market_id: Unique identifier for the market
        side: Trade side ('YES', 'NO', 'BUY', 'SELL')
        size: Number of shares to trade
        order_type: Order type ('MARKET', 'LIMIT')
        limit_price: Price limit for LIMIT orders (None for MARKET)
        client_order_id: Optional client-side unique identifier
    """

    market_id: str
    side: str
    size: float
    order_type: str = "MARKET"  # MARKET or LIMIT
    limit_price: Optional[float] = None
    client_order_id: Optional[str] = None


# ============================================================
# EXECUTION DATA MODEL
# ============================================================


@dataclass
class Execution:
    """
    Represents the result of an order execution.

    Attributes:
        order_id: Unique execution identifier
        market_id: Market where the order was executed
        side: Trade side
        size: Number of shares executed
        price: Average fill price
        timestamp: Execution timestamp
        status: Execution status ('FILLED', 'PARTIAL', 'REJECTED', 'CANCELLED')
        broker_order_id: Broker's internal order identifier (if applicable)
        fees: Total fees charged for this execution
        message: Optional status/error message
    """

    order_id: str
    market_id: str
    side: str
    size: float
    price: float
    timestamp: datetime
    status: str  # FILLED, PARTIAL, REJECTED, CANCELLED
    broker_order_id: Optional[str] = None
    fees: float = 0.0
    message: Optional[str] = None


# ============================================================
# BROKER ADAPTER ABSTRACT CLASS
# ============================================================


class BrokerAdapter(ABC):
    """
    Abstract base class for broker integrations.

    All broker implementations must inherit from this class and implement
    the three core methods: execute_order, get_position, and cancel_order.

    Contract guarantees:
    - execute_order must be idempotent (safe to retry with same client_order_id)
    - get_position must return current state from broker (not cached)
    - cancel_order must handle already-filled orders gracefully (return False, not error)
    """

    @abstractmethod
    def execute_order(self, order: Order) -> Execution:
        """
        Execute a trade order on the broker.

        This method MUST be idempotent. If called multiple times with the same
        client_order_id, it should return the same execution result without
        creating duplicate orders.

        Args:
            order: Order object containing trade details

        Returns:
            Execution object with fill details and status

        Raises:
            BrokerError: If execution fails for reasons other than rejection

        Example:
            >>> order = Order(market_id="btc-100k", side="YES", size=100)
            >>> execution = broker.execute_order(order)
            >>> print(execution.status)  # "FILLED" or "REJECTED"
        """
        pass

    @abstractmethod
    def get_position(self, market_id: str) -> Optional[Position]:
        """
        Retrieve current position for a market from the broker.

        This method MUST return the current state from the broker's API,
        not a cached value. It should reflect all recent executions.

        Args:
            market_id: Market identifier

        Returns:
            Position object if position exists, None if no position

        Raises:
            BrokerError: If unable to fetch position data

        Example:
            >>> position = broker.get_position("btc-100k")
            >>> if position:
            ...     print(f"Size: {position.shares}, PnL: {position.unrealized_pnl}")
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a pending order.

        This method MUST handle already-filled orders gracefully. If the order
        has already been filled or doesn't exist, return False without raising
        an error.

        Args:
            order_id: Order identifier (broker's order ID or client_order_id)

        Returns:
            True if order was successfully cancelled
            False if order was already filled, doesn't exist, or can't be cancelled

        Raises:
            BrokerError: Only for unexpected broker/network errors

        Example:
            >>> success = broker.cancel_order("order-123")
            >>> if not success:
            ...     print("Order already filled or not found")
        """
        pass
