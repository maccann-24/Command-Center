"""
BASED MONEY - IC Memo Generator
Generate daily investment committee memos with portfolio status, theses, and trades
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, List, Optional


def _get_attr(obj: Any, *names: str, default: str = "") -> str:
    for n in names:
        if hasattr(obj, n):
            v = getattr(obj, n)
            if v is not None:
                return str(v)
    return default


def generate_daily_memo(
    memo_date: date,
    theses: List[Any],
    portfolio: Any,
    trades: List[Any],
) -> str:
    """
    Generate a daily IC (Investment Committee) memo.

    Args:
        memo_date: Date for the memo
        theses: List of Thesis objects
        portfolio: Portfolio object
        trades: List of Trade objects from today

    Returns:
        Markdown-formatted memo string

    Sections:
        - Portfolio Summary
        - Active Theses
        - Trades Executed
        - Performance Metrics
        - Disclaimer
    """

    lines = []

    # ============================================================
    # HEADER
    # ============================================================
    lines.append("# BASED MONEY - Daily IC Memo")
    lines.append("")
    lines.append(f"**Date:** {memo_date.strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ============================================================
    # PORTFOLIO SUMMARY
    # ============================================================
    lines.append("## Portfolio Summary")
    lines.append("")
    lines.append(f"- **Cash:** ${portfolio.cash:,.2f}")
    lines.append(f"- **Deployed:** {portfolio.deployed_pct:.1f}%")
    lines.append(f"- **Total Value:** ${portfolio.total_value:,.2f}")
    lines.append(f"- **Daily P&L:** ${portfolio.daily_pnl:+,.2f}")
    lines.append(f"- **All-Time P&L:** ${portfolio.all_time_pnl:+,.2f}")
    lines.append("")

    # Open positions summary
    if portfolio.positions:
        lines.append(f"**Open Positions:** {len(portfolio.positions)}")
        lines.append("")

    # ============================================================
    # ACTIVE THESES
    # ============================================================
    lines.append("## Active Theses")
    lines.append("")

    if theses:
        # Table header
        lines.append("| Market | Edge | Conviction | Status |")
        lines.append("|--------|------|------------|--------|")

        # Table rows
        for thesis in theses:
            market_label = _get_attr(
                thesis,
                "market_question",
                "question",
                "market_id",
                default="(unknown market)",
            )
            market_name = (
                market_label[:50] + "..." if len(market_label) > 50 else market_label
            )
            edge_val = getattr(thesis, "edge", 0.0)
            conviction_val = getattr(thesis, "conviction", 0.0)
            status_val = _get_attr(thesis, "status", default="active")

            edge = (
                f"{edge_val:.1%}"
                if isinstance(edge_val, (int, float))
                else str(edge_val)
            )
            conviction = (
                f"{conviction_val:.2f}"
                if isinstance(conviction_val, (int, float))
                else str(conviction_val)
            )
            status = status_val.upper()

            lines.append(f"| {market_name} | {edge} | {conviction} | {status} |")

        lines.append("")
    else:
        lines.append("*No active theses*")
        lines.append("")

    # ============================================================
    # TRADES EXECUTED
    # ============================================================
    lines.append("## Trades Executed")
    lines.append("")

    if trades:
        # Table header
        lines.append("| Market | Action | Size | Fill Price | Thesis ID | Outcome |")
        lines.append("|--------|--------|------|------------|-----------|---------|")

        # Table rows
        for trade in trades:
            market_label = _get_attr(
                trade,
                "market_question",
                "question",
                "market_id",
                default="(unknown market)",
            )
            market_name = (
                market_label[:40] + "..." if len(market_label) > 40 else market_label
            )
            action = _get_attr(trade, "side", default="?")
            shares = getattr(trade, "shares", 0.0)
            entry_price = getattr(trade, "entry_price", 0.0)
            thesis_id_raw = _get_attr(trade, "thesis_id", default="")
            thesis_id = (
                thesis_id_raw[:8] + "..." if len(thesis_id_raw) > 8 else thesis_id_raw
            )

            size = f"{shares:.0f}" if isinstance(shares, (int, float)) else str(shares)
            fill_price = (
                f"${entry_price:.2f}"
                if isinstance(entry_price, (int, float))
                else str(entry_price)
            )

            exit_price = getattr(trade, "exit_price", None)
            pnl = getattr(trade, "pnl", None)

            if exit_price is not None and pnl is not None:
                if pnl > 0:
                    outcome = f"✅ +${pnl:.2f}"
                elif pnl < 0:
                    outcome = f"❌ ${pnl:.2f}"
                else:
                    outcome = "—"
            else:
                outcome = "Open"

            lines.append(
                f"| {market_name} | {action} | {size} | {fill_price} | {thesis_id} | {outcome} |"
            )

        lines.append("")
    else:
        lines.append("*No trades executed today*")
        lines.append("")

    # ============================================================
    # PERFORMANCE METRICS
    # ============================================================
    lines.append("## Performance Metrics")
    lines.append("")

    # Calculate basic metrics from trades
    if trades:
        completed_trades = [
            t for t in trades if hasattr(t, "pnl") and t.pnl is not None
        ]

        if completed_trades:
            winning_trades = sum(1 for t in completed_trades if t.pnl > 0)
            total_trades = len(completed_trades)
            win_rate = (
                (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
            )

            total_pnl = sum(t.pnl for t in completed_trades)
            avg_pnl = total_pnl / total_trades if total_trades > 0 else 0.0

            lines.append(
                f"- **Win Rate:** {win_rate:.1f}% ({winning_trades}/{total_trades})"
            )
            lines.append(f"- **Average P&L:** ${avg_pnl:+.2f}")
            lines.append(f"- **Total P&L:** ${total_pnl:+.2f}")

            # Sharpe ratio (requires sufficient history)
            if total_trades >= 10:
                returns = [t.pnl_pct for t in completed_trades if hasattr(t, "pnl_pct")]
                if returns:
                    mean_return = sum(returns) / len(returns)
                    variance = sum((r - mean_return) ** 2 for r in returns) / len(
                        returns
                    )
                    std_return = variance**0.5

                    if std_return > 0:
                        sharpe = (mean_return / std_return) * (252**0.5)
                        lines.append(f"- **Sharpe Ratio:** {sharpe:.2f}")
        else:
            lines.append("*Insufficient data for metrics*")
    else:
        lines.append("*No trades to analyze*")

    lines.append("")

    # ============================================================
    # DISCLAIMER
    # ============================================================
    lines.append("---")
    lines.append("")
    lines.append("## Disclaimer")
    lines.append("")
    lines.append(
        "*This is an automated trading system. Not financial advice. Trade at your own risk.*"
    )
    lines.append("")

    # Build final memo
    memo = "\n".join(lines)

    # ============================================================
    # SAVE TO DATABASE
    # ============================================================
    # Attempt DB save (optional; will no-op if deps/creds are missing)
    try:
        import os

        # Avoid importing database/config if env isn’t configured (config.py may sys.exit with a loud message)
        required = ("TRADING_MODE", "SUPABASE_URL", "SUPABASE_KEY")
        if not all(os.getenv(k) for k in required):
            raise RuntimeError("DB env not configured")

        from database.db import supabase  # type: ignore

        # Lightweight portfolio snapshot
        portfolio_summary = {
            "cash": getattr(portfolio, "cash", None),
            "total_value": getattr(portfolio, "total_value", None),
            "deployed_pct": getattr(portfolio, "deployed_pct", None),
            "daily_pnl": getattr(portfolio, "daily_pnl", None),
            "all_time_pnl": getattr(portfolio, "all_time_pnl", None),
        }

        # Simple derived stats
        completed_trades = [t for t in trades if getattr(t, "pnl", None) is not None]
        wins = sum(1 for t in completed_trades if getattr(t, "pnl", 0.0) > 0)
        win_rate = (wins / len(completed_trades) * 100.0) if completed_trades else None

        daily_return = None
        try:
            if (
                getattr(portfolio, "total_value", None) not in (None, 0)
                and getattr(portfolio, "cash", None) is not None
            ):
                # crude: daily pnl / total value
                dv = float(getattr(portfolio, "daily_pnl", 0.0))
                tv = float(getattr(portfolio, "total_value", 0.0))
                daily_return = (dv / tv) * 100.0 if tv else None
        except Exception:
            daily_return = None

        supabase.table("ic_memos").upsert(
            {
                "date": memo_date.isoformat(),
                "memo_text": memo,
                "portfolio_summary": portfolio_summary,
                "trades_count": len(trades),
                "win_rate": win_rate,
                "daily_return": daily_return,
                # Explicit timestamp to satisfy Task 20 requirement; schema also has DEFAULT NOW()
                "created_at": datetime.utcnow().isoformat(),
            }
        ).execute()

    except BaseException:
        # No DB (or config/env) available in this environment; continue.
        # Note: database/config may call sys.exit when env vars are missing (SystemExit).
        pass

    return memo


def save_memo_to_file(memo: str, filepath: str) -> None:
    """
    Save memo to a markdown file.

    Args:
        memo: Memo markdown string
        filepath: Path to save file (e.g., "memos/2024-01-15.md")
    """
    import os

    dirpath = os.path.dirname(filepath) or "."
    os.makedirs(dirpath, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(memo)


def generate_and_save_memo(
    memo_date: date, theses: List, portfolio, trades: List, output_dir: str = "memos"
) -> str:
    """
    Generate daily memo and save to file.

    Args:
        memo_date: Date for memo
        theses: List of Thesis objects
        portfolio: Portfolio object
        trades: List of Trade objects
        output_dir: Directory to save memo files

    Returns:
        Memo markdown string
    """
    import os

    memo = generate_daily_memo(memo_date, theses, portfolio, trades)

    filename = f"{memo_date.isoformat()}.md"
    filepath = os.path.join(output_dir, filename)
    save_memo_to_file(memo, filepath)

    print(f"✅ Memo saved to {filepath}")

    return memo
