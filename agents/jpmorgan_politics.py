"""
BASED MONEY - JPMorgan Politics Agent
Event catalyst analysis for US politics prediction markets
"""

from typing import List, Optional
from datetime import datetime
import sys
sys.path.insert(0, '..')

from agents.base import BaseAgent
from models import Thesis, Market
from database import get_markets, get_news_events


class JPMorganPoliticsAgent(BaseAgent):
    """
    JPMorgan-style event catalyst analyst for US politics markets.
    
    Applies pre/post-event analysis framework to identify how political
    events (debates, primaries, scandals) impact prediction market odds.
    
    System Prompt (Institutional Analysis Framework):
    ================================================
    
    You are a senior event catalyst analyst at JPMorgan analyzing US politics
    prediction markets by modeling pre/post-event probability shifts.
    
    For each political market, systematically assess event catalysts:
    
    1. Debate Analysis:
       - Pre-debate expectations: What is priced in? (polls, prediction markets)
       - Debate performance metrics: Wins/losses in post-debate polls
       - Historical debate effects: How much do debates typically move markets?
       - Post-debate polling bumps: Expected range based on performance
       - Moderator bias and format considerations
    
    2. Primary Results Analysis:
       - Pre-primary polling vs. actual results (beat or miss expectations?)
       - State-by-state delegate math (how many delegates at stake?)
       - Momentum shifts: Does winning/losing create cascading effects?
       - Historical primary patterns: Iowa vs. New Hampshire vs. Super Tuesday
       - Surprise results: How much do markets overreact to unexpected wins?
    
    3. Policy Announcement Impact:
       - Campaign platform changes or major policy rollouts
       - Market reaction to policy shifts (progressive vs. moderate positioning)
       - Voter bloc appeal: Does policy win over key demographics?
       - Opposition attack surface: Does policy create vulnerabilities?
       - Historical impact of similar policy announcements
    
    4. Scandal/News Event Analysis:
       - Event severity: Minor controversy vs. major scandal
       - Historical impact of similar events on candidate odds
       - Time decay: Do scandal impacts fade over weeks/months?
       - Candidate resilience: History of surviving controversies
       - Media cycle duration: 24hr story vs. multi-week coverage
    
    5. Endorsement Events:
       - Endorser influence: Party establishment, celebrities, unions
       - Timing of endorsement (early vs. late in race)
       - Expected vs. surprise endorsements
       - Historical impact on polling and fundraising
       - Correlation with actual vote outcomes
    
    6. Economic/External Events:
       - Jobs reports, GDP, inflation (impact on incumbent odds)
       - International crises (war, terrorism impact on election)
       - Supreme Court decisions affecting key issues
       - Natural disasters or pandemics
       - Historical correlation between economy and election outcomes
    
    Output Format:
    - Pre-event probability: Market price before event
    - Expected post-event range: Probability range based on likely outcomes
    - Catalyst impact score: 1-10 (how much could this event move markets?)
    - Upside/downside scenarios: Best case / base case / worst case probabilities
    - Time to event: Days until catalyst resolves
    - Historical comps: Similar events and their market impacts
    """
    
    def __init__(self):
        """Initialize JPMorgan Politics Agent."""
        super().__init__()
        self.agent_id = "jpmorgan_politics"
        self.theme = "us_politics"
        self.min_volume = 25000.0  # $25K minimum
        self.min_edge = 0.03  # 3% minimum edge (event-driven is tactical)
        self.min_conviction = 0.60  # 60% minimum conviction
    
    @property
    def mandate(self) -> str:
        """Agent's mandate/focus area."""
        return "Event catalyst analysis for US politics: debates, primaries, scandals, policy announcements"
    
    def update_theses(self) -> List[Thesis]:
        """
        Generate theses for US politics markets using event catalyst analysis.
        
        Workflow:
        1. Fetch US politics markets
        2. Identify upcoming events (debates, primaries, announcements)
        3. Model pre/post-event probability shifts
        4. Generate event-driven theses
        
        Returns:
            List of Thesis objects (edge > 3%, conviction > 60%)
        """
        print(f"\n{'='*60}")
        print(f"📅 JPMORGAN POLITICS AGENT - Event Catalyst Analysis")
        print(f"{'='*60}")
        
        try:
            # Fetch US politics markets
            markets = get_markets(filters={
                "category": "politics",
                "min_volume": self.min_volume,
                "resolved": False
            })
            
            print(f"📊 Analyzing {len(markets)} politics markets (event lens)")
            
            # Post chat message about starting analysis
            if len(markets) > 0:
                self.post_message('chat', content=f"👋 Starting analysis on {len(markets)} markets...")
            
            if not markets:
                print("⚠️ No markets found")
                self.post_message('chat', content="Nothing to analyze today 🤷")
                return []
            
            # Fetch news for event identification
            news_events = get_news_events(filters={"hours_back": 48})  # 48h for events
            print(f"📰 Context: {len(news_events)} news events")
            
            # Analyze markets
            theses = []
            for market in markets:
                try:
                    thesis = self.generate_thesis(market, news_events)
                    
                    # generate_thesis() enforces thresholds + posts rejections
                    if thesis is not None:
                        theses.append(thesis)
                        print(f"✅ {market.question[:45]}... | Edge: {thesis.edge:.1%}, Conv: {thesis.conviction:.1%}")
                
                except Exception as e:
                    print(f"⚠️ Error analyzing {market.id}: {e}")
                    continue
            
            self._theses_cache = theses
            print(f"\n📅 Generated {len(theses)} event-driven theses")
            
            # Post completion chat
            if len(theses) > 0:
                self.post_message('chat', content=f"✅ Done! Generated {len(theses)} theses")
            else:
                self.post_message('chat', content="Analysis complete - no opportunities met threshold today")
            print(f"{'='*60}\n")
            
            return theses
        
        except Exception as e:
            print(f"❌ Error in update_theses: {e}")
            return []
    
    def generate_thesis(self, market: Market, news_events: List = None) -> Optional[Thesis]:
        """
        Generate event catalyst thesis for a US politics market.
        
        Analyzes:
        - Upcoming events and their potential impact
        - Pre/post-event probability shifts
        - Historical event impact patterns
        - Market positioning before events
        
        Args:
            market: Market to analyze
            news_events: Recent news for event identification
        
        Returns:
            Thesis object with event-driven conviction, or None
        """
        # 1) START: Trading Floor message
        self.post_message(
            'analyzing',
            market_question=market.question,
            market_id=market.id,
            current_odds=market.yes_price,
            status='analyzing'
        )

        # Placeholder implementation (would call LLM with system prompt in production)
        # For now, use event detection heuristics
        
        if news_events is None:
            news_events = get_news_events(filters={"hours_back": 48})
        
        # Analyze event catalysts + price the market
        try:
            event_analysis = self._analyze_event_catalysts(market, news_events)
            fair_value = self._calculate_event_fair_value(market, event_analysis)
        except Exception as e:
            # 2) REJECTION: Insufficient data / cannot price
            self.post_message(
                'alert',
                market_question=market.question,
                market_id=market.id,
                current_odds=market.yes_price,
                reasoning=f"Rejected: insufficient_data ({type(e).__name__})",
                status='rejected',
                tags=['rejected', 'insufficient_data']
            )
            return None

        if fair_value is None:
            self.post_message(
                'alert',
                market_question=market.question,
                market_id=market.id,
                current_odds=market.yes_price,
                reasoning="Rejected: insufficient_data (no fair_value)",
                status='rejected',
                tags=['rejected', 'insufficient_data']
            )
            return None

        edge = fair_value - market.yes_price
        
        # 3) REJECTION: Insufficient edge
        if abs(edge) < self.min_edge:
            self.post_message(
                'alert',
                market_question=market.question,
                market_id=market.id,
                current_odds=market.yes_price,
                reasoning=f"Rejected: edge {abs(edge):.1%} < min {self.min_edge:.1%}",
                status='rejected',
                tags=['rejected', 'insufficient_edge']
            )
            return None
        
        # Conviction based on event clarity and historical precedent
        conviction = min(0.85, 0.60 + event_analysis['catalyst_score'] * 0.05)

        # 4) REJECTION: Low conviction
        if conviction < self.min_conviction:
            self.post_message(
                'alert',
                market_question=market.question,
                market_id=market.id,
                current_odds=market.yes_price,
                reasoning=f"Rejected: conviction {conviction:.1%} < min {self.min_conviction:.1%}",
                status='rejected',
                tags=['rejected', 'low_conviction']
            )
            return None
        
        # Generate JPMorgan-style event note
        thesis_text = f"""
JPMORGAN POLITICS - EVENT CATALYST ANALYSIS

Market: {market.question}
Current Price: {market.yes_price:.1%} | Event-Adjusted Fair Value: {fair_value:.1%}

EVENT ANALYSIS:

Catalyst Detected: {event_analysis['event_type']}
Catalyst Impact Score: {event_analysis['catalyst_score']:.1f}/10
News Events: {event_analysis['event_count']} related events in last 48h

PRE-EVENT POSITIONING:
Market has {'priced in' if abs(edge) < 0.05 else 'NOT priced in'} the event impact.
Current odds {('undervalue' if edge > 0 else 'overvalue')} post-event probability.

EXPECTED POST-EVENT SCENARIOS:

Bull Case ({fair_value + 0.15:.1%}):
Positive event outcome (strong debate, primary win, favorable news).
Historical precedent: +10-20% probability shift.

Base Case ({fair_value:.1%}):
Expected event outcome consistent with current fundamentals.
Market adjusts {abs(edge):.1%} to reflect new information.

Bear Case ({fair_value - 0.15:.1%}):
Negative event outcome (poor performance, scandal, unexpected loss).
Historical precedent: -10-20% probability shift.

HISTORICAL COMPARABLES:
Similar events typically move markets {abs(edge) * 2:.1%} ± 5%
Time to mean reversion: 3-7 days post-event

RECOMMENDATION: {'ENTER' if abs(edge) > 0.05 else 'MONITOR'} position ahead of catalyst
Expected Return: {abs(edge):.1%}
Risk: Event volatility (position size accordingly)
"""
        
        # Position sizing based on event impact and conviction
        proposed_action = {
            "side": "YES" if edge > 0 else "NO",
            "size_pct": min(0.10, abs(edge) * 0.8)  # Conservative sizing for event risk
        }
        
        thesis = Thesis(
            agent_id=self.agent_id,
            market_id=market.id,
            thesis_text=thesis_text.strip(),
            fair_value=fair_value,
            current_odds=market.yes_price,
            edge=edge,
            conviction=conviction,
            horizon="short",  # Event-driven is short-term
            proposed_action=proposed_action
        )

        # 5) SUCCESS: Post thesis to Trading Floor
        self.post_message(
            'thesis',
            market_question=market.question,
            market_id=market.id,
            current_odds=market.yes_price,
            thesis_odds=fair_value,
            edge=edge,
            conviction=conviction,
            reasoning=thesis_text.strip()[:500],
            status='thesis_generated',
            tags=[
                self.theme,
                'bullish' if edge > 0 else 'bearish'
            ]
        )

        # Conflict/consensus checks should run AFTER a thesis is posted
        try:
            from core.message_utils import detect_conflicts, detect_consensus

            conflict = detect_conflicts(market.id)
            consensus = detect_consensus(market.id)

            tags = ['conflict_check', 'consensus_check']
            summary_bits = []

            if conflict:
                tags.append('conflict_detected')
                summary_bits.append(
                    f"Conflict detected: {conflict.get('agent1')} vs {conflict.get('agent2')} "
                    f"(spread {conflict.get('difference', 0):.0%})"
                )

            if consensus:
                tags.append('consensus_detected')
                summary_bits.append(
                    f"Consensus detected: {consensus.get('count', 0)} agents @ {consensus.get('avg_odds', 0):.0%}"
                )

            if summary_bits:
                self.post_message(
                    'alert',
                    market_question=market.question,
                    market_id=market.id,
                    current_odds=market.yes_price,
                    reasoning=" | ".join(summary_bits)[:500],
                    status='post_thesis_checks',
                    tags=tags
                )

        except Exception:
            # Never block thesis generation due to meta-check failures
            pass
        
        return thesis
    
    def _analyze_event_catalysts(self, market: Market, news_events: List) -> dict:
        """
        Detect and analyze event catalysts for a political market.
        
        In production, this would:
        - Parse debate schedules
        - Track primary calendars
        - Detect breaking news
        - Model scandal severity
        
        For now: news-based event detection.
        
        Args:
            market: Market being analyzed
            news_events: Recent news events
        
        Returns:
            Dict with event_type, catalyst_score, event_count
        """
        question_lower = market.question.lower()
        
        # Detect event keywords
        event_keywords = {
            'debate': ['debate', 'town hall', 'forum'],
            'primary': ['primary', 'caucus', 'election'],
            'scandal': ['scandal', 'controversy', 'investigation'],
            'policy': ['policy', 'platform', 'plan', 'proposal'],
            'endorsement': ['endorses', 'endorsement', 'backs']
        }
        
        # Count events by type
        event_counts = {event_type: 0 for event_type in event_keywords}
        
        for event in news_events:
            headline_lower = event.headline.lower()
            for event_type, keywords in event_keywords.items():
                if any(kw in headline_lower for kw in keywords):
                    event_counts[event_type] += 1
        
        # Determine primary event type
        primary_event = max(event_counts.items(), key=lambda x: x[1])
        event_type = primary_event[0] if primary_event[1] > 0 else 'general'
        event_count = primary_event[1]
        
        # Calculate catalyst impact score (1-10)
        # More news = higher impact
        catalyst_score = min(10.0, 3.0 + event_count * 1.5)
        
        return {
            'event_type': event_type.capitalize(),
            'catalyst_score': catalyst_score,
            'event_count': event_count
        }
    
    def _calculate_event_fair_value(self, market: Market, event_analysis: dict) -> float:
        """
        Calculate fair value incorporating event catalyst impact.
        
        In production: Model pre/post-event shifts based on historical data.
        For now: Adjust price based on event intensity.
        
        Args:
            market: Market being valued
            event_analysis: Event analysis results
        
        Returns:
            Fair value probability (0.0-1.0)
        """
        catalyst_score = event_analysis['catalyst_score']
        
        # Event-driven adjustment
        # Higher catalyst score = more potential for movement
        event_impact = (catalyst_score / 10.0) * 0.12  # Up to 12% impact
        
        # Direction based on current price (mean reversion post-event)
        if market.yes_price > 0.65:
            # Expensive markets: expect negative event surprise
            fair_value = market.yes_price - event_impact
        elif market.yes_price < 0.35:
            # Cheap markets: expect positive event surprise
            fair_value = market.yes_price + event_impact
        else:
            # Normal range: small adjustment
            fair_value = market.yes_price + event_impact * 0.3
        
        # Clamp to valid range
        fair_value = max(0.10, min(0.90, fair_value))
        
        return fair_value
