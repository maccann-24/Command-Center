import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    const { task_id } = await request.json()
    if (!task_id) return NextResponse.json({ error: 'task_id required' }, { status: 400 })

    // Fetch the current task_details for this task
    const { data: detail, error: fetchError } = await supabase
      .from('task_details')
      .select('id, metadata')
      .eq('task_id', task_id)
      .single()

    if (fetchError || !detail) {
      return NextResponse.json({ error: 'Task detail not found' }, { status: 404 })
    }

    // Merge deployed: true into existing metadata
    const updatedMetadata = { ...detail.metadata, deployed: true }

    const { error: updateError } = await supabase
      .from('task_details')
      .update({ metadata: updatedMetadata })
      .eq('id', detail.id)

    if (updateError) return NextResponse.json({ error: updateError.message }, { status: 500 })

    return NextResponse.json({ success: true, task_id })
  } catch {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 })
  }
}
