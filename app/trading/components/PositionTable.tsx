"use client"

import { useState, useMemo } from "react"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import type { Position } from "@/lib/supabase/trading"
import { ChevronDown, ChevronUp, TrendingUp, TrendingDown } from "lucide-react"

type PositionTableProps = {
  positions: Position[]
}

type TabType = "open" | "closed" | "all"

export default function PositionTable({ positions }: PositionTableProps) {
  const [activeTab, setActiveTab] = useState<TabType>("open")
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set())

  // Filter positions by tab
  const filteredPositions = useMemo(() => {
    if (activeTab === "all") return positions
    return positions.filter((p) => p.status === activeTab)
  }, [positions, activeTab])

  // Toggle row expansion
  const toggleRow = (id: string) => {
    setExpandedRows((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  // Calculate duration
  const getDuration = (position: Position): string => {
    const start = new Date(position.opened_at).getTime()
    const end = position.closed_at
      ? new Date(position.closed_at).getTime()
      : Date.now()
    const diffMs = end - start
    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))

    if (days === 0 && hours === 0) return "<1h"
    if (days === 0) return `${hours}h`
    if (hours === 0) return `${days}d`
    return `${days}d ${hours}h`
  }

  // Calculate P&L percentage
  const getPnlPct = (position: Position): number => {
    const invested = position.shares * position.entry_price
    if (invested === 0) return 0
    return (position.pnl / invested) * 100
  }

  return (
    <div className="space-y-4">
      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-[#1e2d3d]">
        <button
          onClick={() => setActiveTab("open")}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === "open"
              ? "border-b-2 border-[#0077ff] text-white"
              : "text-muted-foreground hover:text-white"
          }`}
        >
          Open
        </button>
        <button
          onClick={() => setActiveTab("closed")}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === "closed"
              ? "border-b-2 border-[#0077ff] text-white"
              : "text-muted-foreground hover:text-white"
          }`}
        >
          Closed
        </button>
        <button
          onClick={() => setActiveTab("all")}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === "all"
              ? "border-b-2 border-[#0077ff] text-white"
              : "text-muted-foreground hover:text-white"
          }`}
        >
          All
        </button>
        <div className="ml-auto text-xs text-muted-foreground">
          {filteredPositions.length} positions
        </div>
      </div>

      {/* Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#0d1117] border-b border-[#1e2d3d]">
              <tr>
                <th className="w-8"></th>
                <th className="px-4 py-3 text-left">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Market
                  </span>
                </th>
                <th className="px-4 py-3 text-center">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Side
                  </span>
                </th>
                <th className="px-4 py-3 text-right">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Shares
                  </span>
                </th>
                <th className="px-4 py-3 text-right">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Entry / Current
                  </span>
                </th>
                <th className="px-4 py-3 text-right">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    P&L $
                  </span>
                </th>
                <th className="px-4 py-3 text-right">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    P&L %
                  </span>
                </th>
                <th className="px-4 py-3 text-center">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Stop-Loss
                  </span>
                </th>
                <th className="px-4 py-3 text-right">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Duration
                  </span>
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredPositions.map((position) => {
                const isExpanded = expandedRows.has(position.id)
                const pnlPct = getPnlPct(position)
                const isStoppedOut = position.status === "stopped_out"

                return (
                  <>
                    <tr
                      key={position.id}
                      className="border-b border-[#1e2d3d] hover:bg-[#0d1117] transition-colors cursor-pointer"
                      onClick={() => toggleRow(position.id)}
                    >
                      <td className="px-4 py-3">
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4 text-muted-foreground" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-muted-foreground" />
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-sm max-w-xs truncate">
                          {position.market?.question || `Market ${position.market_id.slice(0, 8)}...`}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <Badge
                          variant={position.side === "YES" ? "success" : "error"}
                        >
                          {position.side}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="text-sm font-mono">
                          {position.shares.toFixed(2)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="text-sm font-mono">
                          <div className="text-muted-foreground">
                            ${position.entry_price.toFixed(2)}
                          </div>
                          <div>${position.current_price.toFixed(2)}</div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span
                          className={`text-sm font-mono font-bold ${
                            position.pnl >= 0 ? "text-green-500" : "text-red-500"
                          }`}
                        >
                          ${position.pnl.toFixed(2)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-1">
                          {pnlPct >= 0 ? (
                            <TrendingUp className="w-3.5 h-3.5 text-green-500" />
                          ) : (
                            <TrendingDown className="w-3.5 h-3.5 text-red-500" />
                          )}
                          <span
                            className={`text-sm font-mono ${
                              pnlPct >= 0 ? "text-green-500" : "text-red-500"
                            }`}
                          >
                            {pnlPct >= 0 ? "+" : ""}
                            {pnlPct.toFixed(1)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center">
                        {isStoppedOut && (
                          <Badge variant="error">TRIGGERED</Badge>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="text-sm text-muted-foreground">
                          {getDuration(position)}
                        </span>
                      </td>
                    </tr>

                    {/* Expanded row content */}
                    {isExpanded && (
                      <tr className="bg-[#0d1117]">
                        <td colSpan={9} className="px-4 py-4">
                          <div className="space-y-3 max-w-4xl">
                            <div>
                              <h4 className="text-xs font-semibold text-muted-foreground mb-1">
                                ENTRY THESIS
                              </h4>
                              {position.thesis_id ? (
                                <p className="text-sm">
                                  Thesis ID: {position.thesis_id}
                                  <br />
                                  <span className="text-muted-foreground text-xs">
                                    (Full thesis details would require a separate lookup)
                                  </span>
                                </p>
                              ) : (
                                <p className="text-sm text-muted-foreground">
                                  No thesis linked to this position
                                </p>
                              )}
                            </div>

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <span className="text-xs text-muted-foreground">
                                  Status:
                                </span>
                                <p className="font-mono capitalize">
                                  {position.status}
                                </p>
                              </div>
                              <div>
                                <span className="text-xs text-muted-foreground">
                                  Opened:
                                </span>
                                <p className="font-mono text-xs">
                                  {new Date(position.opened_at).toLocaleString()}
                                </p>
                              </div>
                              {position.closed_at && (
                                <div>
                                  <span className="text-xs text-muted-foreground">
                                    Closed:
                                  </span>
                                  <p className="font-mono text-xs">
                                    {new Date(position.closed_at).toLocaleString()}
                                  </p>
                                </div>
                              )}
                              <div>
                                <span className="text-xs text-muted-foreground">
                                  Total Invested:
                                </span>
                                <p className="font-mono">
                                  ${(position.shares * position.entry_price).toFixed(2)}
                                </p>
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                )
              })}
            </tbody>
          </table>

          {/* Empty state */}
          {filteredPositions.length === 0 && (
            <div className="p-12 text-center text-muted-foreground">
              No {activeTab === "all" ? "" : activeTab} positions found
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}
