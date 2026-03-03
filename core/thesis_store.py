"""
BASED MONEY - Thesis Store
High-level interface for thesis persistence and retrieval
"""

from typing import List, Optional
from datetime import datetime, timedelta
import sys

# Import database layer
try:
    from database.db import save_thesis as db_save_thesis, get_theses
except ImportError:
    sys.path.insert(0, '..')
    from database.db import save_thesis as db_save_thesis, get_theses

from models import Thesis


class ThesisStore:
    """
    High-level interface for thesis storage and retrieval.
    Wraps database layer with convenience methods.
    """
    
    def save(self, thesis: Thesis) -> bool:
        """
        Save a thesis to the database.
        
        Args:
            thesis: Thesis object to save
        
        Returns:
            True if successful, False otherwise
        """
        return db_save_thesis(thesis)
    
    def get_actionable(self, min_conviction: float = 0.70) -> List[Thesis]:
        """
        Get actionable theses (high conviction, recent, active).
        
        Retrieves theses that meet all criteria:
        - Conviction >= min_conviction
        - Status = 'active'
        - Created within last 4 hours
        
        Args:
            min_conviction: Minimum conviction threshold (default: 0.70)
        
        Returns:
            List of actionable Thesis objects, ordered by conviction (highest first)
        """
        # Calculate time cutoff (4 hours ago)
        cutoff_time = datetime.utcnow() - timedelta(hours=4)
        
        # Query with filters
        filters = {
            "min_conviction": min_conviction,
            "status": "active",
            "created_after": cutoff_time
        }
        
        return get_theses(filters=filters)
    
    def get_by_market(self, market_id: str) -> List[Thesis]:
        """
        Get all active theses for a specific market.
        
        Args:
            market_id: Market identifier
        
        Returns:
            List of active Thesis objects for this market
        """
        filters = {
            "market_id": market_id,
            "status": "active"
        }
        
        return get_theses(filters=filters)


# ============================================================
# CONVENIENCE SINGLETON
# ============================================================

# Single instance for easy import
thesis_store = ThesisStore()
