"""
BASED MONEY - Polymarket API Fetcher
Fetch market data from Polymarket API
"""

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None
from typing import List, Dict, Any, Optional
from datetime import datetime

import sys

sys.path.insert(0, "..")

from models import Market
from database import record_event

# Polymarket API endpoints
POLYMARKET_API_BASE = "https://gamma-api.polymarket.com"
MARKETS_ENDPOINT = f"{POLYMARKET_API_BASE}/markets"


def fetch_markets(limit: int = 100, active_only: bool = True) -> List[Market]:
    """
    Fetch markets from Polymarket API.

    Args:
        limit: Maximum number of markets to fetch
        active_only: Only fetch active (unresolved) markets

    Returns:
        List of Market objects
    """
    try:
        # Build query parameters
        params = {
            "limit": limit,
            "offset": 0,
        }

        if active_only:
            params["closed"] = "false"

        # Make API request
        print(f"📡 Fetching markets from Polymarket API (limit={limit})...")
        response = requests.get(
            MARKETS_ENDPOINT,
            params=params,
            timeout=10,
            headers={"User-Agent": "BasedMoney/1.0"},
        )

        # Check response status
        if response.status_code != 200:
            error_msg = f"Polymarket API returned status {response.status_code}"
            print(f"❌ {error_msg}")
            record_event(
                event_type="api_error",
                details={
                    "source": "polymarket",
                    "status_code": response.status_code,
                    "error": error_msg,
                },
                severity="warning",
            )
            return []

        # Parse JSON response
        data = response.json()

        # Handle different response structures
        # Polymarket API might return array directly or wrapped in object
        if isinstance(data, dict) and "data" in data:
            markets_data = data["data"]
        elif isinstance(data, list):
            markets_data = data
        else:
            print(f"⚠️ Unexpected API response structure: {type(data)}")
            return []

        # Parse markets
        markets = []
        for market_data in markets_data:
            try:
                market = parse_polymarket_market(market_data)
                if market:
                    markets.append(market)
            except Exception as e:
                # Skip individual market parse errors, log and continue
                print(
                    f"⚠️ Error parsing market {market_data.get('id', 'unknown')}: {e}"
                )
                continue

        print(f"✅ Fetched {len(markets)} markets from Polymarket")

        # Log success
        record_event(
            event_type="markets_fetched",
            details={"source": "polymarket", "count": len(markets), "limit": limit},
            severity="info",
        )

        return markets

    except requests.exceptions.Timeout:
        error_msg = "Polymarket API request timed out"
        print(f"❌ {error_msg}")
        record_event(
            event_type="api_error",
            details={"source": "polymarket", "error": error_msg},
            severity="error",
        )
        return []

    except requests.exceptions.ConnectionError:
        error_msg = "Failed to connect to Polymarket API (network error)"
        print(f"❌ {error_msg}")
        record_event(
            event_type="api_error",
            details={"source": "polymarket", "error": error_msg},
            severity="error",
        )
        return []

    except requests.exceptions.RequestException as e:
        error_msg = f"Polymarket API request failed: {str(e)}"
        print(f"❌ {error_msg}")
        record_event(
            event_type="api_error",
            details={"source": "polymarket", "error": error_msg},
            severity="error",
        )
        return []

    except Exception as e:
        error_msg = f"Unexpected error fetching markets: {str(e)}"
        print(f"❌ {error_msg}")
        record_event(
            event_type="api_error",
            details={
                "source": "polymarket",
                "error": error_msg,
                "type": type(e).__name__,
            },
            severity="error",
        )
        return []


def parse_polymarket_market(data: Dict[str, Any]) -> Optional[Market]:
    """
    Parse a single market from Polymarket API response into Market object.

    Polymarket API fields (as of 2026):
    - id: Market ID
    - question: Market question text
    - category: Category/tag
    - outcomes: Array of outcome data with prices
    - volume: 24h volume
    - end_date_iso: Resolution date
    - closed: Boolean for resolved status

    Args:
        data: Raw market data from API

    Returns:
        Market object or None if parsing fails
    """
    try:
        # Extract basic fields
        market_id = data.get("id") or data.get("market_id") or data.get("condition_id")
        question = data.get("question") or data.get("title") or ""
        category = data.get("category") or data.get("tag") or "unknown"

        # Extract prices
        # Polymarket typically has "outcomes" array or direct price fields
        yes_price = 0.0
        no_price = 0.0

        if "outcomes" in data and isinstance(data["outcomes"], list):
            # Parse outcomes array
            for outcome in data["outcomes"]:
                outcome_name = outcome.get("name", "").upper()
                price = float(outcome.get("price", 0.0))

                if "YES" in outcome_name:
                    yes_price = price
                elif "NO" in outcome_name:
                    no_price = price
        elif "yes_price" in data:
            # Direct price fields
            yes_price = float(data.get("yes_price", 0.0))
            no_price = float(data.get("no_price", 0.0))
        elif "outcomePrices" in data:
            # Alternative structure
            prices = data["outcomePrices"]
            if isinstance(prices, list) and len(prices) >= 2:
                yes_price = float(prices[0])
                no_price = float(prices[1])

        # If no_price not provided, calculate as complement
        if yes_price > 0 and no_price == 0:
            no_price = 1.0 - yes_price
        elif no_price > 0 and yes_price == 0:
            yes_price = 1.0 - no_price

        # Extract volume
        volume_24h = float(
            data.get("volume")
            or data.get("volume24hr")
            or data.get("volume_24h")
            or 0.0
        )

        # Extract resolution date
        resolution_date = None
        end_date_str = (
            data.get("end_date_iso") or data.get("endDate") or data.get("end_date")
        )
        if end_date_str:
            try:
                # Try ISO format first
                resolution_date = datetime.fromisoformat(
                    end_date_str.replace("Z", "+00:00")
                )
            except:
                # Try parsing as timestamp
                try:
                    resolution_date = datetime.fromtimestamp(float(end_date_str))
                except:
                    resolution_date = None

        # Extract resolved status
        resolved = bool(data.get("closed") or data.get("resolved") or False)

        # Extract liquidity score (if available)
        liquidity_score = float(
            data.get("liquidityScore") or data.get("liquidity") or 0.0
        )

        # Validate required fields
        if not market_id:
            print(f"⚠️ Market missing ID, skipping")
            return None

        if not question:
            print(f"⚠️ Market {market_id} missing question, skipping")
            return None

        # Create Market object
        market = Market(
            id=str(market_id),
            question=question,
            category=category,
            yes_price=yes_price,
            no_price=no_price,
            volume_24h=volume_24h,
            resolution_date=resolution_date,
            resolved=resolved,
            liquidity_score=liquidity_score,
        )

        return market

    except Exception as e:
        print(f"⚠️ Error parsing market data: {e}")
        return None


def test_fetch():
    """
    Test function to verify API fetching works.
    Run with: python -m ingestion.polymarket
    """
    print("=" * 60)
    print("POLYMARKET API FETCH TEST")
    print("=" * 60)

    # Fetch a small batch
    markets = fetch_markets(limit=5, active_only=True)

    if not markets:
        print("\n⚠️ No markets fetched (API might be down or rate-limited)")
        print("   This is expected if running without network access")
        return

    print(f"\n📊 Sample of {len(markets)} markets:\n")

    for i, market in enumerate(markets[:3], 1):
        print(f"{i}. {market.question[:80]}...")
        print(f"   ID: {market.id}")
        print(f"   Category: {market.category}")
        print(f"   YES: {market.yes_price:.2%} | NO: {market.no_price:.2%}")
        print(f"   Volume 24h: ${market.volume_24h:,.2f}")
        print(f"   Resolved: {market.resolved}")
        print()

    print("=" * 60)
    print("✅ Test complete")


if __name__ == "__main__":
    test_fetch()
