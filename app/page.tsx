"use client"

import { useEffect, useState, useRef, useCallback } from "react"
import { supabase } from "@/lib/supabase"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar } from "@/components/ui/avatar"
import { StatCardSkeleton } from "@/components/ui/skeleton"
import { Users, Activity, MessageSquare, DollarSign, Clock, Heart } from "lucide-react"
import type { Agent, Session } from "@/types/database"

function formatTimeAgo(dateStr: string | null): string {
  if (!dateStr) return "Never"
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

function getHeartbeatStatus(dateStr: string | null): "green" | "amber" | "red" | "unknown" {
  if (!dateStr) return "unknown"
  const diffMin = (Date.now() - new Date(dateStr).getTime()) / 60000
  if (diffMin < 5) return "green"
  if (diffMin < 30) return "amber"
  return "red"
}

function HeartbeatMonitorCard({ session }: { session: (Session & { agent_name: string }) | null }) {
  const [, setTick] = useState(0)

  // Update every 30s
  useEffect(() => {
    const interval = setInterval(() => setTick(t => t + 1), 30000)
    return () => clearInterval(interval)
  }, [])

  const heartbeat = session?.last_heartbeat ?? null
  const status = getHeartbeatStatus(heartbeat)
  const timeAgo = formatTimeAgo(heartbeat)

  // Expected next check-in: +5 min from last heartbeat
  const nextCheckin = heartbeat
    ? new Date(new Date(heartbeat).getTime() + 5 * 60000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    : "—"

  const statusColor =
    status === "green"
      ? "#00d084"
      : status === "amber"
      ? "#f5a623"
      : status === "red"
      ? "#ff3b47"
      : "#64748b"

  const statusLabel =
    status === "green"
      ? "NOMINAL"
      : status === "amber"
      ? "DELAYED"
      : status === "red"
      ? "OFFLINE"
      : "NO DATA"

  return (
    <Card className="p-6">
      <div className="flex items-center gap-2 mb-4">
        <Heart className="w-4 h-4" style={{ color: statusColor }} />
        <h2 className="text-sm font-mono font-semibold text-[#e2e8f0] tracking-widest uppercase">
          Agent Heartbeat
        </h2>
        <span
          className="ml-auto text-xs font-mono px-2 py-0.5 rounded-sm"
          style={{ color: statusColor, backgroundColor: `${statusColor}18`, border: `1px solid ${statusColor}40` }}
        >
          {statusLabel}
        </span>
      </div>

      {/* Status bar */}
      <div className="h-1.5 w-full rounded-full bg-[#1e2d3d] mb-4 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: status === "unknown" ? "0%" : "100%", backgroundColor: statusColor }}
        />
      </div>

      <div className="grid grid-cols-3 gap-4 text-center">
        <div>
          <p className="text-[#64748b] text-xs font-mono uppercase tracking-wider mb-1">Last Sync</p>
          <p className="text-[#e2e8f0] text-sm font-mono font-bold">
            {heartbeat ? new Date(heartbeat).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "—"}
          </p>
        </div>
        <div>
          <p className="text-[#64748b] text-xs font-mono uppercase tracking-wider mb-1">Time Since</p>
          <p className="font-mono text-sm font-bold" style={{ color: statusColor }}>
            {timeAgo}
          </p>
        </div>
        <div>
          <p className="text-[#64748b] text-xs font-mono uppercase tracking-wider mb-1">Next ETA</p>
          <p className="text-[#e2e8f0] text-sm font-mono font-bold">{nextCheckin}</p>
        </div>
      </div>

      {session && (
        <p className="text-[#64748b] text-xs font-mono mt-4 truncate">
          Agent: <span className="text-[#e2e8f0]">{session.agent_name}</span>
          {session.current_task && (
            <> · Task: <span className="text-[#0077ff]">{session.current_task}</span></>
          )}
        </p>
      )}
    </Card>
  )
}

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalAgents: 0,
    activeAgents: 0,
    totalSessions: 0,
    totalMessages: 0,
    totalCost: 0,
  })
  const [agents, setAgents] = useState<Agent[]>([])
  const [recentSessions, setRecentSessions] = useState<(Session & { agent_name: string })[]>([])
  const [activeSession, setActiveSession] = useState<(Session & { agent_name: string }) | null>(null)
  const [loading, setLoading] = useState(true)
  const [liveFlash, setLiveFlash] = useState(false)
  const liveFlashTimeout = useRef<ReturnType<typeof setTimeout> | null>(null)

  const flashLive = useCallback(() => {
    setLiveFlash(true)
    if (liveFlashTimeout.current) clearTimeout(liveFlashTimeout.current)
    liveFlashTimeout.current = setTimeout(() => setLiveFlash(false), 1500)
  }, [])

  const fetchStats = useCallback(async () => {
    const { data: agentsData } = await supabase.from("agents").select("*")
    const { data: sessions } = await supabase.from("sessions").select("*").order("start_time", { ascending: false })
    const { data: messages } = await supabase.from("messages").select("id")
    const { data: metrics } = await supabase.from("metrics").select("cost")

    const totalCost = (metrics || []).reduce((sum, m) => sum + Number(m.cost), 0)
    const activeAgents = (agentsData || []).filter(a => a.status === "active").length

    setStats({
      totalAgents: agentsData?.length || 0,
      activeAgents,
      totalSessions: sessions?.length || 0,
      totalMessages: messages?.length || 0,
      totalCost,
    })

    setAgents(agentsData || [])

    const sessionsWithAgents = (sessions || []).slice(0, 5).map(session => ({
      ...session,
      agent_name: (agentsData || []).find(a => a.id === session.agent_id)?.name || "Unknown",
    }))

    setRecentSessions(sessionsWithAgents)

    // Most recent active session for heartbeat monitor
    const latestActive = (sessions || [])
      .filter(s => s.status === "active")
      .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime())[0]

    if (latestActive) {
      setActiveSession({
        ...latestActive,
        agent_name: (agentsData || []).find(a => a.id === latestActive.agent_id)?.name || "Unknown",
      })
    } else if ((sessions || []).length > 0) {
      // Fallback: most recent session regardless of status
      const latest = sessions![0]
      setActiveSession({
        ...latest,
        agent_name: (agentsData || []).find(a => a.id === latest.agent_id)?.name || "Unknown",
      })
    } else {
      setActiveSession(null)
    }

    setLoading(false)
  }, [])

  useEffect(() => {
    fetchStats()
  }, [fetchStats])

  // Realtime subscriptions for sessions and tasks
  useEffect(() => {
    const sessionsChannel = supabase
      .channel("dashboard-sessions-changes")
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "sessions" },
        () => {
          flashLive()
          fetchStats()
        }
      )
      .subscribe()

    const tasksChannel = supabase
      .channel("dashboard-tasks-changes")
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "tasks" },
        () => {
          flashLive()
          fetchStats()
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(sessionsChannel)
      supabase.removeChannel(tasksChannel)
    }
  }, [fetchStats, flashLive])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (liveFlashTimeout.current) clearTimeout(liveFlashTimeout.current)
    }
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-white/60 mt-1">Overview of your AI agents</p>
        </div>
        {/* LIVE indicator */}
        <div className="flex items-center gap-1.5 px-2 py-1 mb-1">
          <span
            className={`text-xs font-mono transition-colors duration-300 ${
              liveFlash ? "text-[#00d084]" : "text-[#64748b]"
            }`}
          >
            ●
          </span>
          <span
            className={`text-xs font-mono transition-colors duration-300 ${
              liveFlash ? "text-[#00d084]" : "text-[#64748b]"
            }`}
          >
            LIVE
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {loading ? (
          [1, 2, 3, 4].map(i => <StatCardSkeleton key={i} />)
        ) : (
          <>
            <Card className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-white/60 text-sm">Total Agents</p>
                  <h3 className="text-3xl font-bold text-white mt-2">{stats.totalAgents}</h3>
                  <p className="text-green-400 text-sm mt-2">{stats.activeAgents} active</p>
                </div>
                <div className="p-3 bg-brand-primary/20 rounded-lg">
                  <Users className="w-6 h-6 text-brand-primary" />
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-white/60 text-sm">Total Sessions</p>
                  <h3 className="text-3xl font-bold text-white mt-2">{stats.totalSessions}</h3>
                  <p className="text-white/40 text-sm mt-2">All time</p>
                </div>
                <div className="p-3 bg-status-info/20 rounded-lg">
                  <Activity className="w-6 h-6 text-status-info" />
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-white/60 text-sm">Total Messages</p>
                  <h3 className="text-3xl font-bold text-white mt-2">{stats.totalMessages}</h3>
                  <p className="text-white/40 text-sm mt-2">Across all sessions</p>
                </div>
                <div className="p-3 bg-brand-secondary/20 rounded-lg">
                  <MessageSquare className="w-6 h-6 text-brand-secondary" />
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-white/60 text-sm">Total Cost</p>
                  <h3 className="text-3xl font-bold text-white mt-2">${stats.totalCost.toFixed(2)}</h3>
                  <p className="text-white/40 text-sm mt-2">API usage</p>
                </div>
                <div className="p-3 bg-status-warning/20 rounded-lg">
                  <DollarSign className="w-6 h-6 text-status-warning" />
                </div>
              </div>
            </Card>
          </>
        )}
      </div>

      {!loading && (
        <>
          {/* Heartbeat Monitor */}
          <HeartbeatMonitorCard session={activeSession} />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Active Agents</h2>
              <div className="space-y-3">
                {agents.slice(0, 3).map(agent => (
                  <div key={agent.id} className="flex items-center gap-3">
                    <Avatar name={agent.name} size="md" status={agent.status === "active" ? "online" : "offline"} />
                    <div className="flex-1 min-w-0">
                      <p className="text-white font-medium truncate">{agent.name}</p>
                      <p className="text-white/60 text-sm truncate">{agent.model}</p>
                    </div>
                    <Badge
                      variant={agent.status === "active" ? "success" : agent.status === "idle" ? "warning" : "error"}
                      pulse={agent.status === "active"}
                    >
                      {agent.status}
                    </Badge>
                  </div>
                ))}
                {agents.length === 0 && (
                  <p className="text-white/50 text-sm text-center py-4">No agents yet</p>
                )}
              </div>
            </Card>

            <Card className="p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
              <div className="space-y-3">
                {recentSessions.map(session => (
                  <div key={session.id} className="flex items-start gap-3">
                    <div className="p-2 bg-status-info/20 rounded-lg mt-0.5">
                      <Clock className="w-4 h-4 text-status-info" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-white text-sm">
                        <span className="font-medium">{session.agent_name}</span> started a session
                      </p>
                      <p className="text-white/40 text-xs mt-0.5">
                        {new Date(session.start_time).toLocaleString()}
                      </p>
                    </div>
                    <Badge variant="info">{session.status}</Badge>
                  </div>
                ))}
                {recentSessions.length === 0 && (
                  <p className="text-white/50 text-sm text-center py-4">No sessions yet</p>
                )}
              </div>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}
