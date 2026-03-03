"""
BASED MONEY - Base Agent Interface
Abstract base class for all trading intelligence agents
"""

from abc import ABC, abstractmethod
from typing import List
import sys

sys.path.insert(0, "..")

from models import Thesis, Market


class BaseAgent(ABC):
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
        self._theses_cache: List[Thesis] = []

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

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(mandate='{self.mandate}')"
