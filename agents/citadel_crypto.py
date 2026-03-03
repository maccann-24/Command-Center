"""
BASED MONEY - Citadel Crypto Agent
Crypto cycle positioning and sector rotation analysis
"""

from typing import List, Optional
from datetime import datetime
import sys
sys.path.insert(0, '..')

from agents.base import BaseAgent
from models import Thesis, Market
from database import get_markets, get_news_events


class CitadelCryptoAgent(BaseAgent):
    """
    Citadel-style sector rotation strategist for crypto markets.
    
    Applies macro cycle analysis to position in crypto prediction markets
    based on market cycles, Fed policy, and sector rotation.
    
    System Prompt (Institutional Analysis Framework):
    ================================================
    
    You are a senior macro strategist at Citadel analyzing crypto prediction
    markets through the lens of market cycles and sector rotation.
    
    For each crypto market, systematically assess:
    
    1. Market Cycle Phase:
       - Bull market: Risk-on, rising prices, euphoria
       - Bear market: Risk-off, falling prices, capitulation
       - Accumulation: Consolidation, smart money buying
       - Distribution: Topping, smart money selling
       - Cycle indicators: 200-week MA, MVRV ratio, Puell Multiple
    
    2. Federal Reserve Policy Impact:
       - Rate hikes: Tightening liquidity → bearish for crypto
       - Rate cuts: Easing liquidity → bullish for crypto
       - QE (money printing): Bullish for scarce assets (BTC)
       - QT (balance sheet reduction): Bearish for risk assets
       - Fed pivot expectations: Market anticipation of policy changes
    
    3. Regulatory Cycle:
       - Regulatory clarity: SEC approval of ETFs, clear guidelines → bullish
       - Regulatory crackdown: Enforcement actions, exchange shutdowns → bearish
       - Political cycle: Crypto-friendly vs. hostile administration
       - International regulation: EU MiCA, Asia policies
       - Stablecoin regulation: Impact on crypto infrastructure
    
    4. BTC Dominance & Altcoin Seasons:
       - BTC dominance rising: Safe haven behavior, alt weakness
       - BTC dominance falling: Risk-on, altcoin season
       - Altcoin season indicators: ETH/BTC ratio, alt market cap
       - Sector rotation: L1s → DeFi → NFTs → memecoins
       - Late-cycle behavior: Speculative excess in low-cap alts
    
    5. Macro Regime:
       - Risk-on: Equities up, VIX down, crypto correlates positively
       - Risk-off: Flight to safety, crypto sells off with stocks
       - Inflation regime: BTC as inflation hedge narrative
       - Recession: Historically bearish for crypto
       - Geopolitical stress: Safe haven or risk asset?
    
    6. Positioning & Flows:
       - Institutional accumulation: MicroStrategy, Tesla, ETF inflows
       - Retail participation: Coinbase app rankings, Google Trends
       - Miner selling: Hash ribbon indicator
       - Exchange reserves: Decreasing = accumulation
       - Whale activity: Large holder behavior
    
    Output Format:
    - Cycle phase: Bull, bear, accumulation, or distribution
    - Fed policy stance: Hawkish (bearish) or dovish (bullish)
    - Regulatory environment: Favorable, neutral, or hostile
    - BTC dominance trend: Rising or falling
    - Macro regime: Risk-on or risk-off
    - Sector recommendation: BTC, ETH, alts, or cash
    - Position sizing: Aggressive (bull) or defensive (bear)
    """
    
    def __init__(self):
        """Initialize Citadel Crypto Agent."""
        super().__init__()
        self.agent_id = "citadel_crypto"
        self.theme = "crypto"
        self.min_volume = 30000.0  # $30K minimum
        self.min_edge = 0.04  # 4% minimum edge (cycle positioning)
        self.min_conviction = 0.65  # 65% minimum conviction
    
    @property
    def mandate(self) -> str:
        """Agent's mandate/focus area."""
        return "Crypto cycle positioning: market cycles, Fed policy, regulatory environment, sector rotation"
    
    def update_theses(self) -> List[Thesis]:
        """
        Generate theses for crypto markets using cycle analysis.
        
        Workflow:
        1. Fetch crypto markets
        2. Assess market cycle phase
        3. Evaluate Fed policy and regulatory environment
        4. Generate cycle-based theses
        
        Returns:
            List of Thesis objects (edge > 4%, conviction > 65%)
        """
        print(f"\n{'='*60}")
        print(f"🔄 CITADEL CRYPTO AGENT - Cycle Analysis")
        print(f"{'='*60}")
        
        try:
            # Fetch crypto markets
            markets = get_markets(filters={
                "category": "crypto",
                "min_volume": self.min_volume,
                "resolved": False
            })
            
            print(f"📊 Analyzing {len(markets)} crypto markets (cycle lens)")
            
            # Post chat message about starting analysis
            if len(markets) > 0:
                self.post_message('chat', content=f"👋 Starting analysis on {len(markets)} markets...")
            
            if not markets:
                print("⚠️ No markets found")
                self.post_message('chat', content="Nothing to analyze today 🤷")
                return []
            
            # Fetch news for cycle/policy context
            news_events = get_news_events(filters={"hours_back": 48})  # 48h for policy news
            print(f"📰 Macro context: {len(news_events)} news events")
            
            # Cycle analysis
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
            print(f"\n🔄 Generated {len(theses)} cycle theses")
            
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
        Generate cycle-based thesis for a crypto market.
        
        Analyzes:
        - Market cycle phase
        - Fed policy impact
        - Regulatory environment
        - Sector rotation dynamics
        
        Args:
            market: Market to analyze
            news_events: Recent news for cycle context
        
        Returns:
            Thesis object with cycle conviction, or None
        """
        self.post_message('chat', content=f"🔍 Analyzing: {market.question[:60]}...")
        
        # Placeholder implementation (would use macro data in production)
        # For now, use cycle heuristics
        
        if news_events is None:
            news_events = get_news_events(filters={"hours_back": 48})
        
        # Analyze cycle factors
        cycle_analysis = self._analyze_cycle_factors(market, news_events)
        
        # Calculate cycle-adjusted fair value
        fair_value = self._calculate_cycle_fair_value(market, cycle_analysis)
        edge = fair_value - market.yes_price
        
        if abs(edge) < self.min_edge:
            self.post_message('chat', content=f"❌ Passing on {market.question[:50]}... - only {abs(edge):.1%} edge (need {self.min_edge:.1%}+)")
            return None
        
        # Conviction based on cycle clarity
        cycle_strength = cycle_analysis['cycle_strength']
        conviction = min(0.85, 0.65 + cycle_strength * 0.20)
        
        if conviction < self.min_conviction:
            self.post_message('chat', content=f"❌ {market.question[:50]}... - conviction too low ({conviction:.1%})")
            return None
        
        # Generate Citadel-style cycle memo
        thesis_text = f"""
CITADEL - CRYPTO CYCLE ANALYSIS

Market: {market.question}
Current Price: {market.yes_price:.1%} | Cycle-Adjusted Fair Value: {fair_value:.1%}

CYCLE ANALYSIS:

Market Phase: {cycle_analysis['market_phase']}
Fed Policy: {cycle_analysis['fed_policy']}
Regulatory Environment: {cycle_analysis['regulatory_environment']}

MACRO REGIME:
The current macro environment is {('supportive' if cycle_analysis['macro_bullish'] else 'challenging')} for crypto.
{cycle_analysis['regime_description']}

SECTOR POSITIONING:
BTC Dominance: {cycle_analysis['btc_dominance']}
Altcoin Environment: {cycle_analysis['altcoin_environment']}

CYCLE IMPLICATIONS:
Current market pricing {('underestimates' if edge > 0 else 'overestimates')} the impact of:
- Fed policy trajectory
- Regulatory developments
- Market cycle phase

Fair value suggests {abs(edge):.1%} {'upside' if edge > 0 else 'downside'} from cycle positioning.

POSITIONING RECOMMENDATION:
{'Aggressive' if edge > 0 else 'Defensive'} positioning warranted.
Market cycle favors {'bulls' if edge > 0 else 'bears'} in current environment.

RISK FACTORS:
- Fed pivot could {'accelerate' if edge > 0 else 'reverse'} this trend
- Regulatory surprise could change narrative quickly
- Macro regime shift would impact positioning

TIME HORIZON: Medium-term (cycles play out over weeks/months)
"""
        
        # Position sizing based on cycle conviction
        proposed_action = {
            "side": "YES" if edge > 0 else "NO",
            "size_pct": min(0.15, abs(edge) * 0.7 + conviction * 0.05)
        }
        
        thesis = Thesis(
            agent_id=self.agent_id,
            market_id=market.id,
            thesis_text=thesis_text.strip(),
            fair_value=fair_value,
            current_odds=market.yes_price,
            edge=edge,
            conviction=conviction,
            horizon="medium",  # Cycle analysis is medium-term
            proposed_action=proposed_action
        )
        
        capital_allocated = 83.30 * proposed_action["size_pct"] / 0.15
        self.post_message('thesis', market_question=market.question, market_id=market.id, current_odds=market.yes_price, thesis_odds=fair_value, edge=edge, conviction=conviction, capital_allocated=capital_allocated, reasoning=thesis_text[:500], signals={'market_phase': cycle_analysis['market_phase'], 'fed_policy': cycle_analysis['fed_policy'], 'regulatory_environment': cycle_analysis['regulatory_environment'], 'cycle_strength': cycle_strength}, status='thesis_generated', related_thesis_id=str(thesis.id), tags=[self.theme, 'bullish' if edge > 0 else 'bearish', 'macro_cycle'])
        
        
        # Announce in chat
        side_emoji = "🟢" if edge > 0 else "🔴"
        self.post_message('chat', content=f"{side_emoji} Thesis posted: {market.question[:60]}... | Edge: {edge:+.1%} | Conviction: {conviction:.1%}")
        return thesis
    
    def _analyze_cycle_factors(self, market: Market, news_events: List) -> dict:
        """
        Analyze market cycle factors.
        
        In production, this would:
        - Query Fed funds rate and Fed minutes
        - Track regulatory filings and SEC actions
        - Monitor BTC dominance charts
        - Assess macro indicators (VIX, DXY, SPY)
        
        For now: news-based cycle proxy.
        
        Args:
            market: Market being analyzed
            news_events: Recent news events
        
        Returns:
            Dict with cycle analysis
        """
        question_lower = market.question.lower()
        
        # Detect cycle keywords in news
        fed_keywords = ['fed', 'federal reserve', 'interest rate', 'powell', 'fomc']
        reg_keywords = ['sec', 'regulation', 'etf', 'approval', 'crackdown', 'enforcement']
        crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'crypto']
        
        fed_news = sum(1 for e in news_events if any(kw in e.headline.lower() for kw in fed_keywords))
        reg_news = sum(1 for e in news_events if any(kw in e.headline.lower() for kw in reg_keywords))
        crypto_news = sum(1 for e in news_events if any(kw in e.headline.lower() or kw in question_lower for kw in crypto_keywords))
        
        # Market phase assessment
        if market.yes_price > 0.70:
            market_phase = "Late Bull / Distribution"
        elif market.yes_price > 0.55:
            market_phase = "Bull Market"
        elif market.yes_price < 0.30:
            market_phase = "Bear / Accumulation"
        elif market.yes_price < 0.45:
            market_phase = "Bear Market"
        else:
            market_phase = "Consolidation / Neutral"
        
        # Fed policy assessment
        if fed_news > 3:
            fed_policy = "Hawkish (Rate Hikes Expected)" if market.yes_price < 0.50 else "Dovish (Rate Cuts Expected)"
        else:
            fed_policy = "Neutral / Status Quo"
        
        # Regulatory environment
        if reg_news > 2:
            regulatory_environment = "Active (High Regulatory Risk)" if market.yes_price < 0.50 else "Favorable (Approvals Expected)"
        else:
            regulatory_environment = "Neutral"
        
        # BTC dominance (proxy: market conviction)
        if abs(market.yes_price - 0.50) > 0.25:
            btc_dominance = "Rising (Flight to Quality)"
        else:
            btc_dominance = "Falling (Altcoin Season)"
        
        # Altcoin environment
        if market.yes_price > 0.60:
            altcoin_environment = "Bullish (Risk-On)"
        elif market.yes_price < 0.40:
            altcoin_environment = "Bearish (Risk-Off)"
        else:
            altcoin_environment = "Mixed"
        
        # Macro bullishness assessment
        macro_bullish = crypto_news > 5 or (reg_news > 2 and market.yes_price > 0.50)
        
        # Regime description
        if macro_bullish:
            regime_description = "Liquidity expansion, regulatory clarity, and positive sentiment support crypto markets."
        else:
            regime_description = "Tightening liquidity, regulatory uncertainty, or negative sentiment pressure crypto markets."
        
        # Cycle strength (how clear is the cycle signal)
        cycle_clarity_factors = [
            1.0 if fed_news > 2 else 0.5,
            1.0 if reg_news > 2 else 0.5,
            1.0 if crypto_news > 4 else 0.5
        ]
        cycle_strength = sum(cycle_clarity_factors) / len(cycle_clarity_factors)
        
        return {
            'market_phase': market_phase,
            'fed_policy': fed_policy,
            'regulatory_environment': regulatory_environment,
            'btc_dominance': btc_dominance,
            'altcoin_environment': altcoin_environment,
            'macro_bullish': macro_bullish,
            'regime_description': regime_description,
            'cycle_strength': cycle_strength
        }
    
    def _calculate_cycle_fair_value(self, market: Market, cycle_analysis: dict) -> float:
        """
        Calculate fair value from cycle analysis.
        
        In production: Model Fed policy impact, regulatory catalysts, cycle phases.
        For now: Adjust based on cycle bullishness.
        
        Args:
            market: Market being valued
            cycle_analysis: Cycle analysis results
        
        Returns:
            Fair value probability (0.0-1.0)
        """
        macro_bullish = cycle_analysis['macro_bullish']
        cycle_strength = cycle_analysis['cycle_strength']
        
        # Cycle-based adjustment
        if macro_bullish:
            # Bullish cycle: boost probabilities
            cycle_adjustment = 0.12 * cycle_strength
        else:
            # Bearish cycle: reduce probabilities
            cycle_adjustment = -0.12 * cycle_strength
        
        # Apply adjustment
        fair_value = market.yes_price + cycle_adjustment
        
        # Mean reversion component (cycles overshoot)
        if market.yes_price > 0.75:
            fair_value -= 0.05  # Extreme optimism tends to revert
        elif market.yes_price < 0.25:
            fair_value += 0.05  # Extreme pessimism tends to revert
        
        # Clamp to valid range
        fair_value = max(0.10, min(0.90, fair_value))
        
        return fair_value
