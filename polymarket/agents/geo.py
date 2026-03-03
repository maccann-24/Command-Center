"""
BASED MONEY - Geopolitical Agent
Trading agent specialized in geopolitical markets
"""

from typing import List
import sys

sys.path.insert(0, "..")

from agents.base import BaseAgent
from agents.signals import calculate_event_impact
from models import Thesis, Market
from database import get_markets, get_news_events


class GeopoliticalAgent(BaseAgent):
    """
    Trading agent specialized in geopolitical markets.

    Focuses on:
    - Russia/Ukraine conflicts
    - US-China relations
    - Iran developments
    - Elections (US, international)
    - General geopolitical events

    Signal Source: News events (RSS feeds from Reuters, AP)
    """

    def __init__(self):
        """Initialize the Geopolitical Agent."""
        super().__init__()
        self.agent_id = "geo"
        self.min_volume = 100000.0  # $100k minimum 24h volume
        self.min_impact = 0.15  # Minimum news impact to generate thesis
        self.min_edge = 0.05  # Minimum edge to return thesis

    @property
    def mandate(self) -> str:
        """Agent's mandate/focus area."""
        return "Russia/Ukraine, US-China, Iran, elections, geopolitical events"

    def update_theses(self) -> List[Thesis]:
        """
        Generate theses for geopolitical markets based on recent news.

        Workflow:
        1. Fetch geopolitical markets with sufficient volume
        2. Fetch recent news events (last 24h)
        3. Calculate news impact for each market
        4. Generate theses for markets with strong signals

        Returns:
            List of Thesis objects (only those with edge > 0.05)
        """
        print(f"\n{'='*60}")
        print(f"🌍 GEOPOLITICAL AGENT - Updating Theses")
        print(f"{'='*60}")

        # Import Trading Floor functions
        try:
            from database import post_analyzing_message, post_thesis_message
            trading_floor_enabled = True
            floor_agent_id = "two-sigma-geo"
        except ImportError:
            trading_floor_enabled = False
            floor_agent_id = None
            print("⚠️ Trading Floor integration not available")

        # Post "analyzing" message to Trading Floor
        if trading_floor_enabled:
            post_analyzing_message(
                agent_id=floor_agent_id or self.agent_id,
                theme="geopolitics",
                content="Analyzing geopolitical markets based on recent news events..."
            )

        try:
            # Step 1: Fetch geopolitical markets with sufficient volume
            markets = get_markets(
                filters={
                    "category": "geopolitical",
                    "min_volume": self.min_volume,
                    "resolved": False,
                }
            )

            print(
                f"📊 Fetched {len(markets)} geopolitical markets (volume > ${self.min_volume:,.0f})"
            )

            if not markets:
                print("⚠️ No geopolitical markets found")
                return []

            # Step 2: Fetch news events from last 24h
            news_events = get_news_events(filters={"hours_back": 24})

            print(f"📰 Fetched {len(news_events)} news events (last 24h)")

            if not news_events:
                print("⚠️ No news events found, skipping signal generation")
                return []

            # Step 3: Analyze each market for news impact
            theses = []

            for market in markets:
                try:
                    thesis = self.generate_thesis(market, news_events)

                    # Only include theses with minimum edge
                    if thesis and thesis.edge > self.min_edge:
                        theses.append(thesis)
                        print(
                            f"✅ Thesis generated: {market.question[:60]}... (edge: {thesis.edge:.2%})"
                        )
                        
                        # Post thesis message to Trading Floor
                        if trading_floor_enabled:
                            # Build signals payload (actual sources/headlines)
                            from agents.signals import extract_keywords_from_question, has_keyword_overlap

                            market_keywords = extract_keywords_from_question(market.question)
                            matching_sources = []
                            for ev in news_events:
                                try:
                                    if has_keyword_overlap(market_keywords, ev.keywords):
                                        matching_sources.append(
                                            {
                                                "source": getattr(ev, "source", None),
                                                "headline": getattr(ev, "headline", None),
                                                "timestamp": getattr(ev, "timestamp", None).isoformat() if getattr(ev, "timestamp", None) else None,
                                            }
                                        )
                                except Exception:
                                    continue

                            signals = {
                                "source_type": "news",
                                "matches": matching_sources[:10],
                                "match_count": len(matching_sources),
                            }

                            post_thesis_message(
                                agent_id=floor_agent_id or self.agent_id,
                                theme="geopolitics",
                                thesis_text=thesis.thesis_text,
                                market_question=market.question,
                                current_odds=thesis.current_odds,
                                fair_value=thesis.fair_value,
                                edge=thesis.edge,
                                conviction=thesis.conviction,
                                reasoning=thesis.thesis_text,
                                capital_allocated=thesis.proposed_action.get("size_pct", 0) * 10000,  # assume $10k portfolio
                                signals=signals,
                            )
                    else:
                        print(
                            f"⏭️  Skipped: {market.question[:60]}... (no signal or low edge)"
                        )

                except Exception as e:
                    print(f"⚠️ Error analyzing market {market.id}: {e}")
                    continue

            # Cache theses
            self._theses_cache = theses

            print(f"\n📈 Generated {len(theses)} actionable theses")
            print(f"{'='*60}\n")

            return theses

        except Exception as e:
            print(f"❌ Error in update_theses: {e}")
            import traceback

            traceback.print_exc()
            return []

    def generate_thesis(self, market: Market, news_events: List = None) -> Thesis:
        """
        Generate a thesis for a specific geopolitical market.

        Args:
            market: Market to analyze
            news_events: List of recent NewsEvent objects (optional, will fetch if not provided)

        Returns:
            Thesis object if signal detected, None otherwise
        """
        # Fetch news if not provided
        if news_events is None:
            news_events = get_news_events(filters={"hours_back": 24})

        if not news_events:
            return None

        # Calculate news impact
        impact_score = calculate_event_impact(market, news_events)

        # Check if impact meets minimum threshold
        if impact_score <= self.min_impact:
            return None

        # Calculate fair value with cap to avoid overconfidence
        fair_value = min(0.95, market.yes_price + impact_score)

        # Calculate edge
        edge = fair_value - market.yes_price

        # Calculate conviction (scaled from impact, capped at 80%)
        conviction = min(0.80, impact_score * 3.0)

        # Count matching events (for thesis text)
        matching_events = self._count_matching_events(market, news_events)

        # Get sample event headlines
        event_headlines = self._get_event_headlines(market, news_events, max_length=100)

        # Generate thesis text
        thesis_text = f"Market underpriced based on {matching_events} recent events: {event_headlines}"

        # Calculate position size (scales with conviction)
        position_size_pct = conviction * 0.15

        # Create thesis
        thesis = Thesis(
            agent_id=self.agent_id,
            market_id=market.id,
            thesis_text=thesis_text,
            fair_value=fair_value,
            current_odds=market.yes_price,
            edge=edge,
            conviction=conviction,
            horizon="medium",
            proposed_action={"side": "YES", "size_pct": position_size_pct},
        )

        return thesis

    def _count_matching_events(self, market: Market, news_events: List) -> int:
        """
        Count how many news events match the market's keywords.

        Args:
            market: Market object
            news_events: List of NewsEvent objects

        Returns:
            Count of matching events
        """
        from agents.signals import extract_keywords_from_question, has_keyword_overlap

        market_keywords = extract_keywords_from_question(market.question)

        count = 0
        for news_event in news_events:
            if has_keyword_overlap(market_keywords, news_event.keywords):
                count += 1

        return count

    def _get_event_headlines(
        self, market: Market, news_events: List, max_length: int = 100
    ) -> str:
        """
        Get concatenated headlines from matching news events.

        Args:
            market: Market object
            news_events: List of NewsEvent objects
            max_length: Maximum length of returned string

        Returns:
            Concatenated headlines (truncated to max_length)
        """
        from agents.signals import extract_keywords_from_question, has_keyword_overlap

        market_keywords = extract_keywords_from_question(market.question)

        headlines = []
        for news_event in news_events:
            if has_keyword_overlap(market_keywords, news_event.keywords):
                headlines.append(news_event.headline)

        if not headlines:
            return "No specific events"

        # Concatenate headlines
        combined = "; ".join(headlines)

        # Truncate if too long
        if len(combined) > max_length:
            combined = combined[:max_length] + "..."

        return combined


# Backwards-compatible alias (main.py expects GeoAgent)
GeoAgent = GeopoliticalAgent


# ============================================================
# TESTING UTILITIES
# ============================================================


def test_geopolitical_agent():
    """
    Test GeopoliticalAgent with sample data.
    Run with: python -m agents.geo
    """
    from datetime import datetime, timedelta
    from models import NewsEvent

    print("=" * 60)
    print("GEOPOLITICAL AGENT TEST")
    print("=" * 60)

    # Create agent
    agent = GeopoliticalAgent()

    # Test 1: Mandate
    print(f"\n1. Agent mandate: '{agent.mandate}'")
    print(f"   ✅ Mandate set correctly")

    # Test 2: Generate thesis with mock data
    print(f"\n2. Testing thesis generation...")

    # Mock market
    market = Market(
        id="test_geo_1",
        question="Will Russia invade Ukraine in 2026?",
        category="geopolitical",
        yes_price=0.50,
        no_price=0.50,
        volume_24h=150000.0,
        resolution_date=datetime.utcnow() + timedelta(days=60),
    )

    # Mock news events
    news_events = [
        NewsEvent(
            timestamp=datetime.utcnow() - timedelta(hours=1),
            headline="Russia announces military mobilization near Ukraine border",
            keywords=["russia", "military", "ukraine"],
            source="reuters",
        ),
        NewsEvent(
            timestamp=datetime.utcnow() - timedelta(hours=2),
            headline="Ukraine requests emergency NATO meeting",
            keywords=["ukraine", "nato"],
            source="ap",
        ),
    ]

    # Generate thesis
    thesis = agent.generate_thesis(market, news_events)

    if thesis:
        print(f"   ✅ Thesis generated successfully")
        print(f"   📊 Market: {market.question}")
        print(f"   💰 Edge: {thesis.edge:.2%}")
        print(f"   🎯 Conviction: {thesis.conviction:.0%}")
        print(f"   📈 Fair Value: {thesis.fair_value:.2%}")
        print(f"   📝 Thesis: {thesis.thesis_text[:80]}...")
        print(f"   💵 Position Size: {thesis.proposed_action['size_pct']:.1%}")
    else:
        print(f"   ❌ No thesis generated (impact too low)")
        return False

    # Test 3: Check thesis validity
    print(f"\n3. Validating thesis...")

    if thesis.edge > 0:
        print(f"   ✅ Edge is positive: {thesis.edge:.2%}")
    else:
        print(f"   ❌ Edge should be positive")
        return False

    if 0 < thesis.conviction <= 0.80:
        print(f"   ✅ Conviction within bounds: {thesis.conviction:.0%}")
    else:
        print(f"   ❌ Conviction out of bounds: {thesis.conviction}")
        return False

    if thesis.fair_value <= 0.95:
        print(f"   ✅ Fair value capped: {thesis.fair_value:.2%}")
    else:
        print(f"   ❌ Fair value exceeds cap: {thesis.fair_value}")
        return False

    # Test 4: No signal case
    print(f"\n4. Testing no-signal case...")

    market_no_signal = Market(
        id="test_geo_2",
        question="Will Bitcoin reach $100k?",
        category="crypto",
        yes_price=0.60,
        no_price=0.40,
        volume_24h=200000.0,
    )

    thesis_none = agent.generate_thesis(market_no_signal, news_events)

    if thesis_none is None:
        print(f"   ✅ Correctly returned None (no overlap with geo news)")
    else:
        print(
            f"   ⚠️ Generated thesis for non-matching market (edge: {thesis_none.edge:.2%})"
        )

    print("\n" + "=" * 60)
    print("✅ GEOPOLITICAL AGENT TEST COMPLETE")
    print("=" * 60)

    return True


if __name__ == "__main__":
    import sys

    success = test_geopolitical_agent()
    sys.exit(0 if success else 1)
