# TASK 36: Trading Dashboard - Build Plan

**Target:** 2-3 days, 4 phases

---

## PHASE 1: Data Layer + Overview Page (4 hours)

**Prompt:**
```
Create the trading dashboard data layer in Command Center:

1. **Supabase Client Setup**
   - Create `lib/supabase/trading.ts` with typed queries for:
     - getPortfolio() → { cash, total_value, deployed_pct, daily_pnl, all_time_pnl }
     - getPortfolioHistory(days=7) → array for sparkline
     - getMarkets(filters?) → paginated markets list
     - getPositions(status?) → open/closed positions
   
2. **Overview Page** (`app/trading/page.tsx`)
   - Server Component fetching portfolio + history
   - 4 stat cards: Cash, Total Value, Deployed %, Daily P&L
   - Sparkline component (recharts) showing 7-day portfolio value
   - "Bot Status" indicator (green/yellow/red) via FastAPI /health
   - Use shadcn/ui Card, Badge components

3. **Nav Integration**
   - Add "💰 Trading" to sidebar in `app/components/Sidebar.tsx`
   - Collapsible section with: Overview, Markets, Theses, Positions, Events, Memos

**Deliverable:** Working /trading page with live portfolio stats + sparkline

**Files to create:**
- `lib/supabase/trading.ts`
- `app/trading/page.tsx`
- `app/trading/components/PortfolioCard.tsx`
- `app/trading/components/Sparkline.tsx`
- `app/trading/components/BotStatus.tsx`

**Test:** Open http://localhost:3000/trading, see portfolio totals + 7-day chart
```

---

## PHASE 2: Markets + Theses Pages (3 hours)

**Prompt:**
```
Build Markets and Theses pages for the trading dashboard:

1. **Markets Page** (`app/trading/markets/page.tsx`)
   - Server Component with search params for filters
   - Data table (shadcn/ui) with columns:
     - Question (truncated, tooltip on hover)
     - Category (badge)
     - Yes/No prices
     - Volume 24h
     - Liquidity score
     - Days to resolution
   - Client-side filters: category dropdown, min volume slider, "tradeable only" toggle
   - Sort by: volume, liquidity, resolution date
   - Pagination (20 per page)

2. **Theses Page** (`app/trading/theses/page.tsx`)
   - Data table with columns:
     - Agent (icon + name)
     - Market question (link)
     - Edge % (color-coded: >10% green, 5-10% yellow, <5% gray)
     - Conviction (0-1 as percentage)
     - Proposed action (YES/NO badge)
     - Status (approved/rejected/executed)
     - Created timestamp
   - Filter by: status, min conviction, agent
   - "Promote to Task" button (modal → creates Command Center task with thesis text)

**Deliverable:** Filterable tables for markets and theses with working search/sort

**Files to create:**
- `app/trading/markets/page.tsx`
- `app/trading/theses/page.tsx`
- `app/trading/components/MarketTable.tsx`
- `app/trading/components/ThesisTable.tsx`
- `lib/supabase/trading.ts` (add getTheses, getMarkets queries)

**Test:** Filter markets by category, sort theses by conviction
```

---

## PHASE 3: Positions + Event Log (3 hours)

**Prompt:**
```
Build Positions and Event Log pages:

1. **Positions Page** (`app/trading/positions/page.tsx`)
   - Tabs: Open | Closed | All
   - Table columns:
     - Market question
     - Side (YES/NO badge)
     - Shares
     - Entry price / Current price
     - P&L $ (green/red)
     - P&L % (with trend icon ↑↓)
     - Stop-loss triggered? (badge if true)
     - Duration (open positions only)
   - Summary cards above table: Total Open P&L, Win Rate (closed), Largest Win/Loss
   - Click row → expand to show full thesis + entry reasoning

2. **Event Log Page** (`app/trading/events/page.tsx`)
   - Real-time log table with columns:
     - Timestamp (relative, e.g. "2m ago")
     - Severity (badge: INFO/WARN/ERROR with colors)
     - Event type (e.g. "TRADE_EXECUTED", "STOP_LOSS_TRIGGERED")
     - Message (truncated, expandable)
     - Market/Thesis links (if applicable)
   - Filters: severity, event type, date range
   - Auto-refresh every 10s (optional realtime subscription)
   - Export to CSV button

**Deliverable:** Position tracking + full audit trail with severity filtering

**Files to create:**
- `app/trading/positions/page.tsx`
- `app/trading/events/page.tsx`
- `app/trading/components/PositionTable.tsx`
- `app/trading/components/EventLog.tsx`
- `lib/supabase/trading.ts` (add getEvents, getPositionStats queries)

**Test:** Toggle between open/closed positions, filter events by severity
```

---

## PHASE 4: IC Memos + Polish (2 hours)

**Prompt:**
```
Complete the dashboard with IC Memos viewer + final polish:

1. **IC Memos Page** (`app/trading/memos/page.tsx`)
   - List view: Cards showing date + summary stats (trades count, win rate, daily return)
   - Click card → full memo view (markdown rendered)
   - Calendar navigation (jump to specific date)
   - "Latest memo" badge on most recent
   - Markdown rendering with syntax highlighting (react-markdown + rehype-highlight)

2. **Bot Status Enhancement**
   - FastAPI integration: fetch /health and /status every 30s
   - Status card on Overview showing:
     - Running? (green checkmark / red X)
     - Last cycle time
     - Mode (paper/live)
     - Uptime
     - Next cycle countdown
   - "Emergency Stop" button (calls /stop endpoint, requires confirmation modal)

3. **Polish**
   - Loading skeletons for all tables/cards
   - Error states (empty states with helpful messages)
   - Responsive layout (mobile-friendly tables with horizontal scroll)
   - Dark mode support (use Command Center's existing theme)
   - Add route transitions

**Deliverable:** Complete dashboard with memos, real-time status, professional polish

**Files to create:**
- `app/trading/memos/page.tsx`
- `app/trading/components/MemoViewer.tsx`
- `app/trading/components/BotStatusCard.tsx` (enhanced)
- `lib/api/trading.ts` (FastAPI client functions)

**Test:** 
- Navigate through all pages without errors
- Check dark mode
- View IC memo from 3 days ago
- Verify bot status updates every 30s
```

---

## Timeline

- **Day 1 PM:** Phase 1 (Overview + data layer)
- **Day 2 AM:** Phase 2 (Markets + Theses)
- **Day 2 PM:** Phase 3 (Positions + Events)
- **Day 3 AM:** Phase 4 (Memos + Polish)

**Total:** 12 hours focused work = 1.5 days compressed

---

## Pre-requisites

- Command Center repo cloned locally
- Supabase credentials in `.env.local`
- FastAPI bot running on localhost:8000 (for /health endpoint)
- shadcn/ui already installed in Command Center

---

## Phase-Complete Checklist

After each phase, verify:
- [ ] No TypeScript errors
- [ ] Page loads without console errors
- [ ] Data renders correctly (use real Supabase data)
- [ ] Mobile responsive
- [ ] Git commit with message "TASK 36 Phase N complete"
