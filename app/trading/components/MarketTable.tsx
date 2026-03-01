"use client"

import { useState, useMemo } from "react"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import type { Market } from "@/lib/supabase/trading"
import { ChevronLeft, ChevronRight, ArrowUpDown } from "lucide-react"

type MarketTableProps = {
  markets: Market[]
}

type SortField = "volume_24h" | "liquidity_score" | "resolution_date" | "question"
type SortDirection = "asc" | "desc"

export default function MarketTable({ markets }: MarketTableProps) {
  // Filters
  const [categoryFilter, setCategoryFilter] = useState<string>("all")
  const [minVolume, setMinVolume] = useState<number>(0)
  const [tradeableOnly, setTradeableOnly] = useState<boolean>(false)

  // Sorting
  const [sortField, setSortField] = useState<SortField>("volume_24h")
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc")

  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 20

  // Get unique categories
  const categories = useMemo(() => {
    const cats = new Set(
      markets
        .map((m) => m.category)
        .filter((c): c is string => Boolean(c))
    )
    return ["all", ...Array.from(cats).sort()]
  }, [markets])

  // Filter and sort markets
  const filteredMarkets = useMemo(() => {
    let filtered = markets

    // Category filter
    if (categoryFilter !== "all") {
      filtered = filtered.filter((m) => m.category === categoryFilter)
    }

    // Min volume filter
    if (minVolume > 0) {
      filtered = filtered.filter((m) => (m.volume_24h ?? 0) >= minVolume)
    }

    // Tradeable only
    if (tradeableOnly) {
      filtered = filtered.filter((m) => !m.resolved)
    }

    // Sort
    filtered = [...filtered].sort((a, b) => {
      let aVal: any = a[sortField]
      let bVal: any = b[sortField]

      // Handle nulls
      if (aVal === null || aVal === undefined) aVal = 0
      if (bVal === null || bVal === undefined) bVal = 0

      // Handle dates
      if (sortField === "resolution_date") {
        aVal = aVal ? new Date(aVal).getTime() : 0
        bVal = bVal ? new Date(bVal).getTime() : 0
      }

      // Handle strings
      if (typeof aVal === "string") {
        return sortDirection === "asc"
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal)
      }

      // Handle numbers
      return sortDirection === "asc" ? aVal - bVal : bVal - aVal
    })

    return filtered
  }, [markets, categoryFilter, minVolume, tradeableOnly, sortField, sortDirection])

  // Pagination
  const totalPages = Math.ceil(filteredMarkets.length / itemsPerPage)
  const paginatedMarkets = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage
    return filteredMarkets.slice(start, start + itemsPerPage)
  }, [filteredMarkets, currentPage])

  // Reset to page 1 when filters change
  useMemo(() => {
    setCurrentPage(1)
  }, [categoryFilter, minVolume, tradeableOnly, sortField, sortDirection])

  // Toggle sort
  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc")
    } else {
      setSortField(field)
      setSortDirection("desc")
    }
  }

  // Calculate days to resolution
  const daysToResolution = (date: string | null): string => {
    if (!date) return "—"
    const days = Math.ceil(
      (new Date(date).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
    )
    if (days < 0) return "Resolved"
    if (days === 0) return "Today"
    if (days === 1) return "1 day"
    return `${days} days`
  }

  // Format volume
  const formatVolume = (vol: number | null): string => {
    if (!vol) return "$0"
    if (vol >= 1_000_000) return `$${(vol / 1_000_000).toFixed(1)}M`
    if (vol >= 1_000) return `$${(vol / 1_000).toFixed(1)}K`
    return `$${vol.toFixed(0)}`
  }

  // Category badge color
  const categoryColor = (cat: string | null): string => {
    if (!cat) return "default"
    const lowerCat = cat.toLowerCase()
    if (lowerCat.includes("polit")) return "info"
    if (lowerCat.includes("sport")) return "success"
    if (lowerCat.includes("crypto")) return "warning"
    return "default"
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Category */}
          <div>
            <label className="text-xs font-medium text-muted-foreground block mb-2">
              Category
            </label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full px-3 py-2 bg-[#0d1117] border border-[#1e2d3d] rounded text-sm focus:outline-none focus:border-[#0077ff]"
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat === "all" ? "All Categories" : cat}
                </option>
              ))}
            </select>
          </div>

          {/* Min Volume */}
          <div>
            <label className="text-xs font-medium text-muted-foreground block mb-2">
              Min Volume: ${minVolume.toLocaleString()}
            </label>
            <input
              type="range"
              min="0"
              max="100000"
              step="1000"
              value={minVolume}
              onChange={(e) => setMinVolume(Number(e.target.value))}
              className="w-full h-2 bg-[#1e2d3d] rounded-lg appearance-none cursor-pointer accent-[#0077ff]"
            />
          </div>

          {/* Tradeable Only */}
          <div className="flex items-end">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={tradeableOnly}
                onChange={(e) => setTradeableOnly(e.target.checked)}
                className="w-4 h-4 rounded border-[#1e2d3d] bg-[#0d1117] accent-[#0077ff]"
              />
              <span className="text-sm">Tradeable Only</span>
            </label>
          </div>
        </div>

        {/* Results count */}
        <div className="mt-3 text-xs text-muted-foreground">
          Showing {paginatedMarkets.length} of {filteredMarkets.length} markets
        </div>
      </Card>

      {/* Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#0d1117] border-b border-[#1e2d3d]">
              <tr>
                <th className="px-4 py-3 text-left">
                  <button
                    onClick={() => toggleSort("question")}
                    className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-white uppercase tracking-wide"
                  >
                    Question
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="px-4 py-3 text-left">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Category
                  </span>
                </th>
                <th className="px-4 py-3 text-center">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Yes
                  </span>
                </th>
                <th className="px-4 py-3 text-center">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    No
                  </span>
                </th>
                <th className="px-4 py-3 text-right">
                  <button
                    onClick={() => toggleSort("volume_24h")}
                    className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-white uppercase tracking-wide ml-auto"
                  >
                    Volume 24h
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="px-4 py-3 text-right">
                  <button
                    onClick={() => toggleSort("liquidity_score")}
                    className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-white uppercase tracking-wide ml-auto"
                  >
                    Liquidity
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="px-4 py-3 text-right">
                  <button
                    onClick={() => toggleSort("resolution_date")}
                    className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-white uppercase tracking-wide ml-auto"
                  >
                    Days Left
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              {paginatedMarkets.map((market) => (
                <tr
                  key={market.id}
                  className="border-b border-[#1e2d3d] hover:bg-[#0d1117] transition-colors"
                >
                  <td className="px-4 py-3">
                    <div
                      className="text-sm max-w-md truncate"
                      title={market.question}
                    >
                      {market.question}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={categoryColor(market.category) as any}>
                      {market.category || "—"}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="text-sm font-mono">
                      {market.yes_price
                        ? `${(market.yes_price * 100).toFixed(0)}%`
                        : "—"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="text-sm font-mono">
                      {market.no_price
                        ? `${(market.no_price * 100).toFixed(0)}%`
                        : "—"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-sm font-mono">
                      {formatVolume(market.volume_24h)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-sm font-mono">
                      {market.liquidity_score?.toFixed(2) ?? "—"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-sm">
                      {daysToResolution(market.resolution_date)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Empty state */}
          {paginatedMarkets.length === 0 && (
            <div className="p-12 text-center text-muted-foreground">
              No markets found matching your filters
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
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
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
