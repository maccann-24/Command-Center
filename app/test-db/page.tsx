"use client"

import { supabase } from "@/lib/supabase"
import { useEffect, useState } from "react"
import type { Agent, Session, Message } from "@/types/database"

export default function TestDB() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [sessions, setSessions] = useState<Session[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      const { data: agentData } = await supabase.from('agents').select('*')
      const { data: sessionData } = await supabase.from('sessions').select('*')
      const { data: messageData } = await supabase.from('messages').select('*')
      
      setAgents(agentData || [])
      setSessions(sessionData || [])
      setMessages(messageData || [])
      setLoading(false)
    }
    fetchData()
  }, [])

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <div className="text-white text-xl">Loading...</div>
    </div>
  )

  return (
    <div className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold text-white">Database Test ✅</h1>
        
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <h2 className="text-xl font-semibold text-white mb-4">Agents ({agents.length})</h2>
          <div className="space-y-2">
            {agents.map(agent => (
              <div key={agent.id} className="text-white/80 flex gap-4">
                <span className="font-mono text-sm">{agent.name}</span>
                <span className={`px-2 py-1 rounded text-xs ${
                  agent.status === 'active' ? 'bg-green-500/20 text-green-300' :
                  agent.status === 'idle' ? 'bg-yellow-500/20 text-yellow-300' :
                  'bg-red-500/20 text-red-300'
                }`}>{agent.status}</span>
                <span className="text-white/60 text-sm">{agent.model}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <h2 className="text-xl font-semibold text-white mb-4">Sessions ({sessions.length})</h2>
          <div className="space-y-2">
            {sessions.map(session => (
              <div key={session.id} className="text-white/80 text-sm">
                Session {session.id.slice(0, 8)}... - {session.status}
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <h2 className="text-xl font-semibold text-white mb-4">Messages ({messages.length})</h2>
          <div className="space-y-3">
            {messages.map(msg => (
              <div key={msg.id} className={`p-3 rounded ${
                msg.role === 'user' ? 'bg-blue-500/20 text-blue-100' : 'bg-purple-500/20 text-purple-100'
              }`}>
                <div className="text-xs opacity-70 mb-1">{msg.role}</div>
                <div className="text-sm">{msg.content}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
