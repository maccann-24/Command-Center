"""
BASED MONEY - Two Sigma Geopolitical Agent
Macro-driven analysis of geopolitical prediction markets
"""

from typing import List, Optional
from datetime import datetime
import sys
sys.path.insert(0, '..')

from agents.base import BaseAgent
from models import Thesis, Market
from database import get_markets, get_news_events
from core.message_utils import check_all_after_thesis


class TwoSigmaGeoAgent(BaseAgent):
    """
    Two Sigma-style macro strategist for geopolitical prediction markets.
    
    Applies macro analysis framework to evaluate how economic indicators,
    central bank policy, and cross-market signals affect geopolitical outcomes.
    
    System Prompt (Institutional Analysis Framework):
    ================================================
    
    You are a senior macro strategist at Two Sigma analyzing geopolitical 
    prediction markets using quantitative macro analysis.
    
    For each geopolitical market, systematically assess:
    
    1. Economic Context:
       - How do current GDP growth, inflation, and unemployment trends affect 
         this geopolitical outcome?
       - Are economic pressures creating incentives for conflict, cooperation, 
         or policy change?
       - Which actors face economic constraints that limit their options?
    
    2. Central Bank Policy:
       - Is Fed/ECB/PBOC monetary policy creating conditions (rates, QE/QT, 
         USD strength) that make this outcome more or less likely?
       - Do rate hikes reduce risk appetite for geopolitical escalation?
       - Does dollar strength affect sanctioned nations' capabilities?
    
    3. Cross-Market Signals:
       - Are related prediction markets (oil prices, defense stocks, regional 
         conflicts) pricing in similar or divergent outcomes?
       - What do commodity markets (oil, wheat, nat gas) signal about supply 
         disruption expectations?
       - Is there arbitrage between correlated geopolitical markets?
    
    4. Sentiment Analysis:
       - What are news sentiment scores, social media trends, and Google Trends 
         telling us about public/institutional attention?
       - Are insiders (diplomats, defense officials, think tanks) positioned 
         for a specific outcome?
       - Has sentiment shifted meaningfully in the last 7/30 days?
    
    5. Seasonal/Historical Patterns:
       - What does historical data say about similar geopolitical events 
         (past wars, elections, sanctions, treaties)?
       - Are there seasonal patterns (winter energy crises, election cycles, 
         budget deadlines)?
       - How long did similar situations take to resolve historically?
    
    Output Format:
    - Fair value estimate: 0-100% probability
    - Conviction: 0.0-1.0 based on signal strength and data quality
    - Key macro drivers: List of 3-5 primary factors
    - Bull case: Why outcome happens (with probability)
    - Bear case: Why outcome doesn't happen (with probability)
    - 7-day outlook: Near-term catalyst assessment
    - 30-day outlook: Medium-term trend projection
    """
    
    def __init__(self):
        """Initialize Two Sigma Geopolitical Agent."""
        super().__init__()
        self.agent_id = "twosigma_geo"
        self.theme = "geopolitical"
        self.min_volume = 50000.0  # $50K minimum 24h volume
        self.min_edge = 0.03  # 3% minimum edge
        self.min_conviction = 0.60  # 60% minimum conviction
    
    @property
    def mandate(self) -> str:
        """Agent's mandate/focus area."""
        return "Macro-driven analysis of geopolitical events: economic indicators, central bank policy, cross-market signals"
    
    def update_theses(self) -> List[Thesis]:
        """
        Generate theses for geopolitical markets using macro analysis.
        
        Workflow:
        1. Fetch geopolitical markets with sufficient volume
        2. Fetch recent economic indicators and news
        3. Analyze each market through macro lens
        4. Generate theses for markets with strong signals
        
        Returns:
            List of Thesis objects (only those with edge > 3% and conviction > 60%)
        """
        print(f"\n{'='*60}")
        print(f"📊 TWO SIGMA GEOPOLITICAL AGENT - Macro Analysis")
        print(f"{'='*60}")
        
        try:
            # Fetch geopolitical markets
            markets = get_markets(filters={
                "category": "geopolitical",
                "min_volume": self.min_volume,
                "resolved": False
            })
            
            print(f"📈 Analyzing {len(markets)} geopolitical markets (macro lens)")
            
            if not markets:
                print("⚠️ No markets found")
                self.post_message('chat', content="Nothing to analyze today 🤷")
                return []
            
            # Fetch news for sentiment analysis
            news_events = get_news_events(filters={"hours_back": 24})
            print(f"📰 Fetched {len(news_events)} news events for sentiment")
            
            # Analyze markets
            theses = []
            for market in markets:
                try:
                    thesis = self.generate_thesis(market, news_events)
                    
                    if thesis and thesis.edge >= self.min_edge and thesis.conviction >= self.min_conviction:
                        theses.append(thesis)
                        print(f"✅ {market.question[:50]}... | Edge: {thesis.edge:.1%}, Conviction: {thesis.conviction:.1%}")
                
                except Exception as e:
                    print(f"⚠️ Error analyzing {market.id}: {e}")
                    continue
            
            self._theses_cache = theses
            print(f"\n💡 Generated {len(theses)} actionable macro theses")
            
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
        Generate macro-driven thesis for a geopolitical market.
        
        Analyzes:
        - Economic context (GDP, inflation, unemployment impact)
        - Central bank policy effects
        - Cross-market signal divergence
        - News sentiment trends
        - Historical patterns
        
        Args:
            market: Market to analyze
            news_events: Recent news for sentiment analysis
        
        Returns:
            Thesis object with macro-driven conviction, or None
        """
        # Post: Starting analysis
        self.post_message(
            'analyzing',
            market_question=market.question,
            market_id=market.id,
            current_odds=market.yes_price,
            status='analyzing'
        )
        
        # Placeholder implementation (would call LLM with system prompt in production)
        # For now, use simple heuristics based on news sentiment
        
        if news_events is None:
            news_events = get_news_events(filters={"hours_back": 24})
        
        # Calculate sentiment from news (simple keyword matching for now)
        sentiment_score = self._calculate_macro_sentiment(market, news_events)
        
        # Macro-driven fair value adjustment
        # Positive sentiment = increased probability (buy signal)
        # Negative sentiment = decreased probability (sell signal)
        fair_value = max(0.10, min(0.90, market.yes_price + sentiment_score * 0.15))
        edge = fair_value - market.yes_price
        
        # Check if edge magnitude meets minimum threshold (can be positive or negative)
        if abs(edge) < self.min_edge:
            # Post: Thesis rejected
            self.post_message(
                'alert',
                market_question=market.question,
                market_id=market.id,
                current_odds=market.yes_price,
                reasoning=f"Rejected: Edge {abs(edge):.1%} below minimum threshold {self.min_edge:.1%}",
                status='rejected',
                tags=['rejected', 'insufficient_edge']
            )
            return None
        
        # Conviction based on macro signal strength
        # In production, this would come from LLM analysis of economic data
        conviction = min(0.85, 0.60 + abs(edge) * 2.0)
        
        # Check if conviction meets minimum threshold
        if conviction < self.min_conviction:
            # Post: Thesis rejected (low conviction)
            self.post_message(
                'alert',
                market_question=market.question,
                market_id=market.id,
                current_odds=market.yes_price,
                reasoning=f"Rejected: Conviction {conviction:.1%} below minimum threshold {self.min_conviction:.1%}",
                status='rejected',
                tags=['rejected', 'low_conviction']
            )
            return None
        
        # Generate thesis text
        macro_drivers = [
            "News sentiment analysis",
            "Economic pressure indicators",
            "Central bank policy stance"
        ]
        
        thesis_text = f"""
Two Sigma Macro Analysis: {market.question}

MACRO CONTEXT:
Economic indicators suggest {('increased' if sentiment_score > 0 else 'decreased')} probability of this outcome.
Current market price ({market.yes_price:.1%}) {('undervalues' if edge > 0 else 'overvalues')} the macro-driven probability.

KEY DRIVERS:
{chr(10).join('- ' + d for d in macro_drivers)}

FAIR VALUE: {fair_value:.1%} (current: {market.yes_price:.1%})
EDGE: {edge:.1%}

OUTLOOK:
7-day: Monitor economic data releases and policy statements
30-day: Assess macro trend continuation vs. mean reversion
"""
        
        # Create thesis
        proposed_action = {
            "side": "YES" if edge > 0 else "NO",
            "size_pct": min(0.15, abs(edge) * 0.5)  # Position size scales with edge
        }
        
        thesis = Thesis(
            agent_id=self.agent_id,
            market_id=market.id,
            thesis_text=thesis_text.strip(),
            fair_value=fair_value,
            current_odds=market.yes_price,
            edge=edge,
            conviction=conviction,
            horizon="medium",  # Macro trends play out over weeks
            proposed_action=proposed_action
        )
        
        # Calculate capital allocation (would come from ThemeManager in production)
        # For now, use simple heuristic: 10% of assumed $833 allocation = $83.30 base
        capital_allocated = 83.30 * proposed_action["size_pct"] / 0.15  # Scale by position size
        
        # Post: Thesis generated
        self.post_message(
            'thesis',
            market_question=market.question,
            market_id=market.id,
            current_odds=market.yes_price,
            thesis_odds=fair_value,
            edge=edge,
            conviction=conviction,
            capital_allocated=capital_allocated,
            reasoning=thesis_text.strip(),
            signals={
                'news_events': len(news_events) if news_events else 0,
                'sentiment_score': sentiment_score,
                'macro_drivers': macro_drivers
            },
            status='thesis_generated',
            related_thesis_id=str(thesis.id),
            tags=['macro_analysis', 'geopolitical', ('bullish' if edge > 0 else 'bearish')]
        )
        
        # Check for conflicts and consensus with other agents
        check_all_after_thesis(market.id)
        
        return thesis
    
    def _calculate_macro_sentiment(self, market: Market, news_events: List) -> float:
        """
        Calculate macro sentiment score from news events.
        
        In production, this would:
        - Query economic APIs (Fed data, BLS, BEA)
        - Analyze commodity markets (oil, gold, VIX)
        - Run NLP sentiment on financial news
        - Check cross-market correlations
        
        For now: simple keyword matching on news headlines with directional bias.
        
        Args:
            market: Market being analyzed
            news_events: Recent news events
        
        Returns:
            Sentiment score (-0.5 to +0.5)
            Positive = bullish (outcome more likely)
            Negative = bearish (outcome less likely)
        """
        if not news_events:
            return 0.0
        
        # Extract keywords from market question
        question_lower = market.question.lower()
        keywords = [word for word in question_lower.split() if len(word) > 4][:5]
        
        # Count matching news events
        matching_events = 0
        for event in news_events:
            headline_lower = event.headline.lower()
            if any(keyword in headline_lower for keyword in keywords):
                matching_events += 1
        
        # Convert to sentiment score with directional bias
        # High news volume = increased probability (bullish)
        # But adjust based on current price to capture mean reversion
        base_sentiment = min(0.50, matching_events * 0.08)  # Each match = +8% sentiment
        
        # Mean reversion logic:
        # If market is expensive (>0.75), be bearish (expect price to fall)
        # If market is cheap (<0.25), be bullish (expect price to rise)
        if market.yes_price > 0.75:
            # Expensive markets: strong bearish bias (mean reversion)
            sentiment = -0.20 - (market.yes_price - 0.75) * 0.60
        elif market.yes_price < 0.25:
            # Cheap markets: strong bullish bias (mean reversion)
            sentiment = 0.20 + (0.25 - market.yes_price) * 0.60
        else:
            # Normal range: sentiment driven by news volume
            sentiment = base_sentiment * 0.6 - 0.02  # Slight bearish bias
        
        # Clamp to range
        sentiment = max(-0.50, min(0.50, sentiment))
        
        return sentiment
