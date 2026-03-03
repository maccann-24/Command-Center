# TASK 36: Execution Prompts (Copy-Paste Ready)

These prompts are written for you (Mac) to send to me. Each contains full context so I can execute without asking questions.

---

## PHASE 1: Data Layer + Overview Page

```
Build the trading dashboard foundation in Command Center. Work in the command-center repo.

**Context:**
- Supabase tables exist: portfolio, portfolio_history, markets, theses, positions, event_log, ic_memos
- FastAPI bot runs on localhost:8000 with /health and /status endpoints
- Command Center uses Next.js 14 (app router), TypeScript, shadcn/ui, Tailwind
- Supabase client already configured in lib/supabase/client.ts

**Tasks:**

1. Create `lib/supabase/trading.ts`:
   - Export typed functions:
     - `getPortfolio()` → fetch latest from portfolio table
     - `getPortfolioHistory(days: number)` → fetch last N days from portfolio_history, ordered by ts desc
     - Add proper TypeScript types for return values
   - Handle errors gracefully (return null/empty array, don't throw)

2. Create `app/trading/page.tsx`:
   - Server Component
   - Fetch portfolio + last 7 days history
   - Layout: 2x2 grid of stat cards + sparkline below
   - Cards show: Cash, Total Value, Deployed %, Daily P&L
   - P&L cards should be green/red based on positive/negative
   - Include a "Bot Status" indicator (fetch from localhost:8000/health, show green dot if healthy)

3. Create `app/trading/components/Sparkline.tsx`:
   - Client Component (use recharts)
   - Props: `data: Array<{ts: string, total_value: number}>`
   - Minimal line chart, no axes, just the trend line
   - Gradient fill under the line (green if trending up, red if down)
   - Responsive width

4. Create `app/trading/components/BotStatus.tsx`:
   - Client Component with useEffect polling localhost:8000/health every 30s
   - Show: green dot + "Running" or red dot + "Offline"
   - Display last_cycle_time if available

5. Update sidebar navigation:
   - Add "💰 Trading" section in `components/Sidebar.tsx`
   - Initially just link to /trading (we'll add subsections in Phase 2)

**Constraints:**
- Use existing shadcn/ui components (Card, Badge)
- Match Command Center's design system (dark mode support)
- No external state management, keep it simple (Server Components + minimal client state)
- All currency values formatted with $ and 2 decimals
- Percentages shown with 1 decimal + % symbol

**Deliverable:**
- Working /trading route showing live portfolio data
- Sparkline visualizing 7-day trend
- Bot status polling every 30s
- No TypeScript errors, builds successfully

**Test:**
Run `npm run dev` in command-center, navigate to http://localhost:3000/trading, verify data loads.

When complete, commit with message "TASK 36 Phase 1: Overview page + data layer" and tell me it's done.
```

---

## PHASE 2: Markets + Theses Pages

```
Build Markets and Theses pages for the trading dashboard. Continue in command-center repo.

**Context:**
- Phase 1 complete: /trading overview exists, lib/supabase/trading.ts has base queries
- Supabase tables: markets (id, question, category, yes_price, no_price, volume_24h, liquidity_score, resolution_date, resolved)
- Supabase tables: theses (id, agent_id, market_id, thesis_text, edge, conviction, proposed_action, status, created_at)

**Tasks:**

1. Extend `lib/supabase/trading.ts`:
   - Add `getMarkets(filters?: { category?, minVolume?, tradeable? })` → returns markets array
   - Add `getTheses(filters?: { status?, minConviction?, agentId? })` → returns theses array
   - Both should support pagination (offset/limit)
   - Include proper TypeScript interfaces for Market and Thesis

2. Create `app/trading/markets/page.tsx`:
   - Server Component with searchParams support
   - Fetch markets with filters from URL params
   - Render MarketTable component (create below)
   - Add filter controls (category dropdown, min volume slider, "tradeable only" checkbox)
   - Filters should update URL params (use useRouter for client component or form actions)

3. Create `app/trading/components/MarketTable.tsx`:
   - Client Component
   - shadcn/ui Table with columns: Question, Category, Yes/No Price, Volume 24h, Liquidity, Days to Resolution
   - Question column: truncate long text, show tooltip on hover
   - Category: render as Badge with color coding (politics=blue, sports=green, crypto=purple, etc.)
   - Prices: show as percentages (0.65 → 65%)
   - Volume: format with $ and K/M suffix (1500 → $1.5K)
   - Sortable columns (client-side)
   - Pagination footer (20 per page)

4. Create `app/trading/theses/page.tsx`:
   - Server Component with searchParams
   - Fetch theses with filters
   - Render ThesisTable component (create below)
   - Filter controls: status dropdown, min conviction slider, agent filter

5. Create `app/trading/components/ThesisTable.tsx`:
   - Client Component
   - Columns: Agent, Market, Edge %, Conviction, Action, Status, Created
   - Edge: color-coded (>10% green, 5-10% yellow, <5% gray)
   - Conviction: show as percentage
   - Action: YES/NO badge
   - Status: approved=green, rejected=red, executed=blue badge
   - Click row to expand and show full thesis_text
   - "Promote to Task" button (show modal with thesis, confirm creates task in Command Center - stub this for now)

6. Update sidebar:
   - Make "💰 Trading" collapsible with subsections: Overview, Markets, Theses

**Constraints:**
- Use shadcn/ui Table, Select, Slider components
- Keep filters client-side for responsiveness (fetch all data server-side, filter in browser)
- Mobile responsive: tables should horizontal scroll on small screens
- Loading states: show skeleton loaders while data fetches

**Deliverable:**
- /trading/markets with working filters and sortable table
- /trading/theses with expandable rows and status filtering
- Sidebar navigation with subsections

**Test:**
Filter markets by category, sort by volume. Filter theses by status="approved", verify only approved theses show.

When complete, commit with "TASK 36 Phase 2: Markets + Theses pages" and notify me.
```

---

## PHASE 3: Positions + Event Log

```
Build Positions and Event Log pages. Continue in command-center repo.

**Context:**
- Phases 1-2 complete: Overview, Markets, Theses working
- Supabase tables: positions (market_id, side, shares, entry_price, current_price, pnl, status, opened_at, closed_at)
- Supabase tables: event_log (timestamp, severity, event_type, message, market_id, thesis_id, metadata)

**Tasks:**

1. Extend `lib/supabase/trading.ts`:
   - Add `getPositions(status?: 'open' | 'closed')` → returns positions with market details (join on markets.id)
   - Add `getPositionStats()` → returns { total_open_pnl, win_rate, largest_win, largest_loss }
   - Add `getEvents(filters?: { severity?, eventType?, since? })` → returns event_log entries, newest first, limit 100

2. Create `app/trading/positions/page.tsx`:
   - Server Component with tab support (searchParams.tab = 'open' | 'closed' | 'all')
   - Fetch positions based on active tab
   - Fetch position stats for summary cards
   - Render 3 summary cards above table: Total Open P&L, Win Rate, Largest Win/Loss
   - Render PositionTable component

3. Create `app/trading/components/PositionTable.tsx`:
   - Client Component
   - Columns: Market, Side, Shares, Entry Price, Current Price, P&L $, P&L %, Stop-Loss?, Duration
   - P&L $: green if positive, red if negative, bold
   - P&L %: include trend icon (↑ if positive, ↓ if negative)
   - Stop-Loss: show red badge "TRIGGERED" if true
   - Duration: for open positions, show "Xd Yh" format; for closed, show total hold time
   - Click row to expand: show full thesis that led to this position
   - Tabs component at top: Open (default) | Closed | All

4. Create `app/trading/events/page.tsx`:
   - Client Component (needs real-time updates)
   - Fetch initial events server-side, pass to client
   - useEffect with 10s polling to refresh events (or use Supabase realtime subscription)
   - Filter controls: severity (INFO/WARN/ERROR), event type dropdown, date range picker
   - "Export CSV" button (download current filtered events)

5. Create `app/trading/components/EventLog.tsx`:
   - Client Component
   - Table columns: Timestamp (relative, e.g. "2m ago"), Severity, Type, Message, Links
   - Severity: colored badge (INFO=gray, WARN=yellow, ERROR=red)
   - Message: truncate to 100 chars, click to expand in modal
   - Links: if market_id or thesis_id present, render as clickable links to /trading/markets or /trading/theses
   - Auto-scroll to top when new events arrive
   - Max 100 events displayed

6. Update sidebar:
   - Add Positions and Events to subsections

**Constraints:**
- Use shadcn/ui Tabs, Badge, Dialog components
- Relative timestamps: use date-fns (formatDistanceToNow)
- CSV export: simple client-side generation, no backend needed
- Real-time updates: prefer Supabase realtime if easy, otherwise 10s polling is fine

**Deliverable:**
- /trading/positions with tabs, expandable rows, summary stats
- /trading/events with auto-refresh, severity filtering, CSV export
- Full audit trail visibility

**Test:**
Toggle between Open/Closed tabs. Filter events by severity=ERROR. Click a position row to see thesis.

When complete, commit with "TASK 36 Phase 3: Positions + Event Log" and notify me.
```

---

## PHASE 4: IC Memos + Polish

```
Complete the dashboard with IC Memos viewer and final polish. Final phase of TASK 36.

**Context:**
- Phases 1-3 complete: Overview, Markets, Theses, Positions, Events all working
- Supabase table: ic_memos (date, memo_text, portfolio_summary, trades_count, win_rate, daily_return, created_at)
- memo_text is markdown format with sections: Portfolio Summary, Active Theses, Trades Executed, Performance Metrics

**Tasks:**

1. Extend `lib/supabase/trading.ts`:
   - Add `getMemos(limit?: number)` → returns ic_memos ordered by date desc
   - Add `getMemoByDate(date: string)` → fetches specific memo

2. Create `lib/api/trading.ts`:
   - FastAPI client functions:
     - `getBotHealth()` → fetch from localhost:8000/health
     - `getBotStatus()` → fetch from localhost:8000/status (returns runtime stats)
     - `emergencyStop()` → POST to localhost:8000/stop
   - All with proper error handling (return null on failure)

3. Create `app/trading/memos/page.tsx`:
   - Server Component
   - Fetch last 30 memos
   - List view: Card grid showing date + summary stats (trades count, win rate, daily return)
   - "Latest" badge on most recent memo
   - Click card → navigate to /trading/memos/[date] (detail view)

4. Create `app/trading/memos/[date]/page.tsx`:
   - Server Component, fetch memo by date param
   - Render full memo_text as markdown (use react-markdown + rehype-highlight for syntax)
   - Back button to return to list
   - Navigation: Previous/Next memo buttons (by date)

5. Enhance `app/trading/components/BotStatus.tsx`:
   - Upgrade to BotStatusCard (larger, more detailed)
   - Show: Running?, Last cycle time, Mode (paper/live), Uptime, Next cycle countdown
   - Poll both /health and /status every 30s
   - Add "Emergency Stop" button (shows confirmation modal before calling emergencyStop())
   - Visual states: green=healthy, yellow=degraded, red=offline

6. Add loading skeletons:
   - Create `app/trading/components/Skeleton.tsx` (generic skeleton for cards/tables)
   - Add to all pages: show skeleton while data loads
   - Use Suspense boundaries where appropriate

7. Error states:
   - Empty state components for each page (no markets, no theses, etc.)
   - Friendly messages: "No open positions yet" with icon
   - Error boundary for failed data fetches

8. Responsive polish:
   - All tables: horizontal scroll on mobile (<768px)
   - Cards: stack vertically on mobile
   - Test on 375px width (iPhone SE)

9. Dark mode:
   - Verify all components respect Command Center's theme
   - Charts should adapt colors (use CSS variables)

10. Update sidebar:
    - Add Memos to subsections
    - Final order: Overview, Markets, Theses, Positions, Events, Memos

**Constraints:**
- Use react-markdown, rehype-highlight for memo rendering
- Emergency stop requires double confirmation (modal + "Type STOP to confirm")
- All loading states should match Command Center's existing skeleton style
- Empty states should be encouraging, not depressing
- Mobile-first responsive design

**Deliverable:**
- /trading/memos with calendar navigation
- Enhanced bot status card with emergency controls
- Full loading + error states across all pages
- Professional polish, production-ready UI
- Complete sidebar navigation

**Test checklist:**
- [ ] Navigate through all 6 pages without errors
- [ ] Toggle dark mode, verify readability
- [ ] View IC memo from 7 days ago
- [ ] Trigger emergency stop (test modal, don't actually stop bot)
- [ ] Resize browser to 375px width, verify usability
- [ ] All data loads with proper skeletons
- [ ] Empty states show when no data exists

When complete:
1. Run full build: `npm run build` (must succeed)
2. Commit with "TASK 36 Phase 4: IC Memos + Polish - Dashboard complete"
3. Take screenshot of /trading overview page
4. Notify me with summary of what's working

This completes TASK 36. 🎉
```

---

## Quick Reference

**To execute:**
1. Copy prompt for Phase N
2. Send to me in Telegram
3. I execute without asking questions
4. I notify when complete
5. Repeat for next phase

**Total time:** 1.5 days (12 hours focused)

**Dependencies:**
- Command Center repo at `~/clawd/agents/coding/command-center`
- Supabase credentials in `.env.local`
- Trading bot running (for /health endpoint testing)

**Completion criteria:**
All 6 pages functional, no build errors, mobile responsive, production-ready.
