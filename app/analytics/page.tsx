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

export default function AnalyticsPage() {
  const [dailyData, setDailyData] = useState<DailyData[]>([])
  const [agentData, setAgentData] = useState<AgentData[]>([])
  const [totals, setTotals] = useState({ cost: 0, tokens: 0, sessions: 0 })
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

      setDailyData(last7Days)
      setAgentData(agentStats)
      setTotals({
        cost: Math.round(totalCost * 10000) / 10000,
        tokens: Math.round(totalTokens / 1000),
        sessions: (sessions || []).length,
      })
      setLoading(false)
    }
    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white text-lg">Loading analytics...</div>
      </div>
    )
  }

  const chartTooltipStyle = {
    backgroundColor: "rgba(15, 10, 40, 0.95)",
    border: "1px solid rgba(255,255,255,0.15)",
    borderRadius: "12px",
    color: "#fff",
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Analytics</h1>
        <p className="text-white/60 mt-1">Last 7 days of usage</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-6">
        <Card className="p-6 text-center">
          <p className="text-white/50 text-sm mb-2">Total Sessions</p>
          <p className="text-4xl font-bold text-white">{totals.sessions}</p>
        </Card>
        <Card className="p-6 text-center">
          <p className="text-white/50 text-sm mb-2">Total Tokens</p>
          <p className="text-4xl font-bold text-white">{totals.tokens}k</p>
        </Card>
        <Card className="p-6 text-center">
          <p className="text-white/50 text-sm mb-2">Total Cost</p>
          <p className="text-4xl font-bold text-white">${totals.cost}</p>
        </Card>
      </div>

      {/* Cost Over Time */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-white mb-6">Cost Over Time</h2>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={dailyData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
            <XAxis dataKey="date" stroke="rgba(255,255,255,0.4)" tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 12 }} />
            <YAxis stroke="rgba(255,255,255,0.4)" tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 12 }} />
            <Tooltip contentStyle={chartTooltipStyle} formatter={(v: number | undefined) => [`$${v ?? 0}`, "Cost"]} />
            <Area type="monotone" dataKey="cost" stroke="#6366f1" fill="url(#costGradient)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* Sessions Per Day */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-white mb-6">Sessions Per Day</h2>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={dailyData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="sessionsGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
            <XAxis dataKey="date" stroke="rgba(255,255,255,0.4)" tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 12 }} />
            <YAxis stroke="rgba(255,255,255,0.4)" tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 12 }} allowDecimals={false} />
            <Tooltip contentStyle={chartTooltipStyle} formatter={(v: number | undefined) => [v ?? 0, "Sessions"]} />
            <Area type="monotone" dataKey="sessions" stroke="#8b5cf6" fill="url(#sessionsGradient)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* Token Usage Per Agent */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-white mb-6">Token Usage by Agent</h2>
        {agentData.length === 0 ? (
          <p className="text-white/60 text-center py-12">No agent data yet</p>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={agentData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
              <XAxis dataKey="name" stroke="rgba(255,255,255,0.4)" tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 12 }} />
              <YAxis stroke="rgba(255,255,255,0.4)" tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 12 }} />
              <Tooltip contentStyle={chartTooltipStyle} formatter={(v: number | undefined) => [`${v ?? 0}k`, "Tokens"]} />
              <Legend wrapperStyle={{ color: "rgba(255,255,255,0.6)" }} />
              <Bar dataKey="tokens" name="Tokens (k)" fill="#6366f1" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </Card>

      {/* Cost Per Agent Table */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Cost Per Agent</h2>
        <div className="space-y-3">
          {agentData.length === 0 ? (
            <p className="text-white/60 text-center py-8">No agent data yet</p>
          ) : (
            agentData.map(agent => (
              <div key={agent.name} className="flex items-center justify-between py-3 border-b border-white/10 last:border-0">
                <div>
                  <p className="text-white font-medium">{agent.name}</p>
                  <p className="text-white/50 text-xs">{agent.sessions} sessions · {agent.tokens}k tokens</p>
                </div>
                <p className="text-white font-semibold">${agent.cost.toFixed(4)}</p>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  )
}
