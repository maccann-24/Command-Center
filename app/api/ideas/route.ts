import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

// GET /api/ideas — list ideas (tasks tagged with [IDEA] metadata)
export async function GET() {
  // Fetch task_details where metadata type = idea
  const { data: details, error: detailsError } = await supabase
    .from('task_details')
    .select('id, task_id, metadata, created_at, updated_at')
    .filter('metadata->>type', 'eq', 'idea')
    .order('created_at', { ascending: false })

  if (detailsError) return NextResponse.json({ error: detailsError.message }, { status: 500 })
  if (!details || details.length === 0) return NextResponse.json({ ideas: [] })

  // Fetch the corresponding tasks
  const taskIds = details.map((d: Record<string, unknown>) => d.task_id as string)
  const { data: tasks, error: tasksError } = await supabase
    .from('tasks')
    .select('id, title, description, momentum_score, created_at')
    .in('id', taskIds)

  if (tasksError) return NextResponse.json({ error: tasksError.message }, { status: 500 })

  const taskMap = new Map((tasks || []).map((t: Record<string, unknown>) => [t.id, t]))

  const ideas = details.map((d: Record<string, unknown>) => {
    const meta = (d.metadata as Record<string, unknown>) || {}
    const task = taskMap.get(d.task_id as string) || {}
    return {
      id: d.task_id as string,
      detail_id: d.id as string,
      title: (task as Record<string, unknown>).title as string,
      description: (task as Record<string, unknown>).description as string,
      momentum: (task as Record<string, unknown>).momentum_score as number || 0,
      preview: meta.preview as string || '',
      source: meta.source as string || 'twitter',
      source_author: meta.source_author as string || '@agent',
      deployed: meta.deployed === true,
      created_at: d.created_at as string,
    }
  })

  return NextResponse.json({ ideas })
}
