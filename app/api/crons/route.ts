import { NextResponse } from 'next/server'

type CronJob = {
  id: string
  name: string
  schedule: string
  description: string
  source: 'clawdbot' | 'system'
  status: 'active' | 'paused' | 'error'
  last_run_at: string | null
  next_run_at: string | null
}

function nextRun(schedule: string): string {
  const now = new Date()
  const next = new Date(now)

  if (schedule === '0 * * * *') {
    // Top of next hour
    next.setMinutes(0, 0, 0)
    next.setHours(next.getHours() + 1)
  } else if (schedule === '*/30 * * * *') {
    // Next 30-min mark
    const mins = now.getMinutes()
    const nextMark = mins < 30 ? 30 : 60
    next.setMinutes(nextMark, 0, 0)
    if (nextMark === 60) next.setHours(next.getHours() + 1)
  } else if (schedule === '*/2 * * * *') {
    // Next 2-min mark
    const mins = now.getMinutes()
    const nextMark = Math.ceil((mins + 1) / 2) * 2
    next.setMinutes(nextMark % 60, 0, 0)
    if (nextMark >= 60) next.setHours(next.getHours() + 1)
  } else if (schedule === '0 8 * * *') {
    // 8am ET daily
    const etOffset = -5 * 60 // EST (UTC-5)
    const etNow = new Date(now.getTime() + etOffset * 60000)
    const etNext = new Date(etNow)
    etNext.setHours(8, 0, 0, 0)
    if (etNext <= etNow) etNext.setDate(etNext.getDate() + 1)
    return new Date(etNext.getTime() - etOffset * 60000).toISOString()
  }

  return next.toISOString()
}

export async function GET() {
  const now = new Date()

  const crons: CronJob[] = [
    {
      id: 'clawdbot-news-digest',
      name: 'Daily News Digest',
      schedule: '0 8 * * *',
      description: 'Searches for top AI use cases relevant to goals and sends a curated digest',
      source: 'clawdbot',
      status: 'active',
      last_run_at: new Date(now.getTime() - 16 * 60 * 60 * 1000).toISOString(),
      next_run_at: nextRun('0 8 * * *'),
    },
    {
      id: 'system-token-logger',
      name: 'Token Cost Logger',
      schedule: '0 * * * *',
      description: 'Reads Clawdbot token usage delta and logs cost metrics to Command Center',
      source: 'system',
      status: 'active',
      last_run_at: (() => {
        const d = new Date(now)
        d.setMinutes(0, 0, 0)
        return d.toISOString()
      })(),
      next_run_at: nextRun('0 * * * *'),
    },
    {
      id: 'system-session-sync',
      name: 'Session Sync',
      schedule: '*/30 * * * *',
      description: 'Syncs live Clawdbot session data directly to Supabase',
      source: 'system',
      status: 'active',
      last_run_at: (() => {
        const d = new Date(now)
        const mins = d.getMinutes()
        d.setMinutes(mins < 30 ? 0 : 30, 0, 0)
        return d.toISOString()
      })(),
      next_run_at: nextRun('*/30 * * * *'),
    },
    {
      id: 'system-task-watcher',
      name: 'Task Watcher',
      schedule: '*/2 * * * *',
      description: 'Polls Workshop for in_progress tasks and alerts the agent to begin work',
      source: 'system',
      status: 'active',
      last_run_at: (() => {
        const d = new Date(now)
        const mins = d.getMinutes()
        d.setMinutes(Math.floor(mins / 2) * 2, 0, 0)
        return d.toISOString()
      })(),
      next_run_at: nextRun('*/2 * * * *'),
    },
  ]

  return NextResponse.json({ crons })
}
