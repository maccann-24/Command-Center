export type Agent = {
  id: string
  name: string
  model: string
  status: "active" | "idle" | "error"
  created_at: string
  updated_at: string
}

export type Session = {
  id: string
  agent_id: string
  start_time: string
  end_time: string | null
  status: "active" | "completed" | "error"
  last_heartbeat: string | null
  current_task: string | null
  bandwidth_pct: number | null
  created_at: string
}

export type Message = {
  id: string
  session_id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: string
  created_at: string
}

export type Metric = {
  id: string
  session_id: string
  tokens_input: number
  tokens_output: number
  tokens_total: number
  cost: number
  duration_ms: number
  created_at: string
}

export type TaskStatus = "queued" | "in_progress" | "done"
export type TaskPriority = "low" | "medium" | "high"

export type Task = {
  id: string
  title: string
  description: string
  status: TaskStatus
  momentum_score: number
  priority: TaskPriority
  created_at: string
  updated_at: string
}
