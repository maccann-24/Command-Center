"""Live integration test: JPMorganPoliticsAgent → Trading Floor messages.

This script is intentionally "live": if SUPABASE creds are configured,
BaseAgent.post_message() will insert rows into agent_messages.

Run:
  python3 test_jpmorgan_politics_trading_floor.py
"""

import os
import sys

from agents.jpmorgan_politics import JPMorganPoliticsAgent


REQUIRED_ENV_VARS = [
    "SUPABASE_URL",
    "SUPABASE_KEY",
]


def _missing_env_vars() -> list[str]:
    missing = []
    for k in REQUIRED_ENV_VARS:
        v = os.getenv(k)
        if not v:
            missing.append(k)
    return missing


def main() -> None:
    missing = _missing_env_vars()
    if missing:
        print("❌ Missing required env vars for live Trading Floor test:")
        for k in missing:
            print(f"  - {k}")
        print("\nSet them (and ensure Supabase is reachable) then rerun.")
        raise SystemExit(1)

    try:
        agent = JPMorganPoliticsAgent()
        theses = agent.update_theses()

        print("\n=== TEST RESULT: jpmorgan_politics ===")
        print(f"Theses generated: {len(theses)}")
        if theses:
            t0 = theses[0]
            print("Sample thesis:")
            print(f"  market_id: {t0.market_id}")
            print(f"  edge: {t0.edge:.2%}")
            print(f"  conviction: {t0.conviction:.2%}")

    except SystemExit:
        raise
    except Exception as e:
        print(f"❌ Live integration test failed: {type(e).__name__}: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    # Make stack traces available via `PYTHONFAULTHANDLER=1` if desired
    sys.exit(main())
