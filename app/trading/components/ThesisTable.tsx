"use client"

import { useState, useMemo } from "react"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import type { Thesis } from "@/lib/supabase/trading"
import { ChevronLeft, ChevronRight, ChevronDown, ChevronUp } from "lucide-react"

type ThesisTableProps = {
  theses: Thesis[]
}

export default function ThesisTable({ theses }: ThesisTableProps) {
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [minConviction, setMinConviction] = useState<number>(0)
  const [agentFilter, setAgentFilter] = useState<string>("all")

  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 20

  // Expanded rows
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set())

  // Get unique agents
  const agents = useMemo(() => {
    const agentSet = new Set(theses.map((t) => t.agent_id).filter(Boolean))
    return ["all", ...Array.from(agentSet).sort()]
  }, [theses])

  // Filter theses
  const filteredTheses = useMemo(() => {
    let filtered = theses

    // Status filter
    if (statusFilter !== "all") {
      filtered = filtered.filter((t) => t.status === statusFilter)
    }

    // Min conviction
    if (minConviction > 0) {
      filtered = filtered.filter((t) => t.conviction >= minConviction / 100)
    }

    // Agent filter
    if (agentFilter !== "all") {
      filtered = filtered.filter((t) => t.agent_id === agentFilter)
    }

    // Sort by created_at desc (newest first)
    return filtered.sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  }, [theses, statusFilter, minConviction, agentFilter])

  // Pagination
  const totalPages = Math.ceil(filteredTheses.length / itemsPerPage)
  const paginatedTheses = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage
    return filteredTheses.slice(start, start + itemsPerPage)
  }, [filteredTheses, currentPage])

  // Reset to page 1 when filters change
  useMemo(() => {
    setCurrentPage(1)
  }, [statusFilter, minConviction, agentFilter])

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

  // Edge color
  const edgeColor = (edge: number): string => {
    const edgePct = edge * 100
    if (edgePct > 10) return "text-green-500"
    if (edgePct >= 5) return "text-yellow-500"
    return "text-gray-500"
  }

  // Status badge variant
  const statusVariant = (status: string): any => {
    if (status === "executed") return "success"
    if (status === "rejected") return "error"
    if (status === "expired") return "default"
    return "info" // active
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Status */}
          <div>
            <label className="text-xs font-medium text-muted-foreground block mb-2">
              Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 bg-[#0d1117] border border-[#1e2d3d] rounded text-sm focus:outline-none focus:border-[#0077ff]"
            >
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="executed">Executed</option>
              <option value="rejected">Rejected</option>
              <option value="expired">Expired</option>
            </select>
          </div>

          {/* Min Conviction */}
          <div>
            <label className="text-xs font-medium text-muted-foreground block mb-2">
              Min Conviction: {minConviction}%
            </label>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={minConviction}
              onChange={(e) => setMinConviction(Number(e.target.value))}
              className="w-full h-2 bg-[#1e2d3d] rounded-lg appearance-none cursor-pointer accent-[#0077ff]"
            />
          </div>

          {/* Agent */}
          <div>
            <label className="text-xs font-medium text-muted-foreground block mb-2">
              Agent
            </label>
            <select
              value={agentFilter}
              onChange={(e) => setAgentFilter(e.target.value)}
              className="w-full px-3 py-2 bg-[#0d1117] border border-[#1e2d3d] rounded text-sm focus:outline-none focus:border-[#0077ff]"
            >
              {agents.map((agent) => (
                <option key={agent} value={agent}>
                  {agent === "all" ? "All Agents" : agent}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Results count */}
        <div className="mt-3 text-xs text-muted-foreground">
          Showing {paginatedTheses.length} of {filteredTheses.length} theses
        </div>
      </Card>

      {/* Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#0d1117] border-b border-[#1e2d3d]">
              <tr>
                <th className="w-8"></th>
                <th className="px-4 py-3 text-left">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Agent
                  </span>
                </th>
                <th className="px-4 py-3 text-left">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Market
                  </span>
                </th>
                <th className="px-4 py-3 text-right">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Edge %
                  </span>
                </th>
                <th className="px-4 py-3 text-right">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Conviction
                  </span>
                </th>
                <th className="px-4 py-3 text-center">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Action
                  </span>
                </th>
                <th className="px-4 py-3 text-center">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Status
                  </span>
                </th>
                <th className="px-4 py-3 text-right">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Created
                  </span>
                </th>
              </tr>
            </thead>
            <tbody>
              {paginatedTheses.map((thesis) => {
                const isExpanded = expandedRows.has(thesis.id)
                return (
                  <>
                    <tr
                      key={thesis.id}
                      className="border-b border-[#1e2d3d] hover:bg-[#0d1117] transition-colors cursor-pointer"
                      onClick={() => toggleRow(thesis.id)}
                    >
                      <td className="px-4 py-3">
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4 text-muted-foreground" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-muted-foreground" />
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-sm font-mono">
                          {thesis.agent_id}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-sm max-w-md truncate">
                          Market: {thesis.market_id.slice(0, 8)}...
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span
                          className={`text-sm font-mono font-semibold ${edgeColor(
                            thesis.edge
                          )}`}
                        >
                          {(thesis.edge * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="text-sm font-mono">
                          {(thesis.conviction * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <Badge
                          variant={
                            thesis.proposed_action.side === "YES"
                              ? "success"
                              : "error"
                          }
                        >
                          {thesis.proposed_action.side}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <Badge variant={statusVariant(thesis.status)}>
                          {thesis.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="text-sm text-muted-foreground">
                          {new Date(thesis.created_at).toLocaleDateString()}
                        </span>
                      </td>
                    </tr>

                    {/* Expanded row content */}
                    {isExpanded && (
                      <tr className="bg-[#0d1117]">
                        <td colSpan={8} className="px-4 py-4">
                          <div className="space-y-3 max-w-4xl">
                            <div>
                              <h4 className="text-xs font-semibold text-muted-foreground mb-1">
                                THESIS
                              </h4>
                              <p className="text-sm whitespace-pre-wrap">
                                {thesis.thesis_text}
                              </p>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <span className="text-xs text-muted-foreground">
                                  Fair Value:
                                </span>
                                <p className="font-mono">
                                  {(thesis.fair_value * 100).toFixed(1)}%
                                </p>
                              </div>
                              <div>
                                <span className="text-xs text-muted-foreground">
                                  Current Odds:
                                </span>
                                <p className="font-mono">
                                  {(thesis.current_odds * 100).toFixed(1)}%
                                </p>
                              </div>
                              <div>
                                <span className="text-xs text-muted-foreground">
                                  Horizon:
                                </span>
                                <p className="font-mono">
                                  {thesis.horizon || "—"}
                                </p>
                              </div>
                              <div>
                                <span className="text-xs text-muted-foreground">
                                  Size:
                                </span>
                                <p className="font-mono">
                                  {(thesis.proposed_action.size_pct * 100).toFixed(
                                    1
                                  )}
                                  %
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
          {paginatedTheses.length === 0 && (
            <div className="p-12 text-center text-muted-foreground">
              No theses found matching your filters
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-[#1e2d3d]">
            <div className="text-xs text-muted-foreground">
              Page {currentPage} of {totalPages}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 text-sm border border-[#1e2d3d] rounded hover:bg-[#0d1117] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() =>
                  setCurrentPage((p) => Math.min(totalPages, p + 1))
                }
                disabled={currentPage === totalPages}
                className="px-3 py-1 text-sm border border-[#1e2d3d] rounded hover:bg-[#0d1117] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </Card>
    </div>
  )
}
