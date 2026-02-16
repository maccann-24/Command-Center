"use client"

import { useEffect, useState } from "react"
import { supabase } from "@/lib/supabase"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar } from "@/components/ui/avatar"
import { Users, Activity, MessageSquare, DollarSign, Clock } from "lucide-react"
import type { Agent, Session } from "@/types/database"

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalAgents: 0,
    activeAgents: 0,
    totalSessions: 0,
    totalMessages: 0,
    totalCost: 0
  })
  const [agents, setAgents] = useState<Agent[]>([])
  const [recentSessions, setRecentSessions] = useState<(Session & { agent_name: string })[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchStats() {
      const { data: agentsData } = await supabase.from('agents').select('*')
      const { data: sessions } = await supabase.from('sessions').select('*')
      const { data: messages } = await supabase.from('messages').select('*')
      const { data: metrics } = await supabase.from('metrics').select('cost')
      
      const totalCost = metrics?.reduce((sum, m) => sum + Number(m.cost), 0) || 0
      const activeAgents = agentsData?.filter(a => a.status === 'active').length || 0
      
      setStats({
        totalAgents: agentsData?.length || 0,
        activeAgents,
        totalSessions: sessions?.length || 0,
        totalMessages: messages?.length || 0,
        totalCost
      })
      
      setAgents(agentsData || [])
      
      const sessionsWithAgents = sessions?.slice(0, 5).map(session => ({
        ...session,
        agent_name: agentsData?.find(a => a.id === session.agent_id)?.name || 'Unknown'
      })) || []
      
      setRecentSessions(sessionsWithAgents)
      setLoading(false)
    }
    fetchStats()
  }, [])

  if (loading) {
    return <div className="text-white text-lg">Loading dashboard...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-white/60 mt-1">Overview of your AI agents</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Active Agents</h2>
          <div className="space-y-3">
            {agents.slice(0, 3).map(agent => (
              <div key={agent.id} className="flex items-center gap-3">
                <Avatar name={agent.name} size="md" status={agent.status === 'active' ? 'online' : 'offline'} />
                <div className="flex-1">
                  <p className="text-white font-medium">{agent.name}</p>
                  <p className="text-white/60 text-sm">{agent.model}</p>
                </div>
                <Badge 
                  variant={agent.status === 'active' ? 'success' : agent.status === 'idle' ? 'warning' : 'error'}
                  pulse={agent.status === 'active'}
                >
                  {agent.status}
                </Badge>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
          <div className="space-y-3">
            {recentSessions.map(session => (
              <div key={session.id} className="flex items-start gap-3">
                <div className="p-2 bg-status-info/20 rounded-lg mt-1">
                  <Clock className="w-4 h-4 text-status-info" />
                </div>
                <div className="flex-1">
                  <p className="text-white text-sm">
                    <span className="font-medium">{session.agent_name}</span> started a session
                  </p>
                  <p className="text-white/40 text-xs mt-1">
                    {new Date(session.start_time).toLocaleString()}
                  </p>
                </div>
                <Badge variant="info">{session.status}</Badge>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
