# Command Center (Mission Control) — Project Reference

## Overview

A personal AI operations dashboard built in Next.js + Supabase + Tailwind, deployed on Vercel. The user's name for it is "Command Center" (also called "Mission Control" — a term trending on Twitter). The UI is inspired by Apple's liquid glass aesthetic. The user built this by talking to Jarvis (the AI) and describing what they wanted — no prior coding experience.

Live URL: https://command-center-dm3n.vercel.app
GitHub: https://github.com/maccann-24/Command-Center
Stack: Next.js (App Router), Supabase (Postgres + Realtime), Tailwind CSS, Vercel, Recharts

The core purpose: full visibility and control over all AI agents, their work, their costs, and their plans — from one beautiful dashboard.

---

## Architecture

- **Frontend:** Next.js App Router, TypeScript, Tailwind CSS
- **Backend:** Supabase (Postgres + Realtime subscriptions + Row Level Security)
- **Deployment:** Vercel (auto-deploys from GitHub)
- **Data ingestion:** Hourly cron script on gateway (`~/scripts/clawdbot-logger.sh`) POSTs token/cost metrics to `/api/metrics`
- **Auth:** None (anon key, open RLS policies — internal tool only)

### Database Tables
- `agents` — AI agents being managed (name, model, status, personality, version)
- `sessions` — individual agent sessions (agent_id, status, current_task, last_heartbeat, bandwidth_pct)
- `messages` — conversation history per session (role, content, timestamp)
- `metrics` — token usage & costs per session (tokens_input, tokens_output, tokens_total, cost)
- `tasks` — Workshop Kanban tasks (title, description, status, priority, momentum_score, assigned_agent_id)
- `task_details` — extended task info (full_description, acceptance_criteria, notes, metadata)
- `task_history` — audit trail of task changes (action, changes, changed_by)

---

## What's Built (Phase 1 ✅)

### Dashboard (Home)
- Stat cards: Total Agents, Total Sessions, Total Messages, Total Cost
- **Heartbeat Monitor** — shows last sync time, time since, next ETA, NOMINAL/DELAYED/OFFLINE status
- Active agents list with status badges
- Recent activity feed (last 5 sessions)
- LIVE indicator that flashes green on real-time Supabase updates

### Agents Page
- Grid of agent cards (name, model, status badge)
- Create Agent modal
- Search + filter by status
- Delete agent
- Links to individual agent detail + settings pages

### Workshop (Kanban)
- Three columns: Queued / In Progress / Done
- Tasks sorted by **momentum score** (0–100) — highest momentum task gets highlighted as "Start Next"
- Task cards show title, priority, momentum score
- Add Task modal (title, description, priority)
- Task Detail modal — view full description, acceptance criteria, notes
- **Recalculate Momentum** button
- Real-time Supabase updates (live flash indicator)
- Task history auto-logged via Postgres trigger

### Analytics
- 7-day charts: Cost Over Time (area), Sessions Per Day (area), Token Usage by Agent (bar)
- Summary cards: Total Sessions, Total Tokens (k), Total Cost
- Token distribution breakdown (input vs output %)
- Avg cost per session + most expensive session
- Cost per agent table
- Cost estimated at Claude Sonnet 4.5 rates ($3/1M input, $15/1M output)

### Sessions Page
- List of all sessions with agent name, status, message count, tokens, cost
- Search by agent name + filter by status
- Links to individual session detail view

### Cost Logger Integration
- Script: `/home/ubuntu/scripts/clawdbot-logger.sh`
- Runs hourly via gateway cron
- Reads `clawdbot status` for token usage
- Calculates delta since last run
- POSTs to `/api/metrics` on Vercel

---

## What's NOT Built Yet — Remaining Phases

### Phase 2: Cron Jobs Dashboard
A dedicated tab/page showing all scheduled jobs running inside Clawdbot — the things baked in that run every 24 hours (or other intervals). User wants to be able to see:
- What cron jobs exist
- Their schedule
- Last run time / next run time
- What they do (description)
Think of it like a cron job "inbox" — at a glance visibility into all automated background activity.

### Phase 3: Twitter Ideas Feed → Workshop Deploy
The agent (running the bird/Twitter skill) periodically searches Twitter for top AI use cases relevant to the user's goals. These surface in Command Center in an **email-style feed view**:
- Each "idea" is a card with a snapshot/preview of what the use case would look like for the user specifically
- The user reads through them, decides if they like one
- Hits **Deploy** → the task is automatically created in Workshop queue with appropriate momentum score
This closes the loop between discovery (what's possible) and execution (what to build next). It's a key differentiator from what others are building.

### Phase 4: PDF / Doc Digest
An upload area inside Command Center where the user can feed the agent documents (PDFs, etc.) to build up its intelligence and context. Key features:
- Drag-and-drop or file picker upload
- Processes at ~50 pages/second
- Digested content stored and made searchable
- Agent can reference this knowledge base when working on tasks
The user found that dumping documents directly into the chat was too slow — this provides a structured, fast intake pipeline.

### Phase 5: Agent Hub (Inter-Agent Comms Viewer)
A view that shows all agents (Jarvis + sub-agents) and their conversations with each other. Key features:
- **Jarvis** is the commander; sub-agents are "employees" with distinct personalities and roles
- Example sub-agent: "The Architect" — audits Mission Control every 24h, finds bugs/improvements, works on them overnight
- Hub view shows messages between agents in real-time (what Jarvis is telling each sub-agent)
- All agent work output flows into Workshop for visibility
- Eventually: many specialized agents all visible and coordinated from this one hub
This is the most ambitious phase — transforms Command Center from a monitoring tool into a true multi-agent command center.

---

## Key Design Principles
- **Apple liquid glass aesthetic** — the user explicitly values beautiful UI; this is a differentiator vs the "ugly" Mission Control dashboards others are building on Twitter
- **Real-time everything** — Supabase Realtime subscriptions on all key tables; LIVE indicator
- **Momentum-driven work** — tasks ranked by momentum score so the agent always works on the highest-impact next thing
- **Full visibility** — the user should never have to guess what the agent is doing, planning, or spending
- **No surprises on cost** — the analytics/cost tracking exists specifically so the user doesn't accidentally spend thousands on API usage

---

## Agents Configured
- **Coding** (`anthropic/claude-sonnet-4-5`) — main agent, the "Jarvis" / commander
- **Idea Generation** (`openai/gpt-5.2`) — newly created 2026-02-18, workspace initialized

---

## Agent Behavior Requirements

- **Task lifecycle management:** When Jarvis completes a task, it MUST update the task status in Supabase from `in_progress` → `done`. Tasks must not remain stuck in "In Progress" after work is finished. Always close the loop: mark complete in DB before moving on.

---

## Notes
- The `.gitignore` correctly blocks `.env*` files — no secrets committed
- Supabase `.temp/` directory was accidentally committed to the public repo (project ref exposed, no password) — fix: `git rm -r --cached supabase/.temp/` + add to `.gitignore`
- The `messages` table exists in schema but nothing writes to it yet — a future integration point
- The Workshop task assignment to agents exists in DB schema but task dispatch to actual Clawdbot agents isn't wired up yet
