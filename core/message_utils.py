"""
BASED MONEY - Trading Floor Message Utilities
Utilities for detecting conflicts, consensus, and managing agent messages
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from database.db import get_supabase_client

logger = logging.getLogger(__name__)


def detect_conflicts(market_id: str, min_difference: float = 0.20) -> Optional[Dict]:
    """
    Detect conflicts between agents on the same market.
    
    Queries recent theses (last 1 hour) for a given market and identifies
    when multiple agents have significantly different opinions (thesis_odds).
    Posts a 'conflict' message to alert the Trading Floor.
    
    Args:
        market_id: Market to check for conflicts
        min_difference: Minimum difference in thesis_odds to be considered
                       a conflict (default: 0.20 = 20%)
    
    Returns:
        Dict with conflict details if detected, None otherwise
    
    Example:
        conflict = detect_conflicts('poly_market_123')
        if conflict:
            print(f"Conflict detected: {conflict['agent1']} vs {conflict['agent2']}")
    """
    try:
        # Calculate time cutoff (1 hour ago)
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        # Query recent thesis messages for this market
        response = get_supabase_client().table('agent_messages').select('*').eq(
            'market_id', market_id
        ).eq(
            'message_type', 'thesis'
        ).gte(
            'timestamp', cutoff_time.isoformat()
        ).order('timestamp', desc=True).execute()
        
        theses = response.data if response.data else []
        
        # Need at least 2 theses to have a conflict
        if len(theses) < 2:
            return None
        
        # Check each pair of theses for conflicts
        conflicts_detected = []
        
        for i in range(len(theses)):
            for j in range(i + 1, len(theses)):
                thesis1 = theses[i]
                thesis2 = theses[j]
                
                # Skip if same agent (shouldn't happen but be safe)
                if thesis1['agent_id'] == thesis2['agent_id']:
                    continue
                
                # Skip if either thesis is missing thesis_odds
                if thesis1.get('thesis_odds') is None or thesis2.get('thesis_odds') is None:
                    continue
                
                # Calculate difference
                odds_diff = abs(thesis1['thesis_odds'] - thesis2['thesis_odds'])
                
                # Check if difference exceeds threshold
                if odds_diff >= min_difference:
                    conflicts_detected.append({
                        'agent1': thesis1['agent_id'],
                        'agent2': thesis2['agent_id'],
                        'theme1': thesis1['theme'],
                        'theme2': thesis2['theme'],
                        'thesis1_odds': thesis1['thesis_odds'],
                        'thesis2_odds': thesis2['thesis_odds'],
                        'difference': odds_diff,
                        'reasoning1': thesis1.get('reasoning', 'No reasoning provided'),
                        'reasoning2': thesis2.get('reasoning', 'No reasoning provided'),
                        'market_question': thesis1.get('market_question'),
                        'current_odds': thesis1.get('current_odds'),
                        'timestamp1': thesis1['timestamp'],
                        'timestamp2': thesis2['timestamp']
                    })
        
        # If conflicts detected, post the most significant one
        if conflicts_detected:
            # Sort by difference (largest first)
            conflicts_detected.sort(key=lambda x: x['difference'], reverse=True)
            
            # Get the biggest conflict
            conflict = conflicts_detected[0]
            
            # Check if we already posted this conflict (avoid duplicates)
            # Query for existing conflict messages in last hour
            existing_conflict = get_supabase_client().table('agent_messages').select('id').eq(
                'market_id', market_id
            ).eq(
                'message_type', 'conflict'
            ).gte(
                'timestamp', cutoff_time.isoformat()
            ).execute()
            
            if existing_conflict.data and len(existing_conflict.data) > 0:
                logger.debug(f"Conflict already reported for market {market_id}")
                return conflict  # Return but don't post duplicate
            
            # Post conflict message
            _post_conflict_message(market_id, conflict)
            
            return conflict
        
        return None
    
    except Exception as e:
        logger.error(f"Error detecting conflicts for market {market_id}: {e}", exc_info=True)
        return None


def _post_conflict_message(market_id: str, conflict: Dict) -> None:
    """
    Post a conflict message to the Trading Floor.
    
    Args:
        market_id: Market identifier
        conflict: Dict with conflict details
    """
    try:
        # Build reasoning text
        reasoning = f"""
⚠️ CONFLICT DETECTED

{conflict['agent1']} vs {conflict['agent2']}

{conflict['agent1'].upper()}:
Thesis: {conflict['thesis1_odds']:.0%} YES
{conflict['reasoning1'][:200]}{'...' if len(conflict['reasoning1']) > 200 else ''}

{conflict['agent2'].upper()}:
Thesis: {conflict['thesis2_odds']:.0%} YES
{conflict['reasoning2'][:200]}{'...' if len(conflict['reasoning2']) > 200 else ''}

DIFFERENCE: {conflict['difference']:.0%}
This is a significant disagreement that requires review.
""".strip()
        
        # Determine direction
        if conflict['thesis1_odds'] > conflict['thesis2_odds']:
            tags = ['conflict', 'requires_review', f"{conflict['agent1']}_bullish", f"{conflict['agent2']}_bearish"]
        else:
            tags = ['conflict', 'requires_review', f"{conflict['agent1']}_bearish", f"{conflict['agent2']}_bullish"]
        
        # Post conflict message
        conflict_data = {
            'agent_id': 'system',
            'theme': conflict['theme1'],  # Use first agent's theme
            'message_type': 'conflict',
            'market_question': conflict['market_question'],
            'market_id': market_id,
            'current_odds': conflict['current_odds'],
            'reasoning': reasoning,
            'signals': {
                'agent1': conflict['agent1'],
                'agent2': conflict['agent2'],
                'thesis1_odds': conflict['thesis1_odds'],
                'thesis2_odds': conflict['thesis2_odds'],
                'difference': conflict['difference'],
                'timestamp1': conflict['timestamp1'],
                'timestamp2': conflict['timestamp2']
            },
            'status': 'detected',
            'tags': tags,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        get_supabase_client().table('agent_messages').insert(conflict_data).execute()
        
        logger.info(
            f"Posted conflict message for {market_id}: "
            f"{conflict['agent1']} ({conflict['thesis1_odds']:.0%}) vs "
            f"{conflict['agent2']} ({conflict['thesis2_odds']:.0%})"
        )
    
    except Exception as e:
        logger.error(f"Error posting conflict message: {e}", exc_info=True)


def check_for_conflicts_after_thesis(market_id: str) -> None:
    """
    Check for conflicts after a new thesis is posted.
    
    This should be called by agents after they post a thesis message.
    It will automatically detect and post conflict messages if needed.
    
    Args:
        market_id: Market to check for conflicts
    
    Example:
        # In agent code, after posting thesis:
        self.post_message('thesis', ...)
        from core.message_utils import check_for_conflicts_after_thesis
        check_for_conflicts_after_thesis(market.id)
    """
    try:
        conflict = detect_conflicts(market_id)
        if conflict:
            logger.info(
                f"Conflict detected for {market_id}: "
                f"{conflict['agent1']} vs {conflict['agent2']}"
            )
    except Exception as e:
        logger.error(f"Error checking for conflicts: {e}", exc_info=True)


def get_recent_conflicts(hours: int = 24, limit: int = 10) -> List[Dict]:
    """
    Get recent conflict messages.
    
    Args:
        hours: Number of hours to look back (default: 24)
        limit: Maximum number of conflicts to return (default: 10)
    
    Returns:
        List of conflict message dicts
    """
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        response = get_supabase_client().table('agent_messages').select('*').eq(
            'message_type', 'conflict'
        ).gte(
            'timestamp', cutoff_time.isoformat()
        ).order('timestamp', desc=True).limit(limit).execute()
        
        return response.data if response.data else []
    
    except Exception as e:
        logger.error(f"Error getting recent conflicts: {e}", exc_info=True)
        return []


def get_market_conflicts(market_id: str) -> List[Dict]:
    """
    Get all conflict messages for a specific market.
    
    Args:
        market_id: Market identifier
    
    Returns:
        List of conflict message dicts
    """
    try:
        response = get_supabase_client().table('agent_messages').select('*').eq(
            'market_id', market_id
        ).eq(
            'message_type', 'conflict'
        ).order('timestamp', desc=True).execute()
        
        return response.data if response.data else []
    
    except Exception as e:
        logger.error(f"Error getting market conflicts: {e}", exc_info=True)
        return []


# ============================================================
# CONSENSUS DETECTION
# ============================================================

def detect_consensus(market_id: str, min_agents: int = 3, max_spread: float = 0.10) -> Optional[Dict]:
    """
    Detect consensus between multiple agents on the same market.
    
    Queries recent theses (last 1 hour) for a given market and identifies
    when 3+ agents have similar opinions (thesis_odds within 10% of each other).
    Posts a 'consensus' message to highlight high-conviction multi-agent plays.
    
    Args:
        market_id: Market to check for consensus
        min_agents: Minimum number of agents required for consensus (default: 3)
        max_spread: Maximum difference in thesis_odds to be considered
                   consensus (default: 0.10 = 10%)
    
    Returns:
        Dict with consensus details if detected, None otherwise
    
    Example:
        consensus = detect_consensus('poly_market_123')
        if consensus:
            print(f"Consensus: {len(consensus['agents'])} agents agree at {consensus['avg_odds']:.0%}")
    """
    try:
        # Calculate time cutoff (1 hour ago)
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        # Query recent thesis messages for this market
        response = get_supabase_client().table('agent_messages').select('*').eq(
            'market_id', market_id
        ).eq(
            'message_type', 'thesis'
        ).gte(
            'timestamp', cutoff_time.isoformat()
        ).order('timestamp', desc=True).execute()
        
        theses = response.data if response.data else []
        
        # Need at least min_agents theses to have consensus
        if len(theses) < min_agents:
            return None
        
        # Filter out theses without thesis_odds
        valid_theses = [t for t in theses if t.get('thesis_odds') is not None]
        
        if len(valid_theses) < min_agents:
            return None
        
        # Calculate average thesis_odds
        thesis_odds_list = [t['thesis_odds'] for t in valid_theses]
        avg_odds = sum(thesis_odds_list) / len(thesis_odds_list)
        
        # Check if all theses are within max_spread of average
        agreeing_theses = []
        for thesis in valid_theses:
            diff_from_avg = abs(thesis['thesis_odds'] - avg_odds)
            if diff_from_avg <= max_spread:
                agreeing_theses.append(thesis)
        
        # Check if we have enough agreeing agents
        if len(agreeing_theses) < min_agents:
            return None
        
        # Check for duplicate agents (each agent should only appear once)
        unique_agents = {}
        for thesis in agreeing_theses:
            agent_id = thesis['agent_id']
            if agent_id not in unique_agents:
                unique_agents[agent_id] = thesis
        
        if len(unique_agents) < min_agents:
            return None
        
        # Build consensus data
        agreeing_theses = list(unique_agents.values())
        
        # Calculate aggregates
        total_edge = sum(t.get('edge', 0) for t in agreeing_theses)
        total_capital = sum(t.get('capital_allocated', 0) for t in agreeing_theses)
        convictions = [t.get('conviction', 0) for t in agreeing_theses if t.get('conviction')]
        avg_conviction = sum(convictions) / len(convictions) if convictions else 0
        
        # Recalculate average with only agreeing theses
        avg_odds = sum(t['thesis_odds'] for t in agreeing_theses) / len(agreeing_theses)
        
        consensus = {
            'agents': [t['agent_id'] for t in agreeing_theses],
            'themes': list(set(t['theme'] for t in agreeing_theses)),
            'count': len(agreeing_theses),
            'avg_odds': avg_odds,
            'total_edge': total_edge,
            'total_capital': total_capital,
            'avg_conviction': avg_conviction,
            'is_high_conviction': avg_conviction > 0.70,
            'market_question': agreeing_theses[0].get('market_question'),
            'current_odds': agreeing_theses[0].get('current_odds'),
            'theses': agreeing_theses
        }
        
        # Check if we already posted this consensus (avoid duplicates)
        existing_consensus = get_supabase_client().table('agent_messages').select('id').eq(
            'market_id', market_id
        ).eq(
            'message_type', 'consensus'
        ).gte(
            'timestamp', cutoff_time.isoformat()
        ).execute()
        
        if existing_consensus.data and len(existing_consensus.data) > 0:
            logger.debug(f"Consensus already reported for market {market_id}")
            return consensus  # Return but don't post duplicate
        
        # Post consensus message
        _post_consensus_message(market_id, consensus)
        
        return consensus
    
    except Exception as e:
        logger.error(f"Error detecting consensus for market {market_id}: {e}", exc_info=True)
        return None


def _post_consensus_message(market_id: str, consensus: Dict) -> None:
    """
    Post a consensus message to the Trading Floor.
    
    Args:
        market_id: Market identifier
        consensus: Dict with consensus details
    """
    try:
        # Build reasoning text
        agent_list = "\n".join(f"  • {agent}" for agent in consensus['agents'])
        
        conviction_badge = "🔥 HIGH CONVICTION" if consensus['is_high_conviction'] else "CONSENSUS"
        
        reasoning = f"""
🎯 {conviction_badge} - {consensus['count']} AGENTS AGREE

AGENTS:
{agent_list}

CONSENSUS POSITION:
Average Thesis: {consensus['avg_odds']:.0%} {"YES" if consensus['avg_odds'] > 0.5 else "NO"}
Current Market: {consensus['current_odds']:.0%}
Combined Edge: {consensus['total_edge']:+.1%}
Average Conviction: {consensus['avg_conviction']:.0%}

CAPITAL ALLOCATION:
Combined: ${consensus['total_capital']:,.2f}

This is a multi-agent consensus play with strong agreement.
{f"⚠️ HIGH CONVICTION - Average conviction {consensus['avg_conviction']:.0%} exceeds 70%" if consensus['is_high_conviction'] else ""}
""".strip()
        
        # Build tags
        tags = ['consensus', 'multi_agent']
        if consensus['is_high_conviction']:
            tags.append('high_conviction')
        
        # Determine direction
        if consensus['avg_odds'] > consensus['current_odds']:
            tags.append('bullish')
        elif consensus['avg_odds'] < consensus['current_odds']:
            tags.append('bearish')
        
        # Add agent names as tags
        tags.extend(consensus['agents'][:3])  # First 3 agents
        
        # Post consensus message
        consensus_data = {
            'agent_id': 'system',
            'theme': consensus['themes'][0] if consensus['themes'] else 'multi_theme',
            'message_type': 'consensus',
            'market_question': consensus['market_question'],
            'market_id': market_id,
            'current_odds': consensus['current_odds'],
            'thesis_odds': consensus['avg_odds'],
            'edge': consensus['total_edge'],
            'conviction': consensus['avg_conviction'],
            'capital_allocated': consensus['total_capital'],
            'reasoning': reasoning,
            'signals': {
                'agents': consensus['agents'],
                'count': consensus['count'],
                'avg_odds': consensus['avg_odds'],
                'total_edge': consensus['total_edge'],
                'total_capital': consensus['total_capital'],
                'avg_conviction': consensus['avg_conviction'],
                'is_high_conviction': consensus['is_high_conviction'],
                'individual_theses': [
                    {
                        'agent': t['agent_id'],
                        'odds': t['thesis_odds'],
                        'conviction': t.get('conviction')
                    }
                    for t in consensus['theses']
                ]
            },
            'status': 'detected',
            'tags': tags,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        get_supabase_client().table('agent_messages').insert(consensus_data).execute()
        
        logger.info(
            f"Posted consensus message for {market_id}: "
            f"{consensus['count']} agents agree at {consensus['avg_odds']:.0%} "
            f"({'HIGH CONVICTION' if consensus['is_high_conviction'] else 'standard'})"
        )
    
    except Exception as e:
        logger.error(f"Error posting consensus message: {e}", exc_info=True)


def check_for_consensus_after_thesis(market_id: str) -> None:
    """
    Check for consensus after a new thesis is posted.
    
    This should be called by agents after they post a thesis message.
    It will automatically detect and post consensus messages if needed.
    
    Args:
        market_id: Market to check for consensus
    
    Example:
        # In agent code, after posting thesis:
        self.post_message('thesis', ...)
        from core.message_utils import check_for_consensus_after_thesis
        check_for_consensus_after_thesis(market.id)
    """
    try:
        consensus = detect_consensus(market_id)
        if consensus:
            logger.info(
                f"Consensus detected for {market_id}: "
                f"{consensus['count']} agents agree at {consensus['avg_odds']:.0%}"
            )
    except Exception as e:
        logger.error(f"Error checking for consensus: {e}", exc_info=True)


def check_all_after_thesis(market_id: str) -> None:
    """
    Run both conflict and consensus detection after posting thesis.
    
    Convenience function that runs both checks in sequence.
    
    Args:
        market_id: Market to check
    
    Example:
        # In agent code, after posting thesis:
        self.post_message('thesis', ...)
        from core.message_utils import check_all_after_thesis
        check_all_after_thesis(market.id)
    """
    check_for_conflicts_after_thesis(market_id)
    check_for_consensus_after_thesis(market_id)


def get_recent_consensus(hours: int = 24, limit: int = 10) -> List[Dict]:
    """
    Get recent consensus messages.
    
    Args:
        hours: Number of hours to look back (default: 24)
        limit: Maximum number of consensus messages to return (default: 10)
    
    Returns:
        List of consensus message dicts
    """
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        response = get_supabase_client().table('agent_messages').select('*').eq(
            'message_type', 'consensus'
        ).gte(
            'timestamp', cutoff_time.isoformat()
        ).order('timestamp', desc=True).limit(limit).execute()
        
        return response.data if response.data else []
    
    except Exception as e:
        logger.error(f"Error getting recent consensus: {e}", exc_info=True)
        return []


# ============================================================
# USAGE EXAMPLES
# ============================================================

def example_usage():
    """
    Example usage of conflict and consensus detection.
    """
    market_id = "poly_market_123"
    
    # Example 1: Check for both conflicts and consensus after posting thesis
    check_all_after_thesis(market_id)
    
    # Example 2: Get recent conflicts for dashboard
    recent_conflicts = get_recent_conflicts(hours=24, limit=10)
    for conflict in recent_conflicts:
        print(f"Conflict: {conflict['signals']['agent1']} vs {conflict['signals']['agent2']}")
    
    # Example 3: Get recent consensus for dashboard
    recent_consensus = get_recent_consensus(hours=24, limit=10)
    for consensus in recent_consensus:
        signals = consensus.get('signals', {})
        print(f"Consensus: {signals.get('count', 0)} agents agree at {signals.get('avg_odds', 0):.0%}")
    
    # Example 4: Get all conflicts for a specific market
    market_conflicts = get_market_conflicts(market_id)
    print(f"Found {len(market_conflicts)} conflicts for market {market_id}")


if __name__ == "__main__":
    # Run example usage
    print("=" * 60)
    print("MESSAGE UTILITIES - CONFLICTS & CONSENSUS")
    print("=" * 60)
    print()
    print("Conflict Detection:")
    print("  - detect_conflicts(market_id)")
    print("  - check_for_conflicts_after_thesis(market_id)")
    print("  - get_recent_conflicts(hours, limit)")
    print("  - get_market_conflicts(market_id)")
    print()
    print("Consensus Detection:")
    print("  - detect_consensus(market_id)")
    print("  - check_for_consensus_after_thesis(market_id)")
    print("  - get_recent_consensus(hours, limit)")
    print()
    print("Convenience:")
    print("  - check_all_after_thesis(market_id)  ← Use this after posting thesis")
    print()
    print("See docstrings for usage details.")
