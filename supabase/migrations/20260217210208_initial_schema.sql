-- ============================================
-- Command Center - Initial Schema (Phase 1)
-- ============================================

-- Agents table (the AI agents being managed)
create table if not exists agents (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  model text not null default 'anthropic/claude-sonnet-4-5',
  status text not null default 'idle' check (status in ('active', 'idle', 'error')),
  personality text,
  version text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Sessions table (individual agent sessions)
create table if not exists sessions (
  id uuid primary key default gen_random_uuid(),
  agent_id uuid references agents(id) on delete cascade,
  status text not null default 'active' check (status in ('active', 'completed', 'error')),
  current_task text,
  last_heartbeat timestamptz default now(),
  bandwidth_pct integer default 0 check (bandwidth_pct >= 0 and bandwidth_pct <= 100),
  start_time timestamptz not null default now(),
  end_time timestamptz,
  created_at timestamptz not null default now()
);

-- Messages table (conversation history)
create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references sessions(id) on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  timestamp timestamptz not null default now(),
  created_at timestamptz not null default now()
);

-- Metrics table (token usage & costs)
create table if not exists metrics (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references sessions(id) on delete cascade,
  tokens_input integer not null default 0,
  tokens_output integer not null default 0,
  tokens_total integer not null default 0,
  cost numeric(10, 6) not null default 0,
  duration_ms integer,
  created_at timestamptz not null default now()
);

-- ============================================
-- INDEXES
-- ============================================

create index if not exists idx_sessions_agent_id on sessions(agent_id);
create index if not exists idx_sessions_status on sessions(status);
create index if not exists idx_messages_session_id on messages(session_id);
create index if not exists idx_metrics_session_id on metrics(session_id);

-- ============================================
-- ADD NEW COLUMNS TO EXISTING TABLES (if missing)
-- ============================================

alter table agents add column if not exists personality text;
alter table agents add column if not exists version text;
alter table sessions add column if not exists current_task text;
alter table sessions add column if not exists last_heartbeat timestamptz default now();
alter table sessions add column if not exists bandwidth_pct integer default 0;

-- ============================================
-- AUTO-UPDATE updated_at TRIGGER
-- ============================================

create or replace function update_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger agents_updated_at before update on agents
  for each row execute function update_updated_at();

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

alter table agents enable row level security;
alter table sessions enable row level security;
alter table messages enable row level security;
alter table metrics enable row level security;

create policy "anon read agents" on agents for select using (true);
create policy "anon write agents" on agents for all using (true);

create policy "anon read sessions" on sessions for select using (true);
create policy "anon write sessions" on sessions for all using (true);

create policy "anon read messages" on messages for select using (true);
create policy "anon write messages" on messages for all using (true);

create policy "anon read metrics" on metrics for select using (true);
create policy "anon write metrics" on metrics for all using (true);

-- No seed data: all data must be real
