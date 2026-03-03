"""
BASED MONEY - Theme Portfolio Management
Theme-based portfolio with competing agents
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import sys
sys.path.insert(0, '..')

from reallocation_config.reallocation_rules import (
    get_agent_allocation_pct,
    get_theme_capital_adjustment,
    should_pause_theme,
    MIN_THEME_CAPITAL,
    MIN_AGENT_CAPITAL,
    MAX_THEME_CAPITAL_PCT
)
from core.performance_tracker import PerformanceTracker
from database import db


class ThemePortfolio:
    """
    Represents a single theme portfolio with competing agents.
    
    Each theme (Geopolitical, US Politics, Crypto, Weather) manages
    2-3 agents that compete for capital allocation based on performance.
    """
    
    def __init__(self, name: str, initial_capital: float):
        """
        Initialize a theme portfolio.
        
        Args:
            name: Theme name (geopolitical, us_politics, crypto, weather)
            initial_capital: Starting capital allocation
        """
        self.name = name
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.agents: List[str] = []  # List of agent IDs
        self.weekly_pnl: List[float] = []
        self.monthly_pnl: List[float] = []
        self.losing_weeks = 0
        self.losing_months = 0
        self.status = "ACTIVE"  # ACTIVE, PROBATION, PAUSED
        
        self.tracker = PerformanceTracker()
    
    def add_agent(self, agent_id: str) -> None:
        """
        Register an agent to this theme.
        
        Args:
            agent_id: Agent identifier (e.g., "twosigma_geo")
        """
        if agent_id not in self.agents:
            self.agents.append(agent_id)
            print(f"✓ Added agent {agent_id} to theme {self.name}")
    
    def calculate_performance(self, period: str = '7d') -> Dict:
        """
        Calculate aggregate performance metrics for this theme.
        
        Args:
            period: Time period ('7d' or '30d')
        
        Returns:
            Dictionary with win_rate, total_pnl, profit_pct, trades_count
        """
        return self.tracker.get_theme_stats(self.name, period, theme_capital=self.current_capital)
    
    def get_agent_allocations(self) -> Dict[str, float]:
        """
        Distribute theme capital among agents based on performance.
        
        Returns:
            Dictionary mapping agent_id to capital allocation
        """
        allocations = {}
        
        if not self.agents:
            return allocations
        
        # Get performance stats for each agent
        agent_stats = {}
        for agent_id in self.agents:
            stats = self.tracker.get_agent_stats(agent_id, period='7d')
            agent_stats[agent_id] = stats
        
        # Calculate allocation percentages
        total_allocation_pct = 0.0
        agent_pcts = {}
        
        for agent_id, stats in agent_stats.items():
            pct = get_agent_allocation_pct(stats['win_rate'], stats['profit_pct'])
            agent_pcts[agent_id] = pct
            total_allocation_pct += pct
        
        # Normalize to 100% if needed
        if total_allocation_pct > 0:
            for agent_id, pct in agent_pcts.items():
                normalized_pct = (pct / total_allocation_pct)
                capital = self.current_capital * normalized_pct
                allocations[agent_id] = capital
            
            # Apply minimum capital constraint and rebalance if needed
            total_allocated = sum(allocations.values())
            agents_below_min = {aid: cap for aid, cap in allocations.items() if cap < MIN_AGENT_CAPITAL}
            
            if agents_below_min:
                # Boost below-minimum agents to minimum
                deficit = sum(MIN_AGENT_CAPITAL - cap for cap in agents_below_min.values())
                agents_above_min = {aid: cap for aid, cap in allocations.items() if cap >= MIN_AGENT_CAPITAL}
                
                if agents_above_min:
                    # Take proportionally from agents above minimum
                    total_above = sum(agents_above_min.values())
                    for agent_id in agents_below_min:
                        allocations[agent_id] = MIN_AGENT_CAPITAL
                    for agent_id, capital in agents_above_min.items():
                        reduction = deficit * (capital / total_above)
                        allocations[agent_id] = max(capital - reduction, MIN_AGENT_CAPITAL)
                else:
                    # All agents below minimum, just set all to minimum (will exceed theme capital)
                    for agent_id in allocations:
                        allocations[agent_id] = MIN_AGENT_CAPITAL
        else:
            # Equal distribution if no performance data
            capital_per_agent = self.current_capital / len(self.agents)
            if capital_per_agent < MIN_AGENT_CAPITAL:
                # Theme doesn't have enough capital for minimums, distribute evenly anyway
                for agent_id in self.agents:
                    allocations[agent_id] = capital_per_agent
            else:
                for agent_id in self.agents:
                    allocations[agent_id] = capital_per_agent
        
        return allocations
    
    def reallocate_capital(self) -> Dict[str, float]:
        """
        Update agent capital allocations based on last week's performance.
        
        Returns:
            Dictionary of new agent allocations
        """
        print(f"\n🔄 Reallocating capital for theme: {self.name}")
        
        # Get performance stats
        stats = self.calculate_performance(period='7d')
        
        # Update weekly P&L tracking
        self.weekly_pnl.append(stats['total_pnl'])
        if len(self.weekly_pnl) > 12:  # Keep last 12 weeks
            self.weekly_pnl.pop(0)
        
        # Check for losing week
        if stats['total_pnl'] < 0:
            self.losing_weeks += 1
        else:
            self.losing_weeks = 0  # Reset counter on winning week
        
        # Update theme-level capital based on performance
        capital_adjustment = get_theme_capital_adjustment(
            stats['profit_pct'],
            stats['win_rate'],
            self.losing_weeks
        )
        
        self.current_capital *= capital_adjustment
        
        # Apply minimum capital constraint
        self.current_capital = max(self.current_capital, MIN_THEME_CAPITAL)
        
        # Update status
        if self.losing_weeks >= 2:
            self.status = "PROBATION"
        elif stats['profit_pct'] >= 5.0 and stats['win_rate'] >= 0.55:
            self.status = "ACTIVE"
        
        print(f"  Theme capital: ${self.current_capital:.2f} (adjustment: {capital_adjustment:.2f}x)")
        print(f"  Status: {self.status}")
        print(f"  Stats: Win rate {stats['win_rate']:.2%}, P&L ${stats['total_pnl']:.2f}")
        
        # Get new agent allocations
        allocations = self.get_agent_allocations()
        
        for agent_id, capital in allocations.items():
            print(f"    {agent_id}: ${capital:.2f}")
        
        return allocations
    
    def monthly_review(self) -> None:
        """
        Perform monthly performance review and status update.
        """
        stats = self.calculate_performance(period='30d')
        
        # Update monthly P&L tracking
        self.monthly_pnl.append(stats['total_pnl'])
        if len(self.monthly_pnl) > 12:  # Keep last 12 months
            self.monthly_pnl.pop(0)
        
        # Check for losing month
        if stats['total_pnl'] < 0:
            self.losing_months += 1
        else:
            self.losing_months = 0
        
        # Check if should pause
        if should_pause_theme(self.losing_months):
            self.status = "PAUSED"
            print(f"⚠️ Theme {self.name} PAUSED after {self.losing_months} losing months")
        
    def to_dict(self) -> Dict:
        """
        Serialize theme portfolio to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "initial_capital": self.initial_capital,
            "current_capital": self.current_capital,
            "agents": self.agents,
            "weekly_pnl": self.weekly_pnl,
            "monthly_pnl": self.monthly_pnl,
            "losing_weeks": self.losing_weeks,
            "losing_months": self.losing_months,
            "status": self.status
        }


class ThemeManager:
    """
    Manages all theme portfolios and handles reallocation.
    
    Coordinates capital flow between themes based on performance.
    """
    
    def __init__(self, total_capital: float = 10000.0):
        """
        Initialize theme manager with 4 themes.
        
        Args:
            total_capital: Total portfolio capital
        """
        self.total_capital = total_capital
        
        # Initialize 4 themes with equal allocation
        initial_allocation = total_capital / 4
        
        self.themes: Dict[str, ThemePortfolio] = {
            "geopolitical": ThemePortfolio("geopolitical", initial_allocation),
            "us_politics": ThemePortfolio("us_politics", initial_allocation),
            "crypto": ThemePortfolio("crypto", initial_allocation),
            "weather": ThemePortfolio("weather", initial_allocation),
        }
        
        self.tracker = PerformanceTracker()
        self.db = db
    
    def add_agent_to_theme(self, theme_name: str, agent_id: str) -> bool:
        """
        Register an agent to a specific theme.
        
        Args:
            theme_name: Theme identifier
            agent_id: Agent identifier
        
        Returns:
            True if successfully added
        """
        if theme_name not in self.themes:
            print(f"⚠️ Unknown theme: {theme_name}")
            return False
        
        self.themes[theme_name].add_agent(agent_id)
        return True
    
    def weekly_reallocation(self) -> None:
        """
        Execute weekly capital reallocation across all themes and agents.
        
        Called every Sunday to redistribute capital based on performance.
        """
        print(f"\n{'='*60}")
        print(f"📊 WEEKLY REALLOCATION - {datetime.now().strftime('%Y-%m-%d')}")
        print(f"{'='*60}\n")
        
        # Get current week start date
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        # Reallocate within each theme
        for theme_name, theme in self.themes.items():
            if theme.status == "PAUSED":
                print(f"⏸️ Skipping paused theme: {theme_name}")
                continue
            
            allocations = theme.reallocate_capital()
            
            # Save allocation snapshot to database
            self._save_theme_allocation(theme_name, theme.current_capital, week_start)
        
        # Rebalance across themes if needed
        self._rebalance_themes()
        
        print(f"\n{'='*60}")
        print(f"✅ Weekly reallocation complete")
        print(f"{'='*60}\n")
    
    def monthly_theme_rotation(self) -> None:
        """
        Execute monthly theme rotation logic.
        
        Called on 1st of each month to pause/boost themes.
        """
        print(f"\n{'='*60}")
        print(f"🔄 MONTHLY THEME ROTATION - {datetime.now().strftime('%Y-%m-%d')}")
        print(f"{'='*60}\n")
        
        # Perform monthly review for each theme
        for theme_name, theme in self.themes.items():
            theme.monthly_review()
        
        # Get theme rankings
        rankings = self.get_theme_leaderboard(period='30d')
        
        if rankings:
            # Boost winner, penalize loser
            top_theme_name = rankings[0]['theme']
            bottom_theme_name = rankings[-1]['theme']
            
            top_theme = self.themes[top_theme_name]
            bottom_theme = self.themes[bottom_theme_name]
            
            # Transfer 10% from bottom to top
            transfer_amount = bottom_theme.current_capital * 0.10
            
            if bottom_theme.status != "PAUSED":
                bottom_theme.current_capital -= transfer_amount
                top_theme.current_capital += transfer_amount
                
                print(f"💰 Transferred ${transfer_amount:.2f} from {bottom_theme_name} to {top_theme_name}")
        
        print(f"\n{'='*60}")
        print(f"✅ Monthly rotation complete")
        print(f"{'='*60}\n")
    
    def get_theme_leaderboard(self, period: str = '7d') -> List[Dict]:
        """
        Get ranked list of themes by performance.
        
        Args:
            period: Time period ('7d' or '30d')
        
        Returns:
            List of dicts with theme stats, sorted by performance
        """
        leaderboard = []
        
        for theme_name, theme in self.themes.items():
            stats = theme.calculate_performance(period)
            stats['theme'] = theme_name
            stats['current_capital'] = theme.current_capital
            stats['status'] = theme.status
            leaderboard.append(stats)
        
        # Sort by profit_pct desc
        leaderboard.sort(key=lambda x: x['profit_pct'], reverse=True)
        
        return leaderboard
    
    def _rebalance_themes(self) -> None:
        """
        Ensure total capital sums correctly and no theme exceeds max allocation.
        """
        # Calculate total current capital
        total_current = sum(theme.current_capital for theme in self.themes.values())
        
        # Check if any theme exceeds max percentage
        for theme in self.themes.values():
            theme_pct = (theme.current_capital / total_current) * 100
            max_capital = (MAX_THEME_CAPITAL_PCT / 100) * total_current
            
            if theme.current_capital > max_capital:
                excess = theme.current_capital - max_capital
                theme.current_capital = max_capital
                
                # Redistribute excess to other themes
                active_themes = [t for t in self.themes.values() if t.status == "ACTIVE" and t != theme]
                if active_themes:
                    per_theme = excess / len(active_themes)
                    for active_theme in active_themes:
                        active_theme.current_capital += per_theme
    
    def _save_theme_allocation(self, theme_name: str, capital: float, week_start) -> None:
        """
        Save theme capital allocation snapshot to database.
        
        Args:
            theme_name: Theme identifier
            capital: Current capital allocation
            week_start: Start date of week
        """
        try:
            total_capital = sum(t.current_capital for t in self.themes.values())
            allocation_pct = (capital / total_capital) * 100 if total_capital > 0 else 0
            
            data = {
                "theme": theme_name,
                "capital": float(capital),
                "allocation_pct": round(allocation_pct, 2),
                "week_start": week_start.isoformat()
            }
            
            self.db.table('theme_allocations').insert(data).execute()
            
        except Exception as e:
            print(f"⚠️ Failed to save theme allocation: {e}")
    
    def get_total_portfolio_value(self) -> float:
        """
        Get current total portfolio value across all themes.
        
        Returns:
            Total portfolio value
        """
        return sum(theme.current_capital for theme in self.themes.values())
    
    def to_dict(self) -> Dict:
        """
        Serialize theme manager state to dictionary.
        
        Returns:
            Dictionary with all theme states
        """
        return {
            "total_capital": self.total_capital,
            "current_value": self.get_total_portfolio_value(),
            "themes": {name: theme.to_dict() for name, theme in self.themes.items()}
        }
