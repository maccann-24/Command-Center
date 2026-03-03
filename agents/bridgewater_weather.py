"""
BASED MONEY - Bridgewater Weather Agent
Risk management analysis of weather prediction markets
"""

from typing import List, Optional
from datetime import datetime
import sys
sys.path.insert(0, '..')

from agents.base import BaseAgent
from models import Thesis, Market
from database import get_markets, get_news_events


class BridgewaterWeatherAgent(BaseAgent):
    """
    Bridgewater-style risk analyst for weather prediction markets.
    
    Applies risk management framework to assess weather market exposure,
    model uncertainty, geographic correlation, and hedging opportunities.
    
    System Prompt (Institutional Analysis Framework):
    ================================================
    
    You are a senior risk analyst at Bridgewater Associates evaluating
    weather prediction markets through a risk management lens.
    
    For each weather market, systematically assess:
    
    1. Model Uncertainty:
       - Model spread: How much do NOAA, ECMWF, CMC models disagree?
       - Forecast confidence: Do ensembles have tight or wide spread?
       - Historical skill: How accurate have models been recently for this region?
       - Time horizon risk: Forecasts degrade quickly beyond 7-10 days
       - Extreme event uncertainty: Models struggle with rare extremes
    
    2. Geographic Correlation:
       - Regional clustering: Are multiple markets in same geography?
       - Weather system linkage: Hurricane → power outage → crop damage chain
       - Atmospheric teleconnections: El Niño impacts on multiple regions
       - Diversification: Are markets truly independent or correlated?
       - Cascade risk: One weather event triggering multiple outcomes
    
    3. Seasonal Concentration:
       - Season exposure: Overweight summer heat or winter cold markets?
       - Event timing: Multiple markets resolving in same month?
       - Seasonal pattern risk: All markets bet on same seasonal anomaly?
       - Diversification score: Spread across seasons and event types?
    
    4. Hedging Opportunities:
       - Natural hedges: Cold snap market + heating degree days
       - Inverse markets: Wet vs. dry for same region
       - Temperature spreads: Above X degrees vs. below X degrees
       - Geographic hedges: Offsetting exposures in different regions
       - Correlation trades: Markets that move together can offset
    
    5. Tail Risk:
       - Black swan weather: Unprecedented events (500-year floods)
       - Model blind spots: Conditions models haven't seen before
       - Climate change risk: Historical data less reliable
       - Maximum drawdown: Worst-case scenario if wrong
       - Position sizing: Reduce size in high-uncertainty markets
    
    6. Stress Testing:
       - Model failure: What if forecasts are completely wrong?
       - Extreme outcome: Category 5 hurricane, record heatwave
       - Multiple events: Compound disasters hitting portfolio
       - Geographic concentration: All markets in hurricane-prone areas
    
    Output Format:
    - Risk-adjusted fair value: Probability discounted for uncertainty
    - Model uncertainty: 1-10 (10 = highest disagreement)
    - Geographic correlation: 0.0-1.0 (to other weather positions)
    - Recommended hedge: Related markets to offset risk
    - Risk score: 1-10 (10 = highest risk)
    - Position sizing: Conservative sizing based on uncertainty
    """
    
    def __init__(self):
        """Initialize Bridgewater Weather Agent."""
        super().__init__()
        self.agent_id = "bridgewater_weather"
        self.theme = "weather"
        self.min_volume = 20000.0  # $20K minimum
        self.min_edge = 0.03  # 3% minimum edge (risk-managed)
        self.min_conviction = 0.55  # 55% minimum (lower bar, risk-managed)
        self.max_risk_score = 7  # Don't take positions with risk > 7/10
    
    @property
    def mandate(self) -> str:
        """Agent's mandate/focus area."""
        return "Weather market risk management: model uncertainty, geographic correlation, seasonal concentration, hedging"
    
    def update_theses(self) -> List[Thesis]:
        """
        Generate theses for weather markets using risk management framework.
        
        Workflow:
        1. Fetch weather markets
        2. Assess model uncertainty and correlations
        3. Stress test scenarios
        4. Generate risk-managed theses with hedging
        
        Returns:
            List of Thesis objects (acceptable risk scores)
        """
        print(f"\n{'='*60}")
        print(f"⛈️ BRIDGEWATER WEATHER AGENT - Risk Analysis")
        print(f"{'='*60}")
        
        try:
            # Fetch weather markets
            markets = get_markets(filters={
                "category": "weather",
                "min_volume": self.min_volume,
                "resolved": False
            })
            
            print(f"📊 Analyzing {len(markets)} weather markets (risk lens)")
            
            # Post chat message about starting analysis
            if len(markets) > 0:
                self.post_message('chat', content=f"👋 Starting analysis on {len(markets)} markets...")
            
            if not markets:
                print("⚠️ No markets found")
                self.post_message('chat', content="Nothing to analyze today 🤷")
                return []
            
            # Fetch news for risk context
            news_events = get_news_events(filters={"hours_back": 48})
            print(f"📰 Risk context: {len(news_events)} news events")
            
            # Risk analysis
            theses = []
            for market in markets:
                try:
                    thesis = self.generate_thesis(market, markets, news_events)
                    
                    if thesis:  # generate_thesis handles edge/conviction rejections internally
                        # Additional risk score check
                        risk_score = self._calculate_risk_score(thesis, market)
                        
                        if risk_score <= self.max_risk_score:
                            theses.append(thesis)
                            print(f"✅ {market.question[:40]}... | Edge: {thesis.edge:.1%}, Risk: {risk_score}/10")
                        else:
                            # 5️⃣ POST: Rejected (high risk)
                            self.post_message(
                                'alert',
                                market_question=market.question,
                                market_id=market.id,
                                current_odds=market.yes_price,
                                reasoning=f"Rejected: risk score {risk_score}/10 exceeds max {self.max_risk_score}/10",
                                status='rejected',
                                tags=['rejected', 'high_risk']
                            )
                            print(f"⏭️ {market.question[:40]}... | Rejected: Risk too high ({risk_score}/10)")
                
                except Exception as e:
                    print(f"⚠️ Error analyzing {market.id}: {e}")
                    continue
            
            self._theses_cache = theses
            print(f"\n⛈️ Generated {len(theses)} risk-managed weather theses")
            
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
    
    def generate_thesis(self, market: Market, all_markets: List[Market], 
                       news_events: List = None) -> Optional[Thesis]:
        """
        Generate risk-managed weather thesis.
        
        Analyzes:
        - Model uncertainty and forecast spread
        - Geographic correlation to other positions
        - Seasonal concentration risk
        - Hedging opportunities
        
        Args:
            market: Market to analyze
            all_markets: All markets (for correlation analysis)
            news_events: Recent news for context
        
        Returns:
            Thesis object with risk-adjusted sizing, or None
        """
        # 1️⃣ POST: Starting analysis
        self.post_message(
            'analyzing',
            market_question=market.question,
            market_id=market.id,
            current_odds=market.yes_price,
            status='analyzing'
        )
        
        if news_events is None:
            news_events = get_news_events(filters={"hours_back": 48})
        
        # Risk analysis
        risk_analysis = self._analyze_risk_factors(market, all_markets, news_events)
        
        # Risk-adjusted fair value
        base_fair_value = market.yes_price + (0.08 if risk_analysis['model_uncertainty'] < 5 else -0.05)
        risk_discount = risk_analysis['model_uncertainty'] / 100.0  # Discount for uncertainty
        fair_value = max(0.10, min(0.90, base_fair_value - risk_discount))
        
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
        
        # Conviction adjusted for risk
        base_conviction = 0.60 + abs(edge) * 0.8
        risk_adjustment = max(0, 1.0 - risk_analysis['model_uncertainty'] / 10.0)
        conviction = min(0.85, base_conviction * risk_adjustment)
        
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
        
        # Generate Bridgewater-style risk memo
        thesis_text = f"""
BRIDGEWATER ASSOCIATES - WEATHER MARKET RISK ASSESSMENT

Market: {market.question}
Current Price: {market.yes_price:.1%} | Risk-Adjusted Fair Value: {fair_value:.1%}

RISK ANALYSIS:

Model Uncertainty: {risk_analysis['model_uncertainty']:.1f}/10 ({'High' if risk_analysis['model_uncertainty'] > 6 else 'Moderate' if risk_analysis['model_uncertainty'] > 3 else 'Low'})
Geographic Correlation: {risk_analysis['geographic_correlation']:.2f}
Seasonal Concentration: {risk_analysis['seasonal_concentration']}

UNCERTAINTY ASSESSMENT:
Forecast uncertainty is {('elevated' if risk_analysis['model_uncertainty'] > 6 else 'moderate' if risk_analysis['model_uncertainty'] > 3 else 'low')}.
Weather models {'disagree significantly' if risk_analysis['model_uncertainty'] > 6 else 'show moderate spread' if risk_analysis['model_uncertainty'] > 3 else 'are in good agreement'}.

STRESS TESTING:

Extreme Scenario:
If weather models are wrong, position could lose {abs(edge) * 1.5:.1%}.

Portfolio Impact:
Geographic correlation of {risk_analysis['geographic_correlation']:.1%} to other weather positions.

HEDGING RECOMMENDATIONS:
{risk_analysis['hedge_suggestion']}

RISK SCORE: {self._calculate_risk_score_internal(risk_analysis)}/10

POSITION SIZING (Risk-Managed):
- Maximum position: {min(0.08, abs(edge) / max(risk_analysis['model_uncertainty'] / 10.0, 0.3)):.1%}
- Recommended: {min(0.06, abs(edge) / max(risk_analysis['model_uncertainty'] / 10.0, 0.3) * 0.5):.1%} (conservative)

RECOMMENDATION: {'ENTER' if abs(edge) > 0.05 else 'MONITOR'} position with strict risk management
Risk-Reward Ratio: {abs(edge) / max(0.05, abs(edge) * 1.5):.2f}:1
"""
        
        # Conservative position sizing based on uncertainty
        uncertainty_factor = risk_analysis['model_uncertainty'] / 10.0
        position_size = min(0.08, abs(edge) / max(uncertainty_factor, 0.3) * 0.5)
        
        proposed_action = {
            "side": "YES" if edge > 0 else "NO",
            "size_pct": position_size
        }
        
        thesis = Thesis(
            agent_id=self.agent_id,
            market_id=market.id,
            thesis_text=thesis_text.strip(),
            fair_value=fair_value,
            current_odds=market.yes_price,
            edge=edge,
            conviction=conviction,
            horizon="short",  # Weather risk management is short-term
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
                'model_uncertainty': risk_analysis['model_uncertainty'],
                'geographic_correlation': risk_analysis['geographic_correlation'],
                'seasonal_concentration': risk_analysis['seasonal_concentration'],
                'risk_score': self._calculate_risk_score_internal(risk_analysis)
            },
            status='thesis_generated',
            related_thesis_id=str(thesis.id),
            tags=[
                self.theme,
                'bullish' if edge > 0 else 'bearish',
                'risk_managed',
                'bridgewater'
            ]
        )
        
        return thesis
    
    def _analyze_risk_factors(self, market: Market, all_markets: List[Market], 
                              news_events: List) -> dict:
        """
        Analyze weather market risk factors.
        
        In production, this would:
        - Query ensemble forecast spreads
        - Calculate correlation matrices
        - Assess geographic clustering
        - Identify hedging pairs
        
        For now: heuristic risk assessment.
        
        Args:
            market: Market being analyzed
            all_markets: All available markets
            news_events: Recent news events
        
        Returns:
            Dict with risk analysis
        """
        question_lower = market.question.lower()
        
        # Model uncertainty (proxy: extreme prices indicate high uncertainty)
        if market.yes_price > 0.75 or market.yes_price < 0.25:
            model_uncertainty = 7.0  # Extreme events = high uncertainty
        elif market.yes_price > 0.60 or market.yes_price < 0.40:
            model_uncertainty = 5.0  # Moderate uncertainty
        else:
            model_uncertainty = 3.0  # Normal conditions = low uncertainty
        
        # Geographic correlation (proxy: category overlap)
        same_category = sum(1 for m in all_markets if m.category == market.category and m.id != market.id)
        geographic_correlation = min(0.70, same_category / max(len(all_markets), 1))
        
        # Seasonal concentration
        weather_keywords = ['summer', 'winter', 'spring', 'fall', 'hurricane', 'tornado', 'snow', 'heat']
        seasonal_keywords_found = sum(1 for kw in weather_keywords if kw in question_lower)
        
        if seasonal_keywords_found > 2:
            seasonal_concentration = "High (specific seasonal event)"
        elif seasonal_keywords_found > 0:
            seasonal_concentration = "Moderate"
        else:
            seasonal_concentration = "Low (general weather)"
        
        # Hedge suggestion
        if 'hot' in question_lower or 'heat' in question_lower:
            hedge_suggestion = "Consider hedging with cold-weather or cooling-degree-day markets"
        elif 'cold' in question_lower or 'snow' in question_lower:
            hedge_suggestion = "Consider hedging with warm-weather or heating-degree-day markets"
        elif 'rain' in question_lower or 'flood' in question_lower:
            hedge_suggestion = "Consider hedging with drought or dry-weather markets in same region"
        else:
            hedge_suggestion = "Monitor related weather markets for natural hedge opportunities"
        
        return {
            'model_uncertainty': model_uncertainty,
            'geographic_correlation': geographic_correlation,
            'seasonal_concentration': seasonal_concentration,
            'hedge_suggestion': hedge_suggestion
        }
    
    def _calculate_risk_score(self, thesis: Thesis, market: Market) -> int:
        """Calculate risk score from thesis."""
        news_events = get_news_events(filters={"hours_back": 48})
        all_markets = get_markets(filters={"category": "weather", "resolved": False})
        risk_analysis = self._analyze_risk_factors(market, all_markets, news_events)
        return self._calculate_risk_score_internal(risk_analysis)
    
    def _calculate_risk_score_internal(self, risk_analysis: dict) -> int:
        """
        Calculate overall risk score (1-10 scale).
        
        Args:
            risk_analysis: Risk analysis results
        
        Returns:
            Risk score (1-10, higher = riskier)
        """
        # Weight factors
        uncertainty_score = risk_analysis['model_uncertainty'] * 0.50  # 50% weight
        correlation_score = risk_analysis['geographic_correlation'] * 10 * 0.30  # 30% weight
        seasonal_score = (3 if 'High' in risk_analysis['seasonal_concentration'] else 
                         2 if 'Moderate' in risk_analysis['seasonal_concentration'] else 1) * 0.20 * 10  # 20% weight
        
        total_score = uncertainty_score + correlation_score + seasonal_score
        risk_score = max(1, min(10, int(total_score)))
        
        return risk_score
