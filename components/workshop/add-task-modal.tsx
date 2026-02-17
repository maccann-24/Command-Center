"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { supabase } from "@/lib/supabase"
import { Button } from "@/components/ui/button"
import { useToast } from "@/components/ui/toast"
import { X, Plus } from "lucide-react"
import { TaskPriority } from "@/types/database"

interface AddTaskModalProps {
  isOpen: boolean
  onClose: () => void
  onCreated: () => void
}

export function AddTaskModal({ isOpen, onClose, onCreated }: AddTaskModalProps) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [priority, setPriority] = useState<TaskPriority>("medium")
  const [saving, setSaving] = useState(false)
  const { showToast } = useToast()

  async function handleSubmit() {
    if (!title.trim()) {
      showToast("Please enter a task title", "error")
      return
    }

    setSaving(true)

    const { error } = await supabase.from("tasks").insert({
      title: title.trim(),
      description: description.trim(),
      priority,
      status: "queued",
      momentum_score: 50,
    })

    setSaving(false)

    if (error) {
      showToast("Failed to create task: " + error.message, "error")
    } else {
      showToast(`Task "${title.trim()}" created!`, "success")
      setTitle("")
      setDescription("")
      setPriority("medium")
      onCreated()
      onClose()
    }
  }

  function handleClose() {
    setTitle("")
    setDescription("")
    setPriority("medium")
    onClose()
  }

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
                       w-full max-w-md bg-slate-900/95 border border-white/20
                       rounded-2xl shadow-2xl backdrop-blur-xl p-6"
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-white">New Task</h2>
                <p className="text-white/50 text-sm mt-0.5">Add a task to the queue</p>
              </div>
              <button
                onClick={handleClose}
                className="p-2 rounded-lg hover:bg-white/10 transition-colors"
              >
                <X className="w-5 h-5 text-white/60" />
              </button>
            </div>

            {/* Form */}
            <div className="space-y-4">
              {/* Title */}
              <div className="space-y-1.5">
                <label className="text-white/70 text-sm">
                  Title <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSubmit()}
                  autoFocus
                  placeholder="What needs to be done?"
                  className="w-full bg-white/5 border border-white/20 rounded-xl px-4 py-3
                             text-white placeholder:text-white/30 outline-none
                             focus:border-brand-primary/60 transition-colors"
                />
              </div>

              {/* Description */}
              <div className="space-y-1.5">
                <label className="text-white/70 text-sm">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  placeholder="Optional details..."
                  className="w-full bg-white/5 border border-white/20 rounded-xl px-4 py-3
                             text-white placeholder:text-white/30 outline-none resize-none
                             focus:border-brand-primary/60 transition-colors"
                />
              </div>

              {/* Priority */}
              <div className="space-y-1.5">
                <label className="text-white/70 text-sm">Priority</label>
                <div className="flex gap-2">
                  {(["low", "medium", "high"] as TaskPriority[]).map((p) => (
                    <button
                      key={p}
                      onClick={() => setPriority(p)}
                      className={`flex-1 py-2 rounded-xl border text-sm font-medium capitalize transition-all ${
                        priority === p
                          ? p === "high"
                            ? "bg-red-500/20 border-red-500/50 text-red-300"
                            : p === "medium"
                            ? "bg-yellow-500/20 border-yellow-500/50 text-yellow-300"
                            : "bg-blue-500/20 border-blue-500/50 text-blue-300"
                          : "bg-white/5 border-white/15 text-white/50 hover:bg-white/10"
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3 mt-6">
              <Button variant="ghost" onClick={handleClose} className="flex-1">
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleSubmit}
                isLoading={saving}
                className="flex-1"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Task
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
