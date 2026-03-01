import { supabase } from "../supabase"

/**
 * Trading Dashboard - Supabase Queries
 * Type-safe data layer for the trading dashboard
 */

// ============================================================
// TYPES
// ============================================================

export type Portfolio = {
  id: number
  cash: number
  total_value: number
  deployed_pct: number
  daily_pnl: number
  all_time_pnl: number
  updated_at: string
}

export type PortfolioHistoryPoint = {
  id: number
  ts: string
  cash: number
  total_value: number
  deployed_pct: number
  daily_pnl: number
  all_time_pnl: number
}

export type Market = {
  id: string
  question: string
  category: string | null
  yes_price: number | null
  no_price: number | null
  volume_24h: number | null
  resolution_date: string | null
  resolved: boolean
  liquidity_score: number | null
  created_at: string
  updated_at: string
}

export type Thesis = {
  id: string
  agent_id: string
  market_id: string
  thesis_text: string
  fair_value: number
  current_odds: number
  edge: number
  conviction: number
  horizon: string | null
  proposed_action: {
    side: "YES" | "NO"
    size_pct: number
  }
  status: "active" | "executed" | "expired" | "rejected"
  created_at: string
  updated_at: string
}

export type Position = {
  id: string
  market_id: string
  thesis_id: string | null
  side: "YES" | "NO"
  shares: number
  entry_price: number
  current_price: number
  pnl: number
  status: "open" | "closed" | "stopped_out"
  opened_at: string
  closed_at: string | null
  created_at: string
  updated_at: string
  market?: Market // Optional joined market data
}

export type EventLog = {
  id: number
  timestamp: string
  event_type: string
  agent_id: string | null
  market_id: string | null
  thesis_id: string | null
  position_id: string | null
  details: Record<string, any> | null
  severity: "info" | "warning" | "error" | "critical"
  message: string | null
  created_at: string
}

export type ICMemo = {
  id: string
  date: string
  memo_text: string
  portfolio_summary: Record<string, any> | null
  trades_count: number
  win_rate: number | null
  daily_return: number | null
  created_at: string
}

// ============================================================
// FILTERS
// ============================================================

export type MarketFilters = {
  category?: string
  minVolume?: number
  tradeable?: boolean // resolved === false
  limit?: number
  offset?: number
}

export type ThesisFilters = {
  status?: "active" | "executed" | "expired" | "rejected"
  minConviction?: number
  agentId?: string
  limit?: number
  offset?: number
}

export type PositionFilters = {
  status?: "open" | "closed" | "stopped_out"
  limit?: number
  offset?: number
}

export type EventFilters = {
  severity?: "info" | "warning" | "error" | "critical"
  eventType?: string
  since?: string // ISO timestamp
  limit?: number
  offset?: number
}

// ============================================================
// QUERIES
// ============================================================

/**
 * Get current portfolio state
 */
export async function getPortfolio(): Promise<Portfolio | null> {
  try {
    const { data, error } = await supabase
      .from("portfolio")
      .select("*")
      .eq("id", 1)
      .single()

    if (error) {
      console.error("Error fetching portfolio:", error)
      return null
    }

    return data as Portfolio
  } catch (err) {
    console.error("Unexpected error fetching portfolio:", err)
    return null
  }
}

/**
 * Get portfolio history for sparkline
 * @param days - Number of days to fetch (default: 7)
 */
export async function getPortfolioHistory(
  days: number = 7
): Promise<PortfolioHistoryPoint[]> {
  try {
    const cutoff = new Date()
    cutoff.setDate(cutoff.getDate() - days)

    const { data, error } = await supabase
      .from("portfolio_history")
      .select("*")
      .gte("ts", cutoff.toISOString())
      .order("ts", { ascending: true })

    if (error) {
      console.error("Error fetching portfolio history:", error)
      return []
    }

    return (data as PortfolioHistoryPoint[]) || []
  } catch (err) {
    console.error("Unexpected error fetching portfolio history:", err)
    return []
  }
}

/**
 * Get markets with optional filters
 */
export async function getMarkets(
  filters?: MarketFilters
): Promise<Market[]> {
  try {
    let query = supabase.from("markets").select("*")

    // Apply filters
    if (filters?.category) {
      query = query.eq("category", filters.category)
    }

    if (filters?.minVolume !== undefined) {
      query = query.gte("volume_24h", filters.minVolume)
    }

    if (filters?.tradeable) {
      query = query.eq("resolved", false)
    }

    // Pagination
    const limit = filters?.limit ?? 100
    const offset = filters?.offset ?? 0
    query = query.range(offset, offset + limit - 1)

    // Default ordering
    query = query.order("volume_24h", { ascending: false, nullsFirst: false })

    const { data, error } = await query

    if (error) {
      console.error("Error fetching markets:", error)
      return []
    }

    return (data as Market[]) || []
  } catch (err) {
    console.error("Unexpected error fetching markets:", err)
    return []
  }
}

/**
 * Get theses with optional filters
 */
export async function getTheses(
  filters?: ThesisFilters
): Promise<Thesis[]> {
  try {
    let query = supabase.from("theses").select("*")

    // Apply filters
    if (filters?.status) {
      query = query.eq("status", filters.status)
    }

    if (filters?.minConviction !== undefined) {
      query = query.gte("conviction", filters.minConviction)
    }

    if (filters?.agentId) {
      query = query.eq("agent_id", filters.agentId)
    }

    // Pagination
    const limit = filters?.limit ?? 100
    const offset = filters?.offset ?? 0
    query = query.range(offset, offset + limit - 1)

    // Default ordering
    query = query.order("created_at", { ascending: false })

    const { data, error } = await query

    if (error) {
      console.error("Error fetching theses:", error)
      return []
    }

    return (data as Thesis[]) || []
  } catch (err) {
    console.error("Unexpected error fetching theses:", err)
    return []
  }
}

/**
 * Get positions with optional filters and joined market data
 */
export async function getPositions(
  filters?: PositionFilters
): Promise<Position[]> {
  try {
    let query = supabase
      .from("positions")
      .select(`
        *,
        market:markets(*)
      `)

    // Apply filters
    if (filters?.status) {
      query = query.eq("status", filters.status)
    }

    // Pagination
    const limit = filters?.limit ?? 100
    const offset = filters?.offset ?? 0
    query = query.range(offset, offset + limit - 1)

    // Default ordering
    query = query.order("opened_at", { ascending: false })

    const { data, error } = await query

    if (error) {
      console.error("Error fetching positions:", error)
      return []
    }

    return (data as Position[]) || []
  } catch (err) {
    console.error("Unexpected error fetching positions:", err)
    return []
  }
}

/**
 * Get position statistics (for summary cards)
 */
export async function getPositionStats(): Promise<{
  total_open_pnl: number
  win_rate: number | null
  largest_win: number
  largest_loss: number
} | null> {
  try {
    // Fetch all positions
    const { data: positions, error } = await supabase
      .from("positions")
      .select("pnl, status")

    if (error) {
      console.error("Error fetching position stats:", error)
      return null
    }

    if (!positions || positions.length === 0) {
      return {
        total_open_pnl: 0,
        win_rate: null,
        largest_win: 0,
        largest_loss: 0,
      }
    }

    // Calculate stats
    const openPositions = positions.filter((p) => p.status === "open")
    const closedPositions = positions.filter((p) => p.status === "closed")

    const total_open_pnl = openPositions.reduce(
      (sum, p) => sum + (p.pnl || 0),
      0
    )

    const wins = closedPositions.filter((p) => (p.pnl || 0) > 0).length
    const win_rate =
      closedPositions.length > 0 ? (wins / closedPositions.length) * 100 : null

    const allPnls = positions.map((p) => p.pnl || 0)
    const largest_win = allPnls.length > 0 ? Math.max(...allPnls) : 0
    const largest_loss = allPnls.length > 0 ? Math.min(...allPnls) : 0

    return {
      total_open_pnl,
      win_rate,
      largest_win,
      largest_loss,
    }
  } catch (err) {
    console.error("Unexpected error fetching position stats:", err)
    return null
  }
}

/**
 * Get event log entries with optional filters
 */
export async function getEvents(
  filters?: EventFilters
): Promise<EventLog[]> {
  try {
    let query = supabase.from("event_log").select("*")

    // Apply filters
    if (filters?.severity) {
      query = query.eq("severity", filters.severity)
    }

    if (filters?.eventType) {
      query = query.eq("event_type", filters.eventType)
    }

    if (filters?.since) {
      query = query.gte("timestamp", filters.since)
    }

    // Pagination
    const limit = filters?.limit ?? 100
    const offset = filters?.offset ?? 0
    query = query.range(offset, offset + limit - 1)

    // Default ordering (newest first)
    query = query.order("timestamp", { ascending: false })

    const { data, error } = await query

    if (error) {
      console.error("Error fetching events:", error)
      return []
    }

    return (data as EventLog[]) || []
  } catch (err) {
    console.error("Unexpected error fetching events:", err)
    return []
  }
}

/**
 * Get IC memos
 * @param limit - Number of memos to fetch (default: 30)
 */
export async function getMemos(limit: number = 30): Promise<ICMemo[]> {
  try {
    const { data, error } = await supabase
      .from("ic_memos")
      .select("*")
      .order("date", { ascending: false })
      .limit(limit)

    if (error) {
      console.error("Error fetching memos:", error)
      return []
    }

    return (data as ICMemo[]) || []
  } catch (err) {
    console.error("Unexpected error fetching memos:", err)
    return []
  }
}

/**
 * Get a specific IC memo by date
 * @param date - ISO date string (YYYY-MM-DD)
 */
export async function getMemoByDate(date: string): Promise<ICMemo | null> {
  try {
    const { data, error } = await supabase
      .from("ic_memos")
      .select("*")
      .eq("date", date)
      .single()

    if (error) {
      console.error("Error fetching memo by date:", error)
      return null
    }

    return data as ICMemo
  } catch (err) {
    console.error("Unexpected error fetching memo by date:", err)
    return null
  }
}
