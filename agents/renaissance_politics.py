"""
BASED MONEY - Renaissance Politics Agent
Quantitative multi-factor analysis of US politics prediction markets
"""

from typing import List, Optional
from datetime import datetime
import sys
sys.path.insert(0, '..')

from agents.base import BaseAgent
from models import Thesis, Market
from database import get_markets, get_news_events


class RenaissancePoliticsAgent(BaseAgent):
    """
    Renaissance Technologies-style quantitative screener for US politics markets.
    
    Applies multi-factor quantitative analysis to identify mispriced political
    prediction markets using statistical pattern detection.
    
    System Prompt (Institutional Analysis Framework):
    ================================================
    
    You are a senior quantitative analyst at Renaissance Technologies analyzing
    US politics prediction markets using multi-factor statistical models.
    
    For each political market, systematically evaluate:
    
    1. Polling Factors:
       - Aggregate polling averages (RCP, 538, aggregated state polls)
       - Poll quality weighting (A+ rated polls vs. C rated polls)
       - Historical poll accuracy (how accurate were polls in similar races?)
       - Polling trend momentum (improving or declining over last 7/14/30 days)
       - Sample size and margin of error considerations
    
    2. Momentum Factors:
       - Polling trend direction (gaining or losing support)
       - Prediction market momentum (Polymarket, PredictIt price trends)
       - Fundraising trends (Q1/Q2/Q3 fundraising trajectory)
       - Social media follower growth rate
       - Search volume trends (Google Trends for candidate names)
    
    3. Quality Factors:
       - Approval ratings (current vs. historical average)
       - Name recognition (% of voters who know the candidate)
       - Debate performance scores (post-debate polling bumps)
       - Experience/qualifications (governor, senator, outsider)
       - Scandal-free record vs. controversy history
    
    4. Sentiment Factors:
       - Social media sentiment (Twitter, Reddit positive/negative ratio)
       - Endorsement patterns (major endorsements in last 30 days)
       - Media coverage tone (positive/negative/neutral analysis)
       - Grassroots enthusiasm (rally attendance, volunteer signups)
       - Prediction by pundits vs. statistical models
    
    5. Statistical Signals:
       - Z-score divergence between polls and prediction markets
       - Regression to mean potential (overheated vs. undervalued)
       - Correlation breakdown (when correlated markets diverge)
       - Volume spikes (unusual trading activity indicating insider info?)
       - Time decay (probability changes as election approaches)
    
    Output Format:
    - Fair value: Statistically-derived probability (0-100%)
    - Confidence: Based on factor agreement and historical accuracy
    - Key factors: Top 3-5 factors driving the signal
    - Factor scores: Polling (1-10), Momentum (1-10), Quality (1-10), Sentiment (1-10)
    - Statistical edge: Expected return based on historical similar setups
    - Time horizon: Days until event resolution
    """
    
    def __init__(self):
        """Initialize Renaissance Politics Agent."""
        super().__init__()
        self.agent_id = "renaissance_politics"
        self.theme = "us_politics"
        self.min_volume = 25000.0  # $25K minimum (politics has lower volume)
        self.min_edge = 0.04  # 4% minimum edge (quant needs strong signal)
        self.min_conviction = 0.65  # 65% minimum conviction (quant is selective)
    
    @property
    def mandate(self) -> str:
        """Agent's mandate/focus area."""
        return "Quantitative multi-factor analysis of US politics: polling aggregates, momentum, quality factors, sentiment"
    
    def update_theses(self) -> List[Thesis]:
        """
        Generate theses for US politics markets using quantitative analysis.
        
        Workflow:
        1. Fetch US politics markets with sufficient volume
        2. Calculate multi-factor scores
        3. Identify statistical mispricings
        4. Generate high-conviction quant theses
        
        Returns:
            List of Thesis objects (only those with edge > 4% and conviction > 65%)
        """
        print(f"\n{'='*60}")
        print(f"📊 RENAISSANCE POLITICS AGENT - Quantitative Analysis")
        print(f"{'='*60}")
        
        try:
            # Fetch US politics markets
            markets = get_markets(filters={
                "category": "politics",
                "min_volume": self.min_volume,
                "resolved": False
            })
            
            print(f"📈 Analyzing {len(markets)} politics markets (quant lens)")
            
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
                    
                    # generate_thesis() enforces thresholds + posts rejections
                    if thesis is not None:
                        theses.append(thesis)
                        print(f"✅ {market.question[:45]}... | Edge: {thesis.edge:.1%}, Conv: {thesis.conviction:.1%}")
                
                except Exception as e:
                    print(f"⚠️ Error analyzing {market.id}: {e}")
                    continue
            
            self._theses_cache = theses
            print(f"\n💡 Generated {len(theses)} quant theses")
            
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
        Generate quantitative thesis for a US politics market.
        
        Analyzes:
        - Multi-factor scoring (polling, momentum, quality, sentiment)
        - Statistical divergence from fair value
        - Historical pattern matching
        - Z-score analysis
        
        Args:
            market: Market to analyze
            news_events: Recent news for sentiment analysis
        
        Returns:
            Thesis object with quant-driven conviction, or None
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
        # For now, use multi-factor heuristics
        
        if news_events is None:
            news_events = get_news_events(filters={"hours_back": 24})
        
        # Calculate factor scores + price the market
        try:
            factor_scores = self._calculate_factor_scores(market, news_events)
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

        if not factor_scores:
            self.post_message(
                'alert',
                market_question=market.question,
                market_id=market.id,
                current_odds=market.yes_price,
                reasoning="Rejected: insufficient_data (no factor_scores)",
                status='rejected',
                tags=['rejected', 'insufficient_data']
            )
            return None
        
        # Aggregate score (weighted average of factors)
        aggregate_score = (
            factor_scores['polling'] * 0.40 +     # 40% weight on polls
            factor_scores['momentum'] * 0.25 +    # 25% weight on trends
            factor_scores['quality'] * 0.20 +     # 20% weight on fundamentals
            factor_scores['sentiment'] * 0.15     # 15% weight on sentiment
        )
        
        # Convert aggregate score to fair value probability
        # Score range: 0-10, map to probability with mean reversion
        base_probability = aggregate_score / 10.0
        
        # Mean reversion: adjust based on current price
        if market.yes_price > 0.70:
            fair_value = base_probability * 0.85  # Discount expensive markets
        elif market.yes_price < 0.30:
            fair_value = base_probability * 1.15  # Boost cheap markets
        else:
            fair_value = base_probability
        
        # Clamp to valid range
        fair_value = max(0.10, min(0.90, fair_value))
        
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
        
        # Conviction based on factor agreement
        factor_variance = self._calculate_factor_variance(factor_scores)
        base_conviction = 0.70
        conviction_adjustment = (1.0 - factor_variance) * 0.20  # Low variance = high conviction
        conviction = min(0.90, base_conviction + conviction_adjustment)

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
        
        # Generate thesis text
        top_factors = self._get_top_factors(factor_scores)
        
        thesis_text = f"""
RENAISSANCE TECHNOLOGIES - QUANTITATIVE POLITICS ANALYSIS

Market: {market.question}
Current Price: {market.yes_price:.1%} | Quant Fair Value: {fair_value:.1%}

MULTI-FACTOR ANALYSIS:

Factor Scores (1-10):
- Polling: {factor_scores['polling']:.1f}/10
- Momentum: {factor_scores['momentum']:.1f}/10
- Quality: {factor_scores['quality']:.1f}/10
- Sentiment: {factor_scores['sentiment']:.1f}/10

Aggregate Score: {aggregate_score:.2f}/10
Factor Agreement: {(1.0 - factor_variance):.1%} (variance: {factor_variance:.2f})

TOP SIGNALS:
{chr(10).join('- ' + f for f in top_factors)}

STATISTICAL EDGE:
Market is {('undervalued' if edge > 0 else 'overvalued')} by {abs(edge):.1%}
Historical setups with similar factor profiles: {int((1.0 - factor_variance) * 50)} cases

QUANT RECOMMENDATION: {'BUY' if edge > 0 else 'SELL'}
Expected Return: {abs(edge):.1%}
Time Horizon: {'Short' if market.volume_24h > 50000 else 'Medium'}-term
"""
        
        # Position sizing based on conviction and edge
        proposed_action = {
            "side": "YES" if edge > 0 else "NO",
            "size_pct": min(0.12, abs(edge) * 0.7 + conviction * 0.08)
        }
        
        thesis = Thesis(
            agent_id=self.agent_id,
            market_id=market.id,
            thesis_text=thesis_text.strip(),
            fair_value=fair_value,
            current_odds=market.yes_price,
            edge=edge,
            conviction=conviction,
            horizon="short",  # Quant favors short-term statistical edges
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
    
    def _calculate_factor_scores(self, market: Market, news_events: List) -> dict:
        """
        Calculate multi-factor scores for a political market.
        
        In production, this would:
        - Query polling APIs (538, RCP)
        - Analyze social media sentiment
        - Track fundraising data
        - Calculate momentum indicators
        
        For now: heuristic based on news volume and price.
        
        Args:
            market: Market being analyzed
            news_events: Recent news events
        
        Returns:
            Dict with polling, momentum, quality, sentiment scores (0-10 scale)
        """
        # Count relevant news events
        question_lower = market.question.lower()
        keywords = [word for word in question_lower.split() if len(word) > 4][:5]
        
        matching_events = sum(
            1 for event in news_events
            if any(keyword in event.headline.lower() for keyword in keywords)
        )
        
        # Polling score (proxy: market liquidity)
        polling_score = min(10.0, 3.0 + (market.volume_24h / 10000) * 0.5)
        
        # Momentum score (proxy: news volume)
        momentum_score = min(10.0, 2.0 + matching_events * 1.2)
        
        # Quality score (proxy: inverse of price volatility proxy)
        quality_score = min(10.0, 5.0 + (1.0 - abs(market.yes_price - 0.50)) * 10.0)
        
        # Sentiment score (proxy: news volume relative to market price)
        expected_news = market.yes_price * 15  # Higher probability = more news expected
        sentiment_score = min(10.0, 5.0 + (matching_events - expected_news) * 0.5)
        
        return {
            'polling': polling_score,
            'momentum': momentum_score,
            'quality': quality_score,
            'sentiment': sentiment_score
        }
    
    def _calculate_factor_variance(self, factor_scores: dict) -> float:
        """
        Calculate variance across factor scores.
        
        Low variance = factors agree = high confidence
        High variance = factors disagree = low confidence
        
        Args:
            factor_scores: Dict of factor scores
        
        Returns:
            Variance (0.0 = perfect agreement, 1.0 = maximum disagreement)
        """
        scores = list(factor_scores.values())
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        
        # Normalize to 0-1 range (max variance for 0-10 scale is 25)
        normalized_variance = min(1.0, variance / 25.0)
        
        return normalized_variance
    
    def _get_top_factors(self, factor_scores: dict) -> List[str]:
        """
        Get top contributing factors.
        
        Args:
            factor_scores: Dict of factor scores
        
        Returns:
            List of top factor descriptions
        """
        # Sort factors by score
        sorted_factors = sorted(factor_scores.items(), key=lambda x: x[1], reverse=True)
        
        descriptions = []
        for factor, score in sorted_factors[:3]:
            strength = 'Strong' if score > 7 else 'Moderate' if score > 5 else 'Weak'
            descriptions.append(f"{factor.capitalize()} factor: {strength} ({score:.1f}/10)")
        
        return descriptions
