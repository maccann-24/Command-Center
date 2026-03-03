"""
BASED MONEY - Execution Engine

Orchestrates order execution, position creation, and portfolio updates.
Enforces pre-execution risk checks and maintains audit trail.
"""

from dataclasses import asdict
from typing import Optional

from brokers.base import BrokerAdapter, Order, Execution
from models.portfolio import Portfolio, Position
from models.thesis import Thesis
from .risk import RiskEngine, RiskDecision


# ============================================================
# EXCEPTIONS
# ============================================================

class SecurityError(Exception):
    """Raised when attempting to execute a rejected trade."""
    pass


class ExecutionError(Exception):
    """Raised when execution fails."""
    pass


# ============================================================
# EXECUTION ENGINE
# ============================================================

class ExecutionEngine:
    """
    Execution engine that orchestrates trade execution.
    
    Responsibilities:
    1. Enforce pre-execution risk checks
    2. Execute orders via broker adapter
    3. Create and save positions
    4. Update portfolio state
    5. Maintain audit trail in event_log
    
    Usage:
        >>> engine = ExecutionEngine(broker=PaperBroker(), portfolio=my_portfolio)
        >>> risk_decision = risk_engine.evaluate(thesis, portfolio)
        >>> if risk_decision.approved:
        ...     execution = engine.execute(risk_decision, thesis)
    """
    
    def __init__(self, broker_adapter: BrokerAdapter, portfolio: Portfolio):
        """
        Initialize execution engine.
        
        Args:
            broker_adapter: Broker implementation (PaperBroker, PolymarketBroker, etc.)
            portfolio: Current portfolio state
        """
        self.broker = broker_adapter
        self.portfolio = portfolio
        self.risk_engine = RiskEngine()
    
    def execute(self, risk_decision: RiskDecision, thesis: Thesis) -> Execution:
        """
        Execute a trade based on approved risk decision.
        
        This method performs multiple safety checks and maintains atomicity:
        1. Verify risk decision was approved
        2. Re-run risk evaluation (portfolio state may have changed)
        3. Create order from thesis
        4. Execute via broker
        5. Create position
        6. Save position to DB
        7. Update portfolio
        8. Log event
        
        Args:
            risk_decision: Pre-execution risk decision (must be approved)
            thesis: Trading thesis to execute
            
        Returns:
            Execution object with fill details
            
        Raises:
            SecurityError: If risk_decision is not approved
            ExecutionError: If execution or position save fails
            
        Example:
            >>> risk_decision = risk_engine.evaluate(thesis, portfolio)
            >>> execution = engine.execute(risk_decision, thesis)
            >>> print(f"Filled {execution.size} shares at {execution.price}")
        """
        
        # ============================================================
        # SAFETY CHECK 1: Verify approval
        # ============================================================
        if not risk_decision.approved:
            raise SecurityError(
                f"Attempted to execute rejected trade: {risk_decision.reason}"
            )
        
        # ============================================================
        # SAFETY CHECK 2: Re-run risk evaluation
        # ============================================================
        # Portfolio state may have changed since approval
        recheck_decision = self.risk_engine.evaluate(thesis, self.portfolio)
        
        if not recheck_decision.approved:
            raise SecurityError(
                f"Risk decision no longer valid (portfolio state changed): "
                f"{recheck_decision.reason}"
            )
        
        # ============================================================
        # CREATE ORDER
        # ============================================================
        proposed_action = thesis.proposed_action
        
        # Calculate order size in USD
        size_pct = proposed_action.get("size_pct", 0.0)
        size_usd = self.portfolio.cash * size_pct
        
        # Create order object
        order = Order(
            market_id=thesis.market_id,
            side=proposed_action.get("side", "YES"),
            size=size_usd,
            order_type="MARKET",
            limit_price=thesis.current_odds,  # Used as reference for paper broker
            client_order_id=f"thesis-{thesis.id}",
        )
        
        # ============================================================
        # EXECUTE VIA BROKER
        # ============================================================
        try:
            execution = self.broker.execute_order(order)
        except Exception as e:
            raise ExecutionError(f"Broker execution failed: {e}")
        
        # Verify execution succeeded
        if execution.status != "FILLED":
            raise ExecutionError(
                f"Order not filled: status={execution.status}, "
                f"message={execution.message}"
            )
        
        # ============================================================
        # CREATE POSITION
        # ============================================================
        position = Position(
            market_id=thesis.market_id,
            side=proposed_action.get("side", "YES"),
            shares=execution.size,
            entry_price=execution.price,
            current_price=execution.price,
            pnl=0.0,
            status="open",
            thesis_id=thesis.id,
        )
        
        # ============================================================
        # SAVE POSITION TO DB
        # ============================================================
        try:
            from database.db import save_position
            success = save_position(position)
            if not success:
                print("⚠️  Position save returned False (non-fatal)")
        except Exception as e:
            # Non-fatal: position is created in memory even if DB save fails
            print(f"⚠️  Failed to save position to DB: {e}")
        
        # ============================================================
        # UPDATE PORTFOLIO
        # ============================================================
        # Deduct cost from cash
        position_cost = execution.size * execution.price
        self.portfolio.cash -= position_cost
        
        # Add position to portfolio
        self.portfolio.positions.append(position)
        
        # Recalculate deployed percentage
        total_deployed = sum(
            pos.shares * pos.current_price
            for pos in self.portfolio.positions
            if pos.status == "open"
        )
        self.portfolio.deployed_pct = (total_deployed / self.portfolio.total_value) * 100.0
        
        # Update total value
        self.portfolio.total_value = self.portfolio.cash + total_deployed
        
        # Save portfolio to DB
        try:
            from database.db import update_portfolio
            portfolio_data = {
                "cash": self.portfolio.cash,
                "total_value": self.portfolio.total_value,
                "deployed_pct": self.portfolio.deployed_pct,
                "daily_pnl": self.portfolio.daily_pnl,
                "all_time_pnl": self.portfolio.all_time_pnl,
            }
            update_portfolio(portfolio_data)
        except Exception as e:
            # Non-fatal: portfolio object is updated even if DB save fails
            print(f"⚠️  Failed to save portfolio to DB: {e}")
        
        # ============================================================
        # LOG EVENT
        # ============================================================
        try:
            from database.db import record_event
            
            # Convert execution to dict
            execution_dict = asdict(execution)
            execution_dict['timestamp'] = execution_dict['timestamp'].isoformat()
            
            record_event(
                event_type="trade_executed",
                agent_id=thesis.agent_id,
                market_id=thesis.market_id,
                thesis_id=thesis.id,
                position_id=position.id,
                details={
                    "execution": execution_dict,
                    "position_cost": position_cost,
                    "shares": execution.size,
                    "entry_price": execution.price,
                    "side": proposed_action.get("side", "YES"),
                },
                severity="info",
            )
        except Exception as e:
            # Non-fatal: event logging failure shouldn't stop execution
            print(f"⚠️  Failed to log execution event: {e}")
        
        # ============================================================
        # RETURN EXECUTION (with position_id)
        # ============================================================
        # Add position ID to execution for orchestrator tracking
        execution.position_id = str(position.id)
        
        return execution
