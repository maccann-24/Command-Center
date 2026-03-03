"""
BASED MONEY - Performance Tracker
Tracks agent and theme performance, triggers reallocation
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import sys
sys.path.insert(0, '..')

from database import db


class PerformanceTracker:
    """
    Tracks agent and theme trading performance.
    
    Stores trade results in agent_performance table and calculates
    performance metrics for reallocation decisions.
    """
    
    def __init__(self):
        """Initialize the performance tracker."""
        self.db = db
    
    def track_trade(self, agent_id: str, theme: str, thesis_id: Optional[str],
                   trade_result: bool, pnl: float) -> bool:
        """
        Record a trade result for an agent.
        
        Args:
            agent_id: Agent identifier
            theme: Theme name (geopolitical, us_politics, crypto, weather)
            thesis_id: UUID of the thesis that generated this trade
            trade_result: True if winning trade, False if losing
            pnl: Profit/loss in dollars
        
        Returns:
            True if successfully recorded
        """
        try:
            data = {
                "agent_id": agent_id,
                "theme": theme,
                "timestamp": datetime.now().isoformat(),
                "trade_result": trade_result,
                "pnl": float(pnl),
                "thesis_id": thesis_id,
            }
            
            result = self.db.table('agent_performance').insert(data).execute()
            
            if result.data:
                print(f"✓ Tracked trade for {agent_id}: {'WIN' if trade_result else 'LOSS'}, P&L: ${pnl:.2f}")
                return True
            return False
            
        except Exception as e:
            print(f"⚠️ Failed to track trade for {agent_id}: {e}")
            return False
    
    def get_agent_stats(self, agent_id: str, period: str = '7d', 
                        agent_capital: Optional[float] = None) -> Dict:
        """
        Calculate performance statistics for an agent.
        
        Args:
            agent_id: Agent identifier
            period: Time period ('7d' or '30d')
            agent_capital: Agent's current capital allocation (for accurate profit %)
        
        Returns:
            Dictionary with win_rate, total_pnl, sharpe, trades_count, profit_pct
        """
        try:
            # Calculate cutoff time
            days = 7 if period == '7d' else 30
            cutoff = datetime.now() - timedelta(days=days)
            
            # Fetch trades
            result = self.db.table('agent_performance')\
                .select('*')\
                .eq('agent_id', agent_id)\
                .gte('timestamp', cutoff.isoformat())\
                .execute()
            
            trades = result.data if result.data else []
            
            if not trades:
                return {
                    "win_rate": 0.0,
                    "total_pnl": 0.0,
                    "sharpe": 0.0,
                    "trades_count": 0,
                    "profit_pct": 0.0
                }
            
            # Calculate metrics
            wins = sum(1 for t in trades if t['trade_result'])
            total_trades = len(trades)
            win_rate = (wins / total_trades) if total_trades > 0 else 0.0
            
            total_pnl = sum(float(t['pnl']) for t in trades)
            
            # Calculate profit percentage
            if agent_capital and agent_capital > 0:
                profit_pct = (total_pnl / agent_capital) * 100
            else:
                # Fallback: approximate using typical agent allocation (~$833 per agent in a 3-agent theme)
                profit_pct = (total_pnl / 833.0) * 100
            
            # Simple Sharpe calculation (returns / std dev of returns)
            pnls = [float(t['pnl']) for t in trades]
            mean_pnl = sum(pnls) / len(pnls)
            variance = sum((p - mean_pnl) ** 2 for p in pnls) / len(pnls)
            std_dev = variance ** 0.5
            sharpe = (mean_pnl / std_dev) if std_dev > 0 else 0.0
            
            return {
                "win_rate": round(win_rate, 4),
                "total_pnl": round(total_pnl, 2),
                "sharpe": round(sharpe, 2),
                "trades_count": total_trades,
                "profit_pct": round(profit_pct, 2)
            }
            
        except Exception as e:
            print(f"⚠️ Failed to get agent stats for {agent_id}: {e}")
            return {
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "sharpe": 0.0,
                "trades_count": 0,
                "profit_pct": 0.0
            }
    
    def get_theme_stats(self, theme_name: str, period: str = '7d', 
                        theme_capital: Optional[float] = None) -> Dict:
        """
        Calculate aggregate performance statistics for a theme.
        
        Args:
            theme_name: Theme identifier
            period: Time period ('7d' or '30d')
            theme_capital: Theme's current capital allocation (for accurate profit %)
        
        Returns:
            Dictionary with aggregated stats across all theme agents
        """
        try:
            days = 7 if period == '7d' else 30
            cutoff = datetime.now() - timedelta(days=days)
            
            # Fetch all trades for this theme
            result = self.db.table('agent_performance')\
                .select('*')\
                .eq('theme', theme_name)\
                .gte('timestamp', cutoff.isoformat())\
                .execute()
            
            trades = result.data if result.data else []
            
            if not trades:
                return {
                    "win_rate": 0.0,
                    "total_pnl": 0.0,
                    "trades_count": 0,
                    "profit_pct": 0.0,
                    "agent_count": 0
                }
            
            # Calculate theme-wide metrics
            wins = sum(1 for t in trades if t['trade_result'])
            total_trades = len(trades)
            win_rate = (wins / total_trades) if total_trades > 0 else 0.0
            total_pnl = sum(float(t['pnl']) for t in trades)
            
            # Count unique agents
            unique_agents = set(t['agent_id'] for t in trades)
            
            # Calculate profit percentage
            if theme_capital and theme_capital > 0:
                profit_pct = (total_pnl / theme_capital) * 100
            else:
                # Fallback: assume initial theme allocation of $2500
                profit_pct = (total_pnl / 2500.0) * 100
            
            return {
                "win_rate": round(win_rate, 4),
                "total_pnl": round(total_pnl, 2),
                "trades_count": total_trades,
                "profit_pct": round(profit_pct, 2),
                "agent_count": len(unique_agents)
            }
            
        except Exception as e:
            print(f"⚠️ Failed to get theme stats for {theme_name}: {e}")
            return {
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "trades_count": 0,
                "profit_pct": 0.0,
                "agent_count": 0
            }
    
    def get_leaderboard(self, period: str = '7d') -> List[Dict]:
        """
        Get ranked list of all agents by performance.
        
        Args:
            period: Time period ('7d' or '30d')
        
        Returns:
            List of dicts with agent stats, sorted by win rate desc
        """
        try:
            days = 7 if period == '7d' else 30
            cutoff = datetime.now() - timedelta(days=days)
            
            # Fetch all trades in period
            result = self.db.table('agent_performance')\
                .select('*')\
                .gte('timestamp', cutoff.isoformat())\
                .execute()
            
            trades = result.data if result.data else []
            
            if not trades:
                return []
            
            # Group by agent_id
            agent_trades = {}
            for trade in trades:
                agent_id = trade['agent_id']
                if agent_id not in agent_trades:
                    agent_trades[agent_id] = {
                        "agent_id": agent_id,
                        "theme": trade['theme'],
                        "trades": []
                    }
                agent_trades[agent_id]["trades"].append(trade)
            
            # Calculate stats for each agent
            leaderboard = []
            for agent_id, data in agent_trades.items():
                agent_trades_list = data["trades"]
                wins = sum(1 for t in agent_trades_list if t['trade_result'])
                total = len(agent_trades_list)
                win_rate = (wins / total) if total > 0 else 0.0
                total_pnl = sum(float(t['pnl']) for t in agent_trades_list)
                
                leaderboard.append({
                    "agent_id": agent_id,
                    "theme": data["theme"],
                    "win_rate": round(win_rate, 4),
                    "total_pnl": round(total_pnl, 2),
                    "trades_count": total
                })
            
            # Sort by win rate descending
            leaderboard.sort(key=lambda x: (x['win_rate'], x['total_pnl']), reverse=True)
            
            return leaderboard
            
        except Exception as e:
            print(f"⚠️ Failed to get leaderboard: {e}")
            return []
    
    def trigger_weekly_reallocation(self) -> Dict[str, List[str]]:
        """
        Identify winners and losers for weekly capital reallocation.
        
        Returns:
            Dictionary with 'winners', 'losers', and 'probation' agent lists
        """
        leaderboard = self.get_leaderboard(period='7d')
        
        winners = []
        losers = []
        probation = []
        
        for agent in leaderboard:
            # Top performers (win rate >= 60%)
            if agent['win_rate'] >= 0.60:
                winners.append(agent['agent_id'])
            # Probation (win rate < 40%)
            elif agent['win_rate'] < 0.40:
                probation.append(agent['agent_id'])
            # Underperformers
            elif agent['total_pnl'] < 0:
                losers.append(agent['agent_id'])
        
        return {
            "winners": winners,
            "losers": losers,
            "probation": probation
        }
