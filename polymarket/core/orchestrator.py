"""
BASED MONEY - Trading Orchestrator

Main control loop that orchestrates the entire trading system:
ingestion → thesis generation → risk evaluation → execution → monitoring
"""

import time
import traceback
from typing import List, Optional

from .risk import RiskEngine
from .execution import ExecutionEngine
from .positions import PositionMonitor
from .thesis_store import ThesisStore
from models.portfolio import Portfolio

# Optional: Command Center integration
try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# ============================================================
# ORCHESTRATOR
# ============================================================


class Orchestrator:
    """
    Main trading orchestrator that runs the complete trading cycle.

    The orchestrator coordinates all components of the trading system:
    1. Position monitoring and stop-loss management
    2. Thesis generation from multiple agents
    3. Risk evaluation
    4. Trade execution
    5. Error handling and logging

    Usage:
        >>> orchestrator = Orchestrator(
        ...     agents=[geo_agent, signals_agent],
        ...     risk_engine=RiskEngine(),
        ...     execution_engine=ExecutionEngine(broker, portfolio),
        ...     position_monitor=PositionMonitor(broker),
        ... )
        >>> orchestrator.run_cycle()  # Run one cycle
        >>> orchestrator.run_forever()  # Run continuous loop
    """

    def __init__(
        self,
        agents: List,
        risk_engine: RiskEngine,
        execution_engine: ExecutionEngine,
        position_monitor: PositionMonitor,
        thesis_store: Optional[ThesisStore] = None,
    ):
        """
        Initialize orchestrator.

        Args:
            agents: List of agent instances (GeoAgent, SignalsAgent, etc.)
            risk_engine: Risk engine for pre-trade evaluation
            execution_engine: Execution engine for trade placement
            position_monitor: Position monitor for P&L tracking and stop-losses
            thesis_store: Optional thesis store (uses global instance if None)
        """
        self.agents = agents
        self.risk_engine = risk_engine
        self.execution_engine = execution_engine
        self.position_monitor = position_monitor

        # Use provided thesis store or import global
        if thesis_store:
            self.thesis_store = thesis_store
        else:
            from .thesis_store import thesis_store

            self.thesis_store = thesis_store

        # Cycle counter for logging
        self.cycle_count = 0

        # Command Center integration (optional)
        from config import COMMAND_CENTER_URL

        self.command_center_url = f"{COMMAND_CENTER_URL}/api/tasks"
        self.command_center_enabled = REQUESTS_AVAILABLE

    def notify_command_center(self, thesis, portfolio) -> bool:
        """
        Notify Command Center of a trading opportunity.

        Posts a task to Command Center dashboard with opportunity details.

        Args:
            thesis: Approved thesis
            portfolio: Current portfolio state

        Returns:
            True if notification succeeded, False otherwise
        """
        if not self.command_center_enabled:
            return False

        try:
            # Prepare payload per spec
            # Use market_question if available, fallback to market_id
            market_display = (
                thesis.market_question if thesis.market_question else thesis.market_id
            )
            market_truncated = market_display[:80]
            if len(market_display) > 80:
                market_truncated += "..."

            title = f"💰 Opportunity: {market_truncated}"

            size_usd = portfolio.cash * thesis.proposed_action.get("size_pct", 0.0)
            description = (
                f"{thesis.thesis_text} "
                f"Edge: {thesis.edge:.1%} | "
                f"Conviction: {thesis.conviction:.0%} | "
                f"Size: ${size_usd:.0f}"
            )

            priority = "high" if thesis.conviction > 0.80 else "medium"

            payload = {
                "title": title,
                "description": description,
                "priority": priority,
            }

            # POST to Command Center
            response = requests.post(
                self.command_center_url,
                json=payload,
                timeout=5,
            )

            if response.status_code in (200, 201):
                print(f"  📤 Notified Command Center (priority: {priority})")
                return True
            else:
                print(f"  ⚠️  Command Center returned status {response.status_code}")
                return False

        except requests.exceptions.ConnectionError:
            # Command Center might be offline - not critical
            print(f"  ⚠️  Command Center offline (connection refused)")
            return False
        except requests.exceptions.Timeout:
            print(f"  ⚠️  Command Center timeout")
            return False
        except Exception as e:
            print(f"  ⚠️  Command Center notification failed: {e}")
            return False

    def run_cycle(self) -> dict:
        """
        Run one complete trading cycle.

        Returns:
            Dictionary with cycle statistics

        Steps:
            1. Update positions (refresh P&L)
            2. Check stop-losses (execute exits if needed)
            3. Recalculate portfolio state
            4. Generate theses from agents
            5. Get actionable theses (high conviction)
            6. Risk evaluation
            7. Execute approved trades
            8. Sleep before next cycle
        """
        self.cycle_count += 1

        stats = {
            "cycle": self.cycle_count,
            "positions_updated": 0,
            "stop_losses_triggered": 0,
            "theses_generated": 0,
            "theses_actionable": 0,
            "trades_executed": 0,
            "errors": [],
        }

        try:
            # ============================================================
            # STEP 1: UPDATE POSITIONS
            # ============================================================
            print(f"\n{'=' * 60}")
            print(f"CYCLE {self.cycle_count}: Position Update")
            print(f"{'=' * 60}")

            try:
                positions = self.position_monitor.update_positions()
                stats["positions_updated"] = len(positions)
                print(f"✓ Updated {len(positions)} positions")
            except Exception as e:
                error_msg = f"Position update failed: {e}"
                print(f"⚠️  {error_msg}")
                stats["errors"].append(error_msg)
                positions = []

            # ============================================================
            # STEP 2: CHECK STOP-LOSSES
            # ============================================================
            print(f"\n{'=' * 60}")
            print(f"CYCLE {self.cycle_count}: Stop-Loss Check")
            print(f"{'=' * 60}")

            try:
                exit_orders = self.position_monitor.check_stop_losses(positions)
                stats["stop_losses_triggered"] = len(exit_orders)

                if exit_orders:
                    print(f"⚠️  {len(exit_orders)} stop-loss(es) triggered")

                    # Execute stop-loss exits
                    for order in exit_orders:
                        try:
                            execution = self.execution_engine.broker.execute_order(
                                order
                            )
                            print(f"  ✓ Stop-loss executed: {execution.market_id}")
                        except Exception as e:
                            print(f"  ❌ Stop-loss execution failed: {e}")
                            stats["errors"].append(f"Stop-loss execution failed: {e}")
                else:
                    print("✓ No stop-losses triggered")

            except Exception as e:
                error_msg = f"Stop-loss check failed: {e}"
                print(f"⚠️  {error_msg}")
                stats["errors"].append(error_msg)

            # ============================================================
            # STEP 3: RECALCULATE PORTFOLIO
            # ============================================================
            print(f"\n{'=' * 60}")
            print(f"CYCLE {self.cycle_count}: Portfolio State")
            print(f"{'=' * 60}")

            try:
                from database.db import get_portfolio
                from models.portfolio import Portfolio

                portfolio_data = get_portfolio()

                if portfolio_data:
                    # Convert dict to Portfolio object
                    portfolio = Portfolio(
                        cash=portfolio_data.get("cash", 1000.0),
                        total_value=portfolio_data.get("total_value", 1000.0),
                        deployed_pct=portfolio_data.get("deployed_pct", 0.0),
                        daily_pnl=portfolio_data.get("daily_pnl", 0.0),
                        all_time_pnl=portfolio_data.get("all_time_pnl", 0.0),
                        positions=[],
                    )
                    print(f"  Cash: ${portfolio.cash:,.2f}")
                    print(f"  Total Value: ${portfolio.total_value:,.2f}")
                    print(f"  Deployed: {portfolio.deployed_pct:.1f}%")
                    print(f"  Daily P&L: ${portfolio.daily_pnl:+.2f}")
                else:
                    # Fallback to execution engine's portfolio
                    portfolio = self.execution_engine.portfolio
                    print(f"  Using in-memory portfolio (DB unavailable)")

            except Exception as e:
                # Use execution engine's portfolio as fallback
                portfolio = self.execution_engine.portfolio
                print(f"⚠️  DB unavailable, using in-memory portfolio: {e}")

            # Persist a portfolio snapshot for dashboard sparklines (best effort)
            try:
                from database.portfolio_history import save_portfolio_snapshot

                save_portfolio_snapshot(self.execution_engine.portfolio)
            except Exception:
                pass

            # ============================================================
            # STEP 4: GENERATE THESES
            # ============================================================
            print(f"\n{'=' * 60}")
            print(f"CYCLE {self.cycle_count}: Thesis Generation")
            print(f"{'=' * 60}")

            for agent in self.agents:
                try:
                    # Call agent's update_theses method
                    theses = agent.update_theses()

                    if theses:
                        print(f"  {agent.__class__.__name__}: {len(theses)} theses")

                        # Save each thesis to store
                        for thesis in theses:
                            try:
                                self.thesis_store.save(thesis)
                                stats["theses_generated"] += 1
                            except Exception as e:
                                print(f"    ⚠️  Failed to save thesis: {e}")
                    else:
                        print(f"  {agent.__class__.__name__}: No theses generated")

                except Exception as e:
                    error_msg = f"Agent {agent.__class__.__name__} failed: {e}"
                    print(f"  ⚠️  {error_msg}")
                    stats["errors"].append(error_msg)

            # ============================================================
            # STEP 5: GET ACTIONABLE THESES
            # ============================================================
            print(f"\n{'=' * 60}")
            print(f"CYCLE {self.cycle_count}: Actionable Theses")
            print(f"{'=' * 60}")

            try:
                actionable = self.thesis_store.get_actionable(min_conviction=0.70)
                stats["theses_actionable"] = len(actionable)

                if actionable:
                    print(f"✓ {len(actionable)} actionable theses (conviction >= 0.70)")
                else:
                    print("  No actionable theses at this time")

            except Exception as e:
                error_msg = f"Failed to get actionable theses: {e}"
                print(f"⚠️  {error_msg}")
                stats["errors"].append(error_msg)
                actionable = []

            # ============================================================
            # STEP 6 & 7: RISK EVALUATION AND EXECUTION
            # ============================================================
            print(f"\n{'=' * 60}")
            print(f"CYCLE {self.cycle_count}: Risk & Execution")
            print(f"{'=' * 60}")

            for thesis in actionable:
                try:
                    # Risk evaluation
                    risk_decision = self.risk_engine.evaluate(thesis, portfolio)

                    print(f"\n  Thesis: {thesis.market_id[:40]}")
                    print(
                        f"  Edge: {thesis.edge:.2%}, Conviction: {thesis.conviction:.2f}"
                    )
                    print(f"  Risk: {risk_decision}")

                    # Execute if approved
                    if risk_decision.approved:
                        # Notify Command Center of opportunity
                        try:
                            self.notify_command_center(thesis, portfolio)
                        except Exception as e:
                            # Don't let notification failure block execution
                            print(f"  ⚠️  Command Center notification error: {e}")

                        # Execute trade
                        try:
                            execution = self.execution_engine.execute(
                                risk_decision, thesis
                            )
                            stats["trades_executed"] += 1

                            print(
                                f"  ✅ EXECUTED: {execution.size:.2f} shares @ ${execution.price:.4f}"
                            )

                        except Exception as e:
                            error_msg = f"Execution failed for {thesis.market_id}: {e}"
                            print(f"  ❌ {error_msg}")
                            stats["errors"].append(error_msg)
                    else:
                        print(f"  ❌ REJECTED: {risk_decision.reason}")

                except Exception as e:
                    error_msg = f"Risk evaluation failed for thesis: {e}"
                    print(f"  ⚠️  {error_msg}")
                    stats["errors"].append(error_msg)

            # ============================================================
            # CYCLE SUMMARY
            # ============================================================
            print(f"\n{'=' * 60}")
            print(f"CYCLE {self.cycle_count}: Summary")
            print(f"{'=' * 60}")
            print(f"  Positions updated: {stats['positions_updated']}")
            print(f"  Stop-losses triggered: {stats['stop_losses_triggered']}")
            print(f"  Theses generated: {stats['theses_generated']}")
            print(f"  Actionable theses: {stats['theses_actionable']}")
            print(f"  Trades executed: {stats['trades_executed']}")

            if stats["errors"]:
                print(f"  Errors: {len(stats['errors'])}")

            # Log every 10 cycles
            if self.cycle_count % 10 == 0:
                print(f"\n🎯 MILESTONE: Completed {self.cycle_count} cycles")
                print(f"   Portfolio value: ${portfolio.total_value:,.2f}")
                print(f"   Deployed: {portfolio.deployed_pct:.1f}%")
                print(f"   All-time P&L: ${portfolio.all_time_pnl:+,.2f}")

        except Exception as e:
            # Catch-all error handler
            error_msg = f"Cycle {self.cycle_count} failed with exception: {e}"
            full_trace = traceback.format_exc()

            print(f"\n❌ CRITICAL ERROR: {error_msg}")
            print(f"Traceback:\n{full_trace}")

            stats["errors"].append(error_msg)

            # Log to event_log (best effort)
            try:
                from database.db import record_event

                record_event(
                    event_type="orchestrator_error",
                    details={
                        "cycle": self.cycle_count,
                        "error": str(e),
                        "traceback": full_trace,
                        "stats": stats,
                    },
                    severity="critical",
                )
            except Exception as log_error:
                print(f"⚠️  Failed to log error: {log_error}")

        return stats

    def run_forever(self, cycle_delay: int = 60):
        """
        Run orchestrator in continuous loop.

        Args:
            cycle_delay: Seconds to sleep between cycles (default 60)

        This method runs indefinitely until interrupted (Ctrl+C).
        Each cycle is wrapped in error handling to prevent crashes.
        """
        print("\n" + "=" * 60)
        print("BASED MONEY - Trading Orchestrator")
        print("=" * 60)
        print(f"Starting continuous trading loop (cycle delay: {cycle_delay}s)")
        print("Press Ctrl+C to stop")
        print("=" * 60)

        try:
            while True:
                # Run one cycle
                stats = self.run_cycle()

                # Sleep before next cycle
                print(f"\n⏸  Sleeping {cycle_delay}s before next cycle...\n")
                time.sleep(cycle_delay)

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user (Ctrl+C)")
            print(f"Completed {self.cycle_count} cycles")
            print("Shutting down gracefully...")

        except Exception as e:
            print(f"\n\n❌ FATAL ERROR: {e}")
            print(traceback.format_exc())
            raise
