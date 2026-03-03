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

# Import theme portfolio management
from core.theme_portfolio import ThemeManager

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

# Import institutional agents (Geopolitical theme)
try:
    from agents.twosigma_geo import TwoSigmaGeoAgent
    agents_available.append("TwoSigmaGeoAgent")
except ImportError:
    print("⚠️  TwoSigmaGeoAgent not available")
    TwoSigmaGeoAgent = None

try:
    from agents.goldman_geo import GoldmanGeoAgent
    agents_available.append("GoldmanGeoAgent")
except ImportError:
    print("⚠️  GoldmanGeoAgent not available")
    GoldmanGeoAgent = None

try:
    from agents.bridgewater_geo import BridgewaterGeoAgent
    agents_available.append("BridgewaterGeoAgent")
except ImportError:
    print("⚠️  BridgewaterGeoAgent not available")
    BridgewaterGeoAgent = None

# Import institutional agents (US Politics theme)
try:
    from agents.renaissance_politics import RenaissancePoliticsAgent
    agents_available.append("RenaissancePoliticsAgent")
except ImportError:
    print("⚠️  RenaissancePoliticsAgent not available")
    RenaissancePoliticsAgent = None

try:
    from agents.jpmorgan_politics import JPMorganPoliticsAgent
    agents_available.append("JPMorganPoliticsAgent")
except ImportError:
    print("⚠️  JPMorganPoliticsAgent not available")
    JPMorganPoliticsAgent = None

try:
    from agents.goldman_politics import GoldmanPoliticsAgent
    agents_available.append("GoldmanPoliticsAgent")
except ImportError:
    print("⚠️  GoldmanPoliticsAgent not available")
    GoldmanPoliticsAgent = None

# Import institutional agents (Crypto theme)
try:
    from agents.morganstanley_crypto import MorganStanleyCryptoAgent
    agents_available.append("MorganStanleyCryptoAgent")
except ImportError:
    print("⚠️  MorganStanleyCryptoAgent not available")
    MorganStanleyCryptoAgent = None

try:
    from agents.renaissance_crypto import RenaissanceCryptoAgent
    agents_available.append("RenaissanceCryptoAgent")
except ImportError:
    print("⚠️  RenaissanceCryptoAgent not available")
    RenaissanceCryptoAgent = None

try:
    from agents.citadel_crypto import CitadelCryptoAgent
    agents_available.append("CitadelCryptoAgent")
except ImportError:
    print("⚠️  CitadelCryptoAgent not available")
    CitadelCryptoAgent = None

# Import institutional agents (Weather theme)
try:
    from agents.renaissance_weather import RenaissanceWeatherAgent
    agents_available.append("RenaissanceWeatherAgent")
except ImportError:
    print("⚠️  RenaissanceWeatherAgent not available")
    RenaissanceWeatherAgent = None

try:
    from agents.morganstanley_weather import MorganStanleyWeatherAgent
    agents_available.append("MorganStanleyWeatherAgent")
except ImportError:
    print("⚠️  MorganStanleyWeatherAgent not available")
    MorganStanleyWeatherAgent = None

try:
    from agents.bridgewater_weather import BridgewaterWeatherAgent
    agents_available.append("BridgewaterWeatherAgent")
except ImportError:
    print("⚠️  BridgewaterWeatherAgent not available")
    BridgewaterWeatherAgent = None

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
        portfolio = get_portfolio()
        
        if portfolio:
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


def initialize_agents() -> ThemeManager:
    """
    Initialize theme-based portfolio management with all available agents.
    
    Returns:
        ThemeManager instance with agents registered to themes
    """
    # Create theme manager (auto-creates 4 themes with equal allocation)
    theme_manager = ThemeManager(total_capital=config.INITIAL_CAPITAL)
    
    print(f"✓ Created ThemeManager with 4 themes")
    print(f"  Initial capital per theme: ${config.INITIAL_CAPITAL * 0.25:,.2f} (25% each)")
    
    # Track agent instances for extraction
    all_agent_instances = []
    
    # =================================================================
    # GEOPOLITICAL THEME (3 institutional agents)
    # =================================================================
    geo_agents = []
    
    if TwoSigmaGeoAgent:
        try:
            agent = TwoSigmaGeoAgent()
            geo_agents.append(agent)
            all_agent_instances.append(agent)
            print(f"  ✓ TwoSigmaGeoAgent (macro analysis)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize TwoSigmaGeoAgent: {e}")
    
    if GoldmanGeoAgent:
        try:
            agent = GoldmanGeoAgent()
            geo_agents.append(agent)
            all_agent_instances.append(agent)
            print(f"  ✓ GoldmanGeoAgent (fundamental analysis)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize GoldmanGeoAgent: {e}")
    
    if BridgewaterGeoAgent:
        try:
            agent = BridgewaterGeoAgent()
            geo_agents.append(agent)
            all_agent_instances.append(agent)
            print(f"  ✓ BridgewaterGeoAgent (risk-adjusted analysis)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize BridgewaterGeoAgent: {e}")
    
    # Register geopolitical agents (using agent_id)
    if geo_agents:
        for agent in geo_agents:
            theme_manager.add_agent_to_theme("geopolitical", agent.agent_id)
        print(f"✓ Registered {len(geo_agents)} institutional agents to Geopolitical theme")
    else:
        print(f"⚠️  No institutional Geopolitical agents available")
    
    # =================================================================
    # LEGACY AGENTS (assign to appropriate themes)
    # =================================================================
    
    # GeoAgent → Add to geopolitical theme
    if GeoAgent:
        try:
            agent = GeoAgent()
            all_agent_instances.append(agent)
            theme_manager.add_agent_to_theme("geopolitical", agent.agent_id if hasattr(agent, 'agent_id') else 'geo')
            print(f"  ✓ GeoAgent (legacy - added to Geopolitical)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize GeoAgent: {e}")
    
    # SignalsAgent → Add to geopolitical theme for now
    if SignalsAgent:
        try:
            agent = SignalsAgent()
            all_agent_instances.append(agent)
            theme_manager.add_agent_to_theme("geopolitical", agent.agent_id if hasattr(agent, 'agent_id') else 'signals')
            print(f"  ✓ SignalsAgent (added to Geopolitical)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize SignalsAgent: {e}")
    
    # CopyAgent → Add to geopolitical theme for now
    if CopyAgent:
        try:
            agent = CopyAgent()
            all_agent_instances.append(agent)
            theme_manager.add_agent_to_theme("geopolitical", agent.agent_id if hasattr(agent, 'agent_id') else 'copy')
            print(f"  ✓ CopyAgent (added to Geopolitical)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize CopyAgent: {e}")
    
    # =================================================================
    # US POLITICS THEME (3 institutional agents)
    # =================================================================
    politics_agents = []
    
    if RenaissancePoliticsAgent:
        try:
            agent = RenaissancePoliticsAgent()
            politics_agents.append(agent)
            all_agent_instances.append(agent)
            print(f"  ✓ RenaissancePoliticsAgent (quantitative multi-factor)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize RenaissancePoliticsAgent: {e}")
    
    if JPMorganPoliticsAgent:
        try:
            agent = JPMorganPoliticsAgent()
            politics_agents.append(agent)
            all_agent_instances.append(agent)
            print(f"  ✓ JPMorganPoliticsAgent (event catalyst analysis)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize JPMorganPoliticsAgent: {e}")
    
    if GoldmanPoliticsAgent:
        try:
            agent = GoldmanPoliticsAgent()
            politics_agents.append(agent)
            all_agent_instances.append(agent)
            print(f"  ✓ GoldmanPoliticsAgent (fundamental political analysis)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize GoldmanPoliticsAgent: {e}")
    
    # Register US Politics agents
    if politics_agents:
        for agent in politics_agents:
            theme_manager.add_agent_to_theme("us_politics", agent.agent_id)
        print(f"✓ Registered {len(politics_agents)} institutional agents to US Politics theme")
    else:
        print(f"⚠️  No institutional US Politics agents available")
    
    # =================================================================
    # CRYPTO THEME (3 institutional agents)
    # =================================================================
    crypto_agents = []
    
    if MorganStanleyCryptoAgent:
        try:
            agent = MorganStanleyCryptoAgent()
            crypto_agents.append(agent)
            all_agent_instances.append(agent)
            print(f"  ✓ MorganStanleyCryptoAgent (technical analysis)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize MorganStanleyCryptoAgent: {e}")
    
    if RenaissanceCryptoAgent:
        try:
            agent = RenaissanceCryptoAgent()
            crypto_agents.append(agent)
            all_agent_instances.append(agent)
            print(f"  ✓ RenaissanceCryptoAgent (quantitative crypto)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize RenaissanceCryptoAgent: {e}")
    
    if CitadelCryptoAgent:
        try:
            agent = CitadelCryptoAgent()
            crypto_agents.append(agent)
            all_agent_instances.append(agent)
            print(f"  ✓ CitadelCryptoAgent (cycle positioning)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize CitadelCryptoAgent: {e}")
    
    # Register Crypto agents
    if crypto_agents:
        for agent in crypto_agents:
            theme_manager.add_agent_to_theme("crypto", agent.agent_id)
        print(f"✓ Registered {len(crypto_agents)} institutional agents to Crypto theme")
    else:
        print(f"⚠️  No institutional Crypto agents available")
    
    # =================================================================
    # WEATHER THEME (3 institutional agents)
    # =================================================================
    weather_agents = []
    
    if RenaissanceWeatherAgent:
        try:
            agent = RenaissanceWeatherAgent()
            weather_agents.append(agent)
            all_agent_instances.append(agent)
            print(f"  ✓ RenaissanceWeatherAgent (quantitative meteorological)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize RenaissanceWeatherAgent: {e}")
    
    if MorganStanleyWeatherAgent:
        try:
            agent = MorganStanleyWeatherAgent()
            weather_agents.append(agent)
            all_agent_instances.append(agent)
            print(f"  ✓ MorganStanleyWeatherAgent (technical weather patterns)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize MorganStanleyWeatherAgent: {e}")
    
    if BridgewaterWeatherAgent:
        try:
            agent = BridgewaterWeatherAgent()
            weather_agents.append(agent)
            all_agent_instances.append(agent)
            print(f"  ✓ BridgewaterWeatherAgent (weather risk management)")
        except Exception as e:
            print(f"  ⚠️  Failed to initialize BridgewaterWeatherAgent: {e}")
    
    # Register Weather agents
    if weather_agents:
        for agent in weather_agents:
            theme_manager.add_agent_to_theme("weather", agent.agent_id)
        print(f"✓ Registered {len(weather_agents)} institutional agents to Weather theme")
    else:
        print(f"⚠️  No institutional Weather agents available")
    
    # Print summary
    print(f"\n" + "=" * 60)
    print(f"THEME PORTFOLIO SUMMARY")
    print(f"=" * 60)
    for theme_name, theme in theme_manager.themes.items():
        print(f"{theme_name.upper()}: {len(theme.agents)} agents, ${theme.current_capital:,.2f} capital")
        for agent_id in theme.agents:
            print(f"  - {agent_id}")
    print(f"=" * 60)
    
    # Store agent instances on theme_manager for extraction
    theme_manager._agent_instances = all_agent_instances
    
    return theme_manager


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
    
    # Initialize theme manager and agents
    print("\n" + "=" * 60)
    print("THEME MANAGER & AGENT INITIALIZATION")
    print("=" * 60)
    theme_manager = initialize_agents()
    
    # Extract agent instances (stored during initialization)
    agents = getattr(theme_manager, '_agent_instances', [])
    
    print(f"\nTotal agent instances: {len(agents)}")
    for agent in agents:
        agent_id = agent.agent_id if hasattr(agent, 'agent_id') else agent.__class__.__name__
        print(f"  - {agent_id}")
    
    # Store theme_manager for future use (weekly reallocation, etc.)
    # For now, Orchestrator still works with flat agent list
    
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
        theme_manager=theme_manager,
    )
    print(f"✓ Initialized Orchestrator with ThemeManager")
    
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
