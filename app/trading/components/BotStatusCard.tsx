"use client"

import { useEffect, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { getBotHealth, getBotStatus, emergencyStop } from "@/lib/api/trading"
import type { BotHealth, BotStatus } from "@/lib/api/trading"
import { AlertTriangle, CheckCircle, XCircle, Clock } from "lucide-react"

export default function BotStatusCard() {
  const [health, setHealth] = useState<BotHealth | null>(null)
  const [status, setStatus] = useState<BotStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [showStopModal, setShowStopModal] = useState(false)
  const [stopConfirmText, setStopConfirmText] = useState("")
  const [stopping, setStopping] = useState(false)

  // Fetch status
  const fetchStatus = async () => {
    const [healthData, statusData] = await Promise.all([
      getBotHealth(),
      getBotStatus(),
    ])
    setHealth(healthData)
    setStatus(statusData)
    setLoading(false)
  }

  // Poll every 30 seconds
  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  // Handle emergency stop
  const handleEmergencyStop = async () => {
    if (stopConfirmText !== "STOP") return

    setStopping(true)
    const result = await emergencyStop()

    if (result.success) {
      alert("Bot stopped successfully")
      setShowStopModal(false)
      setStopConfirmText("")
      fetchStatus() // Refresh status
    } else {
      alert(`Failed to stop bot: ${result.message}`)
    }
    setStopping(false)
  }

  // Format uptime
  const formatUptime = (seconds: number | undefined): string => {
    if (!seconds) return "—"
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    if (hours === 0) return `${minutes}m`
    return `${hours}h ${minutes}m`
  }

  // Calculate next cycle ETA
  const nextCycleEta = status?.next_cycle_eta_seconds
    ? `${Math.max(0, status.next_cycle_eta_seconds)}s`
    : "—"

  if (loading) {
    return (
      <Card className="p-6">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-[#1e2d3d] rounded w-1/3"></div>
          <div className="h-8 bg-[#1e2d3d] rounded w-1/2"></div>
        </div>
      </Card>
    )
  }

  const isHealthy = health?.status === "healthy"
  const isDegraded = health?.status === "degraded"
  const isOffline = health?.status === "offline"

  return (
    <>
      <Card className="p-6">
        <div className="space-y-4">
          {/* Status Header */}
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Bot Status</h3>
            <Badge
              variant={
                isHealthy ? "success" : isDegraded ? "warning" : "error"
              }
              pulse={isHealthy}
            >
              {isHealthy && <CheckCircle className="w-3.5 h-3.5 mr-1" />}
              {isDegraded && <AlertTriangle className="w-3.5 h-3.5 mr-1" />}
              {isOffline && <XCircle className="w-3.5 h-3.5 mr-1" />}
              {isHealthy ? "Running" : isDegraded ? "Degraded" : "Offline"}
            </Badge>
          </div>

          {/* Status Grid */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-xs text-muted-foreground">Mode</p>
              <p className="font-mono font-semibold">
                {status?.mode || health?.mode || "—"}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Uptime</p>
              <p className="font-mono font-semibold">
                {formatUptime(
                  status?.uptime_seconds || health?.uptime_seconds
                )}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Last Cycle</p>
              <p className="font-mono font-semibold text-xs">
                {status?.last_cycle_time || health?.last_cycle_time
                  ? new Date(
                      status?.last_cycle_time || health?.last_cycle_time || ""
                    ).toLocaleTimeString()
                  : "—"}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Next Cycle</p>
              <p className="font-mono font-semibold flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {nextCycleEta}
              </p>
            </div>
          </div>

          {/* Additional Stats (if available) */}
          {status && (
            <div className="pt-4 border-t border-[#1e2d3d] grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-xs text-muted-foreground">Open Positions</p>
                <p className="font-mono font-semibold">
                  {status.positions_count ?? "—"}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Active Theses</p>
                <p className="font-mono font-semibold">
                  {status.theses_count ?? "—"}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Portfolio</p>
                <p className="font-mono font-semibold">
                  {status.portfolio_value
                    ? `$${status.portfolio_value.toFixed(2)}`
                    : "—"}
                </p>
              </div>
            </div>
          )}

          {/* Emergency Stop Button */}
          <button
            onClick={() => setShowStopModal(true)}
            disabled={isOffline}
            className="w-full px-4 py-2 text-sm bg-red-500/10 text-red-500 border border-red-500/30 rounded hover:bg-red-500/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Emergency Stop
          </button>
        </div>
      </Card>

      {/* Emergency Stop Modal */}
      {showStopModal && (
        <div
          className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"
          onClick={() => {
            if (!stopping) {
              setShowStopModal(false)
              setStopConfirmText("")
            }
          }}
        >
          <div
            className="max-w-md w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <Card className="p-6">
              <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-red-500">
                  Emergency Stop
                </h3>
                <p className="text-sm text-muted-foreground mt-2">
                  This will immediately stop the trading bot. All open
                  positions will remain, but no new trades will be executed.
                </p>
              </div>

              <div>
                <label className="text-xs font-medium text-muted-foreground block mb-2">
                  Type <code className="bg-[#0d1117] px-1 rounded">STOP</code>{" "}
                  to confirm:
                </label>
                <input
                  type="text"
                  value={stopConfirmText}
                  onChange={(e) => setStopConfirmText(e.target.value)}
                  className="w-full px-3 py-2 bg-[#0d1117] border border-[#1e2d3d] rounded text-sm focus:outline-none focus:border-[#0077ff]"
                  placeholder="STOP"
                  disabled={stopping}
                />
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    setShowStopModal(false)
                    setStopConfirmText("")
                  }}
                  disabled={stopping}
                  className="flex-1 px-4 py-2 text-sm border border-[#1e2d3d] rounded hover:bg-[#0d1117] transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleEmergencyStop}
                  disabled={stopConfirmText !== "STOP" || stopping}
                  className="flex-1 px-4 py-2 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {stopping ? "Stopping..." : "Stop Bot"}
                </button>
              </div>
            </div>
          </Card>
          </div>
        </div>
      )}
    </>
  )
}
