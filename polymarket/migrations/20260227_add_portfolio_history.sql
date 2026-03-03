-- Add portfolio_history table for sparklines / equity curve snapshots

create table if not exists public.portfolio_history (
  id bigserial primary key,
  ts timestamptz not null default now(),
  cash numeric(15,2) not null,
  total_value numeric(15,2) not null,
  deployed_pct numeric(6,2) not null default 0,
  daily_pnl numeric(15,2) not null default 0,
  all_time_pnl numeric(15,2) not null default 0
);

create index if not exists idx_portfolio_history_ts_desc
  on public.portfolio_history (ts desc);
