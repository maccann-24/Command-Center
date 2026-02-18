import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET() {
  const { data, error } = await supabase
    .from('tasks')
    .select('*')
    .order('created_at', { ascending: false })
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json({ tasks: data })
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { title, description, status, priority, assigned_agent_id } = body

    if (!title) {
      return NextResponse.json({ error: 'title is required' }, { status: 400 })
    }

    const { data: task, error: taskError } = await supabase
      .from('tasks')
      .insert({
        title,
        description: description || null,
        status: status || 'queued',
        priority: priority || 'medium',
        momentum_score: 0,
        assigned_agent_id: assigned_agent_id || null,
      })
      .select()
      .single()

    if (taskError) return NextResponse.json({ error: taskError.message }, { status: 500 })

    // Recalculate momentum after insert
    try {
      await fetch(`${process.env.NEXT_PUBLIC_APP_URL || 'https://command-center-dm3n.vercel.app'}/api/tasks/calculate-momentum`, {
        method: 'POST'
      })
    } catch {
      // non-fatal
    }

    return NextResponse.json({ success: true, task }, { status: 201 })
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
