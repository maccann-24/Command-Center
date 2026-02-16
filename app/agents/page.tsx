"use client"

import { useEffect, useState } from "react"
import { supabase } from "@/lib/supabase"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import type { Agent } from "@/types/database"
import { Sparkles, Zap, Trash2, Search } from "lucide-react"

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")

  useEffect(() => {
    async function fetchAgents() {
      const { data } = await supabase
        .from('agents')
        .select('*')
        .order('created_at', { ascending: false })
      
      setAgents(data || [])
      setLoading(false)
    }
    fetchAgents()
  }, [])

  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          agent.model.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === "all" || agent.status === statusFilter
    return matchesSearch && matchesStatus
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white text-lg">Loading agents...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Agents</h1>
          <p className="text-white/60 mt-1">{filteredAgents.length} of {agents.length} agents</p>
        </div>
        <Button variant="primary">
          <Sparkles className="w-4 h-4 mr-2" />
          New Agent
        </Button>
      </div>

      <Card className="p-4">
        <div className="flex gap-4">
          <div className="flex-1 flex items-center gap-3">
            <Search className="w-5 h-5 text-white/50" />
            <input
              type="text"
              placeholder="Search by name or model..."
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
            <option value="idle">Idle</option>
            <option value="error">Error</option>
          </select>
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAgents.map((agent) => (
          <Card key={agent.id} variant="hover" className="p-6">
            <div className="flex items-start gap-4">
              <Avatar name={agent.name} size="lg" status={agent.status === 'active' ? 'online' : 'offline'} />
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-white font-semibold truncate">{agent.name}</h3>
                  <Badge 
                    variant={
                      agent.status === 'active' ? 'success' : 
                      agent.status === 'idle' ? 'warning' : 
                      'error'
                    }
                    pulse={agent.status === 'active'}
                  >
                    {agent.status}
                  </Badge>
                </div>
                
                <p className="text-white/60 text-sm mb-4">{agent.model}</p>
                
                <div className="flex gap-2">
                  <Button variant="secondary" size="sm" className="flex-1">
                    <Zap className="w-3 h-3 mr-1" />
                    Details
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
