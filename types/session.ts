export type SessionStatus = 'active' | 'completed' | 'error'

export interface SessionWithDetails {
  id: string
  agent_id: string
  agent_name: string
  start_time: string
  end_time: string | null
  status: SessionStatus
  messageCount: number
  totalTokens: number
  cost: number
}
