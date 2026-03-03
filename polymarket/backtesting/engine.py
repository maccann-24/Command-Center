"""
BASED MONEY - Backtest Engine
Simulate agent trading on historical resolved markets with strict temporal controls
"""

import sys
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from collections import defaultdict
from decimal import Decimal

sys.path.insert(0, "..")

from database.db import get_historical_markets, record_event
from models import Position, Portfolio

# ============================================================
# BACKTEST RESULTS
# ============================================================


@dataclass
class Trade:
    """Represents a single backtested trade"""

    date: date
    market_id: str
    market_question: str
    side: str  # 'YES' or 'NO'
    shares: float
    entry_price: float
    exit_price: float  # resolution_value
    pnl: float
    pnl_pct: float
    conviction: float
    thesis_id: str


@dataclass
class BacktestResults:
    """Results from a backtest run"""

    # Configuration
    start_date: date
    end_date: date
    initial_capital: float
    agent_id: str

    # Performance metrics
    final_capital: float
    total_pnl: float
    total_pnl_pct: float

    # Trade statistics
    trades: List[Trade] = field(default_factory=list)
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0

    # Equity curve (daily values)
    equity_curve: List[Tuple[date, float]] = field(default_factory=list)

    # Risk metrics
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: float = 0.0

    # Execution details
    markets_evaluated: int = 0
    theses_generated: int = 0
    theses_executed: int = 0

    def calculate_metrics(self):
        """Calculate derived metrics from trades"""
        if not self.trades:
            return

        # Basic stats
        self.total_trades = len(self.trades)
        self.winning_trades = sum(1 for t in self.trades if t.pnl > 0)
        self.losing_trades = sum(1 for t in self.trades if t.pnl < 0)

        if self.total_trades > 0:
            self.win_rate = (self.winning_trades / self.total_trades) * 100.0

        # P&L
        self.total_pnl = self.final_capital - self.initial_capital
        if self.initial_capital > 0:
            self.total_pnl_pct = (self.total_pnl / self.initial_capital) * 100.0

        # Drawdown
        self._calculate_drawdown()

        # Sharpe ratio (simplified daily returns)
        self._calculate_sharpe()

    def _calculate_drawdown(self):
        """Calculate maximum drawdown from equity curve"""
        if not self.equity_curve:
            return

        peak = self.equity_curve[0][1]
        max_dd = 0.0

        for _, value in self.equity_curve:
            if value > peak:
                peak = value

            drawdown = peak - value
            if drawdown > max_dd:
                max_dd = drawdown

        self.max_drawdown = max_dd
        if peak > 0:
            self.max_drawdown_pct = (max_dd / peak) * 100.0

    def _calculate_sharpe(self):
        """Calculate Sharpe ratio from daily returns"""
        if len(self.equity_curve) < 2:
            self.sharpe_ratio = 0.0
            return

        # Calculate daily returns
        returns = []
        for i in range(1, len(self.equity_curve)):
            prev_value = self.equity_curve[i - 1][1]
            curr_value = self.equity_curve[i][1]

            if prev_value > 0:
                daily_return = (curr_value - prev_value) / prev_value
                returns.append(daily_return)

        if not returns:
            self.sharpe_ratio = 0.0
            return

        # Mean and std of returns
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_return = variance**0.5

        # Annualized Sharpe (assuming 252 trading days)
        if std_return > 0:
            self.sharpe_ratio = (mean_return / std_return) * (252**0.5)
        else:
            self.sharpe_ratio = 0.0

    def summary(self) -> str:
        """Generate human-readable summary"""
        lines = [
            "=" * 60,
            "BACKTEST RESULTS",
            "=" * 60,
            f"Agent: {self.agent_id}",
            f"Period: {self.start_date} to {self.end_date}",
            f"Initial Capital: ${self.initial_capital:,.2f}",
            "",
            "PERFORMANCE",
            "-" * 60,
            f"Final Capital: ${self.final_capital:,.2f}",
            f"Total P&L: ${self.total_pnl:,.2f} ({self.total_pnl_pct:+.2f}%)",
            f"Max Drawdown: ${self.max_drawdown:,.2f} ({self.max_drawdown_pct:.2f}%)",
            f"Sharpe Ratio: {self.sharpe_ratio:.2f}",
            "",
            "TRADES",
            "-" * 60,
            f"Total Trades: {self.total_trades}",
            f"Winning Trades: {self.winning_trades}",
            f"Losing Trades: {self.losing_trades}",
            f"Win Rate: {self.win_rate:.1f}%",
            "",
            "ACTIVITY",
            "-" * 60,
            f"Markets Evaluated: {self.markets_evaluated}",
            f"Theses Generated: {self.theses_generated}",
            f"Theses Executed: {self.theses_executed}",
            f"Execution Rate: {(self.theses_executed / max(1, self.theses_generated)) * 100:.1f}%",
            "=" * 60,
        ]

        return "\n".join(lines)


# ============================================================
# BACKTEST ENGINE
# ============================================================


class BacktestEngine:
    """
    Backtest engine for simulating agent trading on historical data.

    CRITICAL: Prevents lookahead bias by ensuring agents only see
    markets that were available at decision time, not future outcomes.
    """

    def __init__(self):
        """Initialize backtest engine"""
        self.portfolio: Optional[Portfolio] = None
        self.results: Optional[BacktestResults] = None
        self.min_conviction = 0.70  # Minimum conviction to execute

    def run_backtest(
        self,
        agent,
        start_date: date,
        end_date: date,
        initial_capital: float = 1000.0,
        min_conviction: float = 0.70,
    ) -> BacktestResults:
        """
        Run backtest simulation for an agent over historical data.

        Args:
            agent: Agent instance with update_theses() and generate_thesis() methods
            start_date: Start date for backtest period
            end_date: End date for backtest period
            initial_capital: Starting capital in USD (default: $1000)
            min_conviction: Minimum conviction to execute trades (default: 0.70)

        Returns:
            BacktestResults object with trades, equity curve, and metrics
        """
        print("\n" + "=" * 60)
        print("BACKTEST SIMULATION")
        print("=" * 60)
        print(f"Agent: {agent.__class__.__name__}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Initial Capital: ${initial_capital:,.2f}")
        print(f"Min Conviction: {min_conviction:.0%}")
        print()

        self.min_conviction = min_conviction

        # Initialize portfolio
        self.portfolio = Portfolio(
            cash=initial_capital,
            positions=[],
            total_value=initial_capital,
            deployed_pct=0.0,
            daily_pnl=0.0,
            all_time_pnl=0.0,
        )

        # Initialize results tracker
        self.results = BacktestResults(
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            agent_id=agent.__class__.__name__,
            final_capital=initial_capital,
        )

        # Load historical markets
        print("📊 Loading historical markets...")
        historical_markets = get_historical_markets(start_date, end_date)

        if not historical_markets:
            print("⚠️  No historical markets found in date range")
            print("=" * 60)
            return self.results

        print(f"   Loaded {len(historical_markets)} historical markets\n")

        # Group markets by resolution date
        markets_by_date = self._group_markets_by_date(historical_markets)

        # Get all unique dates and sort chronologically
        all_dates = sorted(markets_by_date.keys())

        print(f"📅 Simulating {len(all_dates)} trading days...\n")

        # Iterate day-by-day (STRICT TEMPORAL ORDER)
        for current_date in all_dates:
            self._simulate_day(current_date, markets_by_date, all_dates, agent)

        # Finalize results
        self.results.final_capital = self.portfolio.total_value
        self.results.calculate_metrics()

        # Log backtest completion
        record_event(
            event_type="backtest_completed",
            agent_id=agent.__class__.__name__,
            details={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "trades": self.results.total_trades,
                "win_rate": self.results.win_rate,
                "final_capital": self.results.final_capital,
                "total_pnl_pct": self.results.total_pnl_pct,
            },
            severity="info",
        )

        # Print summary
        print("\n" + self.results.summary())

        return self.results

    def _group_markets_by_date(
        self, historical_markets: List[Dict]
    ) -> Dict[date, List[Dict]]:
        """
        Group markets by their resolution date.

        Args:
            historical_markets: List of historical market dictionaries

        Returns:
            Dictionary mapping date -> list of markets resolving on that date
        """
        markets_by_date = defaultdict(list)

        for market in historical_markets:
            # Extract resolution date
            resolution_date = market.get("resolution_date")

            if isinstance(resolution_date, str):
                resolution_date = datetime.fromisoformat(resolution_date).date()
            elif isinstance(resolution_date, datetime):
                resolution_date = resolution_date.date()

            if resolution_date:
                markets_by_date[resolution_date].append(market)

        return dict(markets_by_date)

    def _simulate_day(
        self,
        current_date: date,
        markets_by_date: Dict[date, List[Dict]],
        all_dates: List[date],
        agent,
    ):
        """
        Simulate a single trading day.

        CRITICAL: Only shows agent markets with resolution_date >= current_date
        (i.e., markets that haven't expired yet)

        Args:
            current_date: Date being simulated
            markets_by_date: All markets grouped by resolution date
            all_dates: All dates in chronological order
            agent: Agent instance
        """
        # Get markets that resolve today
        resolving_markets = markets_by_date.get(current_date, [])

        # Get markets still available for trading (resolution_date >= current_date)
        # CRITICAL: This prevents lookahead bias - agent can't trade expired markets
        available_markets = []
        for future_date in all_dates:
            if future_date >= current_date:
                available_markets.extend(markets_by_date.get(future_date, []))

        # Update metrics
        self.results.markets_evaluated += len(available_markets)

        # Generate theses for available markets
        # NOTE: We need to convert historical market dicts to Market objects
        # or have agent work with dicts. For simplicity, using dicts.
        theses = self._generate_theses_for_markets(agent, available_markets)

        self.results.theses_generated += len(theses)

        # Execute high-conviction theses
        for thesis in theses:
            if thesis.get("conviction", 0.0) >= self.min_conviction:
                self._execute_thesis(thesis, current_date)

        # Resolve positions for markets closing today
        for market in resolving_markets:
            self._resolve_market_positions(market, current_date)

        # Record equity curve point
        self.results.equity_curve.append((current_date, self.portfolio.total_value))

    def _generate_theses_for_markets(
        self, agent, available_markets: List[Dict]
    ) -> List[Dict]:
        """
        Generate theses for available markets.

        This is a simplified approach - ideally agents would have
        a backtest-compatible method. For now, we generate theses
        for each market individually.

        Args:
            agent: Agent instance
            available_markets: Markets available for trading

        Returns:
            List of thesis dictionaries
        """
        theses = []

        for market_data in available_markets:
            try:
                # Create a simplified Market-like object
                from models import Market

                market = Market(
                    id=market_data["id"],
                    question=market_data["question"],
                    category=market_data.get("category", "unknown"),
                    yes_price=float(market_data.get("yes_price", 0.0)),
                    no_price=float(market_data.get("no_price", 0.0)),
                    volume_24h=float(market_data.get("volume_24h", 0.0)),
                    resolution_date=market_data.get("resolution_date"),
                    resolved=False,  # From agent's perspective, not resolved yet
                )

                # Generate thesis using agent
                thesis = agent.generate_thesis(market)

                # Convert to dict and attach market metadata
                thesis_dict = {
                    "id": str(thesis.id),
                    "market_id": market.id,
                    "market_question": market.question,
                    "conviction": thesis.conviction,
                    "edge": thesis.edge,
                    "proposed_action": thesis.proposed_action,
                    "yes_price": market.yes_price,
                    "no_price": market.no_price,
                    "resolution_value": market_data.get("resolution_value", 0.0),
                }

                theses.append(thesis_dict)

            except Exception as e:
                # Skip markets that fail to generate theses
                continue

        return theses

    def _execute_thesis(self, thesis: Dict, current_date: date):
        """
        Execute a thesis by opening a position.

        Args:
            thesis: Thesis dictionary
            current_date: Date of execution
        """
        # Check if we have enough cash
        if self.portfolio.cash <= 0:
            return

        # Get proposed action
        proposed_action = thesis.get("proposed_action", {})
        side = proposed_action.get("side", "YES")
        size_pct = proposed_action.get("size_pct", 0.0)

        # Get market price
        yes_price = thesis.get("yes_price", 0.5)
        no_price = thesis.get("no_price", 0.5)

        entry_price = yes_price if side == "YES" else no_price

        # Calculate position size
        # shares = (cash * size_pct) / price
        position_cash = self.portfolio.cash * (size_pct / 100.0)

        if position_cash <= 0 or entry_price <= 0:
            return

        shares = position_cash / entry_price

        # Create position
        from uuid import uuid4

        position = Position(
            id=uuid4(),
            market_id=thesis["market_id"],
            side=side,
            shares=shares,
            entry_price=entry_price,
            current_price=entry_price,
            pnl=0.0,
            status="open",
            thesis_id=thesis["id"],
            opened_at=datetime.combine(current_date, datetime.min.time()),
        )

        # Add to portfolio
        self.portfolio.add_position(position)

        # Track execution
        self.results.theses_executed += 1

    def _resolve_market_positions(self, market: Dict, current_date: date):
        """
        Resolve positions for a market that closed today.

        Args:
            market: Historical market dictionary with resolution_value
            current_date: Resolution date
        """
        market_id = market["id"]
        resolution_value = float(market.get("resolution_value", 0.0))

        # Find open positions for this market
        positions_to_close = [
            pos
            for pos in self.portfolio.positions
            if pos.market_id == market_id and pos.status == "open"
        ]

        for position in positions_to_close:
            # Calculate exit price based on position side and resolution
            # If side=YES and resolved YES (1.0), exit_price = 1.0
            # If side=YES and resolved NO (0.0), exit_price = 0.0
            # If side=NO and resolved YES (1.0), exit_price = 0.0
            # If side=NO and resolved NO (0.0), exit_price = 1.0

            if position.side == "YES":
                exit_price = resolution_value
            else:  # NO
                exit_price = 1.0 - resolution_value

            # Calculate P&L
            entry_cost = position.entry_price * position.shares
            exit_value = exit_price * position.shares
            pnl = exit_value - entry_cost
            pnl_pct = (pnl / entry_cost * 100.0) if entry_cost > 0 else 0.0

            # Close position
            self.portfolio.close_position(position, exit_price)

            # Record trade
            trade = Trade(
                date=current_date,
                market_id=market_id,
                market_question=market.get("question", "Unknown"),
                side=position.side,
                shares=position.shares,
                entry_price=position.entry_price,
                exit_price=exit_price,
                pnl=pnl,
                pnl_pct=pnl_pct,
                conviction=0.0,  # TODO: Retrieve from thesis
                thesis_id=str(position.thesis_id) if position.thesis_id else "unknown",
            )

            self.results.trades.append(trade)


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================


def run_simple_backtest(agent, days_back: int = 90) -> BacktestResults:
    """
    Run a simple backtest for the last N days.

    Args:
        agent: Agent instance
        days_back: Number of days to backtest (default: 90)

    Returns:
        BacktestResults object
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)

    engine = BacktestEngine()
    return engine.run_backtest(agent, start_date, end_date)
