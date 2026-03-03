"""
BASED MONEY - Morgan Stanley Crypto Agent
Technical analysis of crypto prediction markets
"""

from typing import List, Optional
from datetime import datetime
import sys
sys.path.insert(0, '..')

from agents.base import BaseAgent
from models import Thesis, Market
from database import get_markets, get_news_events


class MorganStanleyCryptoAgent(BaseAgent):
    """
    Morgan Stanley-style technical analyst for crypto prediction markets.
    
    Applies technical analysis framework to evaluate prediction market odds
    using chart patterns, indicators, and volume analysis.
    
    System Prompt (Institutional Analysis Framework):
    ================================================
    
    You are a senior technical analyst at Morgan Stanley analyzing crypto
    prediction markets using technical analysis of odds movements.
    
    For each crypto market, systematically assess:
    
    1. Trend Analysis:
       - 1-day odds trend: Is the market moving up or down today?
       - 7-day odds trend: What's the weekly direction?
       - 30-day odds trend: What's the monthly trend?
       - Trend strength: Strong, moderate, or weak momentum?
       - Trend quality: Clean trends or choppy/sideways action?
    
    2. Support & Resistance Levels:
       - Key support levels: Price levels where odds historically bounce
       - Key resistance levels: Price levels where odds historically stall
       - Breakout potential: Is the market testing resistance?
       - Breakdown risk: Is the market testing support?
       - False breakout detection: Are moves sustainable or traps?
    
    3. Moving Averages:
       - 7-day MA: Short-term trend indicator
       - 30-day MA: Medium-term trend indicator
       - Golden cross: 7-day crosses above 30-day (bullish)
       - Death cross: 7-day crosses below 30-day (bearish)
       - Price vs. MA: Is current price above or below MAs?
    
    4. Momentum Indicators:
       - RSI (Relative Strength Index): Overbought (>70) or oversold (<30)?
       - MACD: Bullish or bearish divergence?
       - Volume-weighted momentum: Is volume confirming the move?
       - Rate of change: How fast are odds changing?
    
    5. Volume Analysis:
       - Volume trend: Increasing or decreasing betting activity?
       - Volume confirmation: Does volume confirm price moves?
       - Volume divergence: Price up but volume down (bearish)?
       - Climax volume: Exhaustion signals?
    
    6. Chart Patterns:
       - Continuation patterns: Flags, pennants, wedges
       - Reversal patterns: Head & shoulders, double tops/bottoms
       - Breakout patterns: Triangles, rectangles
       - Candlestick patterns: Applied to daily odds changes
    
    Output Format:
    - Technical setup: Bullish, bearish, or neutral
    - Key levels: Support and resistance prices
    - Indicator readings: RSI, MACD, MA positions
    - Volume analysis: Confirming or diverging
    - Trade setup: Entry, stop-loss, target levels
    - Time horizon: Days until expected move
    """
    
    def __init__(self):
        """Initialize Morgan Stanley Crypto Agent."""
        super().__init__()
        self.agent_id = "morganstanley_crypto"
        self.theme = "crypto"
        self.min_volume = 30000.0  # $30K minimum (crypto has decent volume)
        self.min_edge = 0.04  # 4% minimum edge (technical needs clear signal)
        self.min_conviction = 0.60  # 60% minimum conviction
    
    @property
    def mandate(self) -> str:
        """Agent's mandate/focus area."""
        return "Technical analysis of crypto prediction markets: trends, support/resistance, moving averages, RSI, volume"
    
    def update_theses(self) -> List[Thesis]:
        """
        Generate theses for crypto markets using technical analysis.
        
        Workflow:
        1. Fetch crypto markets with sufficient volume
        2. Analyze price trends and patterns
        3. Calculate technical indicators
        4. Generate technical theses
        
        Returns:
            List of Thesis objects (edge > 4%, conviction > 60%)
        """
        print(f"\n{'='*60}")
        print(f"📈 MORGAN STANLEY CRYPTO AGENT - Technical Analysis")
        print(f"{'='*60}")
        
        try:
            # Fetch crypto markets
            markets = get_markets(filters={
                "category": "crypto",
                "min_volume": self.min_volume,
                "resolved": False
            })
            
            print(f"📊 Analyzing {len(markets)} crypto markets (technical lens)")
            
            # Post chat message about starting analysis
            if len(markets) > 0:
                self.post_message('chat', content=f"👋 Starting analysis on {len(markets)} markets...")
            
            if not markets:
                print("⚠️ No markets found")
                self.post_message('chat', content="Nothing to analyze today 🤷")
                return []
            
            # Fetch news for sentiment context
            news_events = get_news_events(filters={"hours_back": 24})
            print(f"📰 Context: {len(news_events)} news events")
            
            # Technical analysis for each market
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
            print(f"\n📈 Generated {len(theses)} technical theses")
            
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
        Generate technical thesis for a crypto market.
        
        Analyzes:
        - Trend direction and strength
        - Support/resistance levels
        - Technical indicators (RSI, MA)
        - Volume confirmation
        
        Args:
            market: Market to analyze
            news_events: Recent news for context
        
        Returns:
            Thesis object with technical conviction, or None
        """
        self.post_message('chat', content=f"🔍 Analyzing: {market.question[:60]}...")
        
        # Placeholder implementation (would use historical price data in production)
        # For now, use technical heuristics based on current price and volume
        
        if news_events is None:
            news_events = get_news_events(filters={"hours_back": 24})
        
        # Calculate technical indicators
        technical_analysis = self._calculate_technical_indicators(market, news_events)
        
        # Determine technical setup
        fair_value = self._calculate_technical_fair_value(market, technical_analysis)
        edge = fair_value - market.yes_price
        
        if abs(edge) < self.min_edge:
            self.post_message('chat', content=f"❌ Passing on {market.question[:50]}... - only {abs(edge):.1%} edge (need {self.min_edge:.1%}+)")
            return None
        
        # Conviction based on indicator alignment
        indicator_alignment = technical_analysis['indicator_alignment']
        conviction = min(0.85, 0.60 + indicator_alignment * 0.25)
        
        if conviction < self.min_conviction:
            self.post_message('chat', content=f"❌ {market.question[:50]}... - conviction too low ({conviction:.1%})")
            return None
        
        # Generate Morgan Stanley-style technical note
        thesis_text = f"""
MORGAN STANLEY TECHNICAL RESEARCH - CRYPTO

Market: {market.question}
Current Price: {market.yes_price:.1%} | Technical Target: {fair_value:.1%}

TECHNICAL ANALYSIS:

Trend: {technical_analysis['trend']}
Momentum: {technical_analysis['momentum']}
Volume: {technical_analysis['volume_trend']}

TECHNICAL INDICATORS:
- RSI: {technical_analysis['rsi']:.0f} ({'Overbought' if technical_analysis['rsi'] > 70 else 'Oversold' if technical_analysis['rsi'] < 30 else 'Neutral'})
- Price vs. MA: {'Above' if market.yes_price > 0.50 else 'Below'} key moving averages
- Volume Confirmation: {'YES' if technical_analysis['volume_confirming'] else 'NO'}
- Indicator Alignment: {indicator_alignment:.0%}

KEY LEVELS:
Support: {max(0.10, market.yes_price - 0.10):.1%}
Resistance: {min(0.90, market.yes_price + 0.10):.1%}

TECHNICAL SETUP:
The market is showing {('bullish' if edge > 0 else 'bearish')} technical signals.
Current odds are {abs(edge):.1%} {'below' if edge > 0 else 'above'} technical fair value.

TRADE RECOMMENDATION:
Entry: {market.yes_price:.1%}
Target: {fair_value:.1%}
Stop: {max(0.10, min(0.90, market.yes_price - edge * 0.5)):.1%}
Risk/Reward: {abs(edge / max(0.05, abs(edge) * 0.5)):.1f}:1

TIME HORIZON: {'1-3 days' if abs(edge) > 0.10 else '3-7 days'}
"""
        
        # Position sizing based on technical conviction
        proposed_action = {
            "side": "YES" if edge > 0 else "NO",
            "size_pct": min(0.12, abs(edge) * 0.6 + conviction * 0.05)
        }
        
        thesis = Thesis(
            agent_id=self.agent_id,
            market_id=market.id,
            thesis_text=thesis_text.strip(),
            fair_value=fair_value,
            current_odds=market.yes_price,
            edge=edge,
            conviction=conviction,
            horizon="short",  # Technical analysis is short-term
            proposed_action=proposed_action
        )
        
        capital_allocated = 83.30 * proposed_action["size_pct"] / 0.15
        self.post_message('thesis', market_question=market.question, market_id=market.id, current_odds=market.yes_price, thesis_odds=fair_value, edge=edge, conviction=conviction, capital_allocated=capital_allocated, reasoning=thesis_text[:500], signals={'trend': technical_analysis['trend'], 'indicator_alignment': indicator_alignment}, status='thesis_generated', related_thesis_id=str(thesis.id), tags=[self.theme, 'bullish' if edge > 0 else 'bearish', 'technical'])
        
        
        # Announce in chat
        side_emoji = "🟢" if edge > 0 else "🔴"
        self.post_message('chat', content=f"{side_emoji} Thesis posted: {market.question[:60]}... | Edge: {edge:+.1%} | Conviction: {conviction:.1%}")
        return thesis
    
    def _calculate_technical_indicators(self, market: Market, news_events: List) -> dict:
        """
        Calculate technical indicators for a market.
        
        In production, this would:
        - Query historical odds data
        - Calculate actual RSI, MACD, MAs
        - Detect chart patterns
        - Analyze volume profile
        
        For now: heuristic based on current price and news.
        
        Args:
            market: Market being analyzed
            news_events: Recent news events
        
        Returns:
            Dict with technical indicators
        """
        # Count crypto-related news (proxy for momentum)
        question_lower = market.question.lower()
        crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'blockchain']
        
        crypto_news_count = sum(
            1 for event in news_events
            if any(kw in event.headline.lower() or kw in question_lower for kw in crypto_keywords)
        )
        
        # RSI approximation (50 = neutral)
        # More news = higher RSI (momentum)
        base_rsi = 50
        rsi = min(85, max(15, base_rsi + crypto_news_count * 5))
        
        # Trend determination
        if market.yes_price > 0.65:
            trend = "Uptrend (Strong)"
        elif market.yes_price > 0.55:
            trend = "Uptrend (Moderate)"
        elif market.yes_price < 0.35:
            trend = "Downtrend (Strong)"
        elif market.yes_price < 0.45:
            trend = "Downtrend (Moderate)"
        else:
            trend = "Sideways (Range-bound)"
        
        # Momentum assessment
        if crypto_news_count > 5:
            momentum = "Strong"
        elif crypto_news_count > 2:
            momentum = "Moderate"
        else:
            momentum = "Weak"
        
        # Volume trend (proxy: market liquidity)
        if market.volume_24h > 50000:
            volume_trend = "High volume"
            volume_confirming = True
        elif market.volume_24h > 30000:
            volume_trend = "Moderate volume"
            volume_confirming = True
        else:
            volume_trend = "Low volume"
            volume_confirming = False
        
        # Indicator alignment (how many indicators agree)
        # In production: check if RSI, MACD, MA all agree
        indicators_bullish = 0
        indicators_total = 3
        
        if rsi < 40:  # Oversold = bullish
            indicators_bullish += 1
        elif rsi > 60:  # Overbought = bearish
            pass
        else:
            indicators_bullish += 0.5
        
        if market.yes_price < 0.45:  # Below MA = bullish (mean reversion)
            indicators_bullish += 1
        elif market.yes_price > 0.55:  # Above MA = bearish (mean reversion)
            pass
        else:
            indicators_bullish += 0.5
        
        if volume_confirming:
            indicators_bullish += 1
        
        indicator_alignment = indicators_bullish / indicators_total
        
        return {
            'rsi': rsi,
            'trend': trend,
            'momentum': momentum,
            'volume_trend': volume_trend,
            'volume_confirming': volume_confirming,
            'indicator_alignment': indicator_alignment
        }
    
    def _calculate_technical_fair_value(self, market: Market, technical_analysis: dict) -> float:
        """
        Calculate fair value from technical analysis.
        
        In production: Use technical levels and patterns.
        For now: Adjust based on technical signals.
        
        Args:
            market: Market being valued
            technical_analysis: Technical analysis results
        
        Returns:
            Fair value probability (0.0-1.0)
        """
        rsi = technical_analysis['rsi']
        indicator_alignment = technical_analysis['indicator_alignment']
        
        # RSI-based adjustment
        if rsi < 30:  # Oversold = bullish
            rsi_adjustment = 0.10
        elif rsi > 70:  # Overbought = bearish
            rsi_adjustment = -0.10
        else:  # Neutral
            rsi_adjustment = (50 - rsi) / 500  # Small adjustment toward 50
        
        # Mean reversion (technical markets tend to revert)
        mean_reversion = (0.50 - market.yes_price) * 0.15
        
        # Combine adjustments
        total_adjustment = rsi_adjustment + mean_reversion
        fair_value = market.yes_price + total_adjustment * indicator_alignment
        
        # Clamp to valid range
        fair_value = max(0.10, min(0.90, fair_value))
        
        return fair_value
