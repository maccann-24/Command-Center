"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { supabase } from "@/lib/supabase"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowLeft, User, Bot } from "lucide-react"
import Link from "next/link"
import type { Session, Message } from "@/types/database"

type SessionMetrics = {
  tokens_total: number
  cost: number
}

export default function SessionDetailPage() {
  const params = useParams()
  const sessionId = params.id as string

  const [session, setSession] = useState<Session | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [metrics, setMetrics] = useState<SessionMetrics>({ tokens_total: 0, cost: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      const { data: sessionData } = await supabase
        .from("sessions")
        .select("*")
        .eq("id", sessionId)
        .single()

      const { data: messagesData } = await supabase
        .from("messages")
        .select("*")
        .eq("session_id", sessionId)
        .order("timestamp", { ascending: true })

      // Sum all metric rows for this session (there may be multiple)
      const { data: metricsData } = await supabase
        .from("metrics")
        .select("tokens_total, cost")
        .eq("session_id", sessionId)

      const totals = (metricsData || []).reduce(
        (acc, m) => ({
          tokens_total: acc.tokens_total + Number(m.tokens_total),
          cost: acc.cost + Number(m.cost),
        }),
        { tokens_total: 0, cost: 0 }
      )

      setSession(sessionData)
      setMessages(messagesData || [])
      setMetrics(totals)
      setLoading(false)
    }
    if (sessionId) fetchData()
  }, [sessionId])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white text-lg">Loading session...</div>
      </div>
    )
  }

  if (!session) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white text-lg">Session not found</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Link href="/sessions">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Sessions
        </Button>
      </Link>

      <Card className="p-6">
        <div className="flex items-start justify-between gap-6 flex-wrap">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <h1 className="text-2xl font-bold text-white">Session Details</h1>
              <Badge variant={session.status === "active" ? "success" : "info"}>
                {session.status}
              </Badge>
            </div>
            <p className="text-white/50 text-xs font-mono">ID: {session.id}</p>
            <p className="text-white/40 text-xs mt-1">
              Started: {new Date(session.start_time).toLocaleString()}
            </p>
          </div>

          <div className="flex gap-8">
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{messages.length}</p>
              <p className="text-white/50 text-xs">messages</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-white">
                {metrics.tokens_total > 0 ? `${(metrics.tokens_total / 1000).toFixed(1)}k` : "—"}
              </p>
              <p className="text-white/50 text-xs">tokens</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-white">${metrics.cost.toFixed(4)}</p>
              <p className="text-white/50 text-xs">cost</p>
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="text-xl font-semibold text-white mb-6">Message Thread</h2>
        <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
          {messages.length === 0 ? (
            <p className="text-white/60 text-center py-12">No messages in this session</p>
          ) : (
            messages.map(msg => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
              >
                <div className={`p-2 rounded-full flex-shrink-0 h-fit ${
                  msg.role === "user" ? "bg-brand-primary/30" : "bg-brand-secondary/30"
                }`}>
                  {msg.role === "user" ? (
                    <User className="w-4 h-4 text-brand-primary" />
                  ) : (
                    <Bot className="w-4 h-4 text-brand-secondary" />
                  )}
                </div>

                <div className={`flex-1 max-w-[80%] ${msg.role === "user" ? "items-end" : "items-start"} flex flex-col`}>
                  <p className="text-xs text-white/40 mb-1">
                    {msg.role} · {new Date(msg.timestamp).toLocaleTimeString()}
                  </p>
                  <div className={`p-4 rounded-xl text-sm text-white leading-relaxed ${
                    msg.role === "user"
                      ? "bg-brand-primary/20 border border-brand-primary/30"
                      : "bg-white/10 border border-white/20"
                  }`}>
                    {msg.content}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  )
}
