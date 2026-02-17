"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { supabase } from "@/lib/supabase"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/components/ui/toast"
import { X, Edit2, Save, Trash2, AlertTriangle, Play, CheckCircle } from "lucide-react"
import { Task, TaskPriority, TaskStatus } from "@/types/database"

interface TaskDetailModalProps {
  task: Task | null
  isOpen: boolean
  onClose: () => void
  onUpdated: () => void
  onDeleted: () => void
}

function getMomentumVariant(score: number): "success" | "warning" | "error" {
  if (score >= 70) return "success"
  if (score >= 40) return "warning"
  return "error"
}

export function TaskDetailModal({
  task,
  isOpen,
  onClose,
  onUpdated,
  onDeleted,
}: TaskDetailModalProps) {
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [saving, setSaving] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [starting, setStarting] = useState(false)
  const [completing, setCompleting] = useState(false)
  const { showToast } = useToast()

  // Sync local state when task changes
  function handleOpen(t: Task) {
    setTitle(t.title)
    setDescription(t.description || "")
    setEditing(false)
    setConfirmDelete(false)
  }

  // We use an effect-like pattern: when isOpen and task change, reset
  if (isOpen && task && !editing && title !== task.title) {
    handleOpen(task)
  }

  async function handleSave() {
    if (!task) return
    if (!title.trim()) {
      showToast("Title cannot be empty", "error")
      return
    }
    setSaving(true)
    const { error } = await supabase
      .from("tasks")
      .update({
        title: title.trim(),
        description: description.trim(),
        updated_at: new Date().toISOString(),
      })
      .eq("id", task.id)

    setSaving(false)
    if (error) {
      showToast("Failed to save: " + error.message, "error")
    } else {
      showToast("Task updated!", "success")
      setEditing(false)
      onUpdated()
    }
  }

  async function handleDelete() {
    if (!task) return
    if (!confirmDelete) {
      setConfirmDelete(true)
      return
    }
    setDeleting(true)
    const { error } = await supabase.from("tasks").delete().eq("id", task.id)
    setDeleting(false)
    if (error) {
      showToast("Failed to delete: " + error.message, "error")
    } else {
      showToast("Task deleted", "success")
      onDeleted()
      handleClose()
    }
  }

  async function handleStartTask() {
    if (!task) return
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
        showToast("Task started! Clawdbot is on it.", "success")
        onUpdated()
        handleClose()
      }
    } catch {
      showToast("Network error", "error")
    } finally {
      setStarting(false)
    }
  }

  async function handleComplete() {
    if (!task) return
    setCompleting(true)
    try {
      const res = await fetch("/api/tasks/complete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ taskId: task.id }),
      })
      const data = await res.json()
      if (!res.ok) {
        showToast(data.error ?? "Failed to complete task", "error")
      } else {
        showToast("Task marked complete!", "success")
        onUpdated()
        handleClose()
      }
    } catch {
      showToast("Network error", "error")
    } finally {
      setCompleting(false)
    }
  }

  function handleClose() {
    setEditing(false)
    setConfirmDelete(false)
    onClose()
  }

  if (!task) return null

  const createdAt = new Date(task.created_at).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50
                       w-full max-w-lg bg-slate-900/95 border border-white/20
                       rounded-2xl shadow-2xl backdrop-blur-xl p-6"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-5 gap-4">
              <div className="flex-1 min-w-0">
                {editing ? (
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    autoFocus
                    className="w-full bg-white/5 border border-white/20 rounded-xl px-3 py-2
                               text-white text-lg font-bold outline-none
                               focus:border-brand-primary/60 transition-colors"
                  />
                ) : (
                  <div className="flex items-center gap-2">
                    {task.status === "in_progress" && (
                      <span className="relative flex h-2.5 w-2.5 flex-shrink-0">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75" />
                        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-yellow-400" />
                      </span>
                    )}
                    <h2 className="text-xl font-bold text-white leading-snug">{task.title}</h2>
                  </div>
                )}
                <p className="text-white/40 text-xs mt-1">Created {createdAt}</p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                {!editing && (
                  <button
                    onClick={() => setEditing(true)}
                    className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                    title="Edit"
                  >
                    <Edit2 className="w-4 h-4 text-white/60" />
                  </button>
                )}
                <button
                  onClick={handleClose}
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                >
                  <X className="w-5 h-5 text-white/60" />
                </button>
              </div>
            </div>

            {/* Badges row */}
            <div className="flex flex-wrap gap-2 mb-5">
              <Badge variant={getMomentumVariant(task.momentum_score)}>
                ⚡ Momentum: {task.momentum_score}
              </Badge>
              <Badge variant="default" className="capitalize">
                {task.status.replace("_", " ")}
              </Badge>
              <Badge
                variant={
                  task.priority === "high"
                    ? "error"
                    : task.priority === "medium"
                    ? "warning"
                    : "info"
                }
                className="capitalize"
              >
                {task.priority} priority
              </Badge>
            </div>

            {/* Description */}
            <div className="mb-5">
              <label className="text-white/50 text-xs uppercase tracking-wider mb-2 block">
                Description
              </label>
              {editing ? (
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={4}
                  placeholder="Add a description..."
                  className="w-full bg-white/5 border border-white/20 rounded-xl px-4 py-3
                             text-white placeholder:text-white/30 outline-none resize-none
                             focus:border-brand-primary/60 transition-colors text-sm"
                />
              ) : (
                <p className="text-white/70 text-sm leading-relaxed whitespace-pre-wrap">
                  {task.description || (
                    <span className="text-white/30 italic">No description</span>
                  )}
                </p>
              )}
            </div>

            {/* Details grid */}
            <div className="grid grid-cols-2 gap-3 mb-6">
              <div className="bg-white/5 rounded-xl p-3">
                <p className="text-white/40 text-xs mb-1">Status</p>
                <p className="text-white text-sm font-medium capitalize">
                  {task.status.replace("_", " ")}
                </p>
              </div>
              <div className="bg-white/5 rounded-xl p-3">
                <p className="text-white/40 text-xs mb-1">Priority</p>
                <p className="text-white text-sm font-medium capitalize">{task.priority}</p>
              </div>
            </div>

            {/* Action buttons */}
            {editing ? (
              <div className="flex gap-3">
                <Button
                  variant="ghost"
                  onClick={() => {
                    setEditing(false)
                    setTitle(task.title)
                    setDescription(task.description || "")
                  }}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  onClick={handleSave}
                  isLoading={saving}
                  className="flex-1"
                >
                  <Save className="w-4 h-4 mr-2" />
                  Save Changes
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {/* Task execution buttons */}
                {task.status === "queued" && (
                  <Button
                    variant="primary"
                    onClick={handleStartTask}
                    isLoading={starting}
                    className="w-full bg-green-600 hover:bg-green-500 shadow-green-500/20"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    ▶ Start Task
                  </Button>
                )}

                {task.status === "in_progress" && (
                  <Button
                    variant="primary"
                    onClick={handleComplete}
                    isLoading={completing}
                    className="w-full bg-emerald-600 hover:bg-emerald-500 shadow-emerald-500/20"
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    ✓ Mark Complete
                  </Button>
                )}

                {/* Delete */}
                <div className="flex gap-3">
                  <Button
                    variant="ghost"
                    onClick={handleDelete}
                    isLoading={deleting}
                    className={`border transition-all ${
                      confirmDelete
                        ? "border-red-500/50 text-red-400 hover:bg-red-500/10"
                        : "border-white/10 text-white/50 hover:text-red-400 hover:border-red-500/30"
                    }`}
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    {confirmDelete ? "Confirm delete" : "Delete"}
                  </Button>
                  {confirmDelete && (
                    <Button
                      variant="ghost"
                      onClick={() => setConfirmDelete(false)}
                      className="text-white/50"
                    >
                      Cancel
                    </Button>
                  )}
                </div>
              </div>
            )}

            {confirmDelete && (
              <p className="text-red-400/70 text-xs mt-2 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                Click &quot;Confirm delete&quot; to permanently remove this task
              </p>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
