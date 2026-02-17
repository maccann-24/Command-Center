"use client"

import { useEffect, useState, useCallback, useRef } from "react"
import { supabase } from "@/lib/supabase"
import { Task, TaskStatus } from "@/types/database"
import { KanbanColumn } from "@/components/workshop/kanban-column"
import { AddTaskModal } from "@/components/workshop/add-task-modal"
import { TaskDetailModal } from "@/components/workshop/task-detail-modal"
import { Layers, AlertCircle, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"

const COLUMNS: { status: TaskStatus; title: string; color: string }[] = [
  { status: "queued", title: "Queued", color: "bg-blue-400" },
  { status: "in_progress", title: "In Progress", color: "bg-yellow-400" },
  { status: "done", title: "Done", color: "bg-green-400" },
]

export default function WorkshopPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [tableError, setTableError] = useState(false)
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [recalculating, setRecalculating] = useState(false)
  const [liveFlash, setLiveFlash] = useState(false)
  const liveFlashTimeout = useRef<ReturnType<typeof setTimeout> | null>(null)

  const recalculateMomentum = useCallback(async () => {
    setRecalculating(true)
    try {
      await fetch("/api/tasks/calculate-momentum", { method: "POST" })
    } catch {
      // non-fatal
    } finally {
      setRecalculating(false)
    }
  }, [])

  const flashLive = useCallback(() => {
    setLiveFlash(true)
    if (liveFlashTimeout.current) clearTimeout(liveFlashTimeout.current)
    liveFlashTimeout.current = setTimeout(() => setLiveFlash(false), 1500)
  }, [])

  const fetchTasks = useCallback(async () => {
    const { data, error } = await supabase
      .from("tasks")
      .select("*")
      .order("created_at", { ascending: false })

    if (error) {
      if (
        error.code === "42P01" ||
        error.message?.includes("does not exist") ||
        error.message?.includes("relation")
      ) {
        setTableError(true)
      }
      setTasks([])
    } else {
      setTableError(false)
      setTasks(data ?? [])
    }
    setLoading(false)
  }, [])

  // On first load: recalculate momentum then fetch
  useEffect(() => {
    recalculateMomentum().then(fetchTasks)
  }, [recalculateMomentum, fetchTasks])

  // Realtime subscription for tasks table
  useEffect(() => {
    const channel = supabase
      .channel("workshop-tasks-changes")
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "tasks" },
        () => {
          flashLive()
          fetchTasks()
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [fetchTasks, flashLive])

  // Cleanup flash timeout on unmount
  useEffect(() => {
    return () => {
      if (liveFlashTimeout.current) clearTimeout(liveFlashTimeout.current)
    }
  }, [])

  async function handleRecalculate() {
    setRecalculating(true)
    try {
      await fetch("/api/tasks/calculate-momentum", { method: "POST" })
      await fetchTasks()
    } catch {
      // non-fatal
    } finally {
      setRecalculating(false)
    }
  }

  // Sort queued by momentum_score descending; others stay as-is
  function tasksByStatus(status: TaskStatus): Task[] {
    const filtered = tasks.filter((t) => t.status === status)
    if (status === "queued") {
      return [...filtered].sort((a, b) => b.momentum_score - a.momentum_score)
    }
    return filtered
  }

  // The top-momentum queued task gets the persistent Start button
  const topMomentumId = tasksByStatus("queued")[0]?.id ?? null

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-white/5 border border-white/10">
            <Layers className="w-6 h-6 text-white/70" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Workshop</h1>
            <p className="text-white/50 text-sm mt-0.5">Kanban task board</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* LIVE indicator */}
          <div className="flex items-center gap-1.5 px-2 py-1">
            <span
              className={`text-xs font-mono transition-colors duration-300 ${
                liveFlash ? "text-[#00d084]" : "text-[#64748b]"
              }`}
            >
              ●
            </span>
            <span
              className={`text-xs font-mono transition-colors duration-300 ${
                liveFlash ? "text-[#00d084]" : "text-[#64748b]"
              }`}
            >
              LIVE
            </span>
          </div>

          {/* Recalculate momentum button */}
          <Button
            variant="secondary"
            size="sm"
            onClick={handleRecalculate}
            disabled={recalculating || loading}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${recalculating ? "animate-spin" : ""}`} />
            {recalculating ? "Recalculating…" : "Recalculate Momentum"}
          </Button>
        </div>
      </div>

      {/* Error / empty state when table doesn't exist */}
      {tableError && (
        <div className="flex items-center gap-3 p-4 rounded-2xl border border-yellow-500/30 bg-yellow-500/10">
          <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0" />
          <div>
            <p className="text-yellow-300 text-sm font-medium">Tasks table not found</p>
            <p className="text-yellow-300/60 text-xs mt-0.5">
              Create a <code className="font-mono bg-yellow-500/10 px-1 rounded">tasks</code> table in
              Supabase to get started. Showing empty state for now.
            </p>
          </div>
        </div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="grid grid-cols-3 gap-6">
          {COLUMNS.map((col) => (
            <div key={col.status} className="space-y-3">
              <div className="h-5 w-32 bg-white/10 rounded-full animate-pulse" />
              {[1, 2].map((i) => (
                <div key={i} className="h-24 bg-white/5 rounded-2xl border border-white/10 animate-pulse" />
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Kanban board */}
      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
          {COLUMNS.map((col) => (
            <KanbanColumn
              key={col.status}
              title={col.title}
              status={col.status}
              tasks={tasksByStatus(col.status)}
              statusColor={col.color}
              topMomentumId={col.status === "queued" ? topMomentumId : null}
              onAddTask={col.status === "queued" ? () => setShowAddModal(true) : undefined}
              onTaskClick={(task) => setSelectedTask(task)}
              onTaskUpdated={fetchTasks}
            />
          ))}
        </div>
      )}

      {/* Add Task Modal */}
      <AddTaskModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onCreated={fetchTasks}
      />

      {/* Task Detail Modal */}
      <TaskDetailModal
        task={selectedTask}
        isOpen={!!selectedTask}
        onClose={() => setSelectedTask(null)}
        onUpdated={fetchTasks}
        onDeleted={() => {
          setSelectedTask(null)
          fetchTasks()
        }}
      />
    </div>
  )
}
