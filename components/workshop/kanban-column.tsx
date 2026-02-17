"use client"

import { Task, TaskStatus } from "@/types/database"
import { TaskCard } from "./task-card"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"

interface KanbanColumnProps {
  title: string
  status: TaskStatus
  tasks: Task[]
  statusColor: string
  onAddTask?: () => void
  onTaskClick: (task: Task) => void
}

const emptyStateMessages: Record<TaskStatus, string> = {
  queued: "No tasks queued yet",
  in_progress: "Nothing in progress",
  done: "No completed tasks",
}

export function KanbanColumn({
  title,
  status,
  tasks,
  statusColor,
  onAddTask,
  onTaskClick,
}: KanbanColumnProps) {
  return (
    <div className="flex flex-col min-h-0 flex-1">
      {/* Column header */}
      <div className="flex items-center justify-between mb-4 px-1">
        <div className="flex items-center gap-2.5">
          <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${statusColor}`} />
          <h3 className="text-white font-semibold text-sm">{title}</h3>
          <span className="bg-white/10 text-white/50 text-xs font-medium px-2 py-0.5 rounded-full">
            {tasks.length}
          </span>
        </div>

        {/* Add button only for Queued column */}
        {onAddTask && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onAddTask}
            className="text-white/50 hover:text-white h-7 px-2"
          >
            <Plus className="w-4 h-4" />
          </Button>
        )}
      </div>

      {/* Task list */}
      <div className="flex flex-col gap-3 flex-1">
        {tasks.length === 0 ? (
          <div className="flex items-center justify-center h-24 rounded-2xl border border-dashed border-white/10 text-white/30 text-sm">
            {emptyStateMessages[status]}
          </div>
        ) : (
          tasks.map((task) => (
            <TaskCard key={task.id} task={task} onClick={onTaskClick} />
          ))
        )}
      </div>
    </div>
  )
}
