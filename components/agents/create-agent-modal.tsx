"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { supabase } from "@/lib/supabase"
import { Button } from "@/components/ui/button"
import { useToast } from "@/components/ui/toast"
import { X, Sparkles } from "lucide-react"

const MODELS = [
  "claude-sonnet-4-5",
  "claude-opus-4",
  "claude-haiku-4",
  "gpt-4",
  "gpt-4o",
  "gpt-3.5-turbo",
]

interface CreateAgentModalProps {
  isOpen: boolean
  onClose: () => void
  onCreated: () => void
}

export function CreateAgentModal({ isOpen, onClose, onCreated }: CreateAgentModalProps) {
  const [name, setName] = useState("")
  const [model, setModel] = useState("claude-sonnet-4-5")
  const [saving, setSaving] = useState(false)
  const { showToast } = useToast()

  async function handleCreate() {
    if (!name.trim()) {
      showToast("Please enter an agent name", "error")
      return
    }

    setSaving(true)

    const { error } = await supabase.from("agents").insert({
      name: name.trim(),
      model,
      status: "idle",
    })

    setSaving(false)

    if (error) {
      showToast("Failed to create agent: " + error.message, "error")
    } else {
      showToast(`Agent "${name.trim()}" created successfully!`, "success")
      setName("")
      setModel("claude-sonnet-4-5")
      onCreated()
      onClose()
    }
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
            onClick={onClose}
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
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-white">New Agent</h2>
                <p className="text-white/50 text-sm mt-0.5">Create a new AI agent to track</p>
              </div>
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-white/10 transition-colors"
              >
                <X className="w-5 h-5 text-white/60" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-white/70 text-sm">Agent Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleCreate()}
                  autoFocus
                  placeholder="e.g. Research Agent, Coding Assistant..."
                  className="w-full bg-white/5 border border-white/20 rounded-xl px-4 py-3
                             text-white placeholder:text-white/30 outline-none
                             focus:border-brand-primary/60 transition-colors"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-white/70 text-sm">Model</label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full bg-white/5 border border-white/20 rounded-xl px-4 py-3
                             text-white outline-none cursor-pointer
                             focus:border-brand-primary/60 transition-colors"
                >
                  {MODELS.map(m => (
                    <option key={m} value={m} className="bg-slate-900">{m}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <Button variant="ghost" onClick={onClose} className="flex-1">
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleCreate}
                isLoading={saving}
                className="flex-1"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Create Agent
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
