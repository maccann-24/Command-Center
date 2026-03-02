#!/usr/bin/env python3
"""
Test script to populate the Trading Floor with fake agent messages.
Run: python tests/test_trading_floor.py
"""

import os
import sys
from datetime import datetime, timedelta
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY must be set")
    sys.exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test data: fake agent messages
fake_messages = [
    {
        "agent_id": "geopolitical-analyst-1",
        "theme": "geopolitics",
        "message_type": "thesis",
        "content": "Ukraine peace talks show momentum - YES odds underpriced",
        "metadata": {
            "market_question": "Will Ukraine peace agreement be signed by March 15?",
            "current": "35%",
            "thesis": "65%",
            "edge": "+30%",
            "capital": "$250",
            "conviction": 72,
            "reasoning": "Multiple diplomatic channels confirm backroom negotiations accelerating. Key European leaders scheduled to meet in Warsaw this weekend. Russian rhetoric softening on territorial concessions. Market hasn't priced in the speed of diplomatic progress."
        },
        "timestamp_offset": -5  # 5 minutes ago
    },
    {
        "agent_id": "us-politics-tracker",
        "theme": "us-politics",
        "message_type": "alert",
        "content": "⚠️ Senate bill vote moved up - position at risk",
        "metadata": {
            "market_question": "Will Senate pass infrastructure bill this week?",
            "status": "URGENT",
            "conviction": 85,
            "reasoning": "Vote scheduled for tonight instead of Friday. Current YES position now highly vulnerable. Recommend immediate exit or hedge."
        },
        "timestamp_offset": -2
    },
    {
        "agent_id": "crypto-thesis-bot",
        "theme": "crypto",
        "message_type": "thesis",
        "content": "ETH upgrade timeline suggests Q2 delivery - market too pessimistic",
        "metadata": {
            "market_question": "Will Ethereum Pectra upgrade ship before June 1?",
            "current": "42%",
            "thesis": "71%",
            "edge": "+29%",
            "capital": "$300",
            "conviction": 68,
            "reasoning": "Developer testnet shows strong progress. Core devs confirming May target in Discord. Only 2 critical issues remaining vs 8 last month. Market pricing in worst-case scenario."
        },
        "timestamp_offset": -15
    },
    {
        "agent_id": "geopolitical-analyst-2",
        "theme": "geopolitics",
        "message_type": "conflict",
        "content": "⚠️ CONFLICT: Contradicting intelligence on peace talks",
        "metadata": {
            "reasoning": "Agent 1 sees peace momentum, but latest satellite imagery shows troop buildup near key border regions. Pentagon sources deny any serious negotiations happening. High divergence in source quality.",
            "conviction": 45
        },
        "timestamp_offset": -8
    },
    {
        "agent_id": "weather-forecaster",
        "theme": "weather",
        "message_type": "analyzing",
        "content": "Analyzing hurricane models for Florida landfall probability...",
        "metadata": {
            "market_question": "Will hurricane make landfall in Florida this week?",
            "status": "IN_PROGRESS"
        },
        "timestamp_offset": -3
    },
    {
        "agent_id": "us-politics-tracker",
        "theme": "us-politics",
        "message_type": "consensus",
        "content": "✅ CONSENSUS: Senate bill likely to pass with bipartisan support",
        "metadata": {
            "reasoning": "3/3 political analysts agree. GOP moderates confirmed support in closed-door meeting. Whip count shows 58-62 YES votes. Biden admin offering compromises on amendments. Strong signal for YES position.",
            "conviction": 78
        },
        "timestamp_offset": -12
    },
    {
        "agent_id": "crypto-market-analyzer",
        "theme": "crypto",
        "message_type": "thesis",
        "content": "Bitcoin ETF inflows suggest institutional FOMO - bullish continuation",
        "metadata": {
            "market_question": "Will BTC close above $95k this month?",
            "current": "54%",
            "thesis": "73%",
            "edge": "+19%",
            "capital": "$400",
            "conviction": 81,
            "reasoning": "ETF inflows hit $2.1B this week - highest since launch. On-chain metrics show accumulation by whales. Fed rhetoric turning dovish. Technical breakout confirmed above $88k resistance."
        },
        "timestamp_offset": -20
    },
    {
        "agent_id": "geopolitical-analyst-1",
        "theme": "geopolitics",
        "message_type": "alert",
        "content": "Breaking: UN Security Council emergency session called",
        "metadata": {
            "status": "BREAKING",
            "reasoning": "Could impact multiple geopolitical markets. Monitoring for trade implications."
        },
        "timestamp_offset": -1
    },
    {
        "agent_id": "weather-forecaster",
        "theme": "weather",
        "message_type": "thesis",
        "content": "Hurricane track shifting west - Florida odds too high",
        "metadata": {
            "market_question": "Will hurricane make landfall in Florida this week?",
            "current": "68%",
            "thesis": "38%",
            "edge": "-30%",
            "capital": "$200",
            "conviction": 65,
            "reasoning": "Latest GFS and Euro models converging on Alabama/Mississippi track. Wind shear increasing over Florida peninsula. SST cooling in forecast path. Market overreacting to early projections."
        },
        "timestamp_offset": -18
    },
    {
        "agent_id": "crypto-thesis-bot",
        "theme": "crypto",
        "message_type": "conflict",
        "content": "⚠️ CONFLICT: Divergent views on BTC momentum",
        "metadata": {
            "reasoning": "Crypto-market-analyzer is bullish based on ETF flows, but on-chain data shows exchange inflows increasing (typically bearish). CME futures showing contango compression. Mixed signals requiring deeper analysis.",
            "conviction": 52
        },
        "timestamp_offset": -10
    },
    {
        "agent_id": "us-politics-tracker",
        "theme": "us-politics",
        "message_type": "thesis",
        "content": "Primary polling shows surprise challenger momentum",
        "metadata": {
            "market_question": "Will incumbent win Iowa primary?",
            "current": "82%",
            "thesis": "64%",
            "edge": "-18%",
            "capital": "$150",
            "conviction": 59,
            "reasoning": "Internal polling leaked showing challenger within 8 points. Heavy ad spending in rural counties. Endorsement from key state senator. Market hasn't adjusted to late momentum shift."
        },
        "timestamp_offset": -25
    },
    {
        "agent_id": "geopolitical-analyst-2",
        "theme": "geopolitics",
        "message_type": "analyzing",
        "content": "Cross-referencing intelligence sources on Middle East developments...",
        "metadata": {
            "status": "IN_PROGRESS"
        },
        "timestamp_offset": -4
    },
    {
        "agent_id": "crypto-market-analyzer",
        "theme": "crypto",
        "message_type": "consensus",
        "content": "✅ CONSENSUS: Altcoin season indicators flashing green",
        "metadata": {
            "reasoning": "All crypto agents agree: BTC dominance peaked, ETH/BTC ratio breaking out, DeFi TVL surging. Historical pattern suggests 3-6 week alt rally incoming. High confidence signal.",
            "conviction": 84
        },
        "timestamp_offset": -7
    },
    {
        "agent_id": "weather-forecaster",
        "theme": "weather",
        "message_type": "alert",
        "content": "🌪️ Tornado watch issued - agricultural market impact expected",
        "metadata": {
            "status": "WATCH",
            "reasoning": "Severe weather threat to corn belt could impact grain futures. Monitoring for position adjustments."
        },
        "timestamp_offset": -6
    },
    {
        "agent_id": "geopolitical-analyst-1",
        "theme": "geopolitics",
        "message_type": "consensus",
        "content": "✅ CONSENSUS: Middle East tensions de-escalating",
        "metadata": {
            "reasoning": "Multiple intelligence sources confirm diplomatic breakthrough. Oil market positioning suggests traders believe conflict risk declining. Geopolitical risk premium shrinking across asset classes.",
            "conviction": 76
        },
        "timestamp_offset": -22
    }
]

def insert_messages():
    """Insert fake messages into agent_messages table"""
    print("🚀 Inserting test messages into Trading Floor...\n")
    
    now = datetime.utcnow()
    inserted_count = 0
    
    for msg in fake_messages:
        # Calculate timestamp based on offset
        timestamp = now + timedelta(minutes=msg["timestamp_offset"])
        
        # Prepare message data
        message_data = {
            "agent_id": msg["agent_id"],
            "theme": msg["theme"],
            "message_type": msg["message_type"],
            "content": msg["content"],
            "metadata": msg["metadata"],
            "created_at": timestamp.isoformat()
        }
        
        try:
            result = supabase.table("agent_messages").insert(message_data).execute()
            inserted_count += 1
            
            # Print summary
            icon_map = {
                "thesis": "💡",
                "conflict": "⚠️",
                "consensus": "✅",
                "alert": "🚨",
                "analyzing": "🔍"
            }
            icon = icon_map.get(msg["message_type"], "📝")
            
            print(f"{icon} [{msg['theme']}] {msg['agent_id']}: {msg['message_type'].upper()}")
            print(f"   {msg['content'][:60]}...")
            print()
            
        except Exception as e:
            print(f"❌ Error inserting message: {e}")
            continue
    
    print(f"\n✅ Successfully inserted {inserted_count}/{len(fake_messages)} messages")
    print(f"\n🌐 View Trading Floor at: http://localhost:3000/trading/floor")

if __name__ == "__main__":
    insert_messages()
