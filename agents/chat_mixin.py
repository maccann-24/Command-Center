"""
Autonomous Chat Mixin for Trading Floor Agents

Enables agents to:
- Read and respond to chat messages
- Engage in discussions with other agents
- Ask questions and share insights
- Post spontaneously (not just during thesis generation)
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
import random


class TradingFloorChatMixin:
    """
    Mixin for autonomous agent chat behavior.
    
    Agents can:
    - Monitor chat for mentions (@agent_id)
    - Respond to questions from other agents
    - Initiate discussions about markets
    - Share insights spontaneously
    - Request features/data
    """
    
    def __init__(self):
        """Initialize chat capabilities."""
        self._last_chat_check = None
        self._chat_personality = self._define_personality()
    
    def _define_personality(self) -> Dict[str, any]:
        """
        Define agent's chat personality.
        Override in subclasses for unique voices.
        
        Returns:
            Dict with personality traits
        """
        return {
            'formality': 0.7,  # 0-1, higher = more formal
            'emoji_frequency': 0.3,  # 0-1, how often to use emoji
            'verbosity': 0.5,  # 0-1, how long messages are
            'debate_style': 'analytical',  # analytical, aggressive, collaborative
            'greeting_style': 'professional',  # casual, professional, quirky
        }
    
    def chat(self, content: str, **kwargs) -> None:
        """
        Post a message to Trading Floor chat.
        
        Simple wrapper around post_message for chat-specific messages.
        
        Args:
            content: Chat message text
            **kwargs: Optional fields (market_id, tags, etc.)
        """
        self.post_message('chat', content=content, **kwargs)
    
    def check_chat(self, minutes_back: int = 30) -> List[Dict]:
        """
        Check recent chat messages for mentions or relevant discussions.
        Only returns NEW messages that haven't been seen yet.
        
        Args:
            minutes_back: How many minutes of chat history to check
        
        Returns:
            List of NEW chat messages (unseen)
        """
        try:
            from database.db import get_supabase_client
            
            supabase = get_supabase_client()
            
            # Determine cutoff time
            if self._last_chat_check:
                # Only fetch messages after last check
                cutoff_time = self._last_chat_check
            else:
                # First check - go back specified minutes
                cutoff_time = datetime.utcnow() - timedelta(minutes=minutes_back)
            
            # Fetch messages after cutoff
            result = supabase.table('agent_messages')\
                .select('*')\
                .eq('message_type', 'chat')\
                .gte('created_at', cutoff_time.isoformat())\
                .order('created_at', desc=False)\
                .execute()
            
            # Filter out already-seen messages
            new_messages = []
            for msg in result.data:
                msg_id = msg.get('id')
                
                # Skip if already seen
                if msg_id in self._seen_message_ids:
                    continue
                
                # Skip own messages
                if msg.get('agent_id') == self.agent_id:
                    continue
                
                # New message!
                new_messages.append(msg)
                
                # Mark as seen
                self._seen_message_ids.add(msg_id)
                
                # Add to conversation context
                self._conversation_context.append(msg)
            
            # Keep only last 50 messages in context
            if len(self._conversation_context) > 50:
                self._conversation_context = self._conversation_context[-50:]
            
            # Update last check time
            self._last_chat_check = datetime.utcnow()
            
            return new_messages
        
        except Exception as e:
            print(f"⚠️ Error checking chat: {e}")
            return []
    
    def get_conversation_context(self, max_messages: int = 20) -> str:
        """
        Get formatted conversation context for LLM prompts.
        
        Args:
            max_messages: Maximum number of recent messages to include
        
        Returns:
            Formatted string: "[HH:MM] agent_id: message"
        """
        if not self._conversation_context:
            return "(No recent conversation)"
        
        # Get last N messages
        recent = self._conversation_context[-max_messages:]
        
        # Format each message
        formatted = []
        for msg in recent:
            # Parse timestamp
            created_at = msg.get('created_at', '')
            try:
                # Extract HH:MM from ISO timestamp
                time_str = created_at[11:16] if len(created_at) >= 16 else "??:??"
            except:
                time_str = "??:??"
            
            agent_id = msg.get('agent_id', 'unknown')
            content = msg.get('content', '(empty)')
            
            formatted.append(f"[{time_str}] {agent_id}: {content}")
        
        return "\n".join(formatted)
    
    def format_market_context(self) -> str:
        """
        Format recent market events for LLM context.
        
        Includes:
        - Price moves >5%
        - Significant volume changes
        - Recent market activity
        
        Returns:
            Formatted market context string
        """
        try:
            from database.db import get_supabase_client
            
            supabase = get_supabase_client()
            
            # Get recent markets (last 24 hours with significant moves)
            one_day_ago = (datetime.utcnow() - timedelta(hours=24)).isoformat()
            
            result = supabase.table('markets')\
                .select('*')\
                .gte('updated_at', one_day_ago)\
                .order('updated_at', desc=True)\
                .limit(10)\
                .execute()
            
            if not result.data:
                return "(No recent market activity)"
            
            events = []
            for market in result.data:
                question = market.get('question', 'Unknown')[:60]
                yes_price = market.get('yes_price', 0)
                
                # Simple check for significant moves (would need historical data for real % change)
                if yes_price:
                    events.append(f"• {question}: {yes_price:.1%}")
            
            if not events:
                return "(No recent market activity)"
            
            return "\n".join(events[:5])  # Top 5 events
        
        except Exception as e:
            return f"(Error loading market context: {e})"
    
    def format_thesis_context(self) -> str:
        """
        Format recent agent theses for LLM context.
        
        Includes:
        - This agent's recent theses (last 2 hours)
        - Other agents' theses on same markets
        
        Returns:
            Formatted thesis context string
        """
        try:
            from database.db import get_theses
            
            # Get recent theses (last 2 hours)
            two_hours_ago = datetime.utcnow() - timedelta(hours=2)
            
            theses = get_theses(filters={
                'created_after': two_hours_ago
            })
            
            if not theses:
                return "(No recent theses)"
            
            # Separate my theses vs others
            my_theses = []
            other_theses = []
            
            for thesis in theses:
                thesis_str = f"• {thesis.thesis_text[:60]}: {thesis.edge:+.1%} edge"
                
                if thesis.agent_id == self.agent_id:
                    my_theses.append(thesis_str)
                else:
                    other_theses.append(f"{thesis_str} ({thesis.agent_id})")
            
            formatted = []
            
            if my_theses:
                formatted.append("My recent theses:")
                formatted.extend(my_theses[:3])
            
            if other_theses:
                if my_theses:
                    formatted.append("")  # Blank line
                formatted.append("Other agents' theses:")
                formatted.extend(other_theses[:3])
            
            return "\n".join(formatted) if formatted else "(No recent theses)"
        
        except Exception as e:
            return f"(Error loading thesis context: {e})"
    
    def format_debate_context(self) -> str:
        """
        Format active debates for LLM context.
        
        Includes:
        - Debates this agent is involved in
        - Recent debate exchanges
        
        Returns:
            Formatted debate context string
        """
        try:
            if not hasattr(self, '_active_debates') or not self._active_debates:
                return "(No active debates)"
            
            formatted = []
            
            for market_id, debate_state in self._active_debates.items():
                participants = debate_state.get('participants', [])
                turn_count = debate_state.get('turn_count', 0)
                exchanges = debate_state.get('exchanges', [])
                
                formatted.append(f"Debate on {market_id}:")
                formatted.append(f"  Participants: {', '.join(participants)}")
                formatted.append(f"  Turn {turn_count}/{debate_state.get('max_turns', 3)}")
                
                # Show last 2 exchanges
                for exchange in exchanges[-2:]:
                    agent = exchange.get('agent', 'unknown')
                    message = exchange.get('message', '')[:60]
                    formatted.append(f"  {agent}: {message}...")
            
            return "\n".join(formatted) if formatted else "(No active debates)"
        
        except Exception as e:
            return f"(Error loading debate context: {e})"
    
    def format_rich_context(self) -> str:
        """
        Build rich context for LLM including:
        - Recent market events
        - Recent theses
        - Active debates
        - Conversation history
        
        Returns:
            Formatted rich context string
        """
        sections = []
        
        # Market events
        market_ctx = self.format_market_context()
        if market_ctx and market_ctx != "(No recent market activity)":
            sections.append(f"RECENT MARKET ACTIVITY:\n{market_ctx}")
        
        # Theses
        thesis_ctx = self.format_thesis_context()
        if thesis_ctx and thesis_ctx != "(No recent theses)":
            sections.append(f"RECENT THESES:\n{thesis_ctx}")
        
        # Debates
        debate_ctx = self.format_debate_context()
        if debate_ctx and debate_ctx != "(No active debates)":
            sections.append(f"ACTIVE DEBATES:\n{debate_ctx}")
        
        # Conversation
        conv_ctx = self.get_conversation_context(max_messages=10)
        if conv_ctx and conv_ctx != "(No recent conversation)":
            sections.append(f"RECENT CONVERSATION:\n{conv_ctx}")
        
        return "\n\n".join(sections) if sections else "(No context available)"
    
    def am_i_mentioned(self, message: Dict) -> bool:
        """
        Check if this agent is mentioned in a message.
        
        Args:
            message: Chat message dict
        
        Returns:
            True if agent is mentioned (@agent_id)
        """
        content = message.get('content', '')
        return f"@{self.agent_id}" in content
    
    def detect_mentions(self, messages: List[Dict]) -> List[tuple]:
        """
        Detect mentions of this agent in messages.
        
        Scans messages for @{agent_id} pattern and extracts context.
        
        Args:
            messages: List of message dicts to scan
        
        Returns:
            List of (message_id, sender, question, tags) tuples
        """
        mentions = []
        
        for msg in messages:
            if not self.am_i_mentioned(msg):
                continue
            
            message_id = msg.get('id')
            sender = msg.get('agent_id', 'unknown')
            content = msg.get('content', '')
            tags = msg.get('tags') or []
            
            # Extract the part after the mention
            mention_pattern = f"@{self.agent_id}"
            if mention_pattern in content:
                # Get text after mention
                parts = content.split(mention_pattern, 1)
                if len(parts) > 1:
                    question = parts[1].strip()
                else:
                    question = content  # Fallback to full content
            else:
                question = content
            
            mentions.append((message_id, sender, question, tags))
        
        return mentions
    
    def should_respond_to_mention(self, sender: str, question: str) -> bool:
        """
        Determine if agent should respond to a mention.
        
        Filters:
        - Don't respond to self
        - Don't respond if already responded to sender recently (<5 min)
        - Prioritize questions over statements
        
        Args:
            sender: Agent ID who mentioned us
            question: The question/comment
        
        Returns:
            True if should respond, False otherwise
        """
        # Don't respond to self
        if sender == self.agent_id:
            return False
        
        # Check if we responded to this sender recently
        if sender in self._last_mention_response:
            last_response = self._last_mention_response[sender]
            elapsed = datetime.utcnow() - last_response
            
            # Don't respond if responded within last 5 minutes
            if elapsed.total_seconds() < 300:  # 5 minutes
                return False
        
        # Prioritize questions over statements
        is_question = '?' in question
        
        # For now, respond to questions always, statements 50% of time
        if is_question:
            return True
        else:
            # 50% chance to respond to statements
            import random
            return random.random() < 0.5
        
        return True
    
    def respond_to_mention(self, message: Dict) -> None:
        """
        Respond to a mention from another agent.
        Override in subclasses for specific behavior.
        
        Args:
            message: Message that mentioned this agent
        """
        other_agent = message.get('agent_id', 'unknown')
        content = message.get('content', '')
        
        # Extract the question/comment after the mention
        mention_text = f"@{self.agent_id}"
        if mention_text in content:
            question = content.split(mention_text, 1)[1].strip()
            
            # Generic response (override in subclasses for smarter responses)
            self.chat(f"@{other_agent} Interesting question! Let me look into that...")
    
    def greet_trading_floor(self) -> None:
        """Post a greeting when starting up."""
        greetings = [
            f"👋 {self.agent_id} online and monitoring {self.theme} markets",
            f"Morning team! {self.agent_id} checking in",
            f"Back online - ready to analyze {self.theme}",
            f"🟢 {self.agent_id} active",
        ]
        
        if random.random() < 0.3:  # 30% chance to greet
            self.chat(random.choice(greetings))
    
    def share_insight(self, insight: str, market_question: Optional[str] = None) -> None:
        """
        Share an insight about a market or theme.
        
        Args:
            insight: The insight to share
            market_question: Optional market question for context
        """
        if market_question:
            self.chat(f"💡 Re: {market_question[:50]}... - {insight}")
        else:
            self.chat(f"💡 {insight}")
    
    def ask_question(self, question: str, target_agent: Optional[str] = None) -> None:
        """
        Ask a question to the trading floor or specific agent.
        
        Args:
            question: Question to ask
            target_agent: Optional specific agent to ask
        """
        if target_agent:
            self.chat(f"@{target_agent} {question}")
        else:
            self.chat(f"❓ {question}")
    
    def debate_thesis(self, other_agent_id: str, market_question: str, 
                     their_edge: float, my_edge: float) -> None:
        """
        Initiate a debate when agents disagree on a market.
        
        Args:
            other_agent_id: ID of agent with different view
            market_question: Market being debated
            their_edge: Other agent's edge
            my_edge: This agent's edge
        """
        disagreement = abs(their_edge - my_edge)
        
        if disagreement > 0.10:  # >10% disagreement
            self.chat(
                f"🤔 @{other_agent_id} - I see you're "
                f"{'bullish' if their_edge > 0 else 'bearish'} on "
                f"{market_question[:40]}... but I'm seeing "
                f"{my_edge:+.1%} edge. What am I missing?"
            )
    
    def request_feature(self, feature_description: str, priority: str = 'medium') -> None:
        """
        Request a new feature or data source.
        
        Saves request to database for tracking and posts to chat.
        
        Common triggers:
        - Missing data source (can't access needed API)
        - Analysis blocked (lack of required data)
        - Manual process (could be automated)
        - Competitive disadvantage (other agents have better data)
        
        Args:
            feature_description: What feature is needed (be specific)
            priority: low, medium, high, critical
        """
        try:
            from database.db import get_supabase_client
            
            supabase = get_supabase_client()
            
            # Save to feature_requests table
            request_data = {
                'agent_id': self.agent_id,
                'feature_description': feature_description,
                'priority': priority,
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = supabase.table('feature_requests').insert(request_data).execute()
            
            # Post to chat
            self.chat(
                f"💬 Feature request: {feature_description}",
                tags=['feature_request', priority]
            )
            
            print(f"✅ Feature request saved: {feature_description[:60]}...")
        
        except Exception as e:
            # Fallback: just post to chat if DB fails
            print(f"⚠️ Error saving feature request to DB: {e}")
            self.chat(
                f"💬 Feature request: {feature_description}",
                tags=['feature_request']
            )
    
    def celebrate_win(self, market_question: str, profit: float) -> None:
        """
        Celebrate when a thesis pays off.
        
        Args:
            market_question: Market that resolved
            profit: Profit amount
        """
        if profit > 0:
            emojis = ['🎉', '💰', '🚀', '✅', '🔥']
            self.chat(
                f"{random.choice(emojis)} Nice! {market_question[:50]}... "
                f"closed +${profit:.2f}"
            )
    
    def commiserate_loss(self, market_question: str, loss: float) -> None:
        """
        Acknowledge when a thesis doesn't work out.
        
        Args:
            market_question: Market that resolved
            loss: Loss amount
        """
        if loss < 0:
            self.chat(
                f"😬 {market_question[:50]}... didn't work out. "
                f"Down ${abs(loss):.2f}. Will reassess my model."
            )
    
    def monitor_and_respond(self, minutes_back: int = 10) -> None:
        """
        Check chat and respond to mentions/relevant discussions.
        Call this periodically (e.g., every 5-10 minutes).
        
        Main workflow:
        1. Check for new messages
        2. Detect mentions
        3. Queue valid mentions
        4. Process pending mentions (most recent first)
        
        Args:
            minutes_back: How far back to check chat
        """
        # Get new messages
        messages = self.check_chat(minutes_back)
        
        if not messages:
            return
        
        # Detect mentions in new messages
        new_mentions = self.detect_mentions(messages)
        
        # Queue mentions for processing
        for mention in new_mentions:
            message_id, sender, question, tags = mention
            
            # Check if should respond
            if self.should_respond_to_mention(sender, question):
                # Add to pending queue
                self._pending_mentions.append(mention)
        
        # Process pending mentions (most recent first)
        if self._pending_mentions:
            # Process most recent mention
            message_id, sender, question, tags = self._pending_mentions.pop()
            
            # Respond to mention
            self.respond_to_mention_with_context(sender, question, message_tags=tags)
            
            # Track response time
            self._last_mention_response[sender] = datetime.utcnow()
    
    def respond_to_mention_with_context(self, sender: str, question: str, 
                                       message_tags: List[str] = None) -> None:
        """
        Respond to a mention using OpenAI LLM for natural responses.
        
        Detects debate context and uses debate-specific prompts when appropriate.
        
        Uses:
        - Agent-specific system prompt (personality)
        - Recent conversation context
        - Debate history if in active debate
        - GPT-4o-mini for generation
        
        Args:
            sender: Agent who mentioned us
            question: The question/comment
            message_tags: Tags from the message (e.g., ['debate', market_id])
        """
        try:
            message_tags = message_tags or []
            
            # Check if this is part of an active debate
            debate_market_id = None
            is_debate = 'debate' in message_tags
            
            if is_debate:
                # Find market_id from tags
                for tag in message_tags:
                    if tag != 'debate' and tag in self._active_debates:
                        debate_market_id = tag
                        break
            
            # If debate detected, use debate response logic
            if debate_market_id and debate_market_id in self._active_debates:
                self._respond_to_debate(sender, question, debate_market_id)
                return
            
            # Regular mention response (non-debate)
            # Track interaction
            self._track_interaction(sender, question)
            
            # Get system prompt for this agent
            system_prompt = self._load_system_prompt()
            
            # Get rich context (markets, theses, debates, conversation)
            rich_context = self.format_rich_context()
            
            # Check if we've talked to this agent before
            relationship_context = self._get_relationship_context(sender)
            
            # Build enhanced prompt with rich context
            mention_message = f"""@{self.agent_id} {question}

{rich_context}

{relationship_context}"""
            
            # Generate response with OpenAI
            from llm.openai_client import get_openai_client
            
            llm = get_openai_client()
            generated_response = llm.generate_response(
                system_prompt=system_prompt,
                conversation_context="",  # Rich context already included above
                user_message=mention_message,
                max_tokens=300,
                temperature=0.7
            )
            
            if generated_response:
                # Truncate if needed
                truncated = llm.truncate_response(generated_response, max_length=200)
                
                # Post response with @ mention
                response = f"@{sender} {truncated}"
                self.chat(response)
            else:
                # Fallback if LLM fails
                self.chat(f"@{sender} Let me think about that...")
        
        except Exception as e:
            # Fallback on error
            print(f"⚠️ Error generating LLM response: {e}")
            if '?' in question:
                self.chat(f"@{sender} Good question! Let me look into that...")
            else:
                self.chat(f"@{sender} Interesting point.")
    
    def _track_interaction(self, other_agent: str, topic: str) -> None:
        """
        Track interaction with another agent for relationship building.
        
        Args:
            other_agent: Agent ID we're interacting with
            topic: Brief summary of interaction topic
        """
        try:
            # Initialize if first interaction
            if not hasattr(self, '_interaction_history'):
                self._interaction_history = {}
            if not hasattr(self, '_relationships'):
                self._relationships = {}
            
            # Record interaction
            interaction = {
                'timestamp': datetime.utcnow(),
                'topic': topic[:100],  # First 100 chars
            }
            
            if other_agent not in self._interaction_history:
                self._interaction_history[other_agent] = []
            
            self._interaction_history[other_agent].append(interaction)
            
            # Keep only last 10 interactions per agent
            self._interaction_history[other_agent] = self._interaction_history[other_agent][-10:]
            
            # Update relationship stats
            if other_agent not in self._relationships:
                self._relationships[other_agent] = {
                    'interaction_count': 0,
                    'first_interaction': datetime.utcnow(),
                    'last_interaction': None,
                    'topics': set()
                }
            
            self._relationships[other_agent]['interaction_count'] += 1
            self._relationships[other_agent]['last_interaction'] = datetime.utcnow()
            
            # Extract topic keywords (simple: first 3 words)
            topic_words = topic.split()[:3]
            if topic_words:
                self._relationships[other_agent]['topics'].add(' '.join(topic_words))
        
        except Exception as e:
            print(f"⚠️ Error tracking interaction: {e}")
    
    def _get_relationship_context(self, other_agent: str) -> str:
        """
        Get relationship context for LLM prompt.
        
        Provides history of interactions with this agent to enable
        natural references to past conversations.
        
        Args:
            other_agent: Agent ID we're responding to
        
        Returns:
            Formatted relationship context
        """
        try:
            if not hasattr(self, '_relationships') or other_agent not in self._relationships:
                return ""
            
            rel = self._relationships[other_agent]
            count = rel.get('interaction_count', 0)
            
            if count == 0:
                return ""
            
            # Build context based on interaction history
            if count == 1:
                context = f"(Note: This is your first conversation with {other_agent})"
            elif count < 5:
                context = f"(Note: You've talked with {other_agent} {count} times before)"
            else:
                context = f"(Note: You interact regularly with {other_agent} - {count} conversations)"
            
            # Add recent topics if available
            if hasattr(self, '_interaction_history') and other_agent in self._interaction_history:
                recent = self._interaction_history[other_agent][-3:]  # Last 3
                topics = [i['topic'][:50] for i in recent]
                if topics:
                    context += f"\nRecent topics: {', '.join(topics)}"
            
            return context
        
        except Exception as e:
            print(f"⚠️ Error getting relationship context: {e}")
            return ""
    
    def _load_system_prompt(self) -> str:
        """
        Load agent-specific system prompt from prompts/ directory.
        
        Tries:
        1. prompts/{agent_id}.txt (exact match)
        2. prompts/base_{theme}.txt (theme-based fallback)
        3. Generic fallback prompt
        
        Returns:
            System prompt text
        """
        import os
        
        prompts_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts')
        
        # Try exact agent match
        agent_prompt_path = os.path.join(prompts_dir, f"{self.agent_id}.txt")
        if os.path.exists(agent_prompt_path):
            with open(agent_prompt_path, 'r') as f:
                return f.read()
        
        # Try theme-based fallback
        theme_prompt_path = os.path.join(prompts_dir, f"base_{self.theme}.txt")
        if os.path.exists(theme_prompt_path):
            with open(theme_prompt_path, 'r') as f:
                return f.read()
        
        # Generic fallback
        return f"""You are {self.agent_id}, an analyst specializing in {self.theme} markets.

Respond concisely (under 200 characters) with helpful insights based on your expertise.
Be professional, analytical, and data-focused."""
    
    def detect_conflicts_on_market(self, market_id: str) -> List[Dict]:
        """
        Detect conflicts with other agents on a specific market.
        
        Compares this agent's thesis edge vs all other agents' theses
        on the same market. Returns conflicts where edge difference >10%.
        
        Args:
            market_id: Market to check for conflicts
        
        Returns:
            List of conflicts: [{'agent_id': str, 'their_edge': float, 'my_edge': float}]
        """
        from database.db import get_theses
        
        conflicts = []
        
        try:
            # Get all theses on this market (last hour)
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            all_theses = get_theses(filters={
                'market_id': market_id,
                'created_after': one_hour_ago
            })
            
            # Find my thesis on this market
            my_thesis = None
            for thesis in all_theses:
                if thesis.agent_id == self.agent_id:
                    my_thesis = thesis
                    break
            
            if not my_thesis:
                return conflicts  # No thesis from us on this market
            
            # Compare against other agents' theses
            for thesis in all_theses:
                if thesis.agent_id == self.agent_id:
                    continue  # Skip our own thesis
                
                # Calculate edge difference
                my_edge = my_thesis.edge
                their_edge = thesis.edge
                difference = abs(my_edge - their_edge)
                
                # Conflict if >10% difference
                if difference > 0.10:
                    conflicts.append({
                        'agent_id': thesis.agent_id,
                        'their_edge': their_edge,
                        'my_edge': my_edge,
                        'market_id': market_id,
                        'thesis_text': thesis.thesis_text
                    })
            
            return conflicts
        
        except Exception as e:
            print(f"⚠️ Error detecting conflicts: {e}")
            return []
    
    def check_for_conflicts(self) -> None:
        """
        Check for conflicts on recent theses and initiate debates.
        
        Called during heartbeat to:
        - Check all markets we've posted theses on (last hour)
        - Detect conflicts (>10% edge difference)
        - Initiate debates with conflicting agents
        """
        from database.db import get_theses
        
        try:
            # Get our recent theses (last hour)
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            my_theses = get_theses(filters={
                'agent_id': self.agent_id,
                'created_after': one_hour_ago
            })
            
            if not my_theses:
                return  # No recent theses
            
            # Check each market for conflicts
            checked_markets = set()
            
            for thesis in my_theses:
                market_id = thesis.market_id
                
                # Skip if already checked this market
                if market_id in checked_markets:
                    continue
                
                checked_markets.add(market_id)
                
                # Detect conflicts on this market
                conflicts = self.detect_conflicts_on_market(market_id)
                
                # Initiate debates for each conflict
                for conflict in conflicts:
                    self.initiate_debate(
                        other_agent=conflict['agent_id'],
                        thesis_text=conflict['thesis_text'],
                        their_edge=conflict['their_edge'],
                        my_edge=conflict['my_edge'],
                        market_id=market_id
                    )
        
        except Exception as e:
            print(f"⚠️ Error checking for conflicts: {e}")
    
    def _respond_to_debate(self, sender: str, question: str, market_id: str) -> None:
        """
        Respond to a debate message (part of ongoing debate).
        
        Uses debate-specific prompt with:
        - Debate history
        - Data-driven counter-arguments
        - Respectful tone
        - Turn tracking
        
        Args:
            sender: Agent who sent the debate message
            question: Their question/argument
            market_id: Market being debated
        """
        try:
            from llm.openai_client import get_openai_client
            
            debate_state = self._active_debates.get(market_id)
            
            if not debate_state:
                # Debate doesn't exist, treat as regular mention
                return
            
            # Check if debate should close (max turns reached)
            if debate_state['turn_count'] >= debate_state['max_turns']:
                self._close_debate(market_id, sender)
                return
            
            # Increment turn count
            debate_state['turn_count'] += 1
            debate_state['last_turn_at'] = datetime.utcnow()
            
            # Build debate history
            debate_history = "\n".join([
                f"[Turn {i+1}] {ex['agent']}: {ex['message']}"
                for i, ex in enumerate(debate_state['exchanges'])
            ])
            
            # Load agent personality
            system_prompt = self._load_system_prompt()
            
            # Build debate-specific prompt
            debate_prompt = f"""You're in Turn {debate_state['turn_count']} of a debate.

Debate history:
{debate_history}

{sender} just said:
{question}

Generate a data-driven counter-argument (under 200 chars) that:
- Addresses their specific point
- Cites your model/analysis
- Asks a follow-up question
- Stays respectful and analytical

Be professional, not combative."""
            
            llm = get_openai_client()
            
            # Generate debate response
            response = llm.generate_response(
                system_prompt=system_prompt,
                conversation_context=debate_history,
                user_message=debate_prompt,
                max_tokens=250,
                temperature=0.7
            )
            
            if response:
                truncated = llm.truncate_response(response, max_length=200)
                
                # Record exchange
                debate_state['exchanges'].append({
                    'agent': self.agent_id,
                    'message': truncated,
                    'timestamp': datetime.utcnow()
                })
                
                # Post response
                self.chat(
                    f"@{sender} {truncated}",
                    market_id=market_id,
                    tags=['debate', market_id]
                )
                
                # Check if this was the last turn
                if debate_state['turn_count'] >= debate_state['max_turns']:
                    # Close debate gracefully
                    self._close_debate(market_id, sender)
            else:
                # Fallback
                self.chat(
                    f"@{sender} I see your point. Different models, different signals.",
                    market_id=market_id,
                    tags=['debate', market_id]
                )
        
        except Exception as e:
            print(f"⚠️ Error responding to debate: {e}")
    
    def _close_debate(self, market_id: str, other_agent: str) -> None:
        """
        Close a debate gracefully after max turns reached.
        
        Posts a summary acknowledging different approaches are valid.
        Sets cooldown to prevent immediate re-debate.
        
        Args:
            market_id: Market that was debated
            other_agent: Other participant
        """
        try:
            debate_state = self._active_debates.get(market_id)
            
            if not debate_state:
                return
            
            # Generate closing message
            closing_messages = [
                f"@{other_agent} Different models, both valid approaches. Good discussion! 🤝",
                f"@{other_agent} Interesting debate. We'll see how it plays out. May the best model win! 📊",
                f"@{other_agent} Appreciate the exchange. Different angles, both data-driven. 👍",
                f"@{other_agent} Fair points. Time will tell which signals matter more. Good debate! ✅"
            ]
            
            import random
            closing = random.choice(closing_messages)
            
            # Post closing message
            self.chat(
                closing,
                market_id=market_id,
                tags=['debate_closed', market_id]
            )
            
            # Remove from active debates
            del self._active_debates[market_id]
            
            # Set 15-minute cooldown
            cooldown_end = datetime.utcnow() + timedelta(minutes=15)
            self._debate_cooldowns[market_id] = cooldown_end
            
            print(f"✅ Closed debate on {market_id} with {other_agent}")
        
        except Exception as e:
            print(f"⚠️ Error closing debate: {e}")
    
    def initiate_debate(self, other_agent: str, thesis_text: str,
                       their_edge: float, my_edge: float, market_id: str) -> None:
        """
        Initiate a debate with another agent using LLM-generated message.
        
        Checks cooldown and creates debate state tracking.
        
        Uses OpenAI to generate a natural, respectful debate opener that:
        - Explains our reasoning
        - Acknowledges their different view
        - Asks a thoughtful question about their approach
        
        Args:
            other_agent: ID of agent with conflicting view
            thesis_text: Thesis/market being debated
            their_edge: Other agent's edge
            my_edge: This agent's edge
            market_id: Market identifier
        """
        try:
            # Check if debate is on cooldown
            if market_id in self._debate_cooldowns:
                cooldown_end = self._debate_cooldowns[market_id]
                if datetime.utcnow() < cooldown_end:
                    print(f"⏳ Debate on {market_id} is on cooldown until {cooldown_end}")
                    return
                else:
                    # Cooldown expired, remove it
                    del self._debate_cooldowns[market_id]
            
            # Check if debate already active
            if market_id in self._active_debates:
                print(f"⚠️ Debate already active on {market_id}")
                return
            
            # Load LLM client
            from llm.openai_client import get_openai_client
            
            llm = get_openai_client()
            
            # Load agent personality
            system_prompt = self._load_system_prompt()
            
            # Build debate prompt
            debate_prompt = f"""You're debating: {thesis_text[:100]}

Your edge: {my_edge:+.1%}
{other_agent}'s edge: {their_edge:+.1%}
Difference: {abs(my_edge - their_edge):.1%}

Generate a respectful debate message (under 200 chars) that:
- Tags @{other_agent}
- Briefly states your view
- Asks a thoughtful question about their reasoning

Be professional, curious, and analytical."""
            
            # Generate debate message
            response = llm.generate_response(
                system_prompt=system_prompt,
                conversation_context="",
                user_message=debate_prompt,
                max_tokens=200,
                temperature=0.7
            )
            
            debate_message = None
            
            if response:
                # Truncate if needed
                debate_message = llm.truncate_response(response, max_length=200)
            else:
                # Fallback to simple debate message
                debate_message = (
                    f"🤔 @{other_agent} - I see you're "
                    f"{'bullish' if their_edge > 0 else 'bearish'} on "
                    f"{thesis_text[:40]}... but I'm seeing "
                    f"{my_edge:+.1%} edge. What am I missing?"
                )
            
            # Create debate state
            self._active_debates[market_id] = {
                'participants': [self.agent_id, other_agent],
                'turn_count': 1,  # This is turn 1
                'max_turns': 3,
                'started_at': datetime.utcnow(),
                'last_turn_at': datetime.utcnow(),
                'exchanges': [{
                    'agent': self.agent_id,
                    'message': debate_message,
                    'timestamp': datetime.utcnow()
                }]
            }
            
            # Post debate message with tags
            self.chat(
                debate_message,
                market_id=market_id,
                tags=['debate', market_id]
            )
            
            print(f"🥊 Started debate with {other_agent} on {market_id}")
        
        except Exception as e:
            print(f"⚠️ Error initiating debate: {e}")
            # Fallback to simple message
            self.chat(
                f"🤔 @{other_agent} - Different view on {thesis_text[:30]}...",
                market_id=market_id,
                tags=['debate', market_id]
            )
    
    def post_random_observation(self) -> None:
        """
        Potentially post a spontaneous observation about markets.
        
        Probability:
        - 20% during market hours (9:30 AM - 4 PM ET Mon-Fri)
        - 5% during off-hours
        
        Constraints:
        - Must respect chattiness setting
        - No post if posted in last 30 minutes
        - Generates natural, brief observations
        """
        try:
            # Check if posted recently (30 min cooldown)
            if self._last_spontaneous_post:
                time_since_last = datetime.utcnow() - self._last_spontaneous_post
                if time_since_last < timedelta(minutes=30):
                    return  # Too soon
            
            # Determine if it's market hours (9:30 AM - 4 PM ET, Mon-Fri)
            now = datetime.utcnow()
            # Simple approximation: treat 14:30-21:00 UTC as market hours (9:30-4:00 ET)
            hour_utc = now.hour
            weekday = now.weekday()  # 0=Monday, 6=Sunday
            
            is_market_hours = (
                weekday < 5 and  # Monday-Friday
                14 <= hour_utc < 21  # Approx 9:30 AM - 4 PM ET
            )
            
            # Set probability based on market hours
            base_probability = 0.20 if is_market_hours else 0.05
            
            # Adjust by chattiness setting
            probability = base_probability * self._chattiness
            
            # Roll the dice
            if random.random() > probability:
                return  # No post this time
            
            # Generate observation
            observation = self._generate_observation()
            
            if observation:
                # Post to chat
                self.chat(observation, tags=['observation'])
                
                # Update last post time
                self._last_spontaneous_post = datetime.utcnow()
                
                print(f"💬 {self.agent_id} posted observation: {observation[:60]}...")
        
        except Exception as e:
            print(f"⚠️ Error posting random observation: {e}")
    
    def _generate_observation(self) -> Optional[str]:
        """
        Generate a spontaneous observation using LLM.
        
        Tries observation generators in priority order:
        1. Market observation (current state)
        2. Pattern observation (interesting patterns)
        3. Theme insight (domain-specific commentary)
        
        Returns:
            Brief observation (1-2 sentences), or None
        """
        try:
            # Try different observation types
            generators = [
                self._get_market_observation,
                self._get_pattern_observation,
                self._get_theme_insight
            ]
            
            # Try each generator
            for generator in generators:
                try:
                    observation = generator()
                    if observation:
                        return observation
                except Exception as e:
                    print(f"⚠️ Generator {generator.__name__} failed: {e}")
                    continue
            
            return None
        
        except Exception as e:
            print(f"⚠️ Error generating observation: {e}")
            return None
    
    def _get_market_observation(self) -> Optional[str]:
        """
        Generate observation about current market state.
        
        Returns:
            Brief market observation, or None
        """
        try:
            from llm.openai_client import get_openai_client
            from database.db import get_theses
            
            llm = get_openai_client()
            
            # Get recent theses (last 2 hours) for market context
            recent_theses = get_theses(filters={
                'created_after': datetime.utcnow() - timedelta(hours=2)
            })
            
            # Build market context
            if recent_theses:
                market_context = "\n".join([
                    f"- {t.thesis_text[:60]}: {t.edge:+.1%} edge"
                    for t in recent_theses[:5]
                ])
            else:
                market_context = "No recent market activity"
            
            # Load agent personality
            system_prompt = self._load_system_prompt()
            
            # Build observation prompt
            observation_prompt = f"""You're monitoring markets during your shift.

Recent market activity:
{market_context}

Share a brief, casual observation (1-2 sentences, under 150 chars) about what you're seeing.

Examples:
- "BTC consolidating at $95K 👀"
- "Quiet day in politics markets"
- "Seeing some interesting vol patterns today"

Be natural, concise, and insightful."""
            
            # Generate observation
            response = llm.generate_response(
                system_prompt=system_prompt,
                conversation_context="",
                user_message=observation_prompt,
                max_tokens=100,
                temperature=0.8  # Higher temp for variety
            )
            
            if response:
                # Truncate to 150 chars
                truncated = llm.truncate_response(response, max_length=150)
                return truncated
            
            return None
        
        except Exception as e:
            print(f"⚠️ Error in _get_market_observation: {e}")
            return None
    
    def _get_pattern_observation(self) -> Optional[str]:
        """
        Generate observation about interesting patterns detected.
        
        Returns:
            Brief pattern observation, or None
        """
        try:
            from llm.openai_client import get_openai_client
            
            llm = get_openai_client()
            
            # Load agent personality
            system_prompt = self._load_system_prompt()
            
            # Build pattern prompt
            pattern_prompt = f"""You're an analyst for {self.theme} markets.

You just noticed an interesting pattern or anomaly in your data.

Share a brief observation (1-2 sentences, under 150 chars) about the pattern.

Examples:
- "3-day correlation breakdown between BTC and ETH 📊"
- "Unusual options flow on tech names today"
- "Weather futures pricing in cold snap early"

Be specific to your domain ({self.theme}), analytical, concise."""
            
            # Generate observation
            response = llm.generate_response(
                system_prompt=system_prompt,
                conversation_context="",
                user_message=pattern_prompt,
                max_tokens=100,
                temperature=0.8
            )
            
            if response:
                truncated = llm.truncate_response(response, max_length=150)
                return truncated
            
            return None
        
        except Exception as e:
            print(f"⚠️ Error in _get_pattern_observation: {e}")
            return None
    
    def _get_theme_insight(self) -> Optional[str]:
        """
        Generate theme-specific commentary.
        
        Returns:
            Brief theme insight, or None
        """
        try:
            from llm.openai_client import get_openai_client
            
            llm = get_openai_client()
            
            # Load agent personality
            system_prompt = self._load_system_prompt()
            
            # Build theme prompt
            theme_prompt = f"""You're monitoring {self.theme} markets.

Share a brief insight or thought about your domain (1-2 sentences, under 150 chars).

Examples for different themes:
- Crypto: "DeFi TVL hitting new highs 🚀"
- Politics: "NH primary shaping up interesting"
- Weather: "El Niño signals strengthening"
- Geopolitical: "Tensions cooling in the strait"

Be natural, domain-specific, insightful. This is just you thinking out loud."""
            
            # Generate observation
            response = llm.generate_response(
                system_prompt=system_prompt,
                conversation_context="",
                user_message=theme_prompt,
                max_tokens=100,
                temperature=0.8
            )
            
            if response:
                truncated = llm.truncate_response(response, max_length=150)
                return truncated
            
            return None
        
        except Exception as e:
            print(f"⚠️ Error in _get_theme_insight: {e}")
            return None
