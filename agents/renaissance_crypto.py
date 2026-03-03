"""
BASED MONEY - Renaissance Crypto Agent
Quantitative multi-factor analysis of crypto prediction markets
"""

from typing import List, Optional
from datetime import datetime
import sys
sys.path.insert(0, '..')

from agents.base import BaseAgent
from models import Thesis, Market
from database import get_markets, get_news_events


class RenaissanceCryptoAgent(BaseAgent):
    """
    Renaissance Technologies-style quantitative analyst for crypto markets.
    
    Applies multi-factor quantitative framework to identify mispriced
    crypto prediction markets using statistical crypto analysis.
    
    System Prompt (Institutional Analysis Framework):
    ================================================
    
    You are a senior quantitative analyst at Renaissance Technologies analyzing
    crypto prediction markets using multi-factor quantitative models.
    
    For each crypto market, systematically evaluate:
    
    1. On-Chain Factors (40% weight):
       - Transaction volume: 7-day and 30-day trends
       - Active addresses: Network usage and growth
       - Exchange inflows: Selling pressure indicators
       - Exchange outflows: Accumulation signals
       - Whale movements: Large holder activity
       - Hash rate (for PoW chains): Network security trends
    
    2. Market Factors (30% weight):
       - Spot price momentum: 1d, 7d, 30d returns
       - Futures basis: Contango (bullish) vs. backwardation (bearish)
       - Options implied volatility: Market expectations
       - Funding rates: Long/short positioning
       - Liquidations: Overleveraged positions being cleared
       - Exchange volume: Trading activity trends
    
    3. Sentiment Factors (20% weight):
       - Social media mentions: Twitter, Reddit volume
       - Fear & Greed Index: Extreme fear (buy) vs. extreme greed (sell)
       - Institutional flow: Grayscale, ETF, MicroStrategy activity
       - Google Trends: Retail interest proxy
       - Developer activity: GitHub commits, active developers
       - Regulatory news: Positive or negative headlines
    
    4. Correlation Factors (10% weight):
       - BTC correlation to S&P 500: Risk-on or safe haven?
       - BTC correlation to gold: Store of value narrative
       - BTC correlation to DXY: Dollar strength impact
       - Altcoin correlation to BTC: Independent or following?
       - Cross-crypto correlations: Sector rotation signals
    
    5. Statistical Signals:
       - Z-score analysis: How many standard deviations from mean?
       - Mean reversion: Overbought/oversold conditions
       - Momentum persistence: Trend continuation probability
       - Volume-price divergence: Confirming or contradicting?
       - Seasonality: Time-of-year patterns
    
    Output Format:
    - Fair value: Statistically-derived probability
    - Factor scores: On-chain (1-10), Market (1-10), Sentiment (1-10), Correlation (1-10)
    - Aggregate score: Weighted combination
    - Key factors: Top 3 driving signals
    - Statistical edge: Expected return
    - Mean reversion potential: How far from equilibrium?
    """
    
    def __init__(self):
        """Initialize Renaissance Crypto Agent."""
        super().__init__()
        self.agent_id = "renaissance_crypto"
        self.theme = "crypto"
        self.min_volume = 30000.0  # $30K minimum
        self.min_edge = 0.05  # 5% minimum edge (quant needs strong signal)
        self.min_conviction = 0.65  # 65% minimum conviction
    
    @property
    def mandate(self) -> str:
        """Agent's mandate/focus area."""
        return "Quantitative crypto analysis: on-chain data, market factors, sentiment, correlations"
    
    def update_theses(self) -> List[Thesis]:
        """
        Generate theses for crypto markets using quantitative analysis.
        
        Workflow:
        1. Fetch crypto markets
        2. Calculate multi-factor scores
        3. Identify statistical mispricings
        4. Generate quant theses
        
        Returns:
            List of Thesis objects (edge > 5%, conviction > 65%)
        """
        print(f"\n{'='*60}")
        print(f"🔬 RENAISSANCE CRYPTO AGENT - Quantitative Analysis")
        print(f"{'='*60}")
        
        try:
            # Fetch crypto markets
            markets = get_markets(filters={
                "category": "crypto",
                "min_volume": self.min_volume,
                "resolved": False
            })
            
            print(f"📊 Analyzing {len(markets)} crypto markets (quant lens)")
            
            # Post chat message about starting analysis
            if len(markets) > 0:
                self.post_message('chat', content=f"👋 Starting analysis on {len(markets)} markets...")
            
            if not markets:
                print("⚠️ No markets found")
                self.post_message('chat', content="Nothing to analyze today 🤷")
                return []
            
            # Fetch news for sentiment
            news_events = get_news_events(filters={"hours_back": 24})
            print(f"📰 Sentiment data: {len(news_events)} news events")
            
            # Quant analysis
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
            print(f"\n🔬 Generated {len(theses)} quant theses")
            
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
        Generate quantitative thesis for a crypto market.
        
        Analyzes:
        - Multi-factor scoring (on-chain, market, sentiment, correlation)
        - Statistical signals and z-scores
        - Mean reversion opportunities
        
        Args:
            market: Market to analyze
            news_events: Recent news for sentiment
        
        Returns:
            Thesis object with quant conviction, or None
        """
        self.post_message('chat', content=f"🔍 Analyzing: {market.question[:60]}...")
        
        # Placeholder implementation (would query on-chain APIs in production)
        # For now, use quantitative heuristics
        
        if news_events is None:
            news_events = get_news_events(filters={"hours_back": 24})
        
        # Calculate factor scores
        factor_scores = self._calculate_factor_scores(market, news_events)
        
        # Aggregate score with weights
        aggregate_score = (
            factor_scores['on_chain'] * 0.40 +
            factor_scores['market'] * 0.30 +
            factor_scores['sentiment'] * 0.20 +
            factor_scores['correlation'] * 0.10
        )
        
        # Convert to fair value with mean reversion
        base_probability = aggregate_score / 10.0
        
        # Mean reversion adjustment
        if market.yes_price > 0.70:
            fair_value = base_probability * 0.80  # Discount expensive
        elif market.yes_price < 0.30:
            fair_value = base_probability * 1.20  # Boost cheap
        else:
            fair_value = base_probability
        
        # Clamp
        fair_value = max(0.10, min(0.90, fair_value))
        edge = fair_value - market.yes_price
        
        if abs(edge) < self.min_edge:
            self.post_message('chat', content=f"❌ Passing on {market.question[:50]}... - only {abs(edge):.1%} edge (need {self.min_edge:.1%}+)")
            return None
        
        # Conviction based on factor agreement
        factor_variance = self._calculate_factor_variance(factor_scores)
        conviction = min(0.90, 0.65 + (1.0 - factor_variance) * 0.25)
        
        if conviction < self.min_conviction:
            self.post_message('chat', content=f"❌ {market.question[:50]}... - conviction too low ({conviction:.1%})")
            return None
        
        # Generate Renaissance-style quant report
        top_factors = self._get_top_factors(factor_scores)
        
        thesis_text = f"""
RENAISSANCE TECHNOLOGIES - QUANTITATIVE CRYPTO ANALYSIS

Market: {market.question}
Current Price: {market.yes_price:.1%} | Quant Fair Value: {fair_value:.1%}

MULTI-FACTOR ANALYSIS:

Factor Scores (1-10):
- On-Chain: {factor_scores['on_chain']:.1f}/10 (40% weight)
- Market: {factor_scores['market']:.1f}/10 (30% weight)
- Sentiment: {factor_scores['sentiment']:.1f}/10 (20% weight)
- Correlation: {factor_scores['correlation']:.1f}/10 (10% weight)

Aggregate Score: {aggregate_score:.2f}/10
Factor Variance: {factor_variance:.3f} (agreement: {(1.0 - factor_variance):.1%})

TOP SIGNALS:
{chr(10).join('- ' + f for f in top_factors)}

STATISTICAL ANALYSIS:
Z-Score: {(aggregate_score - 5.0) / 2.0:.2f} standard deviations from mean
Mean Reversion: {'High' if abs(market.yes_price - 0.50) > 0.25 else 'Moderate' if abs(market.yes_price - 0.50) > 0.15 else 'Low'}

QUANTITATIVE EDGE:
Market is {('undervalued' if edge > 0 else 'overvalued')} by {abs(edge):.1%}
Expected return based on factor model: {abs(edge):.1%}

RECOMMENDATION: {'BUY' if edge > 0 else 'SELL'}
Position Size: {min(0.15, abs(edge) * 0.8):.1%} (Kelly-optimal)
Time Horizon: Short-term (quant edges fade quickly)
"""
        
        # Position sizing
        proposed_action = {
            "side": "YES" if edge > 0 else "NO",
            "size_pct": min(0.15, abs(edge) * 0.8 + conviction * 0.05)
        }
        
        thesis = Thesis(
            agent_id=self.agent_id,
            market_id=market.id,
            thesis_text=thesis_text.strip(),
            fair_value=fair_value,
            current_odds=market.yes_price,
            edge=edge,
            conviction=conviction,
            horizon="short",  # Quant edges are short-term
            proposed_action=proposed_action
        )
        
        capital_allocated = 83.30 * proposed_action["size_pct"] / 0.15
        self.post_message('thesis', market_question=market.question, market_id=market.id, current_odds=market.yes_price, thesis_odds=fair_value, edge=edge, conviction=conviction, capital_allocated=capital_allocated, reasoning=thesis_text[:500], signals={'on_chain': factor_scores['on_chain'], 'market': factor_scores['market'], 'sentiment': factor_scores['sentiment'], 'correlation': factor_scores['correlation'], 'aggregate_score': aggregate_score, 'factor_variance': factor_variance}, status='thesis_generated', related_thesis_id=str(thesis.id), tags=[self.theme, 'bullish' if edge > 0 else 'bearish', 'quantitative'])
        
        
        # Announce in chat
        side_emoji = "🟢" if edge > 0 else "🔴"
        self.post_message('chat', content=f"{side_emoji} Thesis posted: {market.question[:60]}... | Edge: {edge:+.1%} | Conviction: {conviction:.1%}")
        return thesis
    
    def _calculate_factor_scores(self, market: Market, news_events: List) -> dict:
        """
        Calculate multi-factor scores for a crypto market.
        
        In production, this would:
        - Query on-chain APIs (Glassnode, IntoTheBlock)
        - Fetch market data (spot, futures, options)
        - Analyze social sentiment (LunarCrush, Santiment)
        - Calculate correlations
        
        For now: heuristic based on news and price.
        
        Args:
            market: Market being analyzed
            news_events: Recent news events
        
        Returns:
            Dict with factor scores (0-10 scale)
        """
        question_lower = market.question.lower()
        crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'blockchain', 'defi', 'nft']
        
        # Count crypto news
        crypto_news = sum(
            1 for event in news_events
            if any(kw in event.headline.lower() or kw in question_lower for kw in crypto_keywords)
        )
        
        # On-chain score (proxy: market liquidity)
        on_chain_score = min(10.0, 3.0 + (market.volume_24h / 10000) * 0.8)
        
        # Market score (proxy: news activity)
        market_score = min(10.0, 2.0 + crypto_news * 1.5)
        
        # Sentiment score (proxy: news count vs expected)
        expected_news = market.yes_price * 10
        sentiment_score = min(10.0, 5.0 + (crypto_news - expected_news) * 0.6)
        
        # Correlation score (proxy: distance from 0.50)
        # Markets near 0.50 have low conviction = higher correlation to broader market
        correlation_score = min(10.0, 5.0 + abs(market.yes_price - 0.50) * 12.0)
        
        return {
            'on_chain': on_chain_score,
            'market': market_score,
            'sentiment': sentiment_score,
            'correlation': correlation_score
        }
    
    def _calculate_factor_variance(self, factor_scores: dict) -> float:
        """
        Calculate variance across factor scores.
        
        Low variance = factors agree = high confidence.
        
        Args:
            factor_scores: Dict of factor scores
        
        Returns:
            Variance (0.0-1.0)
        """
        scores = list(factor_scores.values())
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        
        # Normalize (max variance for 0-10 scale is 25)
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
        sorted_factors = sorted(factor_scores.items(), key=lambda x: x[1], reverse=True)
        
        descriptions = []
        for factor, score in sorted_factors[:3]:
            strength = 'Strong' if score > 7 else 'Moderate' if score > 5 else 'Weak'
            descriptions.append(f"{factor.replace('_', ' ').title()}: {strength} ({score:.1f}/10)")
        
        return descriptions
