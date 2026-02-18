"use client"

import { useEffect, useState, useCallback } from "react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Newspaper, RefreshCw, ExternalLink, Clock } from "lucide-react"

type NewsItem = {
  headline: string
  summary: string
  source: string
  category: string
  url?: string
}

const CATEGORY_COLORS: Record<string, string> = {
  "AI": "#0077ff",
  "Tech": "#0077ff",
  "Business": "#f5a623",
  "Politics": "#e74c3c",
  "Breaking": "#ff3b47",
  "Science": "#00d084",
  "Finance": "#f5a623",
  "World": "#9b59b6",
}

function categoryColor(cat: string): string {
  for (const [key, color] of Object.entries(CATEGORY_COLORS)) {
    if (cat.toLowerCase().includes(key.toLowerCase())) return color
  }
  return "#64748b"
}

function formatDate(iso: string | null): string {
  if (!iso) return "—"
  return new Date(iso).toLocaleDateString("en-US", {
    weekday: "long", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit"
  })
}

export default function NewsPage() {
  const [items, setItems] = useState<NewsItem[]>([])
  const [date, setDate] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const fetchNews = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true)
    try {
      const res = await fetch("/api/news")
      const data = await res.json()
      setItems(data.items || [])
      setDate(data.date || null)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => {
    fetchNews()
  }, [fetchNews])

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-white/5 border border-white/10">
            <Newspaper className="w-6 h-6 text-white/70" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">News Digest</h1>
            <p className="text-white/50 text-sm mt-0.5">Daily briefing · Top stories</p>
          </div>
        </div>
        <button
          onClick={() => fetchNews(true)}
          disabled={refreshing}
          className="p-2 rounded hover:bg-[#1e2d3d] transition-colors"
        >
          <RefreshCw className={`w-4 h-4 text-[#64748b] ${refreshing ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Date banner */}
      {date && (
        <div className="flex items-center gap-2 px-4 py-2.5 rounded-sm border border-[#1e2d3d] bg-[#0d1117]">
          <Clock className="w-3.5 h-3.5 text-[#0077ff]" />
          <p className="text-[#64748b] text-xs font-mono">
            Digest from <span className="text-[#e2e8f0]">{formatDate(date)}</span>
          </p>
        </div>
      )}

      {/* Stories */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="h-32 bg-white/5 rounded-2xl border border-white/10 animate-pulse" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <Card className="p-16 text-center">
          <Newspaper className="w-10 h-10 text-[#1e3a5f] mx-auto mb-4" />
          <p className="text-[#64748b] font-mono text-sm mb-2">No digest yet</p>
          <p className="text-[#1e3a5f] font-mono text-xs">
            The Daily News Digest runs at 8am ET — check back then
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {items.map((item, i) => {
            const color = categoryColor(item.category)
            return (
              <Card key={i} className="p-5 group">
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-[#64748b] text-xs font-mono">#{i + 1}</span>
                    <span
                      className="text-[10px] font-mono px-1.5 py-0.5 rounded-sm tracking-widest uppercase"
                      style={{
                        color,
                        backgroundColor: `${color}18`,
                        border: `1px solid ${color}30`
                      }}
                    >
                      {item.category}
                    </span>
                  </div>
                  {item.url && (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <ExternalLink className="w-3.5 h-3.5 text-[#64748b] hover:text-[#0077ff]" />
                    </a>
                  )}
                </div>

                <h3 className="text-[#e2e8f0] font-semibold text-sm mb-2 leading-snug">
                  {item.headline}
                </h3>

                <p className="text-[#64748b] text-xs font-mono leading-relaxed mb-3">
                  {item.summary}
                </p>

                <p className="text-[#1e3a5f] text-[10px] font-mono uppercase tracking-widest">
                  Source: {item.source}
                </p>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
