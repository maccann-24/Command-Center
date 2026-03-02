"use client"

import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { AgentPerformance } from "@/lib/supabase/trading"
import { ChevronDown, ChevronUp, Trophy } from "lucide-react"

type SortKey = "rank" | "agent_id" | "theme" | "win_rate" | "pnl_7d" | "total_trades" | "capital_allocation"
type SortDirection = "asc" | "desc"

type AgentLeaderboardProps = {
  agents: AgentPerformance[]
}

export default function AgentLeaderboard({ agents }: AgentLeaderboardProps) {
  const [sortKey, setSortKey] = useState<SortKey>("win_rate")
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc")
  const [selectedTheme, setSelectedTheme] = useState<string>("all")

  // Handle column sorting
  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc")
    } else {
      setSortKey(key)
      setSortDirection("desc")
    }
  }

  // Filter by theme
  const filteredAgents = selectedTheme === "all"
    ? agents
    : agents.filter((a) => a.theme === selectedTheme)

  // Sort agents
  const sortedAgents = [...filteredAgents].sort((a, b) => {
    let aVal: any = a[sortKey as keyof AgentPerformance]
    let bVal: any = b[sortKey as keyof AgentPerformance]

    // Handle special cases
    if (sortKey === "rank") {
      aVal = agents.indexOf(a)
      bVal = agents.indexOf(b)
    }

    if (typeof aVal === "string") {
      return sortDirection === "asc"
        ? aVal.localeCompare(bVal)
        : bVal.localeCompare(aVal)
    }

    return sortDirection === "asc" ? aVal - bVal : bVal - aVal
  })

  // Get unique themes for filter dropdown
  const themes = Array.from(new Set(agents.map((a) => a.theme)))

  // Sort icon
  const SortIcon = ({ column }: { column: SortKey }) => {
    if (sortKey !== column) return null
    return sortDirection === "asc" ? (
      <ChevronUp className="w-3 h-3 inline ml-1" />
    ) : (
      <ChevronDown className="w-3 h-3 inline ml-1" />
    )
  }

  // Format agent name for display
  const formatAgentName = (agentId: string) => {
    return agentId
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ")
  }

  // Get rank color
  const getRankColor = (index: number) => {
    if (index === 0) return "text-yellow-500" // Gold
    if (index === 1) return "text-gray-400" // Silver
    if (index === 2) return "text-orange-500" // Bronze
    if (index >= sortedAgents.length - 3) return "text-red-500" // Bottom 3
    return "text-muted-foreground"
  }

  return (
    <div className="space-y-4">
      {/* Filter Dropdown */}
      <div className="flex items-center gap-2">
        <label className="text-sm text-muted-foreground">Filter by theme:</label>
        <select
          value={selectedTheme}
          onChange={(e) => setSelectedTheme(e.target.value)}
          className="px-3 py-1.5 rounded bg-secondary text-sm border border-border"
        >
          <option value="all">All Themes</option>
          {themes.map((theme) => (
            <option key={theme} value={theme}>
              {theme.split("_").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ")}
            </option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="rounded-md border">
        <table className="w-full">
          <thead className="bg-secondary/50">
            <tr className="border-b">
              <th
                className="px-4 py-3 text-left text-xs font-medium text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort("rank")}
              >
                Rank <SortIcon column="rank" />
              </th>
              <th
                className="px-4 py-3 text-left text-xs font-medium text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort("agent_id")}
              >
                Agent <SortIcon column="agent_id" />
              </th>
              <th
                className="px-4 py-3 text-left text-xs font-medium text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort("theme")}
              >
                Theme <SortIcon column="theme" />
              </th>
              <th
                className="px-4 py-3 text-right text-xs font-medium text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort("win_rate")}
              >
                Win Rate <SortIcon column="win_rate" />
              </th>
              <th
                className="px-4 py-3 text-right text-xs font-medium text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort("pnl_7d")}
              >
                7d P&L <SortIcon column="pnl_7d" />
              </th>
              <th
                className="px-4 py-3 text-right text-xs font-medium text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort("total_trades")}
              >
                Trades <SortIcon column="total_trades" />
              </th>
              <th
                className="px-4 py-3 text-right text-xs font-medium text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort("capital_allocation")}
              >
                Capital <SortIcon column="capital_allocation" />
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedAgents.map((agent, index) => (
              <tr key={agent.agent_id} className="border-b hover:bg-secondary/30 transition-colors">
                <td className={`px-4 py-3 text-sm font-semibold ${getRankColor(index)}`}>
                  {index === 0 && <Trophy className="w-4 h-4 inline mr-1" />}
                  #{index + 1}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">
                      {formatAgentName(agent.agent_id)}
                    </span>
                    {index === 0 && (
                      <Badge className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20 text-xs">
                        Top Performer
                      </Badge>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <Badge variant="default" className="text-xs">
                    {agent.theme.split("_").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ")}
                  </Badge>
                </td>
                <td className="px-4 py-3 text-right text-sm font-semibold">
                  {(agent.win_rate * 100).toFixed(1)}%
                </td>
                <td
                  className={`px-4 py-3 text-right text-sm font-semibold ${
                    agent.pnl_7d >= 0 ? "text-green-500" : "text-red-500"
                  }`}
                >
                  ${agent.pnl_7d >= 0 ? "+" : ""}
                  {agent.pnl_7d.toFixed(2)}
                </td>
                <td className="px-4 py-3 text-right text-sm text-muted-foreground">
                  {agent.total_trades}
                </td>
                <td className="px-4 py-3 text-right text-sm font-mono text-muted-foreground">
                  ${agent.capital_allocation.toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {sortedAgents.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          No agents found
        </div>
      )}
    </div>
  )
}
