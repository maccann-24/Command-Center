"""
BASED MONEY - Base Agent Interface
Abstract base class for all trading intelligence agents
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
import logging

sys.path.insert(0, '..')

from models import Thesis, Market
from database.db import get_supabase_client

# Set up logging
logger = logging.getLogger(__name__)

# Import chat mixin
try:
    from agents.chat_mixin import TradingFloorChatMixin
except ImportError:
    # Fallback if chat_mixin not available
    class TradingFloorChatMixin:
        pass


class BaseAgent(TradingFloorChatMixin, ABC):
    """
    Abstract base class for trading intelligence agents.
    
    Each agent specializes in finding mispriced markets within its domain
    and generates actionable theses with calculated edge and conviction.
    
    Subclasses must implement:
    - update_theses(): Generate theses for current market conditions
    - generate_thesis(market): Create a thesis for a specific market
    - mandate: Property describing the agent's focus area
    """
    
    def __init__(self):
        """Initialize the base agent."""
        # Initialize parent class if it has __init__
        if hasattr(super(), '__init__'):
            try:
                super().__init__()
            except:
                pass
        
        self._theses_cache: List[Thesis] = []
        
        # Chat monitoring state
        self._last_chat_check: Optional[datetime] = None
        self._seen_message_ids: set = set()
        self._conversation_context: List[Dict] = []  # Last 50 messages
        self._pending_mentions: List[tuple] = []  # Queue of (message_id, sender, question)
        self._last_mention_response: Dict[str, datetime] = {}  # Track responses by sender
        
        # Debate tracking state
        self._active_debates: Dict[str, Dict] = {}  # market_id -> debate_state
        # debate_state: {
        #   'participants': [agent_id1, agent_id2],
        #   'turn_count': int,
        #   'max_turns': 3,
        #   'started_at': datetime,
        #   'last_turn_at': datetime,
        #   'exchanges': [{'agent': str, 'message': str, 'timestamp': datetime}]
        # }
        self._debate_cooldowns: Dict[str, datetime] = {}  # market_id -> cooldown_end
        
        # Spontaneous posting state
        self._last_spontaneous_post: Optional[datetime] = None  # Track last spontaneous observation
        self._chattiness: float = 0.5  # 0-1, how often to post spontaneously
        
        # Interaction memory
        self._interaction_history: Dict[str, List[Dict]] = {}  # agent_id -> [{timestamp, topic, summary}]
        self._relationships: Dict[str, Dict] = {}  # agent_id -> {interaction_count, last_interaction, topics}
    
    @property
    @abstractmethod
    def mandate(self) -> str:
        """
        The agent's mandate/focus area.
        
        This describes what markets or conditions the agent specializes in.
        Examples:
        - "Russia/Ukraine, US-China, Iran, elections"
        - "Follow top traders >55% win rate"
        - "Bitcoin, Ethereum, crypto market events"
        
        Returns:
            String describing the agent's focus area
        """
        pass
    
    @abstractmethod
    def update_theses(self) -> List[Thesis]:
        """
        Generate or update theses based on current market conditions.
        
        This is the main entry point called by the orchestrator.
        The agent should:
        1. Query relevant markets from the database
        2. Analyze each market for edge opportunities
        3. Generate Thesis objects for actionable trades
        4. Return list of theses (can be empty if no opportunities)
        
        Returns:
            List of Thesis objects with calculated edge and conviction
        """
        pass
    
    @abstractmethod
    def generate_thesis(self, market: Market) -> Thesis:
        """
        Generate a thesis for a specific market.
        
        Analyzes a single market and creates a Thesis if edge is detected.
        Used internally by update_theses() or for ad-hoc analysis.
        
        Args:
            market: Market object to analyze
        
        Returns:
            Thesis object with edge calculation and trading recommendation
        """
        pass
    
    def get_cached_theses(self) -> List[Thesis]:
        """
        Get cached theses from last update_theses() call.
        
        Returns:
            List of previously generated theses
        """
        return self._theses_cache
    
    def clear_cache(self):
        """Clear the thesis cache."""
        self._theses_cache = []
    
    def chat_heartbeat(self) -> None:
        """
        Chat heartbeat - called periodically by daemon.
        
        This is the entry point for autonomous chat behavior.
        Agents check chat, respond to mentions, and may post spontaneously.
        
        Called on schedule:
        - Every 5 minutes during market hours (9am-5pm EST Mon-Fri)
        - Every 30 minutes outside market hours
        """
        try:
            # Import here to avoid circular dependency
            from datetime import datetime
            
            logger.debug(f"[{self.agent_id}] Chat heartbeat triggered at {datetime.now().isoformat()}")
            
            # Check if we have chat monitoring capability
            if hasattr(self, 'monitor_and_respond'):
                # Check last 10 minutes of chat
                self.monitor_and_respond(minutes_back=10)
            else:
                logger.warning(f"[{self.agent_id}] No monitor_and_respond method - chat_mixin not loaded")
            
            # Check for conflicts (PROMPT 5)
            if hasattr(self, 'check_for_conflicts'):
                self.check_for_conflicts()
            
            # Potentially post spontaneous observation (PROMPT 7)
            if hasattr(self, 'post_random_observation'):
                self.post_random_observation()
        
        except Exception as e:
            logger.error(f"[{self.agent_id}] Chat heartbeat error: {e}", exc_info=True)
    
    def post_message(self, message_type: str, **kwargs) -> None:
        """
        Post a message to the trading floor.
        
        Inserts a message into the agent_messages table for display on the
        Trading Floor dashboard. Messages are used to track agent activity,
        share theses, detect conflicts, and alert on important events.
        
        Args:
            message_type: Type of message. One of:
                - 'thesis': Agent generated a trade idea
                - 'conflict': Agents disagree on same market
                - 'consensus': Multiple agents agree
                - 'alert': Risk warning or important notice
                - 'analyzing': Agent is researching a market
            **kwargs: Additional message fields:
                - market_question (str): Market question text
                - market_id (str): Market identifier
                - current_odds (float): Current market odds (0-1)
                - thesis_odds (float): Agent's estimated odds (0-1)
                - edge (float): Calculated edge (0-1)
                - conviction (float): Confidence level (0-1)
                - capital_allocated (float): Dollar amount to trade
                - reasoning (str): Explanation text
                - signals (dict): Data sources used (news, social, etc.)
                - status (str): Message status
                - related_thesis_id (str): Link to thesis
                - tags (list): List of string tags
        
        Returns:
            None (silently logs errors without raising)
        
        Example usage:
            # When starting analysis
            self.post_message(
                'analyzing',
                market_question="Will Trump win 2024 election?",
                current_odds=0.45,
                status='analyzing'
            )
            
            # When thesis is generated
            self.post_message(
                'thesis',
                market_question="Will Trump win 2024 election?",
                market_id='polymarket_123',
                current_odds=0.45,
                thesis_odds=0.52,
                edge=0.07,
                conviction=0.68,
                capital_allocated=250.00,
                reasoning="Strong polling momentum in swing states...",
                signals={'news': [...], 'polls': [...]},
                status='thesis_generated',
                related_thesis_id='thesis_xyz'
            )
            
            # When trade is rejected
            self.post_message(
                'alert',
                market_question="Will Trump win 2024 election?",
                reasoning="Rejected: Insufficient edge (6.2% < 7% required)",
                status='rejected'
            )
        """
        # Validate message type
        valid_types = ['thesis', 'conflict', 'consensus', 'alert', 'analyzing', 'chat', 'directive']
        if message_type not in valid_types:
            logger.warning(
                f"Invalid message_type '{message_type}'. "
                f"Must be one of: {valid_types}"
            )
            return
        
        # Check that agent has required attributes (set by subclasses)
        if not hasattr(self, 'agent_id'):
            logger.error(
                f"{self.__class__.__name__} missing 'agent_id' attribute. "
                "Cannot post message."
            )
            return
        
        if not hasattr(self, 'theme'):
            logger.error(
                f"{self.__class__.__name__} missing 'theme' attribute. "
                "Cannot post message."
            )
            return
        
        try:
            # Build message data
            message_data = {
                'agent_id': self.agent_id,
                'theme': self.theme,
                'message_type': message_type,
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            # Add optional fields from kwargs
            optional_fields = [
                'content', 'market_question', 'market_id', 'current_odds', 'thesis_odds',
                'edge', 'conviction', 'capital_allocated', 'reasoning',
                'signals', 'status', 'related_thesis_id', 'tags'
            ]
            
            for field in optional_fields:
                if field in kwargs and kwargs[field] is not None:
                    message_data[field] = kwargs[field]
            
            # Insert into database
            supabase = get_supabase_client()
            supabase.table('agent_messages').insert(message_data).execute()
            
            logger.debug(
                f"[{self.agent_id}] Posted {message_type} message: "
                f"{kwargs.get('market_question', 'N/A')}"
            )
        
        except Exception as e:
            # Log error but don't crash the agent
            logger.error(
                f"[{self.agent_id}] Failed to post message: {e}",
                exc_info=True
            )
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(mandate='{self.mandate}')"
