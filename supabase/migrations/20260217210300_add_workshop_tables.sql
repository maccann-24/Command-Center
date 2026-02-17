-- ============================================
-- Workshop Tables (Kanban + Task System)
-- ============================================

-- Tasks table
create table if not exists tasks (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text,
  status text not null default 'queued' check (status in ('queued', 'in_progress', 'done')),
  priority text not null default 'medium' check (priority in ('low', 'medium', 'high')),
  momentum_score integer not null default 0 check (momentum_score >= 0 and momentum_score <= 100),
  assigned_agent_id uuid references agents(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Task details (extended info)
create table if not exists task_details (
  id uuid primary key default gen_random_uuid(),
  task_id uuid references tasks(id) on delete cascade unique,
  full_description text,
  acceptance_criteria text,
  notes text,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Task history (audit trail)
create table if not exists task_history (
  id uuid primary key default gen_random_uuid(),
  task_id uuid references tasks(id) on delete cascade,
  action text not null check (action in ('created', 'status_changed', 'edited', 'assigned', 'deleted')),
  changed_by text default 'system',
  changes jsonb default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- ============================================
-- INDEXES
-- ============================================

create index if not exists idx_tasks_status on tasks(status);
create index if not exists idx_tasks_momentum on tasks(momentum_score desc);
create index if not exists idx_task_history_task_id on task_history(task_id);

-- ============================================
-- AUTO-UPDATE updated_at TRIGGERS
-- ============================================

create or replace function update_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger tasks_updated_at before update on tasks
  for each row execute function update_updated_at();

create trigger task_details_updated_at before update on task_details
  for each row execute function update_updated_at();

-- ============================================
-- TASK HISTORY AUTO-LOG TRIGGER
-- ============================================

create or replace function log_task_status_change()
returns trigger as $$
begin
  if old.status is distinct from new.status then
    insert into task_history (task_id, action, changes)
    values (new.id, 'status_changed', jsonb_build_object(
      'from', old.status,
      'to', new.status
    ));
  end if;
  return new;
end;
$$ language plpgsql;

create trigger task_status_history after update on tasks
  for each row execute function log_task_status_change();

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

alter table tasks enable row level security;
alter table task_details enable row level security;
alter table task_history enable row level security;

create policy "anon read tasks" on tasks for select using (true);
create policy "anon write tasks" on tasks for all using (true);

create policy "anon read task_details" on task_details for select using (true);
create policy "anon write task_details" on task_details for all using (true);

create policy "anon read task_history" on task_history for select using (true);
create policy "anon write task_history" on task_history for all using (true);
