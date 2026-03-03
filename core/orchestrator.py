"""
BASED MONEY - Trading Orchestrator

Main control loop that orchestrates the entire trading system:
ingestion → thesis generation → risk evaluation → execution → monitoring
"""

import time
import traceback
from typing import List, Optional, Dict
from datetime import datetime

from .risk import RiskEngine
from .execution import ExecutionEngine
from .positions import PositionMonitor
from .thesis_store import ThesisStore
from .theme_portfolio import ThemeManager
from .performance_tracker import PerformanceTracker
from models.portfolio import Portfolio


# ============================================================
# ORCHESTRATOR
# ============================================================

class Orchestrator:
    """
    Main trading orchestrator that runs the complete trading cycle.
    
    The orchestrator coordinates all components of the trading system:
    1. Position monitoring and stop-loss management
    2. Thesis generation from multiple agents (routed by theme)
    3. Risk evaluation
    4. Trade execution (tagged with agent_id + theme)
    5. Performance tracking per agent/theme
    6. Weekly/monthly capital reallocation
    
    Usage:
        >>> orchestrator = Orchestrator(
        ...     agents=[geo_agent, signals_agent],
        ...     risk_engine=RiskEngine(),
        ...     execution_engine=ExecutionEngine(broker, portfolio),
        ...     position_monitor=PositionMonitor(broker),
        ...     theme_manager=ThemeManager(total_capital=10000),
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
        theme_manager: Optional[ThemeManager] = None,
        thesis_store: Optional[ThesisStore] = None,
    ):
        """
        Initialize orchestrator.
        
        Args:
            agents: List of agent instances (institutional agents organized by theme)
            risk_engine: Risk engine for pre-trade evaluation
            execution_engine: Execution engine for trade placement
            position_monitor: Position monitor for P&L tracking and stop-losses
            theme_manager: Optional theme manager (creates one if None)
            thesis_store: Optional thesis store (uses global instance if None)
        """
        self.agents = agents
        self.risk_engine = risk_engine
        self.execution_engine = execution_engine
        self.position_monitor = position_monitor
        
        # Theme-based portfolio management
        if theme_manager:
            self.theme_manager = theme_manager
        else:
            # Create default theme manager with portfolio value
            from database.db import get_portfolio
            portfolio = get_portfolio()
            total_capital = portfolio.total_value if portfolio else 10000.0
            self.theme_manager = ThemeManager(total_capital=total_capital)
        
        # Performance tracking
        self.performance_tracker = PerformanceTracker()
        
        # Use provided thesis store or import global
        if thesis_store:
            self.thesis_store = thesis_store
        else:
            from .thesis_store import thesis_store
            self.thesis_store = thesis_store
        
        # Build agent metadata map (agent_id -> agent instance + theme)
        self.agent_map = {}
        for agent in agents:
            agent_id = getattr(agent, 'agent_id', agent.__class__.__name__.lower())
            theme = getattr(agent, 'theme', 'unknown')
            self.agent_map[agent_id] = {
                'instance': agent,
                'theme': theme,
                'agent_id': agent_id
            }
        
        # Cycle counter for logging
        self.cycle_count = 0
    
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
                            execution = self.execution_engine.broker.execute_order(order)
                            print(f"  ✓ Stop-loss executed: {execution.market_id}")
                            
                            # Extract position_id from client_order_id (format: "stop-loss-{position_id}")
                            if hasattr(order, 'client_order_id') and order.client_order_id:
                                position_id = order.client_order_id.replace('stop-loss-', '')
                                
                                # Track closed position for performance
                                self.track_closed_position(position_id)
                                
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
                portfolio = get_portfolio()
                
                if portfolio:
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
            
            # ============================================================
            # STEP 4: GENERATE THESES (THEME-BASED ROUTING)
            # ============================================================
            print(f"\n{'=' * 60}")
            print(f"CYCLE {self.cycle_count}: Thesis Generation (Theme-Based)")
            print(f"{'=' * 60}")
            
            # Group agents by theme for organized output
            theme_groups = {}
            for agent in self.agents:
                agent_id = getattr(agent, 'agent_id', agent.__class__.__name__.lower())
                theme = getattr(agent, 'theme', 'unknown')
                if theme not in theme_groups:
                    theme_groups[theme] = []
                theme_groups[theme].append((agent_id, agent))
            
            # Generate theses per theme
            for theme, theme_agents in theme_groups.items():
                print(f"\n  🎯 Theme: {theme.upper()}")
                
                for agent_id, agent in theme_agents:
                    try:
                        # Call agent's update_theses method
                        theses = agent.update_theses()
                        
                        if theses:
                            print(f"    {agent.__class__.__name__}: {len(theses)} theses")
                            
                            # Save each thesis to store with agent_id tagging
                            for thesis in theses:
                                try:
                                    # Tag thesis with agent_id (should already be set by agent)
                                    if not hasattr(thesis, 'agent_id') or not thesis.agent_id:
                                        thesis.agent_id = agent_id
                                    
                                    # Store metadata for later tracking
                                    if not hasattr(thesis, '_metadata'):
                                        thesis._metadata = {}
                                    thesis._metadata['theme'] = theme
                                    thesis._metadata['agent_id'] = agent_id
                                    
                                    self.thesis_store.save(thesis)
                                    stats["theses_generated"] += 1
                                except Exception as e:
                                    print(f"      ⚠️  Failed to save thesis: {e}")
                        else:
                            print(f"    {agent.__class__.__name__}: No theses")
                            
                    except Exception as e:
                        error_msg = f"Agent {agent.__class__.__name__} failed: {e}"
                        print(f"    ⚠️  {error_msg}")
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
            # STEP 6 & 7: RISK EVALUATION AND EXECUTION (WITH AGENT TRACKING)
            # ============================================================
            print(f"\n{'=' * 60}")
            print(f"CYCLE {self.cycle_count}: Risk & Execution")
            print(f"{'=' * 60}")
            
            for thesis in actionable:
                try:
                    # Extract agent metadata
                    agent_id = thesis.agent_id if hasattr(thesis, 'agent_id') else 'unknown'
                    theme = getattr(thesis, '_metadata', {}).get('theme', 'unknown')
                    
                    # Risk evaluation
                    risk_decision = self.risk_engine.evaluate(thesis, portfolio)
                    
                    print(f"\n  Thesis: {thesis.market_id[:40]}")
                    print(f"  Agent: {agent_id} (Theme: {theme})")
                    print(f"  Edge: {thesis.edge:.2%}, Conviction: {thesis.conviction:.2f}")
                    print(f"  Risk: {risk_decision}")
                    
                    # Execute if approved
                    if risk_decision.approved:
                        try:
                            execution = self.execution_engine.execute(risk_decision, thesis)
                            stats["trades_executed"] += 1
                            
                            print(f"  ✅ EXECUTED: {execution.size:.2f} shares @ ${execution.price:.4f}")
                            
                            # Tag position with agent_id and theme in database
                            self._tag_position_with_agent(
                                execution.position_id,
                                agent_id,
                                theme
                            )
                            
                            # NOTE: Performance tracking happens when position closes
                            # (see position_monitor.check_stop_losses or manual close)
                            
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
    
    def _tag_position_with_agent(self, position_id: str, agent_id: str, theme: str) -> None:
        """
        Tag a position with agent_id and theme in database.
        
        Args:
            position_id: Position UUID
            agent_id: Agent identifier
            theme: Theme name
        """
        try:
            from database.db import supabase_client
            
            supabase_client.table('positions')\
                .update({'agent_id': agent_id, 'theme': theme})\
                .eq('id', position_id)\
                .execute()
            
            print(f"    ✓ Tagged position {position_id[:8]}... with {agent_id}/{theme}")
            
        except Exception as e:
            print(f"    ⚠️ Failed to tag position: {e}")
    
    def track_closed_position(self, position_id: str) -> None:
        """
        Track a closed position's result for agent performance.
        
        Args:
            position_id: Position UUID
        
        This should be called when a position closes (stop-loss or manual).
        """
        try:
            from database.db import supabase_client
            
            # Fetch position details
            result = supabase_client.table('positions')\
                .select('*')\
                .eq('id', position_id)\
                .single()\
                .execute()
            
            if result.data:
                position = result.data
                agent_id = position.get('agent_id')
                theme = position.get('theme')
                pnl = float(position.get('pnl', 0))
                thesis_id = position.get('thesis_id')
                
                if agent_id and theme:
                    # Determine if winning or losing trade
                    trade_result = pnl > 0
                    
                    # Record to agent_performance table
                    self.performance_tracker.track_trade(
                        agent_id=agent_id,
                        theme=theme,
                        thesis_id=thesis_id,
                        trade_result=trade_result,
                        pnl=pnl
                    )
                    
                    # Log to event_log
                    from database.db import record_event
                    record_event(
                        event_type='position_closed_tracked',
                        agent_id=agent_id,
                        position_id=position_id,
                        details={
                            'theme': theme,
                            'pnl': pnl,
                            'result': 'WIN' if trade_result else 'LOSS',
                        },
                        severity='info'
                    )
            
        except Exception as e:
            print(f"⚠️ Failed to track closed position {position_id}: {e}")
    
    def weekly_reallocation_check(self) -> None:
        """
        Execute weekly capital reallocation across themes and agents.
        
        Called every Sunday at 00:00 UTC by scheduler.
        Delegates to ThemeManager.weekly_reallocation().
        """
        try:
            print(f"\n{'='*60}")
            print(f"📊 WEEKLY REALLOCATION CHECK")
            print(f"   Timestamp: {datetime.now().isoformat()}")
            print(f"{'='*60}\n")
            
            # Execute reallocation via ThemeManager
            self.theme_manager.weekly_reallocation()
            
            # Log to database
            from database.db import record_event
            record_event(
                event_type='weekly_reallocation_complete',
                details={
                    'timestamp': datetime.now().isoformat(),
                    'theme_states': self.theme_manager.to_dict()
                },
                severity='info'
            )
            
            print(f"\n{'='*60}")
            print(f"✅ Weekly reallocation complete")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"❌ Weekly reallocation failed: {e}")
            traceback.print_exc()
            
            # Log error
            try:
                from database.db import record_event
                record_event(
                    event_type='weekly_reallocation_error',
                    details={
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    },
                    severity='error'
                )
            except Exception as log_error:
                print(f"⚠️ Failed to log error: {log_error}")
    
    def monthly_theme_review(self) -> None:
        """
        Execute monthly theme rotation logic.
        
        Called on 1st of each month at 00:00 UTC by scheduler.
        Pauses underperforming themes, boosts winners.
        """
        try:
            print(f"\n{'='*60}")
            print(f"🔄 MONTHLY THEME REVIEW")
            print(f"   Timestamp: {datetime.now().isoformat()}")
            print(f"{'='*60}\n")
            
            # Execute rotation via ThemeManager
            self.theme_manager.monthly_theme_rotation()
            
            # Get final theme statuses
            theme_states = {}
            for theme_name, theme in self.theme_manager.themes.items():
                theme_states[theme_name] = {
                    'status': theme.status,
                    'capital': theme.current_capital,
                    'losing_months': theme.losing_months
                }
            
            # Log to database
            from database.db import record_event
            record_event(
                event_type='monthly_theme_review_complete',
                details={
                    'timestamp': datetime.now().isoformat(),
                    'theme_states': theme_states,
                    'full_state': self.theme_manager.to_dict()
                },
                severity='info'
            )
            
            print(f"\n{'='*60}")
            print(f"✅ Monthly theme review complete")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"❌ Monthly theme review failed: {e}")
            traceback.print_exc()
            
            # Log error
            try:
                from database.db import record_event
                record_event(
                    event_type='monthly_theme_review_error',
                    details={
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    },
                    severity='error'
                )
            except Exception as log_error:
                print(f"⚠️ Failed to log error: {log_error}")
    
    def generate_ic_memo(self) -> None:
        """
        Generate daily Investment Committee memo.
        
        Called daily at 23:00 UTC by scheduler.
        Summarizes the day's trading activity, performance, and positions.
        """
        try:
            print(f"\n{'='*60}")
            print(f"📝 GENERATING IC MEMO")
            print(f"   Date: {datetime.now().date()}")
            print(f"{'='*60}\n")
            
            from database.db import get_portfolio, supabase_client
            from datetime import date
            
            # Get portfolio snapshot
            portfolio = get_portfolio()
            
            # Get today's trades
            today = date.today()
            trades_result = supabase_client.table('positions')\
                .select('*')\
                .gte('opened_at', today.isoformat())\
                .execute()
            
            trades = trades_result.data if trades_result.data else []
            
            # Calculate metrics
            trades_count = len(trades)
            winning_trades = sum(1 for t in trades if float(t.get('pnl', 0)) > 0)
            win_rate = (winning_trades / trades_count * 100) if trades_count > 0 else 0
            daily_pnl = portfolio.daily_pnl if portfolio else 0
            
            # Get theme performance
            leaderboard = self.theme_manager.get_theme_leaderboard(period='7d')
            
            # Build memo text (Markdown)
            memo_lines = [
                f"# Investment Committee Memo - {today.isoformat()}",
                "",
                "## Portfolio Summary",
                f"- **Total Value:** ${portfolio.total_value:,.2f}" if portfolio else "- Total Value: N/A",
                f"- **Cash:** ${portfolio.cash:,.2f}" if portfolio else "- Cash: N/A",
                f"- **Daily P&L:** ${daily_pnl:+,.2f}",
                f"- **Deployed:** {portfolio.deployed_pct:.1f}%" if portfolio else "- Deployed: N/A",
                "",
                "## Trading Activity",
                f"- **Trades Today:** {trades_count}",
                f"- **Win Rate:** {win_rate:.1f}%",
                "",
                "## Theme Performance (7d)",
            ]
            
            for rank, theme_data in enumerate(leaderboard, 1):
                memo_lines.append(
                    f"{rank}. **{theme_data['theme'].title()}**: "
                    f"Win Rate {theme_data['win_rate']:.1%}, "
                    f"P&L ${theme_data['total_pnl']:+,.2f}, "
                    f"Capital ${theme_data['current_capital']:,.2f}"
                )
            
            memo_lines.extend([
                "",
                "## Open Positions",
            ])
            
            # Get open positions
            open_result = supabase_client.table('positions')\
                .select('*')\
                .eq('status', 'open')\
                .execute()
            
            open_positions = open_result.data if open_result.data else []
            
            for pos in open_positions[:10]:  # Limit to 10 most recent
                memo_lines.append(
                    f"- {pos.get('market_id', 'Unknown')[:50]}: "
                    f"{pos.get('side')} @ ${float(pos.get('entry_price', 0)):.4f}, "
                    f"P&L ${float(pos.get('pnl', 0)):+,.2f}"
                )
            
            if len(open_positions) > 10:
                memo_lines.append(f"- ... and {len(open_positions) - 10} more positions")
            
            memo_text = "\n".join(memo_lines)
            
            # Save to database
            portfolio_summary = {
                'total_value': float(portfolio.total_value) if portfolio else 0,
                'cash': float(portfolio.cash) if portfolio else 0,
                'deployed_pct': float(portfolio.deployed_pct) if portfolio else 0,
            }
            
            daily_return = (daily_pnl / portfolio.total_value * 100) if portfolio and portfolio.total_value > 0 else 0
            
            memo_data = {
                'date': today.isoformat(),
                'memo_text': memo_text,
                'portfolio_summary': portfolio_summary,
                'trades_count': trades_count,
                'win_rate': round(win_rate, 2),
                'daily_return': round(daily_return, 4)
            }
            
            supabase_client.table('ic_memos').insert(memo_data).execute()
            
            print(f"✅ IC memo generated and saved")
            print(f"\nMemo Preview:")
            print(memo_text[:500])
            print(f"\n{'='*60}\n")
            
        except Exception as e:
            print(f"❌ IC memo generation failed: {e}")
            traceback.print_exc()
    
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
