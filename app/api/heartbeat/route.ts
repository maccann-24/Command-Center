import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { agent_id, current_task, bandwidth_pct } = body
    if (!agent_id) return NextResponse.json({ error: 'agent_id is required' }, { status: 400 })

    const now = new Date().toISOString()

    // Find existing active session for this agent
    const { data: existingSession } = await supabase
      .from('sessions')
      .select('id')
      .eq('agent_id', agent_id)
      .eq('status', 'active')
      .order('start_time', { ascending: false })
      .limit(1)
      .single()

    if (existingSession) {
      // Update heartbeat on existing session
      const { data, error } = await supabase
        .from('sessions')
        .update({
          last_heartbeat: now,
          current_task: current_task || null,
          bandwidth_pct: bandwidth_pct ?? 0,
        })
        .eq('id', existingSession.id)
        .select()
        .single()
      if (error) return NextResponse.json({ error: error.message }, { status: 500 })
      return NextResponse.json({ success: true, session: data, action: 'updated' })
    } else {
      // Create new active session
      const { data, error } = await supabase
        .from('sessions')
        .insert({
          agent_id,
          status: 'active',
          last_heartbeat: now,
          current_task: current_task || null,
          bandwidth_pct: bandwidth_pct ?? 0,
          start_time: now,
        })
        .select()
        .single()
      if (error) return NextResponse.json({ error: error.message }, { status: 500 })
      return NextResponse.json({ success: true, session: data, action: 'created' }, { status: 201 })
    }
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
