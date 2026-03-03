"""
BASED MONEY - Position Monitor

Tracks open positions, updates P&L, and triggers stop-losses.
"""

from typing import List, Optional
from dataclasses import asdict

from brokers.base import BrokerAdapter, Order
from models.portfolio import Position

# ============================================================
# POSITION MONITOR
# ============================================================


class PositionMonitor:
    """
    Position monitoring system for tracking P&L and triggering stop-losses.

    Responsibilities:
    1. Update position prices and P&L from broker/market data
    2. Check stop-loss conditions
    3. Generate exit orders when stop-losses trigger
    4. Log stop-loss events

    Usage:
        >>> monitor = PositionMonitor(broker_adapter=paper_broker)
        >>> positions = monitor.update_positions()
        >>> exit_orders = monitor.check_stop_losses(positions, stop_loss_pct=0.15)
        >>> for order in exit_orders:
        ...     execution = broker.execute_order(order)
    """

    def __init__(self, broker_adapter: BrokerAdapter):
        """
        Initialize position monitor.

        Args:
            broker_adapter: Broker implementation for fetching position data
        """
        self.broker = broker_adapter

    def update_positions(self) -> List[Position]:
        """
        Update all open positions with current prices and P&L.

        Fetches all open positions from database, queries broker for current
        prices, calculates P&L, and saves updates.

        Returns:
            List of updated Position objects

        Process:
            1. Fetch open positions from DB
            2. For each position:
               a. Get current price from broker
               b. Calculate P&L = (current_price - entry_price) * shares
               c. Update position in DB
            3. Return updated positions
        """
        positions = []

        # ============================================================
        # FETCH OPEN POSITIONS FROM DB
        # ============================================================
        try:
            from database.db import get_positions

            positions = get_positions(filters={"status": "open"})

            if not positions:
                print("No open positions to update")
                return []

            print(f"Updating {len(positions)} open positions...")

        except Exception as e:
            print(f"⚠️  Failed to fetch positions from DB: {e}")
            return []

        # ============================================================
        # UPDATE EACH POSITION
        # ============================================================
        updated_positions = []

        for position in positions:
            try:
                # Get current price from broker
                broker_position = self.broker.get_position(position.market_id)

                if broker_position:
                    # Use broker's current price
                    current_price = broker_position.current_price
                else:
                    # Fallback: fetch from market API (not implemented yet)
                    # For now, keep existing current_price
                    current_price = position.current_price
                    print(
                        f"⚠️  No broker data for {position.market_id}, keeping current_price={current_price}"
                    )

                # Calculate P&L
                current_pnl = (current_price - position.entry_price) * position.shares

                # Update position object
                position.current_price = current_price
                position.pnl = current_pnl

                # Save to DB (best effort)
                try:
                    from database.db import save_position

                    save_position(position)
                except Exception as db_error:
                    print(f"⚠️  Failed to save position update: {db_error}")

                updated_positions.append(position)

                # Log update
                pnl_pct = position.pnl_percentage()
                print(
                    f"  Updated {position.market_id[:20]}: ${position.pnl:.2f} ({pnl_pct:+.2f}%)"
                )

            except Exception as e:
                print(f"⚠️  Failed to update position {position.market_id}: {e}")
                continue

        return updated_positions

    def check_stop_losses(
        self, positions: List[Position], stop_loss_pct: float = 15.0
    ) -> List[Order]:
        """
        Check positions for stop-loss triggers and generate exit orders.

        Args:
            positions: List of positions to check
            stop_loss_pct: Stop-loss percentage threshold (default 15.0 = 15%)

        Returns:
            List of exit Order objects for positions that hit stop-loss

        Stop-loss calculation:
            loss_pct = (pnl / position_cost) * 100
            position_cost = entry_price * shares

            Trigger when: loss_pct < -stop_loss_pct

        Example:
            Entry: 100 shares @ $0.50 = $50 cost
            Current: $0.40
            P&L: (0.40 - 0.50) * 100 = -$10
            Loss %: (-10 / 50) * 100 = -20%
            Triggers if stop_loss_pct = 15% (20% > 15%)
        """
        exit_orders = []

        for position in positions:
            # Calculate position cost (original investment)
            position_cost = position.entry_price * position.shares

            if position_cost == 0:
                continue

            # Calculate loss percentage
            loss_pct = (position.pnl / position_cost) * 100.0

            # Check if stop-loss triggered
            if loss_pct < -stop_loss_pct:
                print(f"\n🛑 STOP-LOSS TRIGGERED: {position.market_id}")
                print(f"   Loss: ${position.pnl:.2f} ({loss_pct:.2f}%)")
                print(f"   Threshold: {stop_loss_pct:.2f}%")

                # Determine opposite side for exit
                exit_side = "NO" if position.side == "YES" else "YES"

                # Create exit order
                exit_order = Order(
                    market_id=position.market_id,
                    side=exit_side,
                    size=position.shares,  # Exit entire position
                    order_type="MARKET",
                    limit_price=position.current_price,
                    client_order_id=f"stop-loss-{position.id}",
                )

                exit_orders.append(exit_order)

                # Log event (best effort)
                try:
                    from database.db import record_event

                    record_event(
                        event_type="stop_loss_triggered",
                        market_id=position.market_id,
                        position_id=position.id,
                        thesis_id=position.thesis_id,
                        details={
                            "loss_pct": float(loss_pct),
                            "pnl": float(position.pnl),
                            "position_cost": float(position_cost),
                            "entry_price": float(position.entry_price),
                            "current_price": float(position.current_price),
                            "shares": float(position.shares),
                            "side": position.side,
                            "exit_side": exit_side,
                            "stop_loss_threshold": float(stop_loss_pct),
                        },
                        severity="warning",
                    )
                except Exception as e:
                    print(f"⚠️  Failed to log stop-loss event: {e}")

        if exit_orders:
            print(f"\n📋 Generated {len(exit_orders)} stop-loss exit orders")

        return exit_orders
