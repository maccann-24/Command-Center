"use client"

import { useState, useMemo, useEffect } from "react"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import type { EventLog as EventLogType } from "@/lib/supabase/trading"
import { getEvents } from "@/lib/supabase/trading"
import { Download, ExternalLink } from "lucide-react"

type EventLogProps = {
  initialEvents: EventLogType[]
}

export default function EventLog({ initialEvents }: EventLogProps) {
  const [events, setEvents] = useState<EventLogType[]>(initialEvents)
  const [severityFilter, setSeverityFilter] = useState<string>("all")
  const [eventTypeFilter, setEventTypeFilter] = useState<string>("all")
  const [autoRefresh, setAutoRefresh] = useState<boolean>(true)

  // Get unique event types
  const eventTypes = useMemo(() => {
    const types = new Set(events.map((e) => e.event_type).filter(Boolean))
    return ["all", ...Array.from(types).sort()]
  }, [events])

  // Auto-refresh every 10 seconds
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(async () => {
      const newEvents = await getEvents({ limit: 100 })
      setEvents(newEvents)
    }, 10000)

    return () => clearInterval(interval)
  }, [autoRefresh])

  // Filter events
  const filteredEvents = useMemo(() => {
    let filtered = events

    // Severity filter
    if (severityFilter !== "all") {
      filtered = filtered.filter((e) => e.severity === severityFilter)
    }

    // Event type filter
    if (eventTypeFilter !== "all") {
      filtered = filtered.filter((e) => e.event_type === eventTypeFilter)
    }

    return filtered
  }, [events, severityFilter, eventTypeFilter])

  // Export to CSV
  const exportToCsv = () => {
    const headers = [
      "Timestamp",
      "Severity",
      "Event Type",
      "Message",
      "Market ID",
      "Thesis ID",
    ]
    const rows = filteredEvents.map((e) => [
      e.timestamp,
      e.severity,
      e.event_type,
      e.message || "",
      e.market_id || "",
      e.thesis_id || "",
    ])

    const csv = [
      headers.join(","),
      ...rows.map((row) =>
        row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(",")
      ),
    ].join("\n")

    const blob = new Blob([csv], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `event-log-${new Date().toISOString()}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Severity badge variant
  const severityVariant = (severity: string): any => {
    if (severity === "critical" || severity === "error") return "error"
    if (severity === "warning") return "warning"
    return "info"
  }

  // Relative timestamp
  const relativeTime = (timestamp: string): string => {
    try {
      const now = Date.now()
      const then = new Date(timestamp).getTime()
      const diffMs = now - then
      const diffSec = Math.floor(diffMs / 1000)
      const diffMin = Math.floor(diffSec / 60)
      const diffHour = Math.floor(diffMin / 60)
      const diffDay = Math.floor(diffHour / 24)

      if (diffSec < 60) return `${diffSec}s ago`
      if (diffMin < 60) return `${diffMin}m ago`
      if (diffHour < 24) return `${diffHour}h ago`
      return `${diffDay}d ago`
    } catch {
      return timestamp
    }
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Severity */}
          <div>
            <label className="text-xs font-medium text-muted-foreground block mb-2">
              Severity
            </label>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="w-full px-3 py-2 bg-[#0d1117] border border-[#1e2d3d] rounded text-sm focus:outline-none focus:border-[#0077ff]"
            >
              <option value="all">All Severities</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
              <option value="critical">Critical</option>
            </select>
          </div>

          {/* Event Type */}
          <div>
            <label className="text-xs font-medium text-muted-foreground block mb-2">
              Event Type
            </label>
            <select
              value={eventTypeFilter}
              onChange={(e) => setEventTypeFilter(e.target.value)}
              className="w-full px-3 py-2 bg-[#0d1117] border border-[#1e2d3d] rounded text-sm focus:outline-none focus:border-[#0077ff]"
            >
              {eventTypes.map((type) => (
                <option key={type} value={type}>
                  {type === "all" ? "All Event Types" : type}
                </option>
              ))}
            </select>
          </div>

          {/* Actions */}
          <div className="flex items-end gap-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="w-4 h-4 rounded border-[#1e2d3d] bg-[#0d1117] accent-[#0077ff]"
              />
              <span className="text-sm">Auto-refresh (10s)</span>
            </label>
            <button
              onClick={exportToCsv}
              className="ml-auto px-3 py-2 text-sm border border-[#1e2d3d] rounded hover:bg-[#0d1117] flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
          </div>
        </div>

        {/* Results count */}
        <div className="mt-3 text-xs text-muted-foreground">
          Showing {filteredEvents.length} of {events.length} events
        </div>
      </Card>

      {/* Event Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#0d1117] border-b border-[#1e2d3d]">
              <tr>
                <th className="px-4 py-3 text-left">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Time
                  </span>
                </th>
                <th className="px-4 py-3 text-left">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Severity
                  </span>
                </th>
                <th className="px-4 py-3 text-left">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Type
                  </span>
                </th>
                <th className="px-4 py-3 text-left">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Message
                  </span>
                </th>
                <th className="px-4 py-3 text-left">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Links
                  </span>
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.map((event) => (
                <tr
                  key={event.id}
                  className="border-b border-[#1e2d3d] hover:bg-[#0d1117] transition-colors"
                >
                  <td className="px-4 py-3">
                    <span className="text-xs text-muted-foreground" title={event.timestamp}>
                      {relativeTime(event.timestamp)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={severityVariant(event.severity)}>
                      {event.severity.toUpperCase()}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs font-mono">{event.event_type}</span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="text-sm max-w-2xl">
                      {event.message || (
                        <span className="text-muted-foreground italic">
                          No message
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2 text-xs">
                      {event.market_id && (
                        <a
                          href={`/trading/markets?search=${event.market_id}`}
                          className="text-[#0077ff] hover:underline flex items-center gap-1"
                          onClick={(e) => e.stopPropagation()}
                        >
                          Market
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                      {event.thesis_id && (
                        <a
                          href={`/trading/theses?search=${event.thesis_id}`}
                          className="text-[#0077ff] hover:underline flex items-center gap-1"
                          onClick={(e) => e.stopPropagation()}
                        >
                          Thesis
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                      {!event.market_id && !event.thesis_id && (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Empty state */}
          {filteredEvents.length === 0 && (
            <div className="p-12 text-center text-muted-foreground">
              No events found matching your filters
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}
