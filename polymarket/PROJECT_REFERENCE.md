# Polymarket Bot - Project Reference

This file is meant as a **single, durable reference** for the entire codebase (structure, data model, and how to run things) in case chat memory/context gets compacted.

## 1) What this project is
A research/backtesting + execution scaffold for trading **Polymarket prediction markets**.

Core capabilities implemented so far:
- Market ingestion + filtering
- Thesis generation/storage
- Portfolio/positions representation
- Backtesting engine + metrics + validation
- Risk engine + tests
- Daily IC memo generator (markdown) with optional DB persistence

Key design docs to read first:
- `SYSTEM_DESIGN.md`
- `REVIEW_STATUS.md`
- `COMPREHENSIVE_REVIEW.md`

## 2) Repository layout (high level)

- `config.py`
  - Central config/env validation.
  - Uses `.env` (do **not** commit) and `.env.example` for required variables.

- `schema.sql`
  - Postgres/Supabase schema (tables + indexes).
  - Includes `ic_memos` table used by the memo generator.

- `models/`
  - Dataclasses / core domain objects (markets, theses, portfolio, news).

- `ingestion/`
  - Fetching and filtering Polymarket markets.
  - `ingestion/polymarket.py` is the main ingestion entry.
  - `ingestion/filters.py` contains filter logic.

- `agents/`
  - "Agent" abstractions (base agent + specialized agents like geo/signals).

- `core/`
  - `core/thesis_store.py`: thesis persistence/querying.
  - `core/risk.py`: risk rules/limits used by strategy/execution.
  - `core/memo.py`: Daily IC memo generation + optional save to `ic_memos`.
  - `core/execution.py`: Execution engine (orchestrates trade flow with safety checks).
  - `core/positions.py`: Position monitor (tracks P&L, triggers stop-losses).
  - `core/orchestrator.py`: Main control loop (coordinates entire trading system).

- `brokers/`
  - `brokers/base.py`: Broker adapter interface (ABC, Order, Execution dataclasses).
  - `brokers/paper.py`: Paper broker implementation (simulated execution with 1% slippage).

- `backtesting/`
  - `data_loader.py`: loads historical snapshots/data for markets.
  - `engine.py` (or equivalent): runs strategies on historical series.
  - `metrics.py`: performance metrics (returns, sharpe, etc.).
  - `validator.py`: sanity checks & validation of backtests.

- `tests/`
  - Some tests live at repo root as `test_*.py` (structure + unit behavior).
  - Risk tests: `tests/test_risk.py`

## 3) Database model (schema.sql)
Main tables referenced by the code/docs:
- `markets`, `historical_markets`
- `news_events`
- `theses`
- `portfolio`, `positions`
- `trader_performance`
- `ic_memos`
- `event_log`

### ic_memos table
Defined in `schema.sql`:
- `date` (unique)
- `memo_text` (markdown)
- `portfolio_summary` (JSONB snapshot)
- `trades_count`, `win_rate`, `daily_return`, `created_at`

## 4) Daily IC Memo generator
Implemented in: `core/memo.py`

Primary function:
- `generate_daily_memo(memo_date, theses, portfolio, trades) -> str`

Memo sections (markdown):
- Portfolio Summary
- Active Theses (table)
- Trades Executed (table)
- Performance Metrics (win rate; sharpe when sufficient data)
- Disclaimer

Persistence:
- Attempts to `upsert` into `ic_memos` (by `date`) **only if env vars are present**.
- If DB env isn't configured, it safely no-ops.

Test harness:
- `test_memo_generator.py` (standalone, prints the memo and asserts structure)

## 5) Risk engine
Implemented in: `core/risk.py`

Validated behaviors (see `tests/test_risk.py`):
- Max position size checks
- Max daily loss checks
- Stop-loss enforcement
- Concentration limits

## 6) Backtesting
Docs + scaffolding:
- `BACKTESTING_QUICK_START.md`
- Task summaries: `TASK_14_*` through `TASK_17_*` outline what was built and why.

## 7) Execution Layer

**Broker Adapters** (`brokers/`)
- Abstract `BrokerAdapter` interface with 3 methods:
  - `execute_order(order) -> Execution` (idempotent)
  - `get_position(market_id) -> Position | None` (fresh state)
  - `cancel_order(order_id) -> bool` (graceful)
- `PaperBroker`: Simulated execution with 1% slippage, instant fills
- Ready for live broker implementations (PolymarketBroker)

**Execution Engine** (`core/execution.py`)
- 8-step execution flow: safety check → double-check → order → broker → position → save → portfolio → log
- Safety: SecurityError on rejected, double-check catches stale approvals
- Best-effort persistence, graceful degradation

**Position Monitor** (`core/positions.py`)
- `update_positions()`: Fetch positions, query broker, calculate P&L, save updates
- `check_stop_losses(positions, stop_loss_pct)`: Check loss %, generate exit orders (opposite side)
- Stop-loss: triggers when `loss_pct < -stop_loss_pct`

**Orchestrator** (`core/orchestrator.py`)
- Main control loop: positions → stop-losses → portfolio → theses → risk → execution
- `run_cycle()`: One complete cycle, returns stats
- `run_forever(cycle_delay=60)`: Continuous loop with error handling
- Milestone logging every 10 cycles

## 8) Environment / setup

### Required env vars
See `.env.example` for the authoritative list.
Common ones referenced by code:
- `TRADING_MODE`
- `SUPABASE_URL`
- `SUPABASE_KEY`

### Local venv (recommended)
From repo root:
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### Running tests
```bash
. .venv/bin/activate
pytest -q

# Or specific suites:
pytest -q tests/test_risk.py
python test_memo_generator.py
```

## 9) "Task" document index
The repo contains a sequence of build summaries:
- `TASK_4_SUMMARY.md` … `TASK_12_SUMMARY.md`
- `TASK_13_THESIS_STORE_COMPLETE.md`
- `TASK_14_HISTORICAL_DATA_COMPLETE.md`
- `TASK_15_BACKTEST_ENGINE_COMPLETE.md`
- `TASK_16_METRICS_COMPLETE.md`
- `TASK_17_VALIDATOR_COMPLETE.md`
- `TASK_18_RISK_ENGINE_COMPLETE.md`
- `TASK_19_RISK_TESTS_COMPLETE.md`

If you need to quickly understand *why* something exists, these are the fastest path.

---

### Notes / guardrails
- Do **not** commit `.env`.
- Avoid committing `.venv/`, `__pycache__/`, `*.pyc` (covered by `.gitignore`).
- This reference intentionally avoids secrets/keys; keep credentials out of the repo.
