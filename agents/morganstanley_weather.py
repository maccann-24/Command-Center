"""
BASED MONEY - Morgan Stanley Weather Agent
Technical pattern analysis of weather prediction markets
"""

from typing import List, Optional
from datetime import datetime
import sys
sys.path.insert(0, '..')

from agents.base import BaseAgent
from models import Thesis, Market
from database import get_markets, get_news_events


class MorganStanleyWeatherAgent(BaseAgent):
    """
    Morgan Stanley-style technical analyst for weather prediction markets.
    
    Applies technical analysis framework to evaluate weather prediction
    market odds using temperature trends, moving averages, and patterns.
    
    System Prompt (Institutional Analysis Framework):
    ================================================
    
    You are a senior meteorological analyst at Morgan Stanley analyzing
    weather prediction markets using technical pattern recognition.
    
    For each weather market, systematically assess:
    
    1. Temperature Trend Analysis:
       - Short-term trend: 7-day temperature trajectory
       - Medium-term trend: 30-day temperature trajectory
       - Long-term trend: Seasonal deviation from normal
       - Trend strength: Strong, moderate, or weak momentum?
       - Inflection points: Is the trend accelerating or reversing?
    
    2. Moving Averages:
       - 7-day MA: Short-term average temperature
       - 30-day MA: Medium-term average temperature
       - Historical MA: 10-year average for this date
       - Crossovers: Current above or below averages?
       - Divergence: Temperature vs. MA spread widening or narrowing?
    
    3. Momentum Indicators:
       - Rate of change: How fast is temperature changing?
       - Acceleration: Is the change speeding up or slowing down?
       - Persistence: How long has current pattern lasted?
       - Exhaustion signals: Extreme temps that can't persist?
    
    4. Pattern Recognition:
       - Heatwave buildup: Gradual warming over 7-14 days
       - Cold snap precursors: Rapid cooling patterns
       - Ridge patterns: High-pressure systems bringing warmth
       - Trough patterns: Low-pressure systems bringing cold
       - Blocking patterns: Persistent weather regimes
    
    5. Technical Setups:
       - Breakout: Temperature breaking above/below range
       - Breakdown: Fall below support level (historical norm)
       - Consolidation: Temperature range-bound
       - Reversal patterns: Trend change signals
       - Continuation patterns: Trend expected to persist
    
    Output Format:
    - Technical setup: Bullish (warm), bearish (cold), or neutral
    - Key levels: Historical average, recent high/low
    - Trend direction: Up, down, or sideways
    - Momentum: Accelerating, steady, or decelerating
    - Pattern: Identified weather pattern (heatwave, cold snap, normal)
    - Trade setup: Entry, confidence, time horizon
    """
    
    def __init__(self):
        """Initialize Morgan Stanley Weather Agent."""
        super().__init__()
        self.agent_id = "morganstanley_weather"
        self.theme = "weather"
        self.min_volume = 20000.0  # $20K minimum
        self.min_edge = 0.04  # 4% minimum edge
        self.min_conviction = 0.60  # 60% minimum conviction
    
    @property
    def mandate(self) -> str:
        """Agent's mandate/focus area."""
        return "Technical meteorological pattern analysis: temperature trends, moving averages, momentum, pattern recognition"
    
    def update_theses(self) -> List[Thesis]:
        """
        Generate theses for weather markets using technical analysis.
        
        Workflow:
        1. Fetch weather markets
        2. Analyze temperature trends and patterns
        3. Calculate technical indicators
        4. Generate technical weather theses
        
        Returns:
            List of Thesis objects (edge > 4%, conviction > 60%)
        """
        print(f"\n{'='*60}")
        print(f"🌤️ MORGAN STANLEY WEATHER AGENT - Technical Analysis")
        print(f"{'='*60}")
        
        try:
            # Fetch weather markets
            markets = get_markets(filters={
                "category": "weather",
                "min_volume": self.min_volume,
                "resolved": False
            })
            
            print(f"📊 Analyzing {len(markets)} weather markets (technical lens)")
            
            # Post chat message about starting analysis
            if len(markets) > 0:
                self.post_message('chat', content=f"👋 Starting analysis on {len(markets)} markets...")
            
            if not markets:
                print("⚠️ No markets found")
                self.post_message('chat', content="Nothing to analyze today 🤷")
                return []
            
            # Fetch news for weather pattern context
            news_events = get_news_events(filters={"hours_back": 24})
            print(f"📰 Pattern context: {len(news_events)} news events")
            
            # Technical analysis
            theses = []
            for market in markets:
                try:
                    thesis = self.generate_thesis(market, news_events)
                    
                    if thesis:  # generate_thesis handles rejections internally
                        theses.append(thesis)
                        print(f"✅ {market.question[:45]}... | Edge: {thesis.edge:.1%}, Conv: {thesis.conviction:.1%}")
                
                except Exception as e:
                    print(f"⚠️ Error analyzing {market.id}: {e}")
                    continue
            
            self._theses_cache = theses
            print(f"\n🌤️ Generated {len(theses)} technical weather theses")
            
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
        Generate technical weather thesis for a weather market.
        
        Analyzes:
        - Temperature trend direction
        - Moving average positioning
        - Momentum and acceleration
        - Weather pattern recognition
        
        Args:
            market: Market to analyze
            news_events: Recent news for pattern context
        
        Returns:
            Thesis object with technical conviction, or None
        """
        # 1️⃣ POST: Starting analysis
        self.post_message(
            'analyzing',
            market_question=market.question,
            market_id=market.id,
            current_odds=market.yes_price,
            status='analyzing'
        )
        
        # Placeholder implementation (would use weather time-series data in production)
        # For now, use technical heuristics
        
        if news_events is None:
            news_events = get_news_events(filters={"hours_back": 24})
        
        # Calculate technical indicators
        technical_analysis = self._calculate_technical_indicators(market, news_events)
        
        # Determine technical setup
        fair_value = self._calculate_technical_fair_value(market, technical_analysis)
        edge = fair_value - market.yes_price
        
        # 2️⃣ POST: Rejected (insufficient edge)
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
        
        # Conviction based on pattern clarity
        pattern_strength = technical_analysis['pattern_strength']
        conviction = min(0.85, 0.60 + pattern_strength * 0.25)
        
        # 3️⃣ POST: Rejected (low conviction)
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
        
        # Generate Morgan Stanley-style technical weather note
        thesis_text = f"""
MORGAN STANLEY METEOROLOGICAL RESEARCH - TECHNICAL ANALYSIS

Market: {market.question}
Current Price: {market.yes_price:.1%} | Technical Target: {fair_value:.1%}

TECHNICAL ANALYSIS:

Trend: {technical_analysis['trend']}
Momentum: {technical_analysis['momentum']}
Pattern: {technical_analysis['pattern']}

TECHNICAL INDICATORS:
- Temperature vs. MA: {'Above' if market.yes_price > 0.50 else 'Below'} historical average
- Trend Strength: {pattern_strength:.0%}
- Pattern Recognition: {technical_analysis['pattern']}

TECHNICAL SETUP:
The market is showing {('bullish' if edge > 0 else 'bearish')} weather pattern signals.
Current odds are {abs(edge):.1%} {'below' if edge > 0 else 'above'} technical fair value.

WEATHER PATTERN ANALYSIS:
{technical_analysis['pattern_description']}

TRADE RECOMMENDATION:
Entry: {market.yes_price:.1%}
Target: {fair_value:.1%}
Confidence: {conviction:.0%}

TIME HORIZON: {'3-7 days' if abs(edge) > 0.08 else '7-14 days'} (weather forecast reliability window)
"""
        
        # Position sizing based on pattern conviction
        proposed_action = {
            "side": "YES" if edge > 0 else "NO",
            "size_pct": min(0.10, abs(edge) * 0.6 + conviction * 0.04)
        }
        
        thesis = Thesis(
            agent_id=self.agent_id,
            market_id=market.id,
            thesis_text=thesis_text.strip(),
            fair_value=fair_value,
            current_odds=market.yes_price,
            edge=edge,
            conviction=conviction,
            horizon="short",  # Weather technical analysis is short-term
            proposed_action=proposed_action
        )
        
        # 4️⃣ POST: Thesis generated
        capital_allocated = 83.30 * proposed_action["size_pct"] / 0.15
        self.post_message(
            'thesis',
            market_question=market.question,
            market_id=market.id,
            current_odds=market.yes_price,
            thesis_odds=fair_value,
            edge=edge,
            conviction=conviction,
            capital_allocated=capital_allocated,
            reasoning=thesis_text[:500],
            signals={
                'trend': technical_analysis['trend'],
                'momentum': technical_analysis['momentum'],
                'pattern': technical_analysis['pattern'],
                'pattern_strength': pattern_strength
            },
            status='thesis_generated',
            related_thesis_id=str(thesis.id),
            tags=[
                self.theme,
                'bullish' if edge > 0 else 'bearish',
                'technical',
                'pattern_analysis'
            ]
        )
        
        return thesis
    
    def _calculate_technical_indicators(self, market: Market, news_events: List) -> dict:
        """
        Calculate technical weather indicators.
        
        In production, this would:
        - Query historical temperature data
        - Calculate actual moving averages
        - Detect weather patterns from time-series
        - Analyze temperature momentum
        
        For now: heuristic based on news and price.
        
        Args:
            market: Market being analyzed
            news_events: Recent news events
        
        Returns:
            Dict with technical indicators
        """
        question_lower = market.question.lower()
        
        # Detect weather event types
        is_hot_event = any(kw in question_lower for kw in ['heat', 'hot', 'warm', 'high temperature'])
        is_cold_event = any(kw in question_lower for kw in ['cold', 'freeze', 'snow', 'ice'])
        is_precip_event = any(kw in question_lower for kw in ['rain', 'snow', 'flood', 'drought'])
        
        # Count weather news
        weather_keywords = ['temperature', 'weather', 'forecast', 'climate']
        weather_news_count = sum(
            1 for event in news_events
            if any(kw in event.headline.lower() for kw in weather_keywords)
        )
        
        # Trend determination
        if market.yes_price > 0.65:
            if is_hot_event:
                trend = "Strong warming trend"
            elif is_cold_event:
                trend = "Strong cooling trend"
            else:
                trend = "Uptrend (event likely)"
        elif market.yes_price < 0.35:
            if is_hot_event:
                trend = "Cooling trend (heat unlikely)"
            elif is_cold_event:
                trend = "Warming trend (cold unlikely)"
            else:
                trend = "Downtrend (event unlikely)"
        else:
            trend = "Neutral (range-bound)"
        
        # Momentum assessment
        if weather_news_count > 5:
            momentum = "Strong (high media coverage)"
        elif weather_news_count > 2:
            momentum = "Moderate"
        else:
            momentum = "Weak (low attention)"
        
        # Pattern recognition
        if is_hot_event and market.yes_price > 0.60:
            pattern = "Heatwave buildup pattern"
            pattern_description = "Gradual warming pattern building, typical precursor to heatwave."
        elif is_cold_event and market.yes_price > 0.60:
            pattern = "Cold snap development"
            pattern_description = "Arctic air mass approaching, cold snap pattern forming."
        elif is_precip_event and market.yes_price > 0.60:
            pattern = "Precipitation system"
            pattern_description = "Moisture-laden system tracking, precipitation likely."
        elif market.yes_price < 0.40:
            pattern = "Normal weather pattern"
            pattern_description = "Weather patterns favor normal conditions, extreme event unlikely."
        else:
            pattern = "Consolidation"
            pattern_description = "Weather pattern unclear, market in consolidation range."
        
        # Pattern strength (how clear is the signal)
        if weather_news_count > 4:
            pattern_strength = 0.75
        elif weather_news_count > 2:
            pattern_strength = 0.50
        else:
            pattern_strength = 0.25
        
        return {
            'trend': trend,
            'momentum': momentum,
            'pattern': pattern,
            'pattern_description': pattern_description,
            'pattern_strength': pattern_strength
        }
    
    def _calculate_technical_fair_value(self, market: Market, technical_analysis: dict) -> float:
        """
        Calculate fair value from technical analysis.
        
        In production: Use temperature trends and patterns.
        For now: Adjust based on technical signals.
        
        Args:
            market: Market being valued
            technical_analysis: Technical analysis results
        
        Returns:
            Fair value probability (0.0-1.0)
        """
        pattern_strength = technical_analysis['pattern_strength']
        
        # Pattern-based adjustment
        if 'buildup' in technical_analysis['pattern'].lower() or 'development' in technical_analysis['pattern'].lower():
            # Strong pattern = adjust toward continuation
            pattern_adjustment = 0.08 * pattern_strength
        elif 'normal' in technical_analysis['pattern'].lower():
            # Normal pattern = mean reversion
            pattern_adjustment = (0.50 - market.yes_price) * 0.12
        else:
            # Weak pattern = small adjustment
            pattern_adjustment = (0.50 - market.yes_price) * 0.08
        
        # Apply adjustment
        fair_value = market.yes_price + pattern_adjustment
        
        # Clamp to valid range
        fair_value = max(0.10, min(0.90, fair_value))
        
        return fair_value
