export type AgentStatus = 'active' | 'idle' | 'error'

export interface AgentWithMetrics {
  id: string
  name: string
  status: AgentStatus
  model: string
  totalSessions: number
  totalMessages: number
  totalCost: number
}
