-- RLS for Based Money tables (recommended)
-- Run in Supabase SQL editor for the *trading* project.

-- Enable RLS
alter table if exists public.portfolio enable row level security;
alter table if exists public.positions enable row level security;
alter table if exists public.theses enable row level security;
alter table if exists public.event_log enable row level security;
alter table if exists public.markets enable row level security;
alter table if exists public.news_events enable row level security;

-- Authenticated read access (tightest reasonable default for a personal dashboard)
create policy if not exists "auth read portfolio" on public.portfolio
for select to authenticated
using (true);

create policy if not exists "auth read positions" on public.positions
for select to authenticated
using (true);

create policy if not exists "auth read theses" on public.theses
for select to authenticated
using (true);

create policy if not exists "auth read event_log" on public.event_log
for select to authenticated
using (true);

create policy if not exists "auth read markets" on public.markets
for select to authenticated
using (true);

create policy if not exists "auth read news_events" on public.news_events
for select to authenticated
using (true);

-- NOTE: Writes are performed by the bot using the anon key today.
-- For best security, migrate bot writes to service_role key or use Edge Functions.
