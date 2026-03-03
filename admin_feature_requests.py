#!/usr/bin/env python3
"""
Feature Requests Admin Dashboard

Queries and displays feature requests from agents.

Usage:
    python3 admin_feature_requests.py           # Show top requests
    python3 admin_feature_requests.py --all     # Show all requests
    python3 admin_feature_requests.py --agent goldman_politics  # Show requests from specific agent
    python3 admin_feature_requests.py --pending # Show only pending requests
"""

import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, '.')

from database.db import get_supabase_client


def show_top_requests(limit=10):
    """Show top requested features grouped by description."""
    
    print("="*80)
    print("🔥 TOP FEATURE REQUESTS")
    print("="*80)
    print()
    
    supabase = get_supabase_client()
    
    # Query feature_requests_summary view
    result = supabase.table('feature_requests_summary')\
        .select('*')\
        .limit(limit)\
        .execute()
    
    if not result.data:
        print("  No feature requests found.")
        return
    
    for i, req in enumerate(result.data, 1):
        desc = req.get('feature_description', 'Unknown')
        count = req.get('request_count', 0)
        agents = req.get('requesting_agents', [])
        priority = req.get('max_priority', 'medium')
        first = req.get('first_requested', '')
        
        print(f"{i}. {desc}")
        print(f"   Requests: {count} | Priority: {priority.upper()} | Agents: {', '.join(agents)}")
        print(f"   First requested: {first}")
        print()


def show_all_requests(status_filter=None):
    """Show all feature requests."""
    
    print("="*80)
    print("📋 ALL FEATURE REQUESTS")
    print("="*80)
    print()
    
    supabase = get_supabase_client()
    
    # Build query
    query = supabase.table('feature_requests').select('*').order('created_at', desc=True)
    
    if status_filter:
        query = query.eq('status', status_filter)
    
    result = query.execute()
    
    if not result.data:
        print("  No feature requests found.")
        return
    
    for req in result.data:
        agent = req.get('agent_id', 'unknown')
        desc = req.get('feature_description', '')
        priority = req.get('priority', 'medium')
        status = req.get('status', 'pending')
        created = req.get('created_at', '')
        
        status_emoji = {
            'pending': '⏳',
            'in_progress': '🔨',
            'completed': '✅',
            'rejected': '❌'
        }.get(status, '❓')
        
        priority_emoji = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }.get(priority, '⚪')
        
        print(f"{status_emoji} [{agent}] {desc}")
        print(f"  Priority: {priority_emoji} {priority.upper()} | Status: {status} | {created}")
        print()


def show_agent_requests(agent_id):
    """Show requests from a specific agent."""
    
    print("="*80)
    print(f"📊 FEATURE REQUESTS FROM {agent_id}")
    print("="*80)
    print()
    
    supabase = get_supabase_client()
    
    result = supabase.table('feature_requests')\
        .select('*')\
        .eq('agent_id', agent_id)\
        .order('created_at', desc=True)\
        .execute()
    
    if not result.data:
        print(f"  No requests from {agent_id}.")
        return
    
    for req in result.data:
        desc = req.get('feature_description', '')
        priority = req.get('priority', 'medium')
        status = req.get('status', 'pending')
        created = req.get('created_at', '')
        
        print(f"• {desc}")
        print(f"  Priority: {priority.upper()} | Status: {status} | {created}")
        print()


def show_theme_summary():
    """Show feature requests grouped by theme."""
    
    print("="*80)
    print("🎯 FEATURE REQUESTS BY THEME")
    print("="*80)
    print()
    
    supabase = get_supabase_client()
    
    # Get all pending requests
    result = supabase.table('feature_requests')\
        .select('*')\
        .eq('status', 'pending')\
        .execute()
    
    if not result.data:
        print("  No pending requests.")
        return
    
    # Group by theme (extracted from agent_id)
    themes = {}
    
    for req in result.data:
        agent = req.get('agent_id', 'unknown')
        desc = req.get('feature_description', '')
        
        # Extract theme from agent_id (e.g., "goldman_politics" -> "politics")
        theme = 'other'
        if '_' in agent:
            theme = agent.split('_')[-1]
        
        if theme not in themes:
            themes[theme] = []
        
        themes[theme].append(desc)
    
    # Display by theme
    for theme, requests in sorted(themes.items()):
        print(f"📌 {theme.upper()}")
        for req in requests:
            print(f"  • {req}")
        print()


def show_stats():
    """Show overall statistics."""
    
    print("="*80)
    print("📈 FEATURE REQUEST STATISTICS")
    print("="*80)
    print()
    
    supabase = get_supabase_client()
    
    # Get all requests
    result = supabase.table('feature_requests').select('*').execute()
    
    if not result.data:
        print("  No data available.")
        return
    
    total = len(result.data)
    pending = len([r for r in result.data if r.get('status') == 'pending'])
    in_progress = len([r for r in result.data if r.get('status') == 'in_progress'])
    completed = len([r for r in result.data if r.get('status') == 'completed'])
    rejected = len([r for r in result.data if r.get('status') == 'rejected'])
    
    print(f"  Total requests: {total}")
    print(f"  ⏳ Pending: {pending}")
    print(f"  🔨 In progress: {in_progress}")
    print(f"  ✅ Completed: {completed}")
    print(f"  ❌ Rejected: {rejected}")
    print()
    
    # Count by priority
    high = len([r for r in result.data if r.get('priority') in ['high', 'critical'] and r.get('status') == 'pending'])
    medium = len([r for r in result.data if r.get('priority') == 'medium' and r.get('status') == 'pending'])
    low = len([r for r in result.data if r.get('priority') == 'low' and r.get('status') == 'pending'])
    
    print(f"  Pending by priority:")
    print(f"    🔴 High/Critical: {high}")
    print(f"    🟡 Medium: {medium}")
    print(f"    🟢 Low: {low}")
    print()
    
    # Count by agent
    agents = {}
    for req in result.data:
        if req.get('status') == 'pending':
            agent = req.get('agent_id')
            agents[agent] = agents.get(agent, 0) + 1
    
    if agents:
        print(f"  Top requesting agents:")
        for agent, count in sorted(agents.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {agent}: {count} requests")
    print()


def main():
    parser = argparse.ArgumentParser(description='Feature Requests Admin Dashboard')
    parser.add_argument('--all', action='store_true', help='Show all requests')
    parser.add_argument('--agent', type=str, help='Show requests from specific agent')
    parser.add_argument('--pending', action='store_true', help='Show only pending requests')
    parser.add_argument('--theme', action='store_true', help='Group by theme')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--limit', type=int, default=10, help='Limit for top requests')
    
    args = parser.parse_args()
    
    if args.stats:
        show_stats()
    elif args.theme:
        show_theme_summary()
    elif args.agent:
        show_agent_requests(args.agent)
    elif args.all:
        show_all_requests()
    elif args.pending:
        show_all_requests(status_filter='pending')
    else:
        # Default: show top requests
        show_top_requests(limit=args.limit)
        print()
        show_stats()


if __name__ == "__main__":
    main()
