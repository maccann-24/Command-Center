"use client"

import { useEffect, useState } from "react"
import { supabase } from "@/lib/supabase"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { SessionRowSkeleton } from "@/components/ui/skeleton"
import { Clock, MessageSquare, DollarSign, Search } from "lucide-react"
import Link from "next/link"

type SessionWithAgent = {
  id: string
  agent_id: string
  start_time: string
  end_time: string | null
  status: string
  agent_name: string
  message_count: number
  total_cost: number
  total_tokens: number
}

export default function SessionsPage() {
  const [sessions, setSessions] = useState<SessionWithAgent[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")

  useEffect(() => {
    async function fetchSessions() {
      const { data: sessionsData } = await supabase
        .from("sessions")
        .select("*")
        .order("start_time", { ascending: false })

      const { data: agentsData } = await supabase.from("agents").select("*")
      const { data: messagesData } = await supabase.from("messages").select("session_id")
      const { data: metricsData } = await supabase.from("metrics").select("session_id, cost, tokens_total")

      const enriched = (sessionsData || []).map(session => {
        const agent = (agentsData || []).find(a => a.id === session.agent_id)
        const messages = (messagesData || []).filter(m => m.session_id === session.id)
        const sessionMetrics = (metricsData || []).filter(m => m.session_id === session.id)
        const total_cost = sessionMetrics.reduce((sum, m) => sum + Number(m.cost), 0)
        const total_tokens = sessionMetrics.reduce((sum, m) => sum + Number(m.tokens_total), 0)

        return {
          ...session,
          agent_name: agent?.name || "Unknown",
          message_count: messages.length,
          total_cost,
          total_tokens,
        }
      })

      setSessions(enriched)
      setLoading(false)
    }
    fetchSessions()
  }, [])

  const filtered = sessions.filter(s => {
    const matchSearch = s.agent_name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchStatus = statusFilter === "all" || s.status === statusFilter
    return matchSearch && matchStatus
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Sessions</h1>
        <p className="text-white/60 mt-1">
          {loading ? "Loading..." : `${filtered.length} of ${sessions.length} sessions`}
        </p>
      </div>

      <Card className="p-4">
        <div className="flex gap-4">
          <div className="flex-1 flex items-center gap-3">
            <Search className="w-5 h-5 text-white/50" />
            <input
              type="text"
              placeholder="Search by agent name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent text-white placeholder:text-white/40 outline-none w-full"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-white/10 text-white px-4 py-2 rounded-lg border border-white/20 outline-none cursor-pointer"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="error">Error</option>
          </select>
        </div>
      </Card>

      <div className="space-y-3">
        {loading ? (
          [1, 2, 3, 4, 5].map(i => <SessionRowSkeleton key={i} />)
        ) : filtered.length === 0 ? (
          <Card className="p-12 text-center">
            <p className="text-white/60">No sessions found</p>
          </Card>
        ) : (
          filtered.map(session => (
            <Card key={session.id} variant="hover" className="p-5">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <div className="p-3 bg-status-info/20 rounded-xl flex-shrink-0">
                    <Clock className="w-5 h-5 text-status-info" />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-white font-medium truncate">{session.agent_name}</p>
                      <Badge variant={session.status === "active" ? "success" : "info"}>
                        {session.status}
                      </Badge>
                    </div>
                    <p className="text-white/60 text-sm">
                      {new Date(session.start_time).toLocaleString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-6 flex-shrink-0">
                  <div className="text-center">
                    <div className="flex items-center gap-1 text-white/70 text-sm justify-center">
                      <MessageSquare className="w-4 h-4" />
                      <span>{session.message_count}</span>
                    </div>
                    <p className="text-white/40 text-xs">msgs</p>
                  </div>

                  <div className="text-center">
                    <p className="text-white text-sm font-medium">
                      {session.total_tokens > 0 ? `${(session.total_tokens / 1000).toFixed(1)}k` : "—"}
                    </p>
                    <p className="text-white/40 text-xs">tokens</p>
                  </div>

                  <div className="text-center">
                    <div className="flex items-center gap-1 text-white text-sm font-medium justify-center">
                      <DollarSign className="w-3 h-3" />
                      <span>{session.total_cost.toFixed(4)}</span>
                    </div>
                    <p className="text-white/40 text-xs">cost</p>
                  </div>

                  <Link href={`/sessions/${session.id}`}>
                    <Button variant="secondary" size="sm">View</Button>
                  </Link>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
