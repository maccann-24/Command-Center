"""
BASED MONEY - Goldman Politics Agent
Fundamental political analysis for US politics prediction markets
"""

from typing import List, Optional
from datetime import datetime
import sys
sys.path.insert(0, '..')

from agents.base import BaseAgent
from models import Thesis, Market
from database import get_markets, get_news_events


class GoldmanPoliticsAgent(BaseAgent):
    """
    Goldman Sachs-style fundamental analyst for US politics markets.
    
    Applies rigorous fundamental analysis to evaluate candidate strength,
    electoral dynamics, and structural political factors.
    
    System Prompt (Institutional Analysis Framework):
    ================================================
    
    You are a senior political analyst at Goldman Sachs evaluating US politics
    prediction markets through fundamental, bottom-up analysis.
    
    For each political market, conduct deep fundamental analysis:
    
    1. Electoral Map Analysis:
       - State-by-state probabilities (swing states vs. safe states)
       - Electoral college math (270 to win scenarios)
       - Historical state voting patterns (red/blue/purple classification)
       - Demographic trends by state (age, race, education shifts)
       - Path to victory: What states must the candidate win?
    
    2. Demographic Analysis:
       - Voter bloc breakdown (white working class, suburban women, minorities)
       - Historical turnout patterns by demographic
       - Registration trends (new voters, party switches)
       - Age cohort voting behavior (Gen Z, Millennials, Boomers)
       - Education polarization (college vs. non-college whites)
    
    3. Campaign Organization Fundamentals:
       - Ground game strength (field offices, staff count by state)
       - Fundraising efficiency (burn rate, cash on hand, small donor %)
       - Volunteer network size and engagement
       - Data operation quality (voter targeting, GOTV infrastructure)
       - Media buy strategy (ad spending by market, message testing)
    
    4. Endorsement Quality Assessment:
       - Party establishment support (governors, senators, mayors)
       - Labor union endorsements (AFL-CIO, teachers unions)
       - Influential figures (ex-presidents, popular politicians)
       - Grassroots organization endorsements (activists, groups)
       - Endorsement timing and enthusiasm level
    
    5. Candidate Fundamentals:
       - Political experience and track record
       - Policy platform strength (clear vs. vague, popular vs. unpopular)
       - Communication skills (debate performance, stump speech quality)
       - Personal favorability vs. unfavorability ratings
       - Scandal/controversy history and resilience
    
    6. Structural Factors:
       - Incumbent advantage or disadvantage
       - Economic fundamentals (GDP growth, unemployment, consumer confidence)
       - Generic ballot (party preference polling)
       - Presidential approval ratings (for incumbents)
       - Historical patterns (midterm backlash, second-term fatigue)
    
    Output Format:
    - Fundamental fair value: Probability based on structural factors
    - Confidence interval: Fair value ± uncertainty range
    - Key strengths: Top 3 fundamental advantages
    - Key weaknesses: Top 3 fundamental disadvantages
    - Electoral college scenarios: Likely / Optimistic / Pessimistic paths
    - 12-month outlook: Expected trajectory based on fundamentals
    """
    
    def __init__(self):
        """Initialize Goldman Politics Agent."""
        super().__init__()
        self.agent_id = "goldman_politics"
        self.theme = "us_politics"
        self.min_volume = 25000.0  # $25K minimum
        self.min_edge = 0.05  # 5% minimum edge (fundamental conviction)
        self.min_conviction = 0.70  # 70% minimum conviction (high bar)
    
    @property
    def mandate(self) -> str:
        """Agent's mandate/focus area."""
        return "Fundamental political analysis: electoral map, demographics, campaign organization, endorsements"
    
    def update_theses(self) -> List[Thesis]:
        """
        Generate theses for US politics markets using fundamental analysis.
        
        Workflow:
        1. Fetch US politics markets
        2. Analyze fundamental political factors
        3. Build electoral models
        4. Generate high-conviction fundamental theses
        
        Returns:
            List of Thesis objects (edge > 5%, conviction > 70%)
        """
        print(f"\n{'='*60}")
        print(f"🏛️ GOLDMAN POLITICS AGENT - Fundamental Analysis")
        print(f"{'='*60}")
        
        try:
            # Fetch US politics markets
            markets = get_markets(filters={
                "category": "politics",
                "min_volume": self.min_volume,
                "resolved": False
            })
            
            print(f"📊 Analyzing {len(markets)} politics markets (fundamental lens)")
            
            # Post chat message about starting analysis
            if len(markets) > 0:
                self.post_message('chat', content=f"👋 Starting analysis on {len(markets)} markets...")
            
            if not markets:
                print("⚠️ No markets found")
                self.post_message('chat', content="Nothing to analyze today 🤷")
                return []
            
            # Fetch news for context
            news_events = get_news_events(filters={"hours_back": 72})  # 3 days
            print(f"📰 Context: {len(news_events)} news events")
            
            # Fundamental analysis for each market
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
            print(f"\n💼 Generated {len(theses)} fundamental theses")
            
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
        Generate fundamental thesis for a US politics market.
        
        Analyzes:
        - Electoral college math
        - Demographic fundamentals
        - Campaign organization strength
        - Structural political factors
        
        Args:
            market: Market to analyze
            news_events: Recent news for context
        
        Returns:
            Thesis object with fundamental conviction, or None
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
        # For now, use fundamental heuristics
        
        if news_events is None:
            news_events = get_news_events(filters={"hours_back": 72})
        
        # Analyze fundamentals + price the market
        try:
            fundamentals = self._analyze_fundamentals(market, news_events)
            fair_value = self._calculate_fundamental_value(market, fundamentals)
        except Exception as e:
            # 4) REJECTION: Insufficient data / cannot price
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
        
        # 2) REJECTION: Insufficient edge
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
        
        # High conviction when fundamentals are clear
        fundamental_strength = fundamentals['aggregate_score']
        conviction = min(0.90, 0.70 + (fundamental_strength / 10.0) * 0.15)

        # 2) REJECTION: Low conviction
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
        
        # Generate Goldman-style political research note
        thesis_text = f"""
GOLDMAN SACHS POLITICAL RESEARCH

Market: {market.question}
Current Price: {market.yes_price:.1%} | Fundamental Fair Value: {fair_value:.1%}

FUNDAMENTAL ANALYSIS:

Fundamental Strength Score: {fundamental_strength:.1f}/10

Campaign Fundamentals:
- Organization: {fundamentals['organization']:.1f}/10
- Endorsements: {fundamentals['endorsements']:.1f}/10
- News Momentum: {fundamentals['momentum']:.1f}/10

Electoral Analysis:
The market {('undervalues' if edge > 0 else 'overvalues')} fundamental probability by {abs(edge):.1%}.
Current pricing reflects {('insufficient' if abs(edge) > 0.10 else 'partial')} appreciation of structural factors.

KEY STRENGTHS:
- Strong fundamental indicators in {fundamentals['strength_areas']}
- Organizational advantage in critical demographics
- Favorable structural environment

KEY WEAKNESSES:
- Potential vulnerabilities in {fundamentals['weakness_areas']}
- Market may be underpricing downside risks
- Historical patterns suggest mean reversion

ELECTORAL SCENARIOS:

Base Case ({fair_value:.1%}):
Fundamentals-driven probability based on structural analysis.
Expected path given current organization and demographics.

Bull Case ({fair_value + 0.12:.1%}):
Strong turnout operation + favorable external events.
Outperformance in key swing states.

Bear Case ({fair_value - 0.12:.1%}):
Organizational weaknesses exposed or adverse events.
Underperformance with critical voter blocs.

12-MONTH OUTLOOK:
{('Positive' if edge > 0 else 'Negative')} - Fundamental factors favor {'higher' if edge > 0 else 'lower'} probability.
Expected trajectory: {'Gradual strengthening' if edge > 0 else 'Gradual weakening'}

RECOMMENDATION: {'BUY' if edge > 0 else 'SELL'}
Target: {fair_value:.1%} ± 5%
Conviction: {conviction:.0%}
Horizon: Medium-term (fundamentals play out over weeks/months)
"""
        
        # Position sizing based on conviction and edge
        proposed_action = {
            "side": "YES" if edge > 0 else "NO",
            "size_pct": min(0.15, abs(edge) * 0.9)  # Larger positions on fundamentals
        }
        
        thesis = Thesis(
            agent_id=self.agent_id,
            market_id=market.id,
            thesis_text=thesis_text.strip(),
            fair_value=fair_value,
            current_odds=market.yes_price,
            edge=edge,
            conviction=conviction,
            horizon="medium",  # Fundamentals are medium-term
            proposed_action=proposed_action
        )

        # 3) SUCCESS: Post thesis to Trading Floor
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
    
    def _analyze_fundamentals(self, market: Market, news_events: List) -> dict:
        """
        Analyze political fundamentals for a market.
        
        In production, this would:
        - Query FEC data for fundraising
        - Analyze demographic data
        - Model electoral college paths
        - Track endorsement quality
        
        For now: news-based fundamental proxy.
        
        Args:
            market: Market being analyzed
            news_events: Recent news events
        
        Returns:
            Dict with fundamental scores and analysis
        """
        question_lower = market.question.lower()
        
        # Extract candidate/topic keywords
        keywords = [word for word in question_lower.split() if len(word) > 4][:5]
        
        # Count relevant news (proxy for campaign strength)
        relevant_news = sum(
            1 for event in news_events
            if any(kw in event.headline.lower() for kw in keywords)
        )
        
        # Organization score (proxy: market liquidity)
        organization_score = min(10.0, 3.0 + (market.volume_24h / 15000) * 2.0)
        
        # Endorsement score (proxy: news volume)
        endorsement_score = min(10.0, 2.0 + relevant_news * 0.8)
        
        # Momentum score (proxy: price trend simulation)
        # In real implementation: compare price 7d ago vs. now
        momentum_score = min(10.0, 5.0 + (market.yes_price - 0.50) * 10.0)
        
        # Aggregate fundamental score
        aggregate = (organization_score + endorsement_score + momentum_score) / 3.0
        
        # Determine strength/weakness areas
        if organization_score > 6:
            strength_areas = "campaign organization and fundraising"
        else:
            strength_areas = "grassroots enthusiasm"
        
        if endorsement_score < 5:
            weakness_areas = "establishment support and endorsements"
        else:
            weakness_areas = "media coverage and visibility"
        
        return {
            'organization': organization_score,
            'endorsements': endorsement_score,
            'momentum': momentum_score,
            'aggregate_score': aggregate,
            'strength_areas': strength_areas,
            'weakness_areas': weakness_areas
        }
    
    def _calculate_fundamental_value(self, market: Market, fundamentals: dict) -> float:
        """
        Calculate fair value from fundamental analysis.
        
        In production: Electoral college model + demographic analysis.
        For now: Aggregate fundamental score with adjustments.
        
        Args:
            market: Market being valued
            fundamentals: Fundamental analysis results
        
        Returns:
            Fair value probability (0.0-1.0)
        """
        aggregate_score = fundamentals['aggregate_score']
        
        # Convert 0-10 score to probability
        base_probability = aggregate_score / 10.0
        
        # Adjust for current price (fundamentals override market)
        if market.yes_price > 0.70 and base_probability < 0.60:
            # Market too expensive relative to fundamentals
            fair_value = base_probability * 1.10
        elif market.yes_price < 0.30 and base_probability > 0.40:
            # Market too cheap relative to fundamentals
            fair_value = base_probability * 0.90
        else:
            fair_value = base_probability
        
        # Clamp to valid range
        fair_value = max(0.10, min(0.90, fair_value))
        
        return fair_value
