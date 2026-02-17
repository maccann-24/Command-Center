"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { supabase } from "@/lib/supabase"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/components/ui/toast"
import { ArrowLeft, Save, Trash2, AlertTriangle } from "lucide-react"
import Link from "next/link"

const MODELS = [
  "claude-sonnet-4-5",
  "claude-opus-4",
  "claude-haiku-4",
  "gpt-4",
  "gpt-4o",
  "gpt-3.5-turbo",
]

const STATUSES = ["active", "idle", "error"]

export default function AgentSettingsPage() {
  const params = useParams()
  const router = useRouter()
  const agentId = params.id as string
  const { showToast } = useToast()

  const [name, setName] = useState("")
  const [model, setModel] = useState("")
  const [status, setStatus] = useState("")
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [saved, setSaved] = useState(false)
  const [loading, setLoading] = useState(true)
  const [confirmDelete, setConfirmDelete] = useState(false)

  useEffect(() => {
    async function fetchAgent() {
      const { data } = await supabase
        .from("agents")
        .select("*")
        .eq("id", agentId)
        .single()

      if (data) {
        setName(data.name)
        setModel(data.model)
        setStatus(data.status)
      }
      setLoading(false)
    }
    if (agentId) fetchAgent()
  }, [agentId])

  async function handleSave() {
    setSaving(true)
    setSaved(false)

    const { error } = await supabase
      .from("agents")
      .update({ name, model, status, updated_at: new Date().toISOString() })
      .eq("id", agentId)

    setSaving(false)
    if (!error) {
      setSaved(true)
      showToast("Agent settings saved!", "success")
      setTimeout(() => setSaved(false), 3000)
    } else {
      showToast("Failed to save settings: " + error.message, "error")
    }
  }

  async function handleDelete() {
    if (!confirmDelete) {
      setConfirmDelete(true)
      return
    }
    setDeleting(true)
    await supabase.from("agents").delete().eq("id", agentId)
    showToast("Agent deleted", "success")
    router.push("/agents")
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white text-lg">Loading settings...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <Link href={`/agents/${agentId}`}>
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Agent
        </Button>
      </Link>

      <div>
        <h1 className="text-3xl font-bold text-white">Agent Settings</h1>
        <p className="text-white/60 mt-1">Edit configuration for this agent</p>
      </div>

      <Card className="p-6 space-y-6">
        {/* Name */}
        <div className="space-y-2">
          <label className="text-white/80 text-sm font-medium">Agent Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full bg-white/5 border border-white/20 rounded-xl px-4 py-3
                       text-white placeholder:text-white/30 outline-none
                       focus:border-brand-primary/60 transition-colors"
            placeholder="Agent name..."
          />
        </div>

        {/* Model */}
        <div className="space-y-2">
          <label className="text-white/80 text-sm font-medium">Model</label>
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

        {/* Status */}
        <div className="space-y-2">
          <label className="text-white/80 text-sm font-medium">Status</label>
          <div className="flex gap-3">
            {STATUSES.map(s => (
              <button
                key={s}
                onClick={() => setStatus(s)}
                className={`flex-1 py-2.5 rounded-xl border text-sm font-medium capitalize transition-all ${
                  status === s
                    ? s === "active"
                      ? "bg-green-500/20 border-green-500/50 text-green-300"
                      : s === "idle"
                      ? "bg-yellow-500/20 border-yellow-500/50 text-yellow-300"
                      : "bg-red-500/20 border-red-500/50 text-red-300"
                    : "bg-white/5 border-white/15 text-white/50 hover:bg-white/10"
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Save Button */}
        <Button
          variant="primary"
          onClick={handleSave}
          isLoading={saving}
          className="w-full"
        >
          <Save className="w-4 h-4 mr-2" />
          {saved ? "Saved! ✓" : "Save Changes"}
        </Button>
      </Card>

      {/* Danger Zone */}
      <Card className="p-6 border border-red-500/20">
        <h2 className="text-xl font-semibold text-red-400 mb-2 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5" />
          Danger Zone
        </h2>
        <p className="text-white/50 text-sm mb-4">
          Deleting this agent will remove all associated sessions, messages, and metrics. This cannot be undone.
        </p>
        <Button
          variant="ghost"
          onClick={handleDelete}
          isLoading={deleting}
          className="border border-red-500/30 text-red-400 hover:bg-red-500/10"
        >
          <Trash2 className="w-4 h-4 mr-2" />
          {confirmDelete ? "Click again to confirm delete" : "Delete Agent"}
        </Button>
        {confirmDelete && (
          <p className="text-red-400/70 text-xs mt-2">
            ⚠️ Click the button again to permanently delete this agent
          </p>
        )}
      </Card>
    </div>
  )
}
