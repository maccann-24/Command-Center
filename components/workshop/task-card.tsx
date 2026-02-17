"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Task } from "@/types/database"
import { GripVertical, ChevronUp, Minus, ChevronDown } from "lucide-react"

interface TaskCardProps {
  task: Task
  onClick: (task: Task) => void
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

export function TaskCard({ task, onClick }: TaskCardProps) {
  return (
    <Card variant="hover" onClick={() => onClick(task)} className="p-4">
      <div className="flex items-start gap-2">
        {/* Drag handle (visual only) */}
        <GripVertical className="w-4 h-4 text-white/20 flex-shrink-0 mt-0.5 cursor-grab" />

        <div className="flex-1 min-w-0">
          {/* Title */}
          <p className="text-white text-sm font-medium leading-snug line-clamp-2 mb-1.5">
            {task.title}
          </p>

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

            {/* Momentum badge */}
            <Badge variant={getMomentumVariant(task.momentum_score)} className="text-xs">
              ⚡ {task.momentum_score}
            </Badge>
          </div>
        </div>
      </div>
    </Card>
  )
}
