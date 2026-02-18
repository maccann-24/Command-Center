"use client"

import { useEffect, useState, useCallback } from "react"
import { Lightbulb, X, ChevronRight, AlertCircle, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"

interface Idea {
  id: string
  detail_id: string
  title: string
  description: string
  momentum: number
  preview: string
  source: string
  source_author: string
  deployed: boolean
  created_at: string
}

type Filter = "all" | "pending" | "deployed"

function MomentumBadge({ score }: { score: number }) {
  const color =
    score >= 80
      ? "bg-green-500/20 text-green-400 border-green-500/30"
      : score >= 60
      ? "bg-amber-500/20 text-amber-400 border-amber-500/30"
      : "bg-red-500/20 text-red-400 border-red-500/30"
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold border ${color} tabular-nums`}
    >
      {score}
    </span>
  )
}

function IdeaCard({
  idea,
  onDeploy,
  onDismiss,
}: {
  idea: Idea
  onDeploy: (id: string) => Promise<void>
  onDismiss: (id: string) => Promise<void>
}) {
  const [deploying, setDeploying] = useState(false)
  const [dismissing, setDismissing] = useState(false)
  const [localDeployed, setLocalDeployed] = useState(idea.deployed)

  const handleDeploy = async () => {
    setDeploying(true)
    await onDeploy(idea.id)
    setLocalDeployed(true)
    setDeploying(false)
  }

  const handleDismiss = async () => {
    setDismissing(true)
    await onDismiss(idea.id)
    setDismissing(false)
  }

  return (
    <Card className="bg-[#0d1117] border border-[#1e2d3d] hover:border-[#2a3f55] transition-colors p-4 md:p-5">
      {/* Header row */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <MomentumBadge score={idea.momentum} />
          <span className="text-white font-semibold text-sm md:text-base">{idea.title}</span>
          {localDeployed && (
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-green-500/20 text-green-400 border border-green-500/30">
              DEPLOYED ✓
            </span>
          )}
        </div>
        <button
          onClick={handleDismiss}
          disabled={dismissing}
          className="flex-shrink-0 p-1 rounded text-[#64748b] hover:text-white hover:bg-[#1e2d3d] transition-colors disabled:opacity-50"
          title="Dismiss"
        >
          {dismissing ? (
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <X className="w-3.5 h-3.5" />
          )}
        </button>
      </div>

      {/* Description */}
      <p className="text-[#8b9cb8] text-sm mb-3">{idea.description}</p>

      {/* Preview */}
      {idea.preview && (
        <div className="bg-[#0a0f16] border border-[#1e2d3d] rounded px-3 py-2 mb-4">
          <span className="text-[#64748b] text-xs font-mono">Preview: </span>
          <span className="text-[#a0b4cc] text-xs italic">&ldquo;{idea.preview}&rdquo;</span>
        </div>
      )}

      {/* Footer row */}
      <div className="flex items-center justify-between gap-3">
        <span className="text-[#64748b] text-xs">
          Source:{" "}
          <span className="text-[#8b9cb8] capitalize">{idea.source}</span>
          {" · "}
          <span className="text-[#8b9cb8]">AI use case</span>
        </span>

        {localDeployed ? (
          <Button
            disabled
            size="sm"
            className="bg-green-500/20 text-green-400 border border-green-500/30 cursor-default hover:bg-green-500/20 text-xs px-3 py-1 h-auto"
          >
            Deployed ✓
          </Button>
        ) : (
          <Button
            onClick={handleDeploy}
            disabled={deploying}
            size="sm"
            className="bg-[#0077ff] hover:bg-[#0066dd] text-white text-xs px-3 py-1 h-auto flex items-center gap-1"
          >
            {deploying ? (
              <RefreshCw className="w-3 h-3 animate-spin" />
            ) : (
              <>
                Deploy <ChevronRight className="w-3 h-3" />
              </>
            )}
          </Button>
        )}
      </div>
    </Card>
  )
}

export default function IdeasPage() {
  const [ideas, setIdeas] = useState<Idea[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<Filter>("all")
  const [dismissed, setDismissed] = useState<Set<string>>(new Set())

  const fetchIdeas = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("/api/ideas")
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || "Failed to fetch ideas")
      setIdeas(data.ideas || [])
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchIdeas()
  }, [fetchIdeas])

  const handleDeploy = async (id: string) => {
    await fetch("/api/ideas/deploy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: id }),
    })
    // Update local state
    setIdeas((prev) =>
      prev.map((idea) => (idea.id === id ? { ...idea, deployed: true } : idea))
    )
  }

  const handleDismiss = async (id: string) => {
    await fetch("/api/ideas/dismiss", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: id }),
    })
    setDismissed((prev) => new Set([...prev, id]))
  }

  const visibleIdeas = ideas
    .filter((idea) => !dismissed.has(idea.id))
    .filter((idea) => {
      if (filter === "pending") return !idea.deployed
      if (filter === "deployed") return idea.deployed
      return true
    })

  const filters: { key: Filter; label: string }[] = [
    { key: "all", label: "All" },
    { key: "pending", label: "Pending" },
    { key: "deployed", label: "Deployed" },
  ]

  return (
    <div className="min-h-screen bg-[#060a0f] text-white p-4 md:p-8">
      {/* Header */}
      <div className="flex items-start justify-between mb-8 flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Lightbulb className="w-5 h-5 text-[#0077ff]" />
            <h1 className="text-xl font-bold tracking-wide">Ideas Feed</h1>
          </div>
          <p className="text-[#64748b] text-sm font-mono">AI use cases surfaced for you</p>
        </div>

        {/* Filter tabs */}
        <div className="flex items-center gap-1 bg-[#0d1117] border border-[#1e2d3d] rounded-lg p-1">
          {filters.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setFilter(key)}
              className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
                filter === key
                  ? "bg-[#0077ff] text-white"
                  : "text-[#64748b] hover:text-white hover:bg-[#1e2d3d]"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center h-48 text-[#64748b]">
          <RefreshCw className="w-5 h-5 animate-spin mr-2" />
          <span className="text-sm font-mono">Loading ideas...</span>
        </div>
      ) : error ? (
        <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <div>
            <p className="text-red-400 text-sm font-medium">Failed to load ideas</p>
            <p className="text-red-400/70 text-xs mt-0.5">{error}</p>
          </div>
          <Button
            onClick={fetchIdeas}
            size="sm"
            variant="ghost"
            className="ml-auto border-red-500/30 text-red-400 hover:bg-red-500/10"
          >
            Retry
          </Button>
        </div>
      ) : visibleIdeas.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 text-center">
          <Lightbulb className="w-10 h-10 text-[#1e2d3d] mb-4" />
          <p className="text-[#64748b] text-sm">No ideas yet</p>
          <p className="text-[#3d5166] text-xs mt-1">
            The agent will surface ideas from your Twitter searches
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3 max-w-3xl">
          {visibleIdeas.map((idea) => (
            <IdeaCard
              key={idea.id}
              idea={idea}
              onDeploy={handleDeploy}
              onDismiss={handleDismiss}
            />
          ))}
        </div>
      )}
    </div>
  )
}
