"""Portfolio history snapshot persistence."""

from __future__ import annotations

from typing import Optional

from models.portfolio import Portfolio

from database.db import supabase, record_event


def save_portfolio_snapshot(portfolio: Portfolio) -> bool:
    """Persist a portfolio snapshot to `portfolio_history` for charting."""
    try:
        payload = {
            "cash": float(portfolio.cash),
            "total_value": float(portfolio.total_value),
            "deployed_pct": float(portfolio.deployed_pct),
            "daily_pnl": float(portfolio.daily_pnl),
            "all_time_pnl": float(portfolio.all_time_pnl),
        }
        supabase.table("portfolio_history").insert(payload).execute()

        record_event(
            event_type="portfolio_snapshot",
            details={"total_value": payload["total_value"], "deployed_pct": payload["deployed_pct"]},
            severity="info",
        )
        return True
    except Exception as e:
        print(f"❌ Error saving portfolio snapshot: {e}")
        record_event(
            event_type="database_error",
            details={"error": str(e), "function": "save_portfolio_snapshot"},
            severity="error",
        )
        return False
