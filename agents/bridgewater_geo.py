"""
BASED MONEY - Bridgewater Geopolitical Agent
Risk-adjusted analysis of geopolitical prediction markets
"""

from typing import List, Optional
from datetime import datetime
import sys
sys.path.insert(0, '..')

from agents.base import BaseAgent
from models import Thesis, Market
from database import get_markets, get_news_events


class BridgewaterGeoAgent(BaseAgent):
    """
    Bridgewater-style risk analyst for geopolitical prediction markets.
    
    Applies Ray Dalio's All Weather principles to assess risk-adjusted
    positioning in geopolitical markets with focus on correlation, downside
    protection, and portfolio diversification.
    
    System Prompt (Institutional Analysis Framework):
    ================================================
    
    You are a senior risk analyst at Bridgewater Associates evaluating 
    geopolitical prediction markets through a risk management lens.
    
    For each geopolitical market, assess risk factors systematically:
    
    1. Volatility Profile:
       - How much has the market price moved historically?
       - Is volatility increasing (uncertainty rising) or decreasing (clarity emerging)?
       - What is implied volatility vs historical volatility?
       - Are price swings driven by fundamentals or noise?
    
    2. Correlation Analysis:
       - How does this market correlate with other geopolitical markets?
       - What are the common risk factors (oil prices, USD strength, VIX)?
       - Would this position diversify or concentrate existing portfolio risk?
       - Are correlations stable or regime-dependent?
    
    3. Maximum Drawdown Scenarios:
       - What is the worst-case outcome if our thesis is wrong?
       - How quickly could we lose capital (liquidity analysis)?
       - What percentage of position could we lose in a sharp reversal?
       - Historical precedent: how wrong were similar markets in the past?
    
    4. Geographic Concentration:
       - Are we overexposed to one region (Russia, Middle East, Asia)?
       - Would this trade increase or decrease regional concentration?
       - What is the correlation between regional conflicts?
    
    5. Stress Testing:
       - Escalation scenario: What if conflict intensifies (war, sanctions, breakdown)?
       - De-escalation scenario: What if peace talks succeed (treaties, normalization)?
       - Black swan: What if an unexpected actor intervenes?
       - How does the position perform in each scenario?
    
    6. Hedging Recommendations:
       - What related markets could we take opposite positions in?
       - Natural hedges: oil markets, defense stocks, safe haven currencies?
       - Tail risk protection: how to limit downside while preserving upside?
    
    Output Format:
    - Risk-adjusted fair value: Probability discounted for uncertainty
    - Correlation to existing portfolio: 0.0-1.0
    - Maximum drawdown estimate: % loss in worst case
    - Recommended hedge positions: List with rationale
    - Risk score: 1-10 (10 = highest risk)
    - Kelly criterion position size: % of bankroll
    - Sharpe ratio estimate: Expected return / risk
    """
    
    def __init__(self):
        """Initialize Bridgewater Geopolitical Agent."""
        super().__init__()
        self.agent_id = "bridgewater_geo"
        self.theme = "geopolitical"
        self.min_volume = 50000.0  # $50K minimum 24h volume
        self.min_edge = 0.03  # 3% minimum edge (focus on risk-adjusted returns)
        self.min_conviction = 0.55  # 55% minimum (lower bar, risk-managed positions)
        self.max_risk_score = 7  # Don't take positions with risk > 7/10
    
    @property
    def mandate(self) -> str:
        """Agent's mandate/focus area."""
        return "Risk-adjusted analysis of geopolitical markets: volatility, correlation, drawdown scenarios, hedging"
    
    def update_theses(self) -> List[Thesis]:
        """
        Generate theses for geopolitical markets using risk management framework.
        
        Workflow:
        1. Fetch geopolitical markets with sufficient volume
        2. Assess volatility and correlation profiles
        3. Stress test scenarios (escalation, de-escalation, black swan)
        4. Generate risk-managed theses with hedging recommendations
        
        Returns:
            List of Thesis objects (only those with acceptable risk scores)
        """
        print(f"\n{'='*60}")
        print(f"⚖️ BRIDGEWATER GEOPOLITICAL AGENT - Risk Analysis")
        print(f"{'='*60}")
        
        try:
            # Fetch geopolitical markets
            markets = get_markets(filters={
                "category": "geopolitical",
                "min_volume": self.min_volume,
                "resolved": False
            })
            
            print(f"🎯 Analyzing {len(markets)} markets (risk lens)")
            
            if not markets:
                print("⚠️ No markets found")
                self.post_message('chat', content="Nothing to analyze today 🤷")
                return []
            
            # Fetch historical data for volatility analysis (would use time-series in production)
            news_events = get_news_events(filters={"hours_back": 72})  # 3 days for volatility proxy
            print(f"📊 Risk context: {len(news_events)} events (volatility proxy)")
            
            # Risk-adjusted analysis for each market
            theses = []
            for market in markets:
                try:
                    thesis = self.generate_thesis(market, markets, news_events)
                    
                    if thesis:
                        # Additional risk score check
                        risk_score = self._calculate_risk_score(thesis, market)
                        
                        if risk_score <= self.max_risk_score:
                            theses.append(thesis)
                            print(f"✅ {market.question[:40]}... | Edge: {thesis.edge:.1%}, Risk: {risk_score}/10")
                        else:
                            self.post_message('chat', content=f"⚠️ {market.question[:50]}... - risk too high ({risk_score}/10)")
                            print(f"⏭️ {market.question[:40]}... | Rejected: Risk too high ({risk_score}/10)")
                
                except Exception as e:
                    print(f"⚠️ Error analyzing {market.id}: {e}")
                    continue
            
            self._theses_cache = theses
            print(f"\n🛡️ Generated {len(theses)} risk-managed theses")
            
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
        Generate risk-adjusted thesis for a geopolitical market.
        
        Analyzes:
        - Volatility profile and trend
        - Correlation to other geopolitical markets
        - Maximum drawdown scenarios
        - Stress test outcomes
        - Hedging opportunities
        
        Args:
            market: Market to analyze
            all_markets: All markets (for correlation analysis)
            news_events: Recent events (for volatility proxy)
        
        Returns:
            Thesis object with risk-adjusted sizing, or None
        """
        self.post_message('chat', content=f"🔍 Analyzing: {market.question[:60]}...")
        
        if news_events is None:
            news_events = get_news_events(filters={"hours_back": 72})
        
        # Risk analysis
        volatility = self._estimate_volatility(market, news_events)
        correlation = self._estimate_correlation(market, all_markets)
        max_drawdown = self._estimate_max_drawdown(market, volatility)
        
        # Risk-adjusted fair value (discount for uncertainty)
        # In production: LLM would assess probability distributions and tail risks
        base_fair_value = market.yes_price + (0.10 if volatility < 0.15 else -0.05)
        risk_discount = volatility * 0.3  # Higher vol = higher discount
        fair_value = max(0.10, min(0.90, base_fair_value - risk_discount))
        
        edge = fair_value - market.yes_price
        
        if abs(edge) < self.min_edge:
            self.post_message('chat', content=f"❌ Passing on {market.question[:50]}... - only {abs(edge):.1%} edge (need {self.min_edge:.1%}+)")
            return None
        
        # Conviction adjusted for risk
        # Lower conviction in high-volatility environments
        base_conviction = 0.60 + abs(edge) * 1.0
        risk_adjustment = max(0, 1.0 - volatility * 2.0)  # Vol reduces conviction
        conviction = min(0.85, base_conviction * risk_adjustment)
        
        if conviction < self.min_conviction:
            self.post_message('chat', content=f"❌ {market.question[:50]}... - conviction too low ({conviction:.1%})")
            return None
        
        # Generate Bridgewater-style risk memo
        thesis_text = f"""
BRIDGEWATER ASSOCIATES - GEOPOLITICAL RISK ASSESSMENT

Market: {market.question}
Current Price: {market.yes_price:.1%} | Risk-Adjusted Fair Value: {fair_value:.1%}

RISK ANALYSIS:

Volatility Profile:
- Estimated volatility: {volatility:.1%}
- Classification: {'HIGH' if volatility > 0.20 else 'MODERATE' if volatility > 0.10 else 'LOW'} risk
- News flow intensity: {len([e for e in news_events if market.id in str(e)])} related events

Correlation Analysis:
- Portfolio correlation: {correlation:.2f}
- Diversification benefit: {'YES' if correlation < 0.30 else 'MODERATE' if correlation < 0.60 else 'NO'}

Maximum Drawdown Scenarios:
- Base case loss: -{max_drawdown * 0.5:.1%}
- Stress case loss: -{max_drawdown:.1%}  
- Tail risk: -{max_drawdown * 1.5:.1%}

STRESS TESTING:

Escalation Scenario:
Market would likely move {'UP' if edge > 0 else 'DOWN'} {'sharply' if abs(edge) > 0.10 else 'moderately'}.
Position would {'gain' if edge > 0 else 'lose'} ~{abs(edge) * 100:.0f}%.

De-escalation Scenario:  
Market would likely {'fall' if edge > 0 else 'rise'} to baseline.
Position sizing accounts for this risk.

HEDGING RECOMMENDATIONS:
- Consider offsetting position in related markets
- Tail risk protection: {'Recommended' if volatility > 0.15 else 'Optional'}
- Position correlation to portfolio: {correlation:.1%}

RISK SCORE: {self._calculate_risk_score_internal(volatility, max_drawdown, correlation)}/10

POSITION SIZING (Kelly Criterion):
- Maximum position: {min(0.15, abs(edge) / (volatility + 0.01)):.1%} of capital
- Recommended: {min(0.10, abs(edge) / (volatility + 0.01) * 0.5):.1%} (half-Kelly for safety)

RECOMMENDATION: {'ENTER' if abs(edge) > 0.05 else 'MONITOR'} position with strict risk management
Risk-Reward Ratio: {abs(edge) / max(max_drawdown, 0.05):.2f}:1
"""
        
        # Conservative position sizing based on Kelly criterion
        kelly_fraction = abs(edge) / max(volatility + 0.01, 0.05)
        position_size = min(0.10, kelly_fraction * 0.5)  # Half-Kelly for safety
        
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
            horizon="short",  # Risk management favors shorter holding periods
            proposed_action=proposed_action
        )
        
        capital_allocated = 83.30 * proposed_action["size_pct"] / 0.15
        self.post_message('thesis', market_question=market.question, market_id=market.id, current_odds=market.yes_price, thesis_odds=fair_value, edge=edge, conviction=conviction, capital_allocated=capital_allocated, reasoning=thesis_text[:500], signals={'volatility': volatility, 'correlation': correlation, 'max_drawdown': max_drawdown}, status='thesis_generated', related_thesis_id=str(thesis.id), tags=[self.theme, 'bullish' if edge > 0 else 'bearish', 'risk_managed'])
        
        
        # Announce in chat
        side_emoji = "🟢" if edge > 0 else "🔴"
        self.post_message('chat', content=f"{side_emoji} Thesis posted: {market.question[:60]}... | Edge: {edge:+.1%} | Conviction: {conviction:.1%}")
        return thesis
    
    def _estimate_volatility(self, market: Market, news_events: List) -> float:
        """
        Estimate market volatility from news flow.
        
        In production: Calculate actual price volatility from historical data.
        For now: Use news frequency as proxy (more news = higher uncertainty).
        
        Args:
            market: Market being analyzed
            news_events: Recent news events
        
        Returns:
            Estimated volatility (0.0-1.0)
        """
        # Count relevant news events as volatility proxy
        question_words = set(market.question.lower().split())
        relevant_events = sum(
            1 for event in news_events
            if any(word in event.headline.lower() for word in question_words if len(word) > 4)
        )
        
        # More news = more volatility (uncertainty)
        volatility = min(0.35, 0.05 + relevant_events * 0.02)
        
        return volatility
    
    def _estimate_correlation(self, market: Market, all_markets: List[Market]) -> float:
        """
        Estimate correlation to other markets in portfolio.
        
        In production: Calculate actual correlation from price movements.
        For now: Use category/keyword overlap as proxy.
        
        Args:
            market: Market being analyzed
            all_markets: All available markets
        
        Returns:
            Estimated correlation (0.0-1.0)
        """
        if not all_markets or len(all_markets) < 2:
            return 0.0
        
        # Simple correlation proxy: category + keyword similarity
        same_category = sum(1 for m in all_markets if m.category == market.category)
        correlation = min(0.80, same_category / len(all_markets))
        
        return correlation
    
    def _estimate_max_drawdown(self, market: Market, volatility: float) -> float:
        """
        Estimate maximum potential drawdown.
        
        In production: Historical worst-case analysis + stress scenarios.
        For now: Scale with volatility.
        
        Args:
            market: Market being analyzed
            volatility: Estimated volatility
        
        Returns:
            Maximum drawdown (0.0-1.0)
        """
        # Higher volatility = higher potential drawdown
        # Geopolitical markets can gap quickly (30-50% moves possible)
        base_drawdown = 0.20
        vol_multiplier = 1.0 + volatility * 2.0
        max_drawdown = min(0.50, base_drawdown * vol_multiplier)
        
        return max_drawdown
    
    def _calculate_risk_score(self, thesis: Thesis, market: Market) -> int:
        """Calculate risk score from thesis characteristics."""
        # For backward compatibility with existing call
        news_events = get_news_events(filters={"hours_back": 72})
        volatility = self._estimate_volatility(market, news_events)
        max_drawdown = self._estimate_max_drawdown(market, volatility)
        all_markets = get_markets(filters={"category": "geopolitical", "resolved": False})
        correlation = self._estimate_correlation(market, all_markets)
        
        return self._calculate_risk_score_internal(volatility, max_drawdown, correlation)
    
    def _calculate_risk_score_internal(self, volatility: float, max_drawdown: float, 
                                       correlation: float) -> int:
        """
        Calculate overall risk score (1-10 scale).
        
        Args:
            volatility: Estimated volatility
            max_drawdown: Maximum potential loss
            correlation: Portfolio correlation
        
        Returns:
            Risk score (1-10, higher = riskier)
        """
        # Weight factors
        vol_score = volatility * 10 * 0.4  # 40% weight
        drawdown_score = max_drawdown * 10 * 0.4  # 40% weight
        corr_score = correlation * 10 * 0.2  # 20% weight
        
        total_score = vol_score + drawdown_score + corr_score
        risk_score = max(1, min(10, int(total_score)))
        
        return risk_score
