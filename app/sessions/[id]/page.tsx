"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { supabase } from "@/lib/supabase"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import type { Session, Message } from "@/types/database"

type SessionMetrics = {
  tokens_input: number
  tokens_output: number
  tokens_total: number
  cost: number
}

export default function SessionDetailPage() {
  const params = useParams()
  const sessionId = params.id as string

  const [session, setSession] = useState<Session | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [metrics, setMetrics] = useState<SessionMetrics>({
    tokens_input: 0,
    tokens_output: 0,
    tokens_total: 0,
    cost: 0,
  })
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

      // Sum all metric rows for this session (may be multiple)
      const { data: metricsData } = await supabase
        .from("metrics")
        .select("tokens_input, tokens_output, tokens_total, cost")
        .eq("session_id", sessionId)

      const totals = (metricsData || []).reduce(
        (acc, m) => ({
          tokens_input: acc.tokens_input + Number(m.tokens_input),
          tokens_output: acc.tokens_output + Number(m.tokens_output),
          tokens_total: acc.tokens_total + Number(m.tokens_total),
          cost: acc.cost + Number(m.cost),
        }),
        { tokens_input: 0, tokens_output: 0, tokens_total: 0, cost: 0 }
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
        <div className="text-[#e2e8f0] font-mono text-sm">LOADING SESSION…</div>
      </div>
    )
  }

  if (!session) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-[#ff3b47] font-mono text-sm">SESSION NOT FOUND</div>
      </div>
    )
  }

  // Estimated cost breakdown (70/30 split when no exact data)
  const inputTokens = metrics.tokens_input > 0 ? metrics.tokens_input : Math.round(metrics.tokens_total * 0.7)
  const outputTokens = metrics.tokens_output > 0 ? metrics.tokens_output : Math.round(metrics.tokens_total * 0.3)
  const inputCost = (inputTokens / 1_000_000) * 3
  const outputCost = (outputTokens / 1_000_000) * 15

  return (
    <div className="space-y-6">
      <Link href="/sessions">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Sessions
        </Button>
      </Link>

      {/* Session header + metrics summary */}
      <Card className="p-6">
        <div className="flex items-start justify-between gap-6 flex-wrap">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <h1 className="text-2xl font-bold text-[#e2e8f0]">Session Details</h1>
              <Badge variant={session.status === "active" ? "success" : "info"}>
                {session.status}
              </Badge>
            </div>
            <p className="text-[#64748b] text-xs font-mono">ID: {session.id}</p>
            <p className="text-[#64748b] text-xs font-mono mt-1">
              Started: {new Date(session.start_time).toLocaleString()}
            </p>
          </div>

          <div className="flex gap-8">
            <div className="text-center">
              <p className="text-2xl font-bold text-[#e2e8f0] font-mono">{messages.length}</p>
              <p className="text-[#64748b] text-xs font-mono uppercase tracking-wider mt-1">messages</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-[#e2e8f0] font-mono">
                {metrics.tokens_total > 0 ? `${(metrics.tokens_total / 1000).toFixed(1)}k` : "—"}
              </p>
              <p className="text-[#64748b] text-xs font-mono uppercase tracking-wider mt-1">tokens</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-[#00d084] font-mono">${metrics.cost.toFixed(4)}</p>
              <p className="text-[#64748b] text-xs font-mono uppercase tracking-wider mt-1">cost</p>
            </div>
          </div>
        </div>

        {/* Token breakdown */}
        {metrics.tokens_total > 0 && (
          <div className="mt-6 pt-4 border-t border-[#1e2d3d]">
            <p className="text-[#64748b] text-xs font-mono uppercase tracking-wider mb-3">Token Breakdown</p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-[#64748b] text-xs font-mono">Input Tokens</p>
                <p className="text-[#0077ff] text-sm font-mono font-bold mt-0.5">
                  {inputTokens.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-[#64748b] text-xs font-mono">Output Tokens</p>
                <p className="text-[#f5a623] text-sm font-mono font-bold mt-0.5">
                  {outputTokens.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-[#64748b] text-xs font-mono">Input Cost</p>
                <p className="text-[#e2e8f0] text-sm font-mono font-bold mt-0.5">${inputCost.toFixed(5)}</p>
              </div>
              <div>
                <p className="text-[#64748b] text-xs font-mono">Output Cost</p>
                <p className="text-[#e2e8f0] text-sm font-mono font-bold mt-0.5">${outputCost.toFixed(5)}</p>
              </div>
            </div>
            <p className="text-[#64748b] text-xs font-mono mt-3 opacity-60">
              * Estimated at Claude Sonnet 4.5 rates ($3/1M input, $15/1M output)
              {metrics.tokens_input === 0 && " · 70/30 input/output split applied"}
            </p>
          </div>
        )}
      </Card>

      {/* Message Thread */}
      <Card className="p-6">
        <h2 className="text-sm font-mono font-semibold text-[#e2e8f0] tracking-widest uppercase mb-6">
          Message Thread
        </h2>

        <div className="space-y-4 max-h-[700px] overflow-y-auto pr-1">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 gap-3">
              <div className="w-12 h-12 rounded-sm border border-[#1e2d3d] bg-[#080c14] flex items-center justify-center">
                <span className="text-[#64748b] font-mono text-lg">—</span>
              </div>
              <p className="text-[#64748b] text-sm font-mono">No messages recorded for this session</p>
            </div>
          ) : (
            messages.map(msg => {
              if (msg.role === "system") {
                return (
                  <div key={msg.id} className="flex justify-center">
                    <div className="max-w-[70%] text-center">
                      <p className="text-[#64748b] text-xs font-mono leading-relaxed">{msg.content}</p>
                      <p className="text-[#64748b] text-xs font-mono opacity-50 mt-1">
                        {new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                        {" · system"}
                      </p>
                    </div>
                  </div>
                )
              }

              const isUser = msg.role === "user"

              return (
                <div key={msg.id} className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[78%] flex flex-col ${isUser ? "items-end" : "items-start"}`}>
                    <div
                      className={`px-4 py-3 rounded-sm text-sm text-[#e2e8f0] leading-relaxed whitespace-pre-wrap border ${
                        isUser
                          ? "bg-[#0077ff15] border-[#0077ff30]"
                          : "bg-[#111827] border-[#1e2d3d]"
                      }`}
                    >
                      {msg.content}
                    </div>
                    <p className="text-[#64748b] text-xs font-mono mt-1 px-1">
                      {new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                      {" · "}{msg.role}
                    </p>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </Card>
    </div>
  )
}
