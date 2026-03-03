"""
Trading Floor Message Posting
Posts agent messages to Command Center for real-time display
"""

import os
from typing import Dict, Optional, Any
from datetime import datetime

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = Any

# ============================================================
# SUPABASE CLIENT FOR TRADING FLOOR
# ============================================================

_trading_floor_client: Optional[Client] = None


def get_trading_floor_client() -> Client:
    """Get or create Supabase client for Trading Floor."""
    global _trading_floor_client

    if create_client is None:
        raise RuntimeError("Supabase dependency not installed")

    if _trading_floor_client is None:
        # Try NEXT_PUBLIC_ prefixed first (Next.js convention), fall back to non-prefixed
        url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
        # Prefer service role key for posting messages (server-side operation)
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_KEY (or NEXT_PUBLIC_ prefixed versions) must be set"
            )

        _trading_floor_client = create_client(url, key)

    return _trading_floor_client


# ============================================================
# MESSAGE POSTING
# ============================================================


def post_agent_message(
    agent_id: str,
    message_type: str,
    content: str,
    theme: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Post a message to the Trading Floor.

    Args:
        agent_id: Agent identifier (e.g., "geo-analyst-1")
        message_type: One of: thesis, conflict, consensus, alert, analyzing, chat
        content: Message content
        theme: Theme (e.g., "geopolitics", "crypto", "us-politics", "weather")
        metadata: Additional structured data (dict)

    Returns:
        True if successful, False otherwise

    Example metadata for thesis:
        {
            "market_question": "Will Russia invade Ukraine?",
            "current": "35%",
            "thesis": "65%",
            "edge": "+30%",
            "capital": "$250",
            "conviction": 72,
            "reasoning": "Multiple diplomatic channels..."
        }
    """
    try:
        client = get_trading_floor_client()

        message_data = {
            "agent_id": agent_id,
            "message_type": message_type,
            "content": content,
            "theme": theme,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }

        result = client.table("agent_messages").insert(message_data).execute()

        return True

    except Exception as e:
        print(f"⚠️ Failed to post Trading Floor message: {e}")
        return False


def post_analyzing_message(agent_id: str, theme: str, content: str = None) -> bool:
    """
    Post an "analyzing" message (agent starting work).

    Args:
        agent_id: Agent identifier
        theme: Theme being analyzed
        content: Optional custom message (default: "Analyzing...")

    Returns:
        True if successful
    """
    if content is None:
        content = f"Analyzing {theme} markets..."

    return post_agent_message(
        agent_id=agent_id,
        message_type="analyzing",
        content=content,
        theme=theme,
        metadata={"status": "IN_PROGRESS"},
    )


def post_thesis_message(
    agent_id: str,
    theme: str,
    thesis_text: str,
    market_question: str,
    current_odds: float,
    fair_value: float,
    edge: float,
    conviction: float,
    reasoning: str,
    capital_allocated: Optional[float] = None,
    signals: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Post a thesis message.

    Args:
        agent_id: Agent identifier
        theme: Theme (geopolitics, crypto, etc.)
        thesis_text: Short thesis summary
        market_question: Market question being analyzed
        current_odds: Current market odds (0-1)
        fair_value: Agent's fair value estimate (0-1)
        edge: Edge in percentage points (fair_value - current_odds)
        conviction: Conviction score (0-100)
        reasoning: Detailed reasoning
        capital_allocated: Capital allocated to position

    Returns:
        True if successful
    """
    metadata = {
        "market_question": market_question,
        "current": f"{current_odds * 100:.0f}%",
        "thesis": f"{fair_value * 100:.0f}%",
        "edge": f"{edge:+.0%}",
        "conviction": int(conviction * 100),
        "reasoning": reasoning,
    }

    if capital_allocated:
        metadata["capital"] = f"${capital_allocated:.0f}"

    if signals:
        metadata["signals"] = signals

    return post_agent_message(
        agent_id=agent_id,
        message_type="thesis",
        content=thesis_text,
        theme=theme,
        metadata=metadata,
    )


def post_alert_message(
    agent_id: str, theme: str, content: str, reasoning: Optional[str] = None
) -> bool:
    """
    Post an alert message (urgent notification).

    Args:
        agent_id: Agent identifier
        theme: Theme
        content: Alert content
        reasoning: Optional reasoning

    Returns:
        True if successful
    """
    metadata = {"status": "ALERT"}
    if reasoning:
        metadata["reasoning"] = reasoning

    return post_agent_message(
        agent_id=agent_id,
        message_type="alert",
        content=content,
        theme=theme,
        metadata=metadata,
    )


def post_conflict_message(
    agent_id: str, theme: str, content: str, reasoning: str, conviction: Optional[int] = None
) -> bool:
    """
    Post a conflict message (divergent views).

    Args:
        agent_id: Agent identifier
        theme: Theme
        content: Conflict description
        reasoning: Explanation of conflicting signals
        conviction: Confidence in the conflict (0-100)

    Returns:
        True if successful
    """
    metadata = {"reasoning": reasoning}
    if conviction:
        metadata["conviction"] = conviction

    return post_agent_message(
        agent_id=agent_id,
        message_type="conflict",
        content=content,
        theme=theme,
        metadata=metadata,
    )


def post_consensus_message(
    agent_id: str, theme: str, content: str, reasoning: str, conviction: Optional[int] = None
) -> bool:
    """
    Post a consensus message (agreement between agents/sources).

    Args:
        agent_id: Agent identifier
        theme: Theme
        content: Consensus description
        reasoning: Explanation of consensus
        conviction: Confidence in the consensus (0-100)

    Returns:
        True if successful
    """
    metadata = {"reasoning": reasoning}
    if conviction:
        metadata["conviction"] = conviction

    return post_agent_message(
        agent_id=agent_id,
        message_type="consensus",
        content=content,
        theme=theme,
        metadata=metadata,
    )
