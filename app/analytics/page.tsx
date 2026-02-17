"use client"

import { useEffect, useState } from "react"
import { supabase } from "@/lib/supabase"
import { Card } from "@/components/ui/card"
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend
} from "recharts"

type DailyData = {
  date: string
  sessions: number
  cost: number
  tokens: number
}

type AgentData = {
  name: string
  tokens: number
  cost: number
  sessions: number
}

type SessionCostEntry = {
  session_id: string
  cost: number
  tokens_input: number
  tokens_output: number
  tokens_total: number
}

export default function AnalyticsPage() {
  const [dailyData, setDailyData] = useState<DailyData[]>([])
  const [agentData, setAgentData] = useState<AgentData[]>([])
  const [totals, setTotals] = useState({ cost: 0, tokens: 0, sessions: 0 })
  const [tokenBreakdown, setTokenBreakdown] = useState({
    inputTokens: 0,
    outputTokens: 0,
    avgCostPerSession: 0,
    mostExpensiveSession: null as { id: string; cost: number } | null,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      const { data: sessions } = await supabase.from("sessions").select("*")
      const { data: agents } = await supabase.from("agents").select("*")
      const { data: metrics } = await supabase.from("metrics").select("*")

      // Build last 7 days array
      const last7Days: DailyData[] = Array.from({ length: 7 }, (_, i) => {
        const d = new Date()
        d.setDate(d.getDate() - (6 - i))
        return {
          date: d.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
          sessions: 0,
          cost: 0,
          tokens: 0,
        }
      })

      // Count sessions per day
      ;(sessions || []).forEach(session => {
        const label = new Date(session.start_time).toLocaleDateString("en-US", { month: "short", day: "numeric" })
        const dayEntry = last7Days.find(d => d.date === label)
        if (dayEntry) dayEntry.sessions += 1
      })

      // Add cost & tokens per day from metrics
      ;(metrics || []).forEach(metric => {
        const label = new Date(metric.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })
        const dayEntry = last7Days.find(d => d.date === label)
        if (dayEntry) {
          dayEntry.cost += Number(metric.cost)
          dayEntry.tokens += Number(metric.tokens_total)
        }
      })

      // Round values
      last7Days.forEach(d => {
        d.cost = Math.round(d.cost * 10000) / 10000
        d.tokens = Math.round(d.tokens / 1000) // convert to k
      })

      // Build per-agent data
      const agentStats: AgentData[] = (agents || []).map(agent => {
        const agentSessions = (sessions || []).filter(s => s.agent_id === agent.id)
        const agentSessionIds = agentSessions.map(s => s.id)
        const agentMetrics = (metrics || []).filter(m => agentSessionIds.includes(m.session_id))

        return {
          name: agent.name,
          tokens: Math.round(agentMetrics.reduce((sum, m) => sum + Number(m.tokens_total), 0) / 1000),
          cost: Math.round(agentMetrics.reduce((sum, m) => sum + Number(m.cost), 0) * 100) / 100,
          sessions: agentSessions.length,
        }
      })

      // Overall totals
      const totalCost = (metrics || []).reduce((sum, m) => sum + Number(m.cost), 0)
      const totalTokens = (metrics || []).reduce((sum, m) => sum + Number(m.tokens_total), 0)
      const totalInputTokens = (metrics || []).reduce((sum, m) => sum + Number(m.tokens_input), 0)
      const totalOutputTokens = (metrics || []).reduce((sum, m) => sum + Number(m.tokens_output), 0)

      // Cost per session (group by session_id)
      const sessionCostMap: Record<string, SessionCostEntry> = {}
      ;(metrics || []).forEach(m => {
        if (!sessionCostMap[m.session_id]) {
          sessionCostMap[m.session_id] = {
            session_id: m.session_id,
            cost: 0,
            tokens_input: 0,
            tokens_output: 0,
            tokens_total: 0,
          }
        }
        sessionCostMap[m.session_id].cost += Number(m.cost)
        sessionCostMap[m.session_id].tokens_input += Number(m.tokens_input)
        sessionCostMap[m.session_id].tokens_output += Number(m.tokens_output)
        sessionCostMap[m.session_id].tokens_total += Number(m.tokens_total)
      })

      const sessionCostEntries = Object.values(sessionCostMap)
      const avgCostPerSession = sessionCostEntries.length > 0
        ? totalCost / sessionCostEntries.length
        : 0

      const mostExpensive = sessionCostEntries.reduce<SessionCostEntry | null>(
        (max, entry) => (!max || entry.cost > max.cost ? entry : max),
        null
      )

      // If no input/output tokens recorded, apply 70/30 split
      const estimatedInput = totalInputTokens > 0 ? totalInputTokens : Math.round(totalTokens * 0.7)
      const estimatedOutput = totalOutputTokens > 0 ? totalOutputTokens : Math.round(totalTokens * 0.3)
      const usingSplit = totalInputTokens === 0 && totalTokens > 0

      setDailyData(last7Days)
      setAgentData(agentStats)
      setTotals({
        cost: Math.round(totalCost * 10000) / 10000,
        tokens: Math.round(totalTokens / 1000),
        sessions: (sessions || []).length,
      })
      setTokenBreakdown({
        inputTokens: estimatedInput,
        outputTokens: estimatedOutput,
        avgCostPerSession,
        mostExpensiveSession: mostExpensive
          ? { id: mostExpensive.session_id, cost: mostExpensive.cost }
          : null,
      })

      // Store the split flag alongside — we'll use closure
      void usingSplit
      setLoading(false)
    }
    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-[#e2e8f0] font-mono text-sm">LOADING ANALYTICS…</div>
      </div>
    )
  }

  const chartTooltipStyle = {
    backgroundColor: "#0d1117",
    border: "1px solid #1e2d3d",
    borderRadius: "2px",
    color: "#e2e8f0",
    fontFamily: "monospace",
    fontSize: "12px",
  }

  const totalTokensRaw = tokenBreakdown.inputTokens + tokenBreakdown.outputTokens
  const inputPct = totalTokensRaw > 0 ? Math.round((tokenBreakdown.inputTokens / totalTokensRaw) * 100) : 70
  const outputPct = 100 - inputPct

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Analytics</h1>
        <p className="text-white/60 mt-1">Last 7 days of usage</p>
      </div>

      {/* Cost estimation note */}
      <div className="flex items-center gap-2 px-4 py-2.5 rounded-sm border border-[#1e2d3d] bg-[#0d1117]">
        <span className="text-[#0077ff] text-xs font-mono">ℹ</span>
        <p className="text-[#64748b] text-xs font-mono">
          Costs estimated at Claude Sonnet 4.5 rates ($3/1M input, $15/1M output)
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-6">
        <Card className="p-6 text-center">
          <p className="text-[#64748b] text-xs font-mono uppercase tracking-wider mb-2">Total Sessions</p>
          <p className="text-4xl font-bold text-[#e2e8f0] font-mono">{totals.sessions}</p>
        </Card>
        <Card className="p-6 text-center">
          <p className="text-[#64748b] text-xs font-mono uppercase tracking-wider mb-2">Total Tokens</p>
          <p className="text-4xl font-bold text-[#e2e8f0] font-mono">{totals.tokens}k</p>
        </Card>
        <Card className="p-6 text-center">
          <p className="text-[#64748b] text-xs font-mono uppercase tracking-wider mb-2">Total Cost</p>
          <p className="text-4xl font-bold text-[#00d084] font-mono">${totals.cost}</p>
        </Card>
      </div>

      {/* Token + Cost Breakdown */}
      <Card className="p-6">
        <h2 className="text-sm font-mono font-semibold text-[#e2e8f0] tracking-widest uppercase mb-5">
          Cost Breakdown
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Token split */}
          <div>
            <p className="text-[#64748b] text-xs font-mono uppercase tracking-wider mb-3">Token Distribution</p>
            <div className="flex h-3 rounded-sm overflow-hidden mb-3">
              <div
                className="bg-[#0077ff] transition-all duration-500"
                style={{ width: `${inputPct}%` }}
              />
              <div
                className="bg-[#f5a623] transition-all duration-500"
                style={{ width: `${outputPct}%` }}
              />
            </div>
            <div className="flex gap-6">
              <div>
                <div className="flex items-center gap-1.5 mb-1">
                  <div className="w-2 h-2 rounded-full bg-[#0077ff]" />
                  <span className="text-[#64748b] text-xs font-mono">Input</span>
                </div>
                <p className="text-[#0077ff] text-lg font-mono font-bold">
                  {inputPct}%
                </p>
                <p className="text-[#64748b] text-xs font-mono">
                  {(tokenBreakdown.inputTokens / 1000).toFixed(1)}k tokens
                </p>
              </div>
              <div>
                <div className="flex items-center gap-1.5 mb-1">
                  <div className="w-2 h-2 rounded-full bg-[#f5a623]" />
                  <span className="text-[#64748b] text-xs font-mono">Output</span>
                </div>
                <p className="text-[#f5a623] text-lg font-mono font-bold">
                  {outputPct}%
                </p>
                <p className="text-[#64748b] text-xs font-mono">
                  {(tokenBreakdown.outputTokens / 1000).toFixed(1)}k tokens
                </p>
              </div>
            </div>
          </div>

          {/* Session cost metrics */}
          <div className="space-y-4">
            <div>
              <p className="text-[#64748b] text-xs font-mono uppercase tracking-wider mb-1">Avg Cost / Session</p>
              <p className="text-[#e2e8f0] text-2xl font-mono font-bold">
                ${tokenBreakdown.avgCostPerSession.toFixed(4)}
              </p>
            </div>
            <div className="pt-3 border-t border-[#1e2d3d]">
              <p className="text-[#64748b] text-xs font-mono uppercase tracking-wider mb-1">Most Expensive Session</p>
              {tokenBreakdown.mostExpensiveSession ? (
                <>
                  <p className="text-[#ff3b47] text-lg font-mono font-bold">
                    ${tokenBreakdown.mostExpensiveSession.cost.toFixed(4)}
                  </p>
                  <p className="text-[#64748b] text-xs font-mono mt-0.5 truncate">
                    {tokenBreakdown.mostExpensiveSession.id}
                  </p>
                </>
              ) : (
                <p className="text-[#64748b] text-sm font-mono">—</p>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Cost Over Time */}
      <Card className="p-6">
        <h2 className="text-sm font-mono font-semibold text-[#e2e8f0] tracking-widest uppercase mb-6">
          Cost Over Time
        </h2>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={dailyData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0077ff" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#0077ff" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e2d3d" />
            <XAxis dataKey="date" stroke="#1e2d3d" tick={{ fill: "#64748b", fontSize: 11, fontFamily: "monospace" }} />
            <YAxis stroke="#1e2d3d" tick={{ fill: "#64748b", fontSize: 11, fontFamily: "monospace" }} />
            <Tooltip contentStyle={chartTooltipStyle} formatter={(v: number | undefined) => [`$${v ?? 0}`, "Cost"]} />
            <Area type="monotone" dataKey="cost" stroke="#0077ff" fill="url(#costGradient)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* Sessions Per Day */}
      <Card className="p-6">
        <h2 className="text-sm font-mono font-semibold text-[#e2e8f0] tracking-widest uppercase mb-6">
          Sessions Per Day
        </h2>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={dailyData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="sessionsGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00d084" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#00d084" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e2d3d" />
            <XAxis dataKey="date" stroke="#1e2d3d" tick={{ fill: "#64748b", fontSize: 11, fontFamily: "monospace" }} />
            <YAxis stroke="#1e2d3d" tick={{ fill: "#64748b", fontSize: 11, fontFamily: "monospace" }} allowDecimals={false} />
            <Tooltip contentStyle={chartTooltipStyle} formatter={(v: number | undefined) => [v ?? 0, "Sessions"]} />
            <Area type="monotone" dataKey="sessions" stroke="#00d084" fill="url(#sessionsGradient)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* Token Usage Per Agent */}
      <Card className="p-6">
        <h2 className="text-sm font-mono font-semibold text-[#e2e8f0] tracking-widest uppercase mb-6">
          Token Usage by Agent
        </h2>
        {agentData.length === 0 ? (
          <p className="text-[#64748b] text-sm font-mono text-center py-12">No agent data yet</p>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={agentData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2d3d" />
              <XAxis dataKey="name" stroke="#1e2d3d" tick={{ fill: "#64748b", fontSize: 11, fontFamily: "monospace" }} />
              <YAxis stroke="#1e2d3d" tick={{ fill: "#64748b", fontSize: 11, fontFamily: "monospace" }} />
              <Tooltip contentStyle={chartTooltipStyle} formatter={(v: number | undefined) => [`${v ?? 0}k`, "Tokens"]} />
              <Legend wrapperStyle={{ color: "#64748b", fontFamily: "monospace", fontSize: "11px" }} />
              <Bar dataKey="tokens" name="Tokens (k)" fill="#0077ff" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </Card>

      {/* Cost Per Agent Table */}
      <Card className="p-6">
        <h2 className="text-sm font-mono font-semibold text-[#e2e8f0] tracking-widest uppercase mb-4">
          Cost Per Agent
        </h2>
        <div className="space-y-0">
          {agentData.length === 0 ? (
            <p className="text-[#64748b] text-sm font-mono text-center py-8">No agent data yet</p>
          ) : (
            agentData.map(agent => (
              <div
                key={agent.name}
                className="flex items-center justify-between py-3 border-b border-[#1e2d3d] last:border-0"
              >
                <div>
                  <p className="text-[#e2e8f0] font-medium font-mono">{agent.name}</p>
                  <p className="text-[#64748b] text-xs font-mono mt-0.5">
                    {agent.sessions} sessions · {agent.tokens}k tokens
                  </p>
                </div>
                <p className="text-[#00d084] font-mono font-semibold">${agent.cost.toFixed(4)}</p>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  )
}
