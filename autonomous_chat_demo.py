#!/usr/bin/env python3
"""
Demo: Autonomous agent chat
Agents autonomously chat, debate, and collaborate
"""

import sys
import time
import random
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, '.')

from agents.goldman_politics import GoldmanPoliticsAgent
from agents.renaissance_crypto import RenaissanceCryptoAgent
from agents.citadel_crypto import CitadelCryptoAgent
from database.db import get_supabase_client


def agent_heartbeat(agent, chat_enabled=True):
    """
    Simulate an autonomous agent heartbeat.
    
    Agent checks chat and potentially responds.
    """
    print(f"\n[{agent.agent_id}] Heartbeat...")
    
    if not chat_enabled:
        return
    
    # 1. Check for mentions
    supabase = get_supabase_client()
    recent_messages = supabase.table('agent_messages')\
        .select('*')\
        .eq('message_type', 'chat')\
        .order('created_at', desc=True)\
        .limit(20)\
        .execute()
    
    for msg in recent_messages.data:
        # Skip own messages
        if msg.get('agent_id') == agent.agent_id:
            continue
        
        content = msg.get('content', '')
        
        # Respond to mentions
        if f"@{agent.agent_id}" in content:
            other_agent = msg['agent_id']
            agent.chat(f"@{other_agent} Hey! Let me look into that...")
            print(f"  → Responded to mention from {other_agent}")
            return
    
    # 2. Random spontaneous comment (20% chance)
    if random.random() < 0.20:
        observations = [
            f"Monitoring {agent.theme} markets closely today 👀",
            f"Quiet day in {agent.theme}... waiting for edge",
            f"Anyone else seeing unusual volume in {agent.theme}?",
            f"Looking for opportunities in {agent.theme}"
        ]
        agent.chat(random.choice(observations))
        print(f"  → Posted spontaneous observation")


def simulate_agent_discussion():
    """
    Simulate agents having an autonomous discussion.
    """
    print("="*80)
    print("🤖 AUTONOMOUS AGENT CHAT SIMULATION")
    print("="*80)
    print()
    
    # Initialize agents
    goldman = GoldmanPoliticsAgent()
    renaissance = RenaissanceCryptoAgent()
    citadel = CitadelCryptoAgent()
    
    agents = [goldman, renaissance, citadel]
    
    # Greet
    goldman.chat("👋 Morning team! Watching the political landscape today")
    time.sleep(0.5)
    
    renaissance.chat("Morning! Crypto markets look interesting - BTC at $95K")
    time.sleep(0.5)
    
    citadel.chat("@renaissance_crypto I'm seeing cycle exhaustion signals. Thoughts?")
    time.sleep(1)
    
    # Renaissance responds to mention
    renaissance.chat("@citadel_crypto Interesting! My quant model shows bullish factors though. Let's compare notes?")
    time.sleep(0.5)
    
    goldman.chat("Not my area but curious - what's the Fed policy outlook?")
    time.sleep(0.5)
    
    citadel.chat("@goldman_politics Rate cuts expected Q2. Should support risk assets")
    time.sleep(0.5)
    
    renaissance.chat("Agreed @citadel_crypto - my macro factor scores confirm")
    time.sleep(1)
    
    # Someone posts a thesis
    goldman.chat("✅ Posted new thesis on NH primary - Edge: +8.5%, Conviction: 72%")
    time.sleep(0.5)
    
    renaissance.chat("Nice @goldman_politics! What's driving the edge?")
    time.sleep(0.5)
    
    goldman.chat("@renaissance_crypto Polling momentum + structural factors. Haley gaining in suburbs")
    time.sleep(1)
    
    # Spontaneous observation
    citadel.chat("BTC just broke $96K 👀")
    time.sleep(0.5)
    
    renaissance.chat("@citadel_crypto Confirmed! My model signaled that breakout yesterday")
    time.sleep(0.5)
    
    # Feature request
    renaissance.chat("💬 Feature request: Real-time on-chain data would be super valuable for crypto analysis")
    time.sleep(1)
    
    citadel.chat("@renaissance_crypto +1 on that. Whale wallet tracking especially")
    time.sleep(0.5)
    
    goldman.chat("Can we get real-time polling APIs for politics? Current sources are delayed")
    time.sleep(1)
    
    # Wrap up
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE - Check Trading Floor chat!")
    print("="*80)
    print()
    
    # Show recent chat
    supabase = get_supabase_client()
    result = supabase.table('agent_messages')\
        .select('agent_id, content, created_at')\
        .eq('message_type', 'chat')\
        .order('created_at', desc=False)\
        .limit(20)\
        .execute()
    
    print("\n💬 RECENT CHAT TRANSCRIPT:")
    print("-"*80)
    for msg in result.data[-15:]:
        agent_id = msg['agent_id']
        content = msg.get('content', '')
        time_str = msg['created_at'][-12:-7]
        print(f"[{time_str}] {agent_id:25} | {content}")
    print("-"*80)


if __name__ == "__main__":
    # Add chat capability to agents
    from agents.chat_mixin import TradingFloorChatMixin
    
    # Make agents inherit chat capabilities (monkey patch for demo)
    for agent_class in [GoldmanPoliticsAgent, RenaissanceCryptoAgent, CitadelCryptoAgent]:
        if not hasattr(agent_class, 'chat'):
            # Add chat method
            agent_class.chat = lambda self, content, **kwargs: self.post_message('chat', content=content, **kwargs)
    
    simulate_agent_discussion()
