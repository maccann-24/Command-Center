"use client"

import { useEffect, useState, useCallback, useRef } from "react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CalendarClock, Terminal, RefreshCw } from "lucide-react"

type CronJob = {
  id: string
  name: string
  schedule: string
  description: string
  source: 'clawdbot' | 'system'
  status: 'active' | 'paused' | 'error'
  last_run_at: string | null
  next_run_at: string | null
}

const HUMAN_SCHEDULE: Record<string, string> = {
  "0 * * * *": "Every hour",
  "*/30 * * * *": "Every 30 min",
  "*/2 * * * *": "Every 2 min",
  "0 8 * * *": "Daily at 8am ET",
}

function humanSchedule(s: string): string {
  return HUMAN_SCHEDULE[s] || s
}

function formatTimeAgo(iso: string | null): string {
  if (!iso) return "—"
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

function formatTimeUntil(iso: string | null): string {
  if (!iso) return "—"
  const diff = Math.floor((new Date(iso).getTime() - Date.now()) / 1000)
  if (diff <= 0) return "now"
  if (diff < 60) return `in ${diff}s`
  if (diff < 3600) return `in ${Math.floor(diff / 60)}m`
  if (diff < 86400) return `in ${Math.floor(diff / 3600)}h`
  return `in ${Math.floor(diff / 86400)}d`
}

function CronCard({ job }: { job: CronJob }) {
  const [, setTick] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => setTick(t => t + 1), 10000)
    return () => clearInterval(interval)
  }, [])

  const statusVariant =
    job.status === "active" ? "success" :
    job.status === "paused" ? "warning" : "error"

  const sourceColor = job.source === "clawdbot" ? "#0077ff" : "#64748b"
  const sourceLabel = job.source === "clawdbot" ? "CLAWDBOT" : "SYSTEM"

  return (
    <Card className="p-5">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <h3 className="text-[#e2e8f0] font-mono font-semibold text-sm">{job.name}</h3>
            <span
              className="text-[10px] font-mono px-1.5 py-0.5 rounded-sm tracking-widest"
              style={{
                color: sourceColor,
                backgroundColor: `${sourceColor}18`,
                border: `1px solid ${sourceColor}30`
              }}
            >
              {sourceLabel}
            </span>
          </div>
          <p className="text-[#64748b] text-xs font-mono leading-relaxed">{job.description}</p>
        </div>
        <Badge variant={statusVariant} pulse={job.status === "active"}>
          {job.status.toUpperCase()}
        </Badge>
      </div>

      {/* Schedule */}
      <div className="flex items-center gap-2 mb-4">
        <CalendarClock className="w-3.5 h-3.5 text-[#0077ff] flex-shrink-0" />
        <span className="text-[#0077ff] text-xs font-mono font-medium">
          {humanSchedule(job.schedule)}
        </span>
        <span className="text-[#1e3a5f] text-[10px] font-mono">{job.schedule}</span>
      </div>

      {/* Timing grid */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-[#080c14] rounded-sm p-3 border border-[#1e2d3d]">
          <p className="text-[#64748b] text-[10px] font-mono uppercase tracking-widest mb-1">Last Run</p>
          <p className="text-[#94a3b8] text-sm font-mono font-bold">
            {formatTimeAgo(job.last_run_at)}
          </p>
          {job.last_run_at && (
            <p className="text-[#1e3a5f] text-[10px] font-mono mt-0.5">
              {new Date(job.last_run_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </p>
          )}
        </div>
        <div className="bg-[#080c14] rounded-sm p-3 border border-[#1e2d3d]">
          <p className="text-[#64748b] text-[10px] font-mono uppercase tracking-widest mb-1">Next Run</p>
          <p className="text-[#00d084] text-sm font-mono font-bold">
            {formatTimeUntil(job.next_run_at)}
          </p>
          {job.next_run_at && (
            <p className="text-[#1e3a5f] text-[10px] font-mono mt-0.5">
              {new Date(job.next_run_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </p>
          )}
        </div>
      </div>
    </Card>
  )
}

export default function CronsPage() {
  const [crons, setCrons] = useState<CronJob[]>([])
  const [loading, setLoading] = useState(true)
  const [liveFlash, setLiveFlash] = useState(false)
  const liveFlashTimeout = useRef<ReturnType<typeof setTimeout> | null>(null)

  const flashLive = useCallback(() => {
    setLiveFlash(true)
    if (liveFlashTimeout.current) clearTimeout(liveFlashTimeout.current)
    liveFlashTimeout.current = setTimeout(() => setLiveFlash(false), 1500)
  }, [])

  const fetchCrons = useCallback(async () => {
    const res = await fetch("/api/crons")
    const data = await res.json()
    setCrons(data.crons || [])
    setLoading(false)
    flashLive()
  }, [flashLive])

  useEffect(() => {
    fetchCrons()
    const interval = setInterval(() => fetchCrons(), 60000)
    return () => clearInterval(interval)
  }, [fetchCrons])

  useEffect(() => {
    return () => {
      if (liveFlashTimeout.current) clearTimeout(liveFlashTimeout.current)
    }
  }, [])

  const clawdbotCrons = crons.filter(c => c.source === "clawdbot")
  const systemCrons = crons.filter(c => c.source === "system")

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-white/5 border border-white/10">
            <CalendarClock className="w-6 h-6 text-white/70" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Cron Jobs</h1>
            <p className="text-white/50 text-sm mt-0.5">Scheduled background tasks</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-2 py-1">
            <span className={`text-xs font-mono transition-colors duration-300 ${liveFlash ? "text-[#00d084]" : "text-[#64748b]"}`}>●</span>
            <span className={`text-xs font-mono transition-colors duration-300 ${liveFlash ? "text-[#00d084]" : "text-[#64748b]"}`}>LIVE</span>
          </div>
          <button
            onClick={fetchCrons}
            className="p-1.5 rounded hover:bg-[#1e2d3d] transition-colors"
          >
            <RefreshCw className="w-4 h-4 text-[#64748b]" />
          </button>
        </div>
      </div>

      {/* Summary bar */}
      {!loading && (
        <div className="flex items-center gap-6 px-4 py-2.5 rounded-sm border border-[#1e2d3d] bg-[#0d1117]">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#00d084] inline-block" />
            <span className="text-[#64748b] text-xs font-mono">
              <span className="text-[#e2e8f0] font-bold">{crons.filter(c => c.status === "active").length}</span> active
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Terminal className="w-3 h-3 text-[#0077ff]" />
            <span className="text-[#64748b] text-xs font-mono">
              <span className="text-[#0077ff] font-bold">{clawdbotCrons.length}</span> clawdbot managed
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[#64748b] text-xs font-mono">
              <span className="text-[#94a3b8] font-bold">{systemCrons.length}</span> system crontab
            </span>
          </div>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-40 bg-white/5 rounded-2xl border border-white/10 animate-pulse" />
          ))}
        </div>
      ) : (
        <>
          {/* Clawdbot managed */}
          {clawdbotCrons.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Terminal className="w-4 h-4 text-[#0077ff]" />
                <h2 className="text-xs font-mono font-semibold text-[#0077ff] tracking-widest uppercase">
                  Clawdbot Managed
                </h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {clawdbotCrons.map(job => <CronCard key={job.id} job={job} />)}
              </div>
            </div>
          )}

          {/* System crontab */}
          {systemCrons.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="w-4 h-4 flex items-center justify-center">
                  <span className="text-[#64748b] text-xs font-mono">$</span>
                </span>
                <h2 className="text-xs font-mono font-semibold text-[#64748b] tracking-widest uppercase">
                  System Crontab
                </h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {systemCrons.map(job => <CronCard key={job.id} job={job} />)}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
