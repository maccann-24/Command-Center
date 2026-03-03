"""
BASED MONEY - Configuration System
Loads environment variables and defines risk parameters
"""

import os
import sys

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover
    load_dotenv = None

# Load environment variables from .env file (if python-dotenv is installed)
if load_dotenv is not None:
    load_dotenv()


# ============================================================
# REQUIRED ENVIRONMENT VARIABLES
# ============================================================

REQUIRED_ENV_VARS = [
    "TRADING_MODE",  # 'paper' or 'live'
    "SUPABASE_URL",  # Supabase project URL
    "SUPABASE_KEY",  # Supabase anon/service key
]


def validate_env_vars():
    """Validate that all required environment variables are set"""
    missing = []

    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print("❌ ERROR: Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print(
            "\n💡 Create a .env file with these variables or set them in your environment."
        )
        print("   See .env.example for reference.\n")
        sys.exit(1)


# Validate on module import (can be skipped for tests/local linting)
if os.getenv("BASED_MONEY_SKIP_ENV_VALIDATION", "").lower() not in {"1", "true", "yes"}:
    validate_env_vars()


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

# Trading mode
TRADING_MODE = os.getenv("TRADING_MODE")  # 'paper' or 'live'
LIVE_TEST_MODE = os.getenv("LIVE_TEST_MODE", "false").lower() == "true"

# Database
SUPABASE_URL = os.getenv("SUPABASE_URL")
# Public/anon key (OK to use on clients). Server-side bot may also use this if service role is not set.
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# Server-only key (bypasses RLS). Recommended for the trading bot writes.
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# News sources
NEWS_SOURCE = os.getenv("NEWS_SOURCE", "rss")  # 'rss' or 'twitter'
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

# Polymarket (for live trading)
POLYMARKET_API_KEY = os.getenv("POLYMARKET_API_KEY", "")
POLYMARKET_PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY", "")
POLYMARKET_CHAIN_ID = int(os.getenv("POLYMARKET_CHAIN_ID", "137"))  # Polygon mainnet

# Alerting
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Command Center
COMMAND_CENTER_URL = os.getenv(
    "COMMAND_CENTER_URL", "https://command-center-dm3n.vercel.app"
)


# ============================================================
# RISK PARAMETERS
# ============================================================


def _as_percent(value: str, default_percent: float) -> float:
    """Parse an env var that may be expressed as 0-1 fraction or 0-100 percent."""
    try:
        v = float(value)
    except Exception:
        return float(default_percent)

    # Heuristic: treat 0-1 as a fraction.
    if 0.0 <= v <= 1.0:
        return v * 100.0
    return v


RISK_PARAMS = {
    # Stored as percentage points (20.0 == 20%)
    "max_position_pct": _as_percent(os.getenv("MAX_POSITION_PCT", "0.20"), 20.0),
    "max_deployed_pct": _as_percent(os.getenv("MAX_DEPLOYED_PCT", "0.60"), 60.0),
    "max_category_pct": _as_percent(os.getenv("MAX_CATEGORY_PCT", "0.40"), 40.0),
    # Conviction remains 0-1
    "min_conviction": float(os.getenv("MIN_CONVICTION", "0.70")),
    # Stored as percentage points (15.0 == 15%)
    "stop_loss_pct": _as_percent(os.getenv("STOP_LOSS_PCT", "0.15"), 15.0),
    # Maximum daily loss limit in USD
    "daily_loss_limit": float(os.getenv("DAILY_LOSS_LIMIT", "150.00")),
}


# ============================================================
# MARKET FILTERING PARAMETERS
# ============================================================

MARKET_FILTERS = {
    # Minimum 24h volume to consider market tradeable
    "min_volume_24h": float(os.getenv("MIN_VOLUME_24H", "50000.00")),
    # Minimum liquidity score (0.0 to 1.0)
    "min_liquidity_score": float(os.getenv("MIN_LIQUIDITY_SCORE", "0.30")),
    # Minimum days to resolution
    "min_days_to_resolution": int(os.getenv("MIN_DAYS_TO_RESOLUTION", "2")),
}


# ============================================================
# LIVE TRADING LIMITS (for LIVE_TEST_MODE)
# ============================================================

LIVE_TEST_LIMITS = {
    # Maximum trade size in USD when in test mode
    "max_trade_size_usd": float(os.getenv("LIVE_TEST_MAX_TRADE", "10.00")),
}


# ============================================================
# INITIAL PORTFOLIO SETTINGS
# ============================================================

INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL", "1000.00"))


# ============================================================
# VALIDATION
# ============================================================


def validate_config():
    """Validate configuration values"""
    errors = []

    # Validate TRADING_MODE
    if TRADING_MODE not in ["paper", "live"]:
        errors.append(f"TRADING_MODE must be 'paper' or 'live', got '{TRADING_MODE}'")

    # Validate risk parameters are within bounds
    # max_position_pct and max_deployed_pct are stored as percentages (0-100)
    if not 0.0 < RISK_PARAMS["max_position_pct"] <= 100.0:
        errors.append(
            f"max_position_pct must be between 0 and 100, got {RISK_PARAMS['max_position_pct']}"
        )

    if not 0.0 < RISK_PARAMS["max_deployed_pct"] <= 100.0:
        errors.append(
            f"max_deployed_pct must be between 0 and 100, got {RISK_PARAMS['max_deployed_pct']}"
        )

    # min_conviction is stored as fraction (0-1)
    if not 0.0 < RISK_PARAMS["min_conviction"] <= 1.0:
        errors.append(
            f"min_conviction must be between 0 and 1, got {RISK_PARAMS['min_conviction']}"
        )

    # Validate live trading requirements
    if TRADING_MODE == "live":
        if not POLYMARKET_API_KEY:
            errors.append("POLYMARKET_API_KEY required for live trading")
        if not POLYMARKET_PRIVATE_KEY:
            errors.append("POLYMARKET_PRIVATE_KEY required for live trading")

    # Print errors and exit if any
    if errors:
        print("❌ CONFIG VALIDATION FAILED:")
        for error in errors:
            print(f"   - {error}")
        print()
        sys.exit(1)


# Validate config on module import
validate_config()


# ============================================================
# STARTUP BANNER
# ============================================================


def print_config_summary():
    """Print configuration summary on startup"""
    print("=" * 60)
    print("BASED MONEY - Configuration Loaded")
    print("=" * 60)
    print(f"Trading Mode:        {TRADING_MODE.upper()}")
    if LIVE_TEST_MODE:
        print(
            f"Live Test Mode:      ENABLED (max ${LIVE_TEST_LIMITS['max_trade_size_usd']:.2f} per trade)"
        )
    print(f"Initial Capital:     ${INITIAL_CAPITAL:,.2f}")
    print(f"Max Position Size:   {RISK_PARAMS['max_position_pct']:.0%}")
    print(f"Max Deployed:        {RISK_PARAMS['max_deployed_pct']:.0%}")
    print(f"Min Conviction:      {RISK_PARAMS['min_conviction']:.0%}")
    print(f"Stop Loss:           {RISK_PARAMS['stop_loss_pct']:.0%}")
    print(f"Daily Loss Limit:    ${RISK_PARAMS['daily_loss_limit']:,.2f}")
    print(f"News Source:         {NEWS_SOURCE.upper()}")
    print("=" * 60)
    print()


if __name__ == "__main__":
    # Print config when run directly
    print_config_summary()
