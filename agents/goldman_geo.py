"""
BASED MONEY - Goldman Sachs Geopolitical Agent  
Fundamental analysis of geopolitical prediction markets
"""

from typing import List, Optional
from datetime import datetime
import sys
sys.path.insert(0, '..')

from agents.base import BaseAgent
from models import Thesis, Market
from database import get_markets, get_news_events


class GoldmanGeoAgent(BaseAgent):
    """
    Goldman Sachs-style fundamental analyst for geopolitical prediction markets.
    
    Applies rigorous fundamental analysis to evaluate geopolitical actors'
    capabilities, incentives, and strategic positioning.
    
    System Prompt (Institutional Analysis Framework):
    ================================================
    
    You are a senior geopolitical analyst at Goldman Sachs evaluating prediction 
    markets with fundamental, bottom-up analysis.
    
    For each geopolitical market, conduct deep fundamental analysis:
    
    1. Outcome Model:
       - What are the fundamental drivers that determine this outcome?
       - Break down the causal chain: what must happen for YES vs NO?
       - Which variables are most sensitive? Which are independent?
    
    2. Actor Analysis:
       - Who are the key players (nations, leaders, organizations, factions)?
       - What are each actor's:
         * Core incentives (political survival, economic gain, ideology)?
         * Capabilities (military strength, economic resources, diplomatic reach)?
         * Constraints (domestic politics, alliances, public opinion, budget)?
       - Who has the most to gain/lose from each outcome?
    
    3. Resource Assessment:
       - Military resources: troop strength, equipment quality, logistics, morale
       - Economic resources: GDP, reserves, budget flexibility, trade dependencies
       - Diplomatic resources: alliances, international support, sanctions leverage
       - How do resource imbalances affect outcome probability?
    
    4. Strategic Positioning:
       - Who has leverage? (escalation dominance, veto power, first-mover advantage)
       - What alliances or dependencies are critical?
       - Are there asymmetric advantages (terrain, home field, resolve)?
       - What are the opportunity costs of action vs. inaction for each actor?
    
    5. Leadership Quality:
       - Historical decision-making patterns of key leaders
       - Track record on similar situations (risk appetite, consistency, rationality)
       - Domestic political pressures and approval ratings
       - Is leadership stable or vulnerable to replacement?
    
    6. Timeline Analysis:
       - What are critical dates, events, or thresholds (elections, summits, deadlines)?
       - What is the natural timeline for this outcome (days, weeks, months, years)?
       - Are there forcing functions that accelerate or delay resolution?
       - What early indicators would signal outcome direction?
    
    Output Format:
    - Fair value estimate: X% ± Y% (with confidence interval)
    - Bull case: Why outcome happens (probability, key assumptions)
    - Bear case: Why outcome doesn't happen (probability, key assumptions)
    - Key catalysts to watch: 3-5 specific events or indicators
    - Base case / Bull case / Bear case probabilities
    - 12-month outlook: Expected trajectory
    """
    
    def __init__(self):
        """Initialize Goldman Geopolitical Agent."""
        super().__init__()
        self.agent_id = "goldman_geo"
        self.theme = "geopolitical"
        self.min_volume = 50000.0  # $50K minimum 24h volume
        self.min_edge = 0.04  # 4% minimum edge (higher bar for fundamental conviction)
        self.min_conviction = 0.65  # 65% minimum conviction
    
    @property
    def mandate(self) -> str:
        """Agent's mandate/focus area."""
        return "Fundamental analysis of geopolitical actors: capabilities, incentives, resources, strategic positioning"
    
    def update_theses(self) -> List[Thesis]:
        """
        Generate theses for geopolitical markets using fundamental analysis.
        
        Workflow:
        1. Fetch geopolitical markets with sufficient volume
        2. Conduct deep actor/resource/strategic analysis
        3. Build outcome models from fundamentals
        4. Generate high-conviction theses
        
        Returns:
            List of Thesis objects (only those with edge > 4% and conviction > 65%)
        """
        print(f"\n{'='*60}")
        print(f"🏛️ GOLDMAN SACHS GEOPOLITICAL AGENT - Fundamental Analysis")
        print(f"{'='*60}")
        
        try:
            # Fetch geopolitical markets
            markets = get_markets(filters={
                "category": "geopolitical",
                "min_volume": self.min_volume,
                "resolved": False
            })
            
            print(f"📊 Analyzing {len(markets)} markets (fundamental lens)")
            
            # Post chat message about starting analysis
            if len(markets) > 0:
                self.post_message('chat', content=f"👋 Starting analysis on {len(markets)} markets...")
            
            if not markets:
                print("⚠️ No markets found")
                self.post_message('chat', content="Nothing to analyze today 🤷")
                return []
            
            # Fetch news for actor/event context
            news_events = get_news_events(filters={"hours_back": 48})  # 48h for deeper context
            print(f"📰 Context: {len(news_events)} news events")
            
            # Fundamental analysis for each market
            theses = []
            for market in markets:
                try:
                    thesis = self.generate_thesis(market, news_events)
                    
                    if thesis:
                        theses.append(thesis)
                        print(f"✅ {market.question[:45]}... | Edge: {thesis.edge:.1%}, Conv: {thesis.conviction:.1%}")
                
                except Exception as e:
                    print(f"⚠️ Error analyzing {market.id}: {e}")
                    continue
            
            self._theses_cache = theses
            print(f"\n💼 Generated {len(theses)} high-conviction fundamental theses")
            
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
        Generate fundamentals-driven thesis for a geopolitical market.
        
        Analyzes:
        - Actor capabilities and incentives
        - Resource balance (military, economic, diplomatic)
        - Strategic positioning and leverage
        - Leadership decision-making patterns
        - Timeline and catalysts
        
        Args:
            market: Market to analyze
            news_events: Recent news for actor context
        
        Returns:
            Thesis object with fundamentals-driven conviction, or None
        """
        self.post_message('chat', content=f"🔍 Analyzing: {market.question[:60]}...")
        
        # Placeholder implementation (would call LLM with system prompt in production)
        # For now, use actor analysis heuristics
        
        if news_events is None:
            news_events = get_news_events(filters={"hours_back": 48})
        
        # Analyze actor fundamentals from news
        actor_analysis = self._analyze_actors(market, news_events)
        
        # Fundamental fair value based on actor balance
        # In production: LLM would assess capabilities, incentives, constraints
        fair_value = self._calculate_fundamental_value(market, actor_analysis)
        edge = fair_value - market.yes_price
        
        if abs(edge) < self.min_edge:
            self.post_message('chat', content=f"❌ Passing on {market.question[:50]}... - only {abs(edge):.1%} edge (need {self.min_edge:.1%}+)")
            return None
        
        # High conviction when fundamentals are clear
        # In production: LLM confidence based on information quality
        conviction = min(0.90, 0.65 + abs(edge) * 1.5)
        
        if conviction < self.min_conviction:
            self.post_message('chat', content=f"❌ {market.question[:50]}... - conviction too low ({conviction:.1%})")
            return None
        
        # Generate Goldman-style research note
        thesis_text = f"""
GOLDMAN SACHS GEOPOLITICAL RESEARCH

Market: {market.question}
Current Price: {market.yes_price:.1%} | Fair Value: {fair_value:.1%}

FUNDAMENTAL ANALYSIS:

Actor Balance:
{actor_analysis['summary']}

Resource Assessment:
- Information events detected: {actor_analysis['event_count']}
- Market liquidity: ${market.volume_24h:,.0f}
- Price discovery: {'Active' if market.volume_24h > 100000 else 'Limited'}

Strategic Positioning:
The current market price {'undervalues' if edge > 0 else 'overvalues'} the fundamental 
probability based on actor capabilities and incentives.

BULL CASE ({fair_value + 0.10:.1%}):
Key actors have demonstrated capability and intent to pursue this outcome.
Historical patterns support escalation probability.

BEAR CASE ({fair_value - 0.10:.1%}):  
Significant constraints or disincentives may prevent outcome.
Alternative paths remain available to actors.

KEY CATALYSTS TO WATCH:
- Diplomatic statements from key leaders
- Economic data affecting actor constraints  
- Alliance positioning and signaling
- Timeline-forcing events (elections, summits, deadlines)

12-MONTH OUTLOOK:
{('Positive' if edge > 0 else 'Negative')} - Fundamental drivers favor {'YES' if edge > 0 else 'NO'} outcome.

RECOMMENDATION: {'BUY' if edge > 0 else 'SELL'} at current levels
Target: {fair_value:.1%} ± 5%
Conviction: {conviction:.0%}
"""
        
        # Position sizing based on conviction and edge
        proposed_action = {
            "side": "YES" if edge > 0 else "NO",
            "size_pct": min(0.20, abs(edge) * 1.0)  # Up to 20% on strong fundamentals
        }
        
        thesis = Thesis(
            agent_id=self.agent_id,
            market_id=market.id,
            thesis_text=thesis_text.strip(),
            fair_value=fair_value,
            current_odds=market.yes_price,
            edge=edge,
            conviction=conviction,
            horizon="long",  # Fundamental analysis for medium-long term
            proposed_action=proposed_action
        )
        
        capital_allocated = 83.30 * proposed_action["size_pct"] / 0.15
        self.post_message('thesis', market_question=market.question, market_id=market.id, current_odds=market.yes_price, thesis_odds=fair_value, edge=edge, conviction=conviction, capital_allocated=capital_allocated, reasoning=thesis_text[:500], signals={'event_count': actor_analysis['event_count'], 'volume_24h': market.volume_24h}, status='thesis_generated', related_thesis_id=str(thesis.id), tags=[self.theme, 'bullish' if edge > 0 else 'bearish', 'fundamental'])
        
        
        # Announce in chat
        side_emoji = "🟢" if edge > 0 else "🔴"
        self.post_message('chat', content=f"{side_emoji} Thesis posted: {market.question[:60]}... | Edge: {edge:+.1%} | Conviction: {conviction:.1%}")
        return thesis
    
    def _analyze_actors(self, market: Market, news_events: List) -> dict:
        """
        Analyze geopolitical actors' capabilities and incentives.
        
        In production, this would:
        - Query databases of military strength (SIPRI, IISS)
        - Assess economic capabilities (IMF, World Bank data)
        - Analyze leadership track records and approval ratings
        - Map alliance structures and dependencies
        
        For now: basic news correlation analysis.
        
        Args:
            market: Market being analyzed
            news_events: Recent news for context
        
        Returns:
            Dict with actor analysis summary
        """
        question_lower = market.question.lower()
        
        # Extract potential actors from question
        actors = []
        actor_keywords = ['russia', 'china', 'us', 'ukraine', 'iran', 'israel', 
                         'nato', 'eu', 'un', 'taiwan', 'korea']
        
        for keyword in actor_keywords:
            if keyword in question_lower:
                actors.append(keyword.upper())
        
        # Count relevant news events
        relevant_events = 0
        for event in news_events:
            headline_lower = event.headline.lower()
            if any(actor.lower() in headline_lower for actor in actors):
                relevant_events += 1
        
        summary = f"Actors identified: {', '.join(actors) if actors else 'Multiple'}\n"
        summary += f"Recent news activity suggests {'high' if relevant_events > 5 else 'moderate' if relevant_events > 2 else 'low'} engagement."
        
        return {
            "actors": actors,
            "event_count": relevant_events,
            "summary": summary
        }
    
    def _calculate_fundamental_value(self, market: Market, actor_analysis: dict) -> float:
        """
        Calculate fair value based on fundamental actor analysis.
        
        In production: LLM would integrate:
        - Capability assessments
        - Incentive analysis  
        - Historical precedents
        - Game theory outcomes
        
        For now: simple heuristic based on news activity.
        
        Args:
            market: Market being valued
            actor_analysis: Actor analysis results
        
        Returns:
            Fair value probability (0.0-1.0)
        """
        # Base fair value on news activity (proxy for fundamental engagement)
        event_count = actor_analysis['event_count']
        
        # More events = higher probability something will happen
        activity_boost = min(0.20, event_count * 0.03)
        
        # Adjust from current price
        fair_value = min(0.85, max(0.15, market.yes_price + activity_boost))
        
        return fair_value
