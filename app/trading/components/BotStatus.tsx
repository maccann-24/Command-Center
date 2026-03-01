"use client"

import { useEffect, useState } from "react"
import { Badge } from "@/components/ui/badge"

type BotHealth = {
  status: "healthy" | "degraded" | "offline"
  last_cycle_time?: string
  uptime_seconds?: number
}

export default function BotStatus() {
  const [health, setHealth] = useState<BotHealth>({ status: "offline" })
  const [loading, setLoading] = useState(true)

  // Fetch health status
  const fetchHealth = async () => {
    try {
      const res = await fetch("http://localhost:8000/health", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      })

      if (!res.ok) {
        setHealth({ status: "offline" })
        return
      }

      const data = await res.json()

      // Determine status from response
      if (data.status === "healthy" || data.healthy === true) {
        setHealth({
          status: "healthy",
          last_cycle_time: data.last_cycle_time,
          uptime_seconds: data.uptime_seconds,
        })
      } else {
        setHealth({ status: "degraded" })
      }
    } catch (error) {
      console.error("Failed to fetch bot health:", error)
      setHealth({ status: "offline" })
    } finally {
      setLoading(false)
    }
  }

  // Poll every 30 seconds
  useEffect(() => {
    fetchHealth()
    const interval = setInterval(fetchHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  // Status badge styling
  const badgeVariant =
    health.status === "healthy"
      ? "success"
      : health.status === "degraded"
      ? "warning"
      : "error"

  const statusText =
    health.status === "healthy"
      ? "🟢 Running"
      : health.status === "degraded"
      ? "🟡 Degraded"
      : "🔴 Offline"

  const statusColor =
    health.status === "healthy"
      ? "text-green-500"
      : health.status === "degraded"
      ? "text-yellow-500"
      : "text-red-500"

  if (loading) {
    return (
      <Badge variant="info" className="animate-pulse">
        Checking...
      </Badge>
    )
  }

  return (
    <div className="flex items-center gap-3">
      <Badge variant={badgeVariant} className={statusColor}>
        {statusText}
      </Badge>
      {health.last_cycle_time && (
        <span className="text-xs text-muted-foreground">
          Last cycle: {new Date(health.last_cycle_time).toLocaleTimeString()}
        </span>
      )}
    </div>
  )
}
