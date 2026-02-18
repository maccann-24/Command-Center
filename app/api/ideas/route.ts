import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET() {
  // Fetch tasks that have task_details with metadata->>'type' = 'idea'
  const { data, error } = await supabase
    .from('task_details')
    .select(`
      id,
      task_id,
      metadata,
      tasks (
        id,
        title,
        description,
        momentum_score,
        created_at
      )
    `)
    .eq('metadata->>type', 'idea')
    .order('created_at', { ascending: false })

  if (error) return NextResponse.json({ error: error.message }, { status: 500 })

  const ideas = (data || []).map((d: any) => ({
    id: d.task_id,
    detail_id: d.id,
    title: d.tasks?.title,
    description: d.tasks?.description,
    momentum: d.tasks?.momentum_score,
    preview: d.metadata?.preview,
    source: d.metadata?.source || 'twitter',
    source_author: d.metadata?.source_author || '@agent',
    deployed: d.metadata?.deployed === true,
    created_at: d.tasks?.created_at,
  }))

  return NextResponse.json({ ideas })
}
