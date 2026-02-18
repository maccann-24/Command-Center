import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    const { task_id } = await request.json()
    if (!task_id) return NextResponse.json({ error: 'task_id required' }, { status: 400 })

    // Delete the task — task_details cascade via FK
    const { error } = await supabase
      .from('tasks')
      .delete()
      .eq('id', task_id)

    if (error) return NextResponse.json({ error: error.message }, { status: 500 })

    return NextResponse.json({ success: true, task_id })
  } catch {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 })
  }
}
