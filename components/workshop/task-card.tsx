"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Task } from "@/types/database"
import { GripVertical, ChevronUp, Minus, ChevronDown, Play } from "lucide-react"
import { useToast } from "@/components/ui/toast"

interface TaskCardProps {
  task: Task
  onClick: (task: Task) => void
  onUpdated?: () => void
  isTopMomentum?: boolean
}

function getMomentumVariant(score: number): "success" | "warning" | "error" {
  if (score >= 70) return "success"
  if (score >= 40) return "warning"
  return "error"
}

function getPriorityIcon(priority: Task["priority"]) {
  if (priority === "high") return <ChevronUp className="w-3.5 h-3.5 text-red-400" />
  if (priority === "medium") return <Minus className="w-3.5 h-3.5 text-yellow-400" />
  return <ChevronDown className="w-3.5 h-3.5 text-blue-400" />
}

function getPriorityLabel(priority: Task["priority"]) {
  if (priority === "high") return <span className="text-red-400 capitalize">{priority}</span>
  if (priority === "medium") return <span className="text-yellow-400 capitalize">{priority}</span>
  return <span className="text-blue-400 capitalize">{priority}</span>
}

export function TaskCard({ task, onClick, onUpdated, isTopMomentum = false }: TaskCardProps) {
  const [hovering, setHovering] = useState(false)
  const [starting, setStarting] = useState(false)
  const { showToast } = useToast()

  const isQueued = task.status === "queued"
  const isInProgress = task.status === "in_progress"
  const showStartButton = isQueued && (hovering || isTopMomentum)

  async function handleStart(e: React.MouseEvent) {
    e.stopPropagation()
    if (starting) return
    setStarting(true)
    try {
      const res = await fetch("/api/tasks/assign", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ taskId: task.id }),
      })
      const data = await res.json()
      if (!res.ok) {
        showToast(data.error ?? "Failed to start task", "error")
      } else {
        showToast("Task started!", "success")
        onUpdated?.()
      }
    } catch {
      showToast("Network error", "error")
    } finally {
      setStarting(false)
    }
  }

  return (
    <div
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
    >
    <Card
      variant="hover"
      onClick={() => onClick(task)}
      className="p-4 relative group"
    >
      <div className="flex items-start gap-2">
        {/* Drag handle (visual only) */}
        <GripVertical className="w-4 h-4 text-white/20 flex-shrink-0 mt-0.5 cursor-grab" />

        <div className="flex-1 min-w-0">
          {/* Title row with in-progress pulse */}
          <div className="flex items-center gap-2 mb-1.5">
            {isInProgress && (
              <span className="relative flex h-2 w-2 flex-shrink-0">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-yellow-400" />
              </span>
            )}
            <p className="text-white text-sm font-medium leading-snug line-clamp-2 flex-1">
              {task.title}
            </p>
          </div>

          {/* Description truncated */}
          {task.description && (
            <p className="text-white/40 text-xs line-clamp-2 mb-3">
              {task.description}
            </p>
          )}

          {/* Footer row */}
          <div className="flex items-center justify-between gap-2 flex-wrap">
            {/* Priority */}
            <div className="flex items-center gap-1 text-xs">
              {getPriorityIcon(task.priority)}
              {getPriorityLabel(task.priority)}
            </div>

            <div className="flex items-center gap-2">
              {/* Momentum badge */}
              <Badge variant={getMomentumVariant(task.momentum_score)} className="text-xs">
                ⚡ {task.momentum_score}
              </Badge>

              {/* Start button */}
              {showStartButton && (
                <button
                  onClick={handleStart}
                  disabled={starting}
                  title="Start task"
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium
                             bg-green-500/20 text-green-300 border border-green-500/30
                             hover:bg-green-500/30 transition-all disabled:opacity-50"
                >
                  <Play className="w-3 h-3" />
                  {starting ? "…" : "Start"}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </Card>
    </div>
  )
}
