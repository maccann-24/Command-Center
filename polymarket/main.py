#!/usr/bin/env python3
"""
BASED MONEY - Main Entry Point

Automated trading system for Polymarket prediction markets.
Coordinates ingestion, thesis generation, risk evaluation, and execution.
"""

import sys
import signal
from typing import List

# Load and validate config first
import config

print(f"\n{'=' * 60}")
print("BASED MONEY v1.0 - Initializing...")
print(f"{'=' * 60}")
print(f"Trading Mode: {config.TRADING_MODE.upper()}")
print(f"Initial Capital: ${config.INITIAL_CAPITAL:,.2f}")
print(f"{'=' * 60}\n")

# Import core components
from core.risk import RiskEngine
from core.execution import ExecutionEngine
from core.positions import PositionMonitor
from core.orchestrator import Orchestrator
from models.portfolio import Portfolio

# Import brokers
from brokers.paper import PaperBroker

# Try to import agents (may not all exist yet)
agents_available = []

try:
    from agents.geo import GeoAgent

    agents_available.append("GeoAgent")
except ImportError:
    print("⚠️  GeoAgent not available")
    GeoAgent = None

try:
    from agents.copy import CopyAgent

    agents_available.append("CopyAgent")
except ImportError:
    print("⚠️  CopyAgent not available (stub)")
    CopyAgent = None

try:
    from agents.signals import SignalsAgent

    agents_available.append("SignalsAgent")
except ImportError:
    print("⚠️  SignalsAgent not available")
    SignalsAgent = None

# Try to import ingestion scheduler
try:
    from ingestion.scheduler import start_scheduler, stop_scheduler

    scheduler_available = True
except ImportError:
    print("⚠️  Ingestion scheduler not available")
    scheduler_available = False
    start_scheduler = None
    stop_scheduler = None


# ============================================================
# STUB AGENTS (if not implemented yet)
# ============================================================


class StubAgent:
    """Stub agent for testing"""

    def __init__(self, name: str):
        self.name = name
        self.agent_id = name.lower().replace(" ", "-")

    def update_theses(self):
        """Stub method - returns empty list"""
        return []

    def __repr__(self):
        return f"<StubAgent: {self.name}>"


# ============================================================
# INITIALIZATION
# ============================================================


def initialize_portfolio() -> Portfolio:
    """
    Initialize portfolio from database or create new one.

    Returns:
        Portfolio object with current state
    """
    try:
        from database.db import get_portfolio

        portfolio_data = get_portfolio()

        if portfolio_data:
            # Convert dict to Portfolio object
            portfolio = Portfolio(
                cash=portfolio_data.get("cash", config.INITIAL_CAPITAL),
                total_value=portfolio_data.get("total_value", config.INITIAL_CAPITAL),
                deployed_pct=portfolio_data.get("deployed_pct", 0.0),
                daily_pnl=portfolio_data.get("daily_pnl", 0.0),
                all_time_pnl=portfolio_data.get("all_time_pnl", 0.0),
                positions=[],
            )
            print(f"✓ Loaded portfolio from database")
            print(f"  Cash: ${portfolio.cash:,.2f}")
            print(f"  Total Value: ${portfolio.total_value:,.2f}")
            print(f"  Deployed: {portfolio.deployed_pct:.1f}%")
            return portfolio
    except Exception as e:
        print(f"⚠️  Could not load portfolio from DB: {e}")

    # Create new portfolio
    portfolio = Portfolio(
        cash=config.INITIAL_CAPITAL,
        total_value=config.INITIAL_CAPITAL,
        deployed_pct=0.0,
        daily_pnl=0.0,
        all_time_pnl=0.0,
        positions=[],
    )

    print(f"✓ Created new portfolio")
    print(f"  Initial Capital: ${portfolio.cash:,.2f}")

    return portfolio


def initialize_agents() -> List:
    """
    Initialize all available agents.

    Returns:
        List of agent instances
    """
    agents = []

    # Try to initialize each agent type
    if GeoAgent:
        try:
            agent = GeoAgent()
            agents.append(agent)
            print(f"✓ Initialized GeoAgent")
        except Exception as e:
            print(f"⚠️  Failed to initialize GeoAgent: {e}")

    if SignalsAgent:
        try:
            agent = SignalsAgent()
            agents.append(agent)
            print(f"✓ Initialized SignalsAgent")
        except Exception as e:
            print(f"⚠️  Failed to initialize SignalsAgent: {e}")

    if CopyAgent:
        try:
            agent = CopyAgent()
            agents.append(agent)
            print(f"✓ Initialized CopyAgent")
        except Exception as e:
            print(f"⚠️  Failed to initialize CopyAgent: {e}")

    # Add stub agents if no real agents available
    if not agents:
        print("⚠️  No agents available, using stub agents for testing")
        agents = [
            StubAgent("Geopolitical Agent"),
            StubAgent("Copy Agent"),
        ]

    return agents


def initialize_broker():
    """
    Initialize broker based on trading mode.

    Returns:
        Broker adapter instance
    """
    if config.TRADING_MODE == "paper":
        broker = PaperBroker()
        print(f"✓ Initialized PaperBroker (simulated execution)")
        return broker

    elif config.TRADING_MODE == "live":
        # Try to import PolymarketBroker
        try:
            from brokers.polymarket import PolymarketBroker

            broker = PolymarketBroker()
            print(f"✓ Initialized PolymarketBroker (LIVE TRADING)")
            return broker
        except ImportError:
            print(f"❌ PolymarketBroker not implemented yet")
            print(f"   Falling back to PaperBroker")
            return PaperBroker()

    else:
        raise ValueError(f"Invalid TRADING_MODE: {config.TRADING_MODE}")


def start_ingestion():
    """
    Start market and news ingestion scheduler.
    """
    if scheduler_available and start_scheduler:
        try:
            start_scheduler()
            print(f"✓ Started ingestion scheduler (markets + news)")
        except Exception as e:
            print(f"⚠️  Failed to start scheduler: {e}")
    else:
        print(f"⚠️  Ingestion scheduler not available")


def stop_ingestion():
    """
    Stop market and news ingestion scheduler.
    """
    if scheduler_available and stop_scheduler:
        try:
            stop_scheduler()
            print(f"✓ Stopped ingestion scheduler")
        except Exception as e:
            print(f"⚠️  Failed to stop scheduler: {e}")


def save_final_state(portfolio: Portfolio):
    """
    Save final portfolio state to database before shutdown.

    Args:
        portfolio: Portfolio object to save
    """
    try:
        from database.db import update_portfolio

        portfolio_data = {
            "cash": portfolio.cash,
            "total_value": portfolio.total_value,
            "deployed_pct": portfolio.deployed_pct,
            "daily_pnl": portfolio.daily_pnl,
            "all_time_pnl": portfolio.all_time_pnl,
        }

        update_portfolio(portfolio_data)
        print(f"✓ Saved final portfolio state to database")

    except Exception as e:
        print(f"⚠️  Failed to save portfolio: {e}")


# ============================================================
# SIGNAL HANDLERS
# ============================================================


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n\n⚠️  Received shutdown signal")
    raise KeyboardInterrupt


# ============================================================
# MAIN
# ============================================================


def main():
    """
    Main entry point for the trading system.

    Initializes all components and runs the orchestrator in a continuous loop.
    """
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize portfolio
    print("\n" + "=" * 60)
    print("PORTFOLIO INITIALIZATION")
    print("=" * 60)
    portfolio = initialize_portfolio()

    # Initialize agents
    print("\n" + "=" * 60)
    print("AGENT INITIALIZATION")
    print("=" * 60)
    agents = initialize_agents()
    print(f"\nTotal agents: {len(agents)}")
    for agent in agents:
        print(f"  - {agent}")

    # Initialize broker
    print("\n" + "=" * 60)
    print("BROKER INITIALIZATION")
    print("=" * 60)
    broker = initialize_broker()

    # Initialize risk engine
    print("\n" + "=" * 60)
    print("RISK ENGINE INITIALIZATION")
    print("=" * 60)
    risk_engine = RiskEngine()
    print(f"✓ Initialized RiskEngine")
    print(f"  Max Position: {config.RISK_PARAMS['max_position_pct']:.1f}%")
    print(f"  Max Deployed: {config.RISK_PARAMS['max_deployed_pct']:.1f}%")
    print(f"  Min Conviction: {config.RISK_PARAMS['min_conviction']:.2f}")
    print(f"  Stop Loss: {config.RISK_PARAMS['stop_loss_pct']:.1f}%")

    # Initialize execution engine
    print("\n" + "=" * 60)
    print("EXECUTION ENGINE INITIALIZATION")
    print("=" * 60)
    execution_engine = ExecutionEngine(broker_adapter=broker, portfolio=portfolio)
    print(f"✓ Initialized ExecutionEngine")

    # Initialize position monitor
    print("\n" + "=" * 60)
    print("POSITION MONITOR INITIALIZATION")
    print("=" * 60)
    position_monitor = PositionMonitor(broker_adapter=broker)
    print(f"✓ Initialized PositionMonitor")

    # Initialize orchestrator
    print("\n" + "=" * 60)
    print("ORCHESTRATOR INITIALIZATION")
    print("=" * 60)
    orchestrator = Orchestrator(
        agents=agents,
        risk_engine=risk_engine,
        execution_engine=execution_engine,
        position_monitor=position_monitor,
    )
    print(f"✓ Initialized Orchestrator")

    # Start ingestion
    print("\n" + "=" * 60)
    print("INGESTION INITIALIZATION")
    print("=" * 60)
    start_ingestion()

    # Ready to trade
    print("\n" + "=" * 60)
    print("🚀 SYSTEM READY")
    print("=" * 60)
    print(f"Trading Mode: {config.TRADING_MODE.upper()}")
    print(f"Agents: {len(agents)}")
    print(f"Portfolio: ${portfolio.total_value:,.2f}")
    print(f"\nStarting trading loop...")
    print(f"Press Ctrl+C to stop")
    print("=" * 60 + "\n")

    # Run orchestrator
    try:
        orchestrator.run_forever(cycle_delay=60)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("SHUTTING DOWN GRACEFULLY")
        print("=" * 60)

        # Stop ingestion
        stop_ingestion()

        # Save final state
        print("\nSaving final portfolio state...")
        save_final_state(portfolio)

        # Print final stats
        print("\n" + "=" * 60)
        print("FINAL STATISTICS")
        print("=" * 60)
        print(f"Total Cycles: {orchestrator.cycle_count}")
        print(f"Final Cash: ${portfolio.cash:,.2f}")
        print(f"Final Value: ${portfolio.total_value:,.2f}")
        print(f"All-Time P&L: ${portfolio.all_time_pnl:+,.2f}")
        print(f"Open Positions: {len(portfolio.positions)}")

        print("\n" + "=" * 60)
        print("✓ Shutdown complete")
        print("=" * 60 + "\n")

        sys.exit(0)

    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()

        # Try to save state even on error
        try:
            save_final_state(portfolio)
        except:
            pass

        sys.exit(1)


if __name__ == "__main__":
    main()
