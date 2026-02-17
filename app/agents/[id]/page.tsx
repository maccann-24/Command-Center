"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { supabase } from "@/lib/supabase"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import type { Agent, Session, Metric } from "@/types/database"
import { ArrowLeft, Settings, Zap } from "lucide-react"
import Link from "next/link"

export default function AgentDetailPage() {
  const params = useParams()
  const agentId = params.id as string

  const [agent, setAgent] = useState<Agent | null>(null)
  const [sessions, setSessions] = useState<Session[]>([])
  const [metrics, setMetrics] = useState<Metric[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      const { data: agentData } = await supabase
        .from("agents").select("*").eq("id", agentId).single()

      const { data: sessionsData } = await supabase
        .from("sessions").select("*").eq("agent_id", agentId)
        .order("start_time", { ascending: false })

      const sessionIds = (sessionsData || []).map(s => s.id)
      const { data: metricsData } = sessionIds.length > 0
        ? await supabase.from("metrics").select("*").in("session_id", sessionIds)
        : { data: [] }

      setAgent(agentData)
      setSessions(sessionsData || [])
      setMetrics(metricsData || [])
      setLoading(false)
    }
    if (agentId) fetchData()
  }, [agentId])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white text-lg">Loading agent details...</div>
      </div>
    )
  }

  if (!agent) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white text-lg">Agent not found</div>
      </div>
    )
  }

  const totalCost = metrics.reduce((sum, m) => sum + Number(m.cost), 0)
  const totalTokens = metrics.reduce((sum, m) => sum + Number(m.tokens_total), 0)

  return (
    <div className="space-y-6">
      <Link href="/agents">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Agents
        </Button>
      </Link>

      <Card className="p-8">
        <div className="flex items-start gap-6">
          <Avatar name={agent.name} size="lg" status={agent.status === "active" ? "online" : "offline"} />

          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-white">{agent.name}</h1>
              <Badge
                variant={agent.status === "active" ? "success" : agent.status === "idle" ? "warning" : "error"}
                pulse={agent.status === "active"}
              >
                {agent.status}
              </Badge>
            </div>

            <p className="text-white/60 mb-6">{agent.model}</p>

            <div className="grid grid-cols-3 gap-6 mb-6">
              <div>
                <p className="text-white/40 text-xs">Total Sessions</p>
                <p className="text-2xl font-semibold text-white">{sessions.length}</p>
              </div>
              <div>
                <p className="text-white/40 text-xs">Total Tokens</p>
                <p className="text-2xl font-semibold text-white">
                  {totalTokens > 0 ? `${(totalTokens / 1000).toFixed(1)}k` : "—"}
                </p>
              </div>
              <div>
                <p className="text-white/40 text-xs">Total Cost</p>
                <p className="text-2xl font-semibold text-white">${totalCost.toFixed(4)}</p>
              </div>
            </div>

            <div className="flex gap-3">
              <Button variant="primary">
                <Zap className="w-4 h-4 mr-2" />
                Restart Agent
              </Button>
              <Link href={`/agents/${agentId}/settings`}>
                <Button variant="secondary">
                  <Settings className="w-4 h-4 mr-2" />
                  Settings
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Recent Sessions</h2>

        {sessions.length === 0 ? (
          <p className="text-white/60 text-center py-8">No sessions yet</p>
        ) : (
          <div className="space-y-3">
            {sessions.slice(0, 10).map(session => {
              const sessionMetrics = metrics.filter(m => m.session_id === session.id)
              const sessionCost = sessionMetrics.reduce((sum, m) => sum + Number(m.cost), 0)
              const sessionTokens = sessionMetrics.reduce((sum, m) => sum + Number(m.tokens_total), 0)

              return (
                <Card key={session.id} variant="hover" className="p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-white text-sm font-medium font-mono">
                          {session.id.slice(0, 8)}...
                        </p>
                        <Badge variant={session.status === "active" ? "success" : "info"}>
                          {session.status}
                        </Badge>
                      </div>
                      <p className="text-white/50 text-xs">
                        {new Date(session.start_time).toLocaleString()}
                      </p>
                    </div>

                    <div className="flex items-center gap-6 text-right">
                      <div>
                        <p className="text-white text-sm">
                          {sessionTokens > 0 ? `${(sessionTokens / 1000).toFixed(1)}k` : "—"}
                        </p>
                        <p className="text-white/40 text-xs">tokens</p>
                      </div>
                      <div>
                        <p className="text-white text-sm">${sessionCost.toFixed(4)}</p>
                        <p className="text-white/40 text-xs">cost</p>
                      </div>
                      <Link href={`/sessions/${session.id}`}>
                        <Button variant="ghost" size="sm">View</Button>
                      </Link>
                    </div>
                  </div>
                </Card>
              )
            })}
          </div>
        )}
      </Card>
    </div>
  )
}
