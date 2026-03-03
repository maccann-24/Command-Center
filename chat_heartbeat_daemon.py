#!/usr/bin/env python3
"""
Trading Floor Chat Heartbeat Daemon

Runs continuously, triggering agent chat heartbeats on schedule:
- Every 5 minutes during market hours (9am-5pm EST Mon-Fri)
- Every 30 minutes outside market hours

Each agent checks chat, responds to mentions, and may post spontaneously.
"""

import sys
import os
import time
import signal
import logging
from datetime import datetime, time as dt_time
from pathlib import Path
import yaml
import pytz
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import agents
from agents.goldman_geo import GoldmanGeoAgent
from agents.bridgewater_geo import BridgewaterGeoAgent
from agents.twosigma_geo import TwoSigmaGeoAgent
from agents.goldman_politics import GoldmanPoliticsAgent
from agents.jpmorgan_politics import JPMorganPoliticsAgent
from agents.renaissance_politics import RenaissancePoliticsAgent
from agents.morganstanley_crypto import MorganStanleyCryptoAgent
from agents.renaissance_crypto import RenaissanceCryptoAgent
from agents.citadel_crypto import CitadelCryptoAgent
from agents.renaissance_weather import RenaissanceWeatherAgent
from agents.morganstanley_weather import MorganStanleyWeatherAgent
from agents.bridgewater_weather import BridgewaterWeatherAgent


class ChatHeartbeatDaemon:
    """
    Autonomous chat heartbeat daemon.
    
    Wakes agents on schedule to check chat and participate in discussions.
    """
    
    def __init__(self, config_path='config/chat_config.yaml'):
        """Initialize daemon with config."""
        self.config = self._load_config(config_path)
        self.running = True
        self.last_heartbeat = {}
        self.est = pytz.timezone('US/Eastern')
        
        # Setup logging
        self._setup_logging()
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
        
        self.logger.info("="*60)
        self.logger.info("Chat Heartbeat Daemon Started")
        self.logger.info(f"Initialized {len(self.agents)} agents")
        self.logger.info("="*60)
    
    def _load_config(self, config_path):
        """Load configuration from YAML."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _setup_logging(self):
        """Configure logging."""
        log_config = self.config.get('logging', {})
        log_file = log_config.get('file', 'logs/chat_heartbeat.log')
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        
        # Create logs directory if needed
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _initialize_agents(self):
        """Initialize all enabled agents."""
        agents = {}
        agent_classes = {
            'goldman_geo': GoldmanGeoAgent,
            'bridgewater_geo': BridgewaterGeoAgent,
            'twosigma_geo': TwoSigmaGeoAgent,
            'goldman_politics': GoldmanPoliticsAgent,
            'jpmorgan_politics': JPMorganPoliticsAgent,
            'renaissance_politics': RenaissancePoliticsAgent,
            'morganstanley_crypto': MorganStanleyCryptoAgent,
            'renaissance_crypto': RenaissanceCryptoAgent,
            'citadel_crypto': CitadelCryptoAgent,
            'renaissance_weather': RenaissanceWeatherAgent,
            'morganstanley_weather': MorganStanleyWeatherAgent,
            'bridgewater_weather': BridgewaterWeatherAgent,
        }
        
        for agent_id, agent_config in self.config.get('agents', {}).items():
            if not agent_config.get('enabled', False):
                self.logger.info(f"Skipping disabled agent: {agent_id}")
                continue
            
            if agent_id not in agent_classes:
                self.logger.warning(f"Unknown agent: {agent_id}")
                continue
            
            try:
                agent = agent_classes[agent_id]()
                agent.chattiness = agent_config.get('chattiness', 0.5)
                agents[agent_id] = agent
                self.logger.info(f"Initialized: {agent_id} (chattiness: {agent.chattiness})")
            except Exception as e:
                self.logger.error(f"Failed to initialize {agent_id}: {e}")
        
        return agents
    
    def is_market_hours(self) -> bool:
        """Check if current time is market hours (9am-5pm EST Mon-Fri)."""
        now_est = datetime.now(self.est)
        
        # Check day of week (Monday=0, Sunday=6)
        if now_est.weekday() not in [0, 1, 2, 3, 4]:  # Mon-Fri
            return False
        
        # Check time
        market_start = dt_time(9, 0)   # 9:00 AM
        market_end = dt_time(17, 0)    # 5:00 PM
        current_time = now_est.time()
        
        return market_start <= current_time <= market_end
    
    def get_heartbeat_interval(self) -> int:
        """Get current heartbeat interval in seconds."""
        if self.is_market_hours():
            minutes = self.config['schedule']['market_hours']['heartbeat_interval_minutes']
        else:
            minutes = self.config['schedule']['off_hours']['heartbeat_interval_minutes']
        
        return minutes * 60  # Convert to seconds
    
    def should_run_heartbeat(self, agent_id: str) -> bool:
        """Check if agent should run heartbeat now."""
        interval = self.get_heartbeat_interval()
        last = self.last_heartbeat.get(agent_id, 0)
        elapsed = time.time() - last
        
        return elapsed >= interval
    
    def run_agent_heartbeat(self, agent_id: str, agent) -> None:
        """Run heartbeat for a single agent."""
        try:
            self.logger.info(f"[{agent_id}] Heartbeat starting...")
            
            # Call agent's chat_heartbeat method
            agent.chat_heartbeat()
            
            # Update last heartbeat time
            self.last_heartbeat[agent_id] = time.time()
            
            self.logger.info(f"[{agent_id}] Heartbeat complete")
        
        except Exception as e:
            self.logger.error(f"[{agent_id}] Heartbeat error: {e}", exc_info=True)
    
    def run(self):
        """Main daemon loop."""
        self.logger.info("Daemon running. Press Ctrl+C to stop.")
        
        check_interval = 60  # Check every minute
        
        while self.running:
            try:
                # Log current mode
                mode = "MARKET HOURS" if self.is_market_hours() else "OFF HOURS"
                interval = self.get_heartbeat_interval() // 60
                
                self.logger.debug(f"Status check - Mode: {mode}, Interval: {interval}min")
                
                # Check each agent
                for agent_id, agent in self.agents.items():
                    if self.should_run_heartbeat(agent_id):
                        self.run_agent_heartbeat(agent_id, agent)
                
                # Sleep until next check
                time.sleep(check_interval)
            
            except KeyboardInterrupt:
                self.logger.info("Received keyboard interrupt")
                break
            except Exception as e:
                self.logger.error(f"Daemon error: {e}", exc_info=True)
                time.sleep(check_interval)
        
        self._shutdown()
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def _shutdown(self):
        """Clean shutdown."""
        self.logger.info("="*60)
        self.logger.info("Chat Heartbeat Daemon Shutting Down")
        self.logger.info(f"Total heartbeats run: {len(self.last_heartbeat)}")
        self.logger.info("="*60)


def main():
    """Main entry point."""
    daemon = ChatHeartbeatDaemon()
    daemon.run()


if __name__ == "__main__":
    main()
