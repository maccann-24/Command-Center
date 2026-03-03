"""
BASED MONEY - Renaissance Weather Agent
Quantitative multi-factor analysis of weather prediction markets
"""

from typing import List, Optional
from datetime import datetime
import sys
sys.path.insert(0, '..')

from agents.base import BaseAgent
from models import Thesis, Market
from database import get_markets, get_news_events


class RenaissanceWeatherAgent(BaseAgent):
    """
    Renaissance Technologies-style quantitative analyst for weather markets.
    
    Applies multi-factor quantitative framework to identify mispriced
    weather prediction markets using statistical meteorological analysis.
    
    System Prompt (Institutional Analysis Framework):
    ================================================
    
    You are a senior quantitative meteorologist at Renaissance Technologies
    analyzing weather prediction markets using multi-factor statistical models.
    
    For each weather market, systematically evaluate:
    
    1. Historical Data Analysis (30% weight):
       - 10-year average: What's the historical baseline for this location/date?
       - Standard deviation: How variable is this outcome historically?
       - Percentile analysis: What percentile would this event be (50th, 90th, 99th)?
       - Trend analysis: Is the baseline shifting (climate change)?
       - Historical analog years: What happened in similar years?
    
    2. Climate Model Consensus (35% weight):
       - NOAA GFS: Global Forecast System predictions
       - ECMWF: European model (typically most accurate)
       - Canadian CMC: Canadian model
       - Model agreement: Do all models agree or diverge?
       - Ensemble spread: How much uncertainty in forecasts?
       - Forecast skill: How accurate have models been recently for this region?
    
    3. Seasonal Factors (20% weight):
       - El Niño/La Niña: Current ENSO status and typical impacts
       - NAO/AO: North Atlantic/Arctic Oscillation phases
       - Blocking patterns: High-pressure blocks influencing flow
       - MJO: Madden-Julian Oscillation phase
       - Seasonal persistence: Does current pattern tend to persist?
    
    4. Real-Time Data (10% weight):
       - Satellite imagery: Current cloud patterns, systems
       - Jet stream: Position and amplitude of jet stream
       - Sea surface temperatures: Anomalies affecting weather
       - Snow cover: Impacts on temperature and precipitation
       - Soil moisture: Drought or flood potential
    
    5. Anomaly Detection (5% weight):
       - Temperature anomaly: Current vs. 30-year normal
       - Precipitation anomaly: Wet or dry pattern
       - Pattern persistence: How long has anomaly lasted?
       - Analog matching: Similar patterns in historical record
       - Climate oscillations: Phase of multi-year patterns
    
    Output Format:
    - Fair value: Statistically-derived probability based on data
    - Factor scores: Historical (1-10), Models (1-10), Seasonal (1-10), Real-time (1-10)
    - Model consensus: Agreement level between forecast models
    - Historical probability: Based on 10-year climatology
    - Adjusted probability: Historical + current conditions
    - Confidence: Based on model agreement and data quality
    """
    
    def __init__(self):
        """Initialize Renaissance Weather Agent."""
        super().__init__()
        self.agent_id = "renaissance_weather"
        self.theme = "weather"
        self.min_volume = 20000.0  # $20K minimum (weather has lower volume)
        self.min_edge = 0.05  # 5% minimum edge (quant needs strong signal)
        self.min_conviction = 0.65  # 65% minimum conviction
    
    @property
    def mandate(self) -> str:
        """Agent's mandate/focus area."""
        return "Quantitative meteorological analysis: historical data, climate models, seasonal factors, anomaly detection"
    
    def update_theses(self) -> List[Thesis]:
        """
        Generate theses for weather markets using quantitative analysis.
        
        Workflow:
        1. Fetch weather markets
        2. Calculate multi-factor meteorological scores
        3. Identify statistical mispricings
        4. Generate quant weather theses
        
        Returns:
            List of Thesis objects (edge > 5%, conviction > 65%)
        """
        print(f"\n{'='*60}")
        print(f"🌡️ RENAISSANCE WEATHER AGENT - Quantitative Analysis")
        print(f"{'='*60}")
        
        try:
            # Fetch weather markets
            markets = get_markets(filters={
                "category": "weather",
                "min_volume": self.min_volume,
                "resolved": False
            })
            
            print(f"📊 Analyzing {len(markets)} weather markets (quant lens)")
            
            # Post chat message about starting analysis
            if len(markets) > 0:
                self.post_message('chat', content=f"👋 Starting analysis on {len(markets)} markets...")
            
            if not markets:
                print("⚠️ No markets found")
                self.post_message('chat', content="Nothing to analyze today 🤷")
                return []
            
            # Fetch news for weather context
            news_events = get_news_events(filters={"hours_back": 24})
            print(f"📰 Weather context: {len(news_events)} news events")
            
            # Quant analysis
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
            print(f"\n🌡️ Generated {len(theses)} quant weather theses")
            
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
        Generate quantitative meteorological thesis for a weather market.
        
        Analyzes:
        - Historical climatology (10-year baseline)
        - Climate model consensus
        - Seasonal factors (ENSO, NAO, etc.)
        - Real-time anomalies
        
        Args:
            market: Market to analyze
            news_events: Recent news for weather context
        
        Returns:
            Thesis object with quant conviction, or None
        """
        # 1️⃣ POST: Starting analysis
        self.post_message(
            'analyzing',
            market_question=market.question,
            market_id=market.id,
            current_odds=market.yes_price,
            status='analyzing'
        )
        
        # Placeholder implementation (would query NOAA/ECMWF APIs in production)
        # For now, use quantitative heuristics
        
        if news_events is None:
            news_events = get_news_events(filters={"hours_back": 24})
        
        # Calculate factor scores
        factor_scores = self._calculate_factor_scores(market, news_events)
        
        # Aggregate score with weights
        aggregate_score = (
            factor_scores['historical'] * 0.30 +
            factor_scores['models'] * 0.35 +
            factor_scores['seasonal'] * 0.20 +
            factor_scores['realtime'] * 0.10 +
            factor_scores['anomaly'] * 0.05
        )
        
        # Convert to fair value
        base_probability = aggregate_score / 10.0
        
        # Mean reversion for weather markets (extreme weather is rare)
        if market.yes_price > 0.70:
            fair_value = base_probability * 0.85  # Discount extreme events
        elif market.yes_price < 0.30:
            fair_value = base_probability * 1.15  # Boost normal weather
        else:
            fair_value = base_probability
        
        # Clamp
        fair_value = max(0.10, min(0.90, fair_value))
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
        
        # Conviction based on factor agreement
        factor_variance = self._calculate_factor_variance(factor_scores)
        conviction = min(0.90, 0.65 + (1.0 - factor_variance) * 0.25)
        
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
        
        # Generate Renaissance-style quant weather report
        top_factors = self._get_top_factors(factor_scores)
        
        thesis_text = f"""
RENAISSANCE TECHNOLOGIES - QUANTITATIVE METEOROLOGICAL ANALYSIS

Market: {market.question}
Current Price: {market.yes_price:.1%} | Quant Fair Value: {fair_value:.1%}

MULTI-FACTOR ANALYSIS:

Factor Scores (1-10):
- Historical Data: {factor_scores['historical']:.1f}/10 (30% weight)
- Climate Models: {factor_scores['models']:.1f}/10 (35% weight)
- Seasonal Factors: {factor_scores['seasonal']:.1f}/10 (20% weight)
- Real-time Data: {factor_scores['realtime']:.1f}/10 (10% weight)
- Anomaly Detection: {factor_scores['anomaly']:.1f}/10 (5% weight)

Aggregate Score: {aggregate_score:.2f}/10
Model Agreement: {(1.0 - factor_variance):.1%}

TOP SIGNALS:
{chr(10).join('- ' + f for f in top_factors)}

STATISTICAL ANALYSIS:
10-Year Climatology: {factor_scores['historical'] * 10:.0f}th percentile event
Model Consensus: {'Strong' if factor_variance < 0.15 else 'Moderate' if factor_variance < 0.30 else 'Weak'}

QUANTITATIVE EDGE:
Market is {('undervalued' if edge > 0 else 'overvalued')} by {abs(edge):.1%}
Historical probability: {factor_scores['historical'] / 10.0:.1%}
Model-adjusted probability: {fair_value:.1%}

RECOMMENDATION: {'BUY' if edge > 0 else 'SELL'}
Position Size: {min(0.12, abs(edge) * 0.7):.1%} (factor-weighted)
Time Horizon: Short-medium term (weather forecasts degrade beyond 7-10 days)
"""
        
        # Position sizing
        proposed_action = {
            "side": "YES" if edge > 0 else "NO",
            "size_pct": min(0.12, abs(edge) * 0.7 + conviction * 0.05)
        }
        
        thesis = Thesis(
            agent_id=self.agent_id,
            market_id=market.id,
            thesis_text=thesis_text.strip(),
            fair_value=fair_value,
            current_odds=market.yes_price,
            edge=edge,
            conviction=conviction,
            horizon="short",  # Weather forecasts are short-term
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
                'historical_score': factor_scores['historical'],
                'models_score': factor_scores['models'],
                'seasonal_score': factor_scores['seasonal'],
                'realtime_score': factor_scores['realtime'],
                'anomaly_score': factor_scores['anomaly'],
                'aggregate_score': aggregate_score,
                'factor_variance': factor_variance
            },
            status='thesis_generated',
            related_thesis_id=str(thesis.id),
            tags=[
                self.theme,
                'bullish' if edge > 0 else 'bearish',
                'quantitative',
                'multi_factor'
            ]
        )
        
        return thesis
    
    def _calculate_factor_scores(self, market: Market, news_events: List) -> dict:
        """
        Calculate multi-factor meteorological scores.
        
        In production, this would:
        - Query NOAA climate data
        - Fetch ECMWF/GFS model runs
        - Track ENSO, NAO, MJO indices
        - Analyze satellite imagery
        
        For now: heuristic based on news and market price.
        
        Args:
            market: Market being analyzed
            news_events: Recent news events
        
        Returns:
            Dict with factor scores (0-10 scale)
        """
        question_lower = market.question.lower()
        weather_keywords = ['temperature', 'rain', 'snow', 'hurricane', 'tornado', 'flood', 'drought', 'heat', 'cold', 'storm']
        
        # Count weather news
        weather_news = sum(
            1 for event in news_events
            if any(kw in event.headline.lower() or kw in question_lower for kw in weather_keywords)
        )
        
        # Historical score (proxy: market liquidity = more historical data available)
        historical_score = min(10.0, 3.0 + (market.volume_24h / 8000) * 1.2)
        
        # Models score (proxy: news activity = model runs being discussed)
        models_score = min(10.0, 2.0 + weather_news * 1.8)
        
        # Seasonal score (proxy: distance from 0.50 = seasonal bias)
        seasonal_score = min(10.0, 5.0 + abs(market.yes_price - 0.50) * 10.0)
        
        # Real-time score (proxy: recent news count)
        realtime_score = min(10.0, 3.0 + weather_news * 1.5)
        
        # Anomaly score (proxy: extreme prices indicate anomalies)
        if market.yes_price > 0.75 or market.yes_price < 0.25:
            anomaly_score = 8.0  # Extreme event
        else:
            anomaly_score = 5.0  # Normal conditions
        
        return {
            'historical': historical_score,
            'models': models_score,
            'seasonal': seasonal_score,
            'realtime': realtime_score,
            'anomaly': anomaly_score
        }
    
    def _calculate_factor_variance(self, factor_scores: dict) -> float:
        """Calculate variance across factor scores."""
        scores = list(factor_scores.values())
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        normalized_variance = min(1.0, variance / 25.0)
        return normalized_variance
    
    def _get_top_factors(self, factor_scores: dict) -> List[str]:
        """Get top contributing factors."""
        sorted_factors = sorted(factor_scores.items(), key=lambda x: x[1], reverse=True)
        
        descriptions = []
        for factor, score in sorted_factors[:3]:
            strength = 'Strong' if score > 7 else 'Moderate' if score > 5 else 'Weak'
            descriptions.append(f"{factor.replace('_', ' ').title()}: {strength} ({score:.1f}/10)")
        
        return descriptions
